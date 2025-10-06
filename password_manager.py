import secrets
from banner import clear_screen
from termcolor import colored
from storage import Storage
from debug import log_info

class PasswordManager:
    @staticmethod
    def add_password(conn, fernet):
        clear_screen()
        print("=== Add New Password ===")
        service = input("Service: ").strip()
        if not service:
            print(colored("\nERROR:", "red"), "Service name is required. No changes made.")
            input("Press Enter to return to menu...")
            return

        username = input("Username: ").strip()
        if not username:
            print(colored("\nERROR:", "red"), "Username is required. No changes made.")
            input("Press Enter to return to menu...")
            return

        password = input("Enter password (leave blank to generate a random password): ")
        if not password:
            gen_choice = input("Generate a random password? (Y/n): ").strip().lower()
            if gen_choice in ['', 'y', 'yes']:
                length_input = input("Password length (default 16): ")
                try:
                    length = int(length_input) if length_input else 16
                except ValueError:
                    length = 16
                chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+'
                password = ''.join(secrets.choice(chars) for _ in range(length))
                print(f"\nGenerated password: {password}")
            else:
                print("\nNo password generated.")
                input("Press Enter to return to menu...")
                return

        Storage.add_password(conn, fernet, service, username, password)
        print("\nNew credentials created:")
        print(colored("Service:", "cyan"), service)
        print(f"Username: {username}")
        print(f"Password: {password}")
        log_info(f"Added password for service: {service}")
        input("\nPress Enter to return to menu...")

    @staticmethod
    def retrieve_password(conn, fernet):
        clear_screen()
        services = Storage.get_all_services(conn, fernet)
        if not services:
            print("No services found in the database.")
            input("\nPress Enter to return to menu...")
            return

        print("Available services:")
        for idx, service in enumerate(services, 1):
            print(f"{idx}. {service}")

        selection = input("\nSelect service by number or name: ").strip()
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(services):
                service = services[idx]
            else:
                print("Invalid selection.")
                input("Press Enter to return to menu...")
                return
        else:
            service = selection.strip()

        entry = Storage.get_password(conn, fernet, service)
        if entry and 'username' in entry and 'password' in entry:
            print(f"\nCredentials for {colored(service, 'cyan')}:")
            print(f"Username: {entry['username']}")
            print(f"Password: {entry['password']}")
        else:
            print("\nService not found or no credentials stored.")

        input("Press Enter to return to menu...")

    @staticmethod
    def edit_password(conn, fernet):
        clear_screen()
        services = Storage.get_all_services(conn, fernet)
        if not services:
            print("No services found in the database.")
            input("\nPress Enter to return to menu...")
            return

        print("Available services:")
        for idx, service in enumerate(services, 1):
            print(f"{idx}. {service}")

        selection = input("Select service to edit by number or name: ").strip()
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(services):
                service = services[idx]
            else:
                print("Invalid selection.")
                input("\nPress Enter to return to menu...")
                return
        else:
            service = selection.strip()

        # Display current credentials before editing
        entry = Storage.get_password(conn, fernet, service)
        if entry and 'username' in entry and 'password' in entry:
            print(f"\nCurrent credentials for {colored(service, 'cyan')}:")
            print(f"Username: {entry['username']}")
            print(f"Password: {entry['password']}")
        else:
            print("Service not found or no credentials stored.")
            input("\nPress Enter to return to menu...")
            return

        new_service = input("\nNew service name (leave blank to keep the same): ").strip()
        username = input("New username (blank to skip): ")
        password = input("New password (blank to skip): ")

        success = Storage.update_password(
            conn, fernet, service,
            username if username else None,
            password if password else None,
            new_service if new_service else None
        )
        if success:
            print(f"\nPassword for '{colored(service, 'cyan')}' was updated.")
            log_info(f"Edited password for service: {service}")
        else:
            print("Service not found or could not be updated.")
        input("Press Enter to return to menu...")

    @staticmethod
    def delete_password(conn, fernet):
        clear_screen()
        services = Storage.get_all_services(conn, fernet)
        if not services:
            print("No services found in the database.")
            input("\nPress Enter to return to menu...")
            return

        print("Available services:")
        for idx, service in enumerate(services, 1):
            print(f"{idx}. {service}")

        selection = input("Select service to delete by number or name: ").strip()
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(services):
                service = services[idx]
            else:
                print("Invalid selection.")
                input("Press Enter to return to menu...")
                return
        else:
            service = selection.strip()

        success = Storage.delete_password(conn, fernet, service)
        if success:
            print(f"Password for '{colored(service, 'cyan')}' deleted.")
            log_info(f"Deleted password for service: {service}")
        else:
            print("Service not found or could not be deleted.")
        input("Press Enter to return to menu...")

    @staticmethod
    def generate_random_password(conn, fernet):
        clear_screen()
        print("=== Generate Random Password ===")
        length_input = input("Password length (default 16): ")
        try:
            length = int(length_input) if length_input else 16
        except ValueError:
            length = 16
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+'
        password = ''.join(secrets.choice(chars) for _ in range(length))
        print(f"\nGenerated password: {password}")

        attach = input("\nWould you like to attach a service to this password? (Y/n): ").strip().lower()
        if attach in ['', 'y', 'yes']:
            service = input("Service: ").strip()
            if not service:
                print(colored("\nERROR:", "red"), "Service name is required. No changes made.")
                input("Press Enter to return to menu...")
                return

            username = input("Username: ").strip()
            if not username:
                print(colored("\nERROR:", "red"), "Username is required. No changes made.")
                input("Press Enter to return to menu...")
                return

            Storage.add_password(conn, fernet, service, username, password)
            print("\nNew credentials created:")
            print(colored("Service:", "cyan"), service)
            print(f"Username: {username}")
            print(f"Password: {password}")
            log_info(f"Generated and stored password for service: {service}")
        else:
            print("\nNo changes made.")

        input("Press Enter to return to menu...")