from debug import log_debug, log_info, log_error
from termcolor import colored
import time
import base64, hashlib
import pyfiglet
import getpass
import os
import sys
import json
import hashlib
import secrets

# Clears the terminal screen

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Displays the ASCII art banner

class Banner:
    @staticmethod
    def print():
        clear_screen()
        banner = "Nexa"
        font = "the_edge"
        ascii_banner = pyfiglet.figlet_format(banner, font=font)
        print(colored(ascii_banner, 'magenta'))
        log_debug("Displayed Nexa ASCII banner.")

# Handles storage paths and data operations - JSON file storage at the moment *ENCRYPT*

class Storage:
    @staticmethod
    def get_data_dir():
        if os.name == 'nt':
            base_dir = os.getenv('LOCALAPPDATA') or os.getenv('APPDATA')
        elif sys.platform == 'darwin':
            base_dir = os.path.expanduser('~/Library/Application Support')
        else:
            base_dir = os.path.expanduser('~/.local/share')
        data_dir = os.path.join(base_dir, "Nexa")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            log_info(f"Created data directory: {data_dir}")
        else:
            log_debug(f"Data directory already exists: {data_dir}")
        return data_dir

    # This is where we store the encrypted passwords.

    @staticmethod
    def get_secure_data_path():
        path = os.path.join(Storage.get_data_dir(), "coredump.json")
        log_debug(f"Secure data path: {path}")
        return path

    # This is where we store master password hash.

    @staticmethod
    def get_master_password_hash_path():
        path = os.path.join(Storage.get_data_dir(), "master.hash")
        log_debug(f"Master password hash path: {path}")
        return path
    
    # Check to see if master password file exists and is not empty.

    @staticmethod
    def is_master_password_set():
        hash_path = Storage.get_master_password_hash_path()
        exists = os.path.exists(hash_path) and os.path.getsize(hash_path) > 0
        log_debug(f"Master password set: {exists}")
        return exists

    # Load and save password data (JSON format for now, later *encrypted*)

    @staticmethod
    def load_password_data():
        data_file = Storage.get_secure_data_path()
        if not os.path.exists(data_file):
            log_info("No password data file found. Returning empty dictionary.")
            return {}
        with open(data_file, "r") as f:
            try:
                data = json.load(f)
                log_debug("Loaded password data from file.")
                return data
            except json.JSONDecodeError:
                log_error("Password data file is corrupted. Returning empty dictionary.")
                return {}

    # Save password data to file

    @staticmethod
    def save_password_data(data):
        data_file = Storage.get_secure_data_path()
        data_dir = os.path.dirname(data_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            log_info(f"Created password data directory: {data_dir}")
        with open(data_file, "w") as f:
            json.dump(data, f, indent=4)
            log_info("Saved password data to file.")

# Master Password Management and Verification

class MasterPasswordManager:
    @staticmethod
    def set_master_password():
        clear_screen()
        print("=== Set Master Password ===")
        hash_path = Storage.get_master_password_hash_path()
        data_dir = os.path.dirname(hash_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            log_info(f"Created master password directory: {data_dir}")
        while True:
            pwd1 = getpass.getpass("Enter new master password: ")
            pwd2 = getpass.getpass("Confirm master password: ")
            if pwd1 == pwd2 and pwd1:
                hash_val = hashlib.sha256(pwd1.encode()).hexdigest()
                with open(hash_path, "w") as f:
                    f.write(hash_val)
                print("Master password set successfully.")
                log_info("Master password set successfully.")
                break
            else:
                print("Passwords do not match or are empty. Try again.")
                log_error("Failed to set master password: passwords do not match or are empty.")
        input("Press Enter to continue...")
        clear_screen()

    # Verify the master password with up to 3 attempts, then show animated ACCESS DENIED if failed.

    @staticmethod
    def verify_master_password():
        clear_screen()
        hash_path = Storage.get_master_password_hash_path()
        print("=== Master Login ===")
        with open(hash_path, "r") as f:
            stored_hash = f.read().strip()
        for attempt in range(3):
            pwd = getpass.getpass("Enter master password: ")
            if hashlib.sha256(pwd.encode()).hexdigest() == stored_hash:
                clear_screen()
                access_granted = "Access Granted"
                font = "smbraille"
                ascii_access = pyfiglet.figlet_format(access_granted, font=font)
                print(colored(ascii_access, 'green'))
                log_info("Master password verified. Access granted.")

                # --- Cool Loading Page ---
                spinner = ['|', '/', '-', '\\']
                print(colored("Please wait while we unlock your vault...", 'yellow'))
                for i in range(40):
                    print(colored(f"\r{spinner[i % 4]} Unlocking...", 'red'), end='', flush=True)
                    time.sleep(0.1)
                print(colored("\r✔  Vault Unlocked!           ", 'green'))
                time.sleep(2)
                clear_screen()
                return True
            else:
                print("Incorrect password.")
                log_error(f"Incorrect master password attempt {attempt + 1}.")
        # If we reach here: too many failed attempts -> show animated ACCESS DENIED, then exit
        MasterPasswordManager.access_denied_animation(duration_seconds=5)

    @staticmethod
    def access_denied_animation(duration_seconds: int = 4):
        """
        Animated ACCESS DENIED screen in red.
        duration_seconds: total approximate seconds the animation should run.
        """
        clear_screen()
        denied_text = "ACCESS DENIED"
        font = "smbraille"
        ascii_denied = pyfiglet.figlet_format(denied_text, font=font)
        spinner = ['|', '/', '-', '\\']
        # Number of outer blink cycles. More cycles => longer animation.
        cycles = max(2, int(duration_seconds / 0.5))

        start = time.time()
        for cycle in range(cycles):
            # Show the big red text
            print(colored(ascii_denied, 'red'))
            # Small spinner line that updates several times
            for i in range(8):
                elapsed = int(time.time() - start)
                msg = f"\r{spinner[i % 4]} Unauthorized access detected. Locking in {max(0, duration_seconds - elapsed)}s..."
                print(colored(msg, 'red'), end='', flush=True)
                time.sleep(0.12)
            # clear the spinner line before next blink cycle
            print('\r' + ' ' * 80, end='\r')
            # quick blank-screen blink to emphasize the flash
            clear_screen()
            time.sleep(0.06)

        # Final full-screen denied (no blinking) and a short pause before exit
        clear_screen()
        print(colored(ascii_denied, 'red'))
        print(colored("Too many failed attempts. System locked.", 'red'))
        log_error("Master password access denied animation shown; exiting.")
        time.sleep(2)
        clear_screen()
        # exit with non-zero to indicate error
        exit(1)

        # Password Management functions
class PasswordManager:
    @staticmethod
    def add_new_password():
        clear_screen()
        print("=== Add New Password ===")
        service = input("Service name: ")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        data = Storage.load_password_data()
        data[service] = {"username": username, "password": password}
        Storage.save_password_data(data)
        print(f"Password for '{service}' added.")
        log_info(f"Added password for service: {service}")
        input("Press Enter to continue...")
        clear_screen()

    @staticmethod
    def retrieve_password():
        clear_screen()
        print("=== Retrieve Password ===")
        data = Storage.load_password_data()
        if not data:
            print("No services stored yet.")
            log_info("No services available for retrieval.")
            input("Press Enter to continue...")
            clear_screen()
            return
        services = list(data.keys())
        print("Available services:")
        for idx, service in enumerate(services, 1):
            print(f"  {idx}. {service}")
        selection = input("Select service by number or name: ").strip()
        entry = None
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(services):
                service = services[idx]
                entry = data[service]
            else:
                service = selection
        else:
            service = selection
            entry = data.get(service)
        if entry:
            print(f"Username: {entry['username']}")
            print(f"Password: {entry['password']}")
            log_info(f"Retrieved password for service: {service}")
        else:
            print("Service not found.")
            log_error(f"Service not found: {service}")
        input("Press Enter to continue...")
        clear_screen()

    @staticmethod
    def edit_password():
        clear_screen()
        print("=== Edit Password ===")
        data = Storage.load_password_data()
        if not data:
            print("No services stored yet.")
            log_info("No services available for edit.")
            input("Press Enter to continue...")
            clear_screen()
            return

        services = list(data.keys())
        print("Available services:")
        for idx, service in enumerate(services, 1):
            print(f"  {idx}. {service}")

        selection = input("Select service by number or name: ").strip()
        entry = None
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(services):
                service = services[idx]
                entry = data[service]
            else:
                service = selection
        else:
            service = selection
            entry = data.get(service)

        if entry:
            username = input(f"New username (leave blank to keep '{entry['username']}'): ").strip()
            password = getpass.getpass("New password (leave blank to keep current): ")
            if username:
                data[service]['username'] = username
            if password:
                data[service]['password'] = password
            Storage.save_password_data(data)
            print(f"Password for '{service}' updated.")
            log_info(f"Edited password for service: {service}")
        else:
            print("Service not found.")
            log_error(f"Service not found for edit: {service}")

        input("Press Enter to continue...")
        clear_screen()

    @staticmethod
    def generate_random_password():
        clear_screen()
        print("=== Generate Random Password ===")
        service = input("Attach to service (leave blank to just display): ").strip()
        username = ""
        if service:
            username = input("Username (optional): ").strip()
        length = input("Password length (default 16): ")
        try:
            length = int(length)
        except ValueError:
            length = 16
        password = ''.join(secrets.choice(
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+'
        ) for _ in range(length))
        print(f"Generated password: {password}")
        log_info("Generated random password.")
        if service:
            data = Storage.load_password_data()
            data[service] = {"username": username, "password": password}
            Storage.save_password_data(data)
            print(f"Password stored for service '{service}'.")
            log_info(f"Stored generated password for service: {service}")
        input("Press Enter to continue...")
        clear_screen()

class UI:
    @staticmethod
    def main_menu():
        Banner.print()
        print("=== Password Manager ===")
        print("1. Add New Password")
        print("2. Retrieve Password")
        print("3. Edit Password")
        print("4. Generate Random Password")
        print("5. Exit")
        choice = input("Select an option (1-5): ")
        log_debug(f"User selected menu option: {choice}")
        return choice

    @staticmethod
    def run():
        while True:
            choice = UI.main_menu()
            if choice == '1':
                PasswordManager.add_new_password()
            elif choice == '2':
                PasswordManager.retrieve_password()
            elif choice == '3':
                PasswordManager.edit_password()
            elif choice == '4':
                PasswordManager.generate_random_password()
            elif choice == '5':
                clear_screen()
                closing = "Exiting . . ."
                font = "smbraille"
                ascii_closing = pyfiglet.figlet_format(closing, font=font)
                print(colored(ascii_closing, 'red'))
                log_info("Exited Password Manager.")
                exit()
            else:
                print("Invalid choice. Please try again.")
                log_error(f"Invalid menu choice: {choice}")
                input("Press Enter to continue...")
                clear_screen()

if __name__ == "__main__":
    data_dir = Storage.get_data_dir()
    log_debug(f"Data directory: {data_dir}")
    print(f"Data directory: {data_dir}")

    if not Storage.is_master_password_set():
        MasterPasswordManager.set_master_password()
    MasterPasswordManager.verify_master_password()
    UI.run()