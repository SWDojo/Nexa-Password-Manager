import os
import sqlite3
from banner import clear_screen
from cryptography.fernet import Fernet, InvalidToken
from debug import log_info, log_error


class Storage:
    DB_FILENAME = "vault.db"

    # ----------------- Path helpers -----------------
    @staticmethod
    def get_data_dir():
        """Return platform-specific data dir and ensure it exists."""
        if os.name == "nt":
            base_dir = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        elif os.sys.platform == "darwin":
            base_dir = os.path.expanduser("~/Library/Application Support")
        else:
            base_dir = os.path.expanduser("~/.local/share")
        data_dir = os.path.join(base_dir, "Nexa")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir

    @staticmethod
    def get_db_path():
        return os.path.join(Storage.get_data_dir(), Storage.DB_FILENAME)

    # ----------------- DB init -----------------
    @staticmethod
    def init_db():
        """Initialize database if not exists, return connection."""
        conn = sqlite3.connect(Storage.get_db_path())
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                service BLOB NOT NULL,
                username BLOB NOT NULL,
                password BLOB NOT NULL
            )
        """)
        conn.commit()
        return conn

    # ----------------- CRUD -----------------
    @staticmethod
    def add_password(conn, fernet: Fernet, service: str, username: str, password: str):
        """Encrypt and insert a new credential."""
        username_enc = fernet.encrypt(username.encode("utf-8"))
        password_enc = fernet.encrypt(password.encode("utf-8"))
        service_enc = fernet.encrypt(service.encode("utf-8"))
        conn.execute(
            "INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)",
            (service_enc, username_enc, password_enc)
        )
        conn.commit()
        log_info(f"Added password for service: {service}")

    @staticmethod
    def get_all_services(conn, fernet: Fernet):
        """Return all decrypted service names."""
        cursor = conn.cursor()
        cursor.execute("SELECT service FROM passwords")
        rows = cursor.fetchall()
        services = []
        for row in rows:
            try:
                decrypted_service = fernet.decrypt(row[0]).decode("utf-8")
                services.append(decrypted_service)
            except InvalidToken:
                log_error("Failed to decrypt a service name.")
        return services

    @staticmethod
    def get_password(conn, fernet: Fernet, service: str):
        """Retrieve the decrypted username and password by scanning all entries."""
        cursor = conn.cursor()
        cursor.execute("SELECT service, username, password FROM passwords")
        rows = cursor.fetchall()
        for enc_service, enc_username, enc_password in rows:
            try:
                decrypted_service = fernet.decrypt(enc_service).decode("utf-8")
                if decrypted_service.lower() == service.lower():
                    username = fernet.decrypt(enc_username).decode("utf-8")
                    password = fernet.decrypt(enc_password).decode("utf-8")
                    return {"username": username, "password": password}
            except InvalidToken:
                continue
        log_error(f"Service not found or invalid key: {service}")
        return None

    @staticmethod
    def update_password(conn, fernet: Fernet, service: str, username=None, password=None, new_service=None):
        """Update credentials and optionally rename the service."""
        cursor = conn.cursor()
        cursor.execute("SELECT service FROM passwords")
        rows = cursor.fetchall()
        for row in rows:
            enc_service = row[0]
            try:
                decrypted_service = fernet.decrypt(enc_service).decode("utf-8")
                if decrypted_service.lower() == service.lower():
                    if username:
                        username_enc = fernet.encrypt(username.encode("utf-8"))
                        cursor.execute(
                            "UPDATE passwords SET username=? WHERE service=?",
                            (username_enc, enc_service)
                        )
                    if password:
                        password_enc = fernet.encrypt(password.encode("utf-8"))
                        cursor.execute(
                            "UPDATE passwords SET password=? WHERE service=?",
                            (password_enc, enc_service)
                        )
                    if new_service:
                        new_service_enc = fernet.encrypt(new_service.encode("utf-8"))
                        cursor.execute(
                            "UPDATE passwords SET service=? WHERE service=?",
                            (new_service_enc, enc_service)
                        )
                    conn.commit()
                    log_info(f"Updated credentials for: {service}")
                    return True
            except InvalidToken:
                continue
        log_error(f"Service not found for update: {service}")
        return False

    @staticmethod
    def delete_password(conn, fernet, service):
        """
        Delete a credential by scanning all entries for the service.
        Returns True if deleted, False otherwise.
        """
        cursor = conn.cursor()
        cursor.execute("SELECT service FROM passwords")
        rows = cursor.fetchall()
        for row in rows:
            enc_service = row[0]
            try:
                decrypted_service = fernet.decrypt(enc_service).decode("utf-8")
                if decrypted_service.lower() == service.lower():
                    cursor.execute("DELETE FROM passwords WHERE service=?", (enc_service,))
                    conn.commit()
                    if cursor.rowcount > 0:
                        log_info(f"Deleted service: {service}")
                        return True
                    else:
                        log_error(f"Delete failed for service: {service}")
                        return False
            except InvalidToken:
                log_error("Failed to decrypt a service name during deletion.")
                continue
        log_error(f"Service not found for deletion: {service}")
        return False