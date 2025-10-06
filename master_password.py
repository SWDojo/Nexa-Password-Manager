import os
import json
import base64
import getpass
import hashlib
from termcolor import colored
from banner import Banner, clear_screen
from debug import log_info, log_error
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend



class MasterPasswordManager:
    HASH_FILENAME = "master.hash"

    # ----------------- Path helpers -----------------
    @staticmethod
    def get_hash_path():
        """Return the path to the master password hash file."""
        if os.name == "nt":
            base_dir = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        elif os.sys.platform == "darwin":
            base_dir = os.path.expanduser("~/Library/Application Support")
        else:
            base_dir = os.path.expanduser("~/.local/share")
        data_dir = os.path.join(base_dir, "Nexa")
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, MasterPasswordManager.HASH_FILENAME)

    # ----------------- Internal helpers -----------------
    @staticmethod
    def _derive_hash(password: str, salt: bytes, iterations: int = 200_000) -> str:
        """Derive a base64-encoded password hash using PBKDF2HMAC."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )
        return base64.b64encode(kdf.derive(password.encode("utf-8"))).decode("utf-8")

    # ----------------- Main methods -----------------
    @staticmethod
    def is_set() -> bool:
        """Check if the master password hash file exists and is valid JSON."""
        path = MasterPasswordManager.get_hash_path()
        return os.path.exists(path) and os.path.getsize(path) > 0

    @staticmethod
    def set_master_password():
        """Prompt user to set a new master password and store its salted hash, with a welcoming intro."""
        clear_screen()
        Banner.print()
        print(colored("Welcome to Nexa!", "cyan"))
        print()
        print(colored("IMPORTANT:", "red"), "Your master password is the key to your vault.")
        print(colored("* Do not share it with anyone.", "yellow"))
        print(colored("* Use a mix of letters, numbers, and symbols.", "yellow"))
        print(colored("* If you forget it, your data cannot be recovered.", "yellow"))
        print("-" * 50)
        print(colored("Step 1 of 2: Enter your master password.", "cyan"))
        print(colored("Step 2 of 2: Confirm your master password.", "cyan"))
        print()

        hash_path = MasterPasswordManager.get_hash_path()

        while True:
            pwd1 = getpass.getpass("Enter new master password: ")
            pwd2 = getpass.getpass("Confirm master password: ")
            if not pwd1:
                print(colored("ERROR:", "red"), "Password cannot be empty.")
                log_error("Password cannot be empty.")
                continue
            if pwd1 != pwd2:
                print(colored("ERROR:", "red"), "Passwords do not match.")
                log_error("Passwords do not match.")
                continue

            salt = os.urandom(16)
            derived_hash = MasterPasswordManager._derive_hash(pwd1, salt)

            payload = {
                "salt": base64.b64encode(salt).decode("utf-8"),
                "hash": derived_hash,
            }
            with open(hash_path, "w") as f:
                json.dump(payload, f)

            log_info("Master password set successfully.")
            print(colored("\nMaster password set successfully!", "green"))
            input("Press Enter to continue...")
            break

    @staticmethod
    def verify_master_password() -> str:
        """Prompt user to verify the master password, up to 3 attempts, with a polished login page."""
        clear_screen()
        Banner.print()
        print(colored("v.1.0.0", "yellow"))
        print(colored("Login", "cyan"))
        print("-" * 50)
        print("Please enter your master password to unlock your vault.")
        print("-" * 50)

        hash_path = MasterPasswordManager.get_hash_path()

        try:
            with open(hash_path, "r") as f:
                data = json.load(f)
            salt = base64.b64decode(data["salt"])
            stored_hash = data["hash"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            log_error("Master password file invalid or missing.")
            print(colored("ERROR:", "red"), "Master password file not found. Exiting.")
            exit(1)

        for attempt in range(1, 4):
            print(colored(f"\nAttempt {attempt} of 3", "yellow"))
            pwd = getpass.getpass("Enter master password: ")
            derived_hash = MasterPasswordManager._derive_hash(pwd, salt)

            if derived_hash == stored_hash:
                log_info("Master password verified.")
                Banner.access_granted_animation()
                print(colored("Access granted. Welcome to Nexa!", "green"))
                return pwd
            else:
                print(colored("ERROR:", "red"), "Incorrect password. Try again.")
                log_error(f"Incorrect master password attempt {attempt}.")

        # After 3 failed attempts
        Banner.access_denied_animation()
        print(colored("Too many failed attempts. Exiting.", "red"))
        exit(1)