from banner import Banner, clear_screen
from termcolor import colored
from password_manager import PasswordManager

class UI:
    @staticmethod
    def main_menu(conn, fernet):
        while True:
            Banner.print()
            print(colored("version 1.0.0", "yellow"))
            print("=== Password Manager ===")
            print("1. Add Password")
            print("2. Retrieve Password")
            print("3. Edit Password")
            print("4. Delete Password")
            print("5. Generate Password")
            print("6. Exit")
            choice = input("Select: ")

            if choice == '1':
                clear_screen()
                PasswordManager.add_password(conn, fernet)
            elif choice == '2':
                clear_screen()
                PasswordManager.retrieve_password(conn, fernet)
            elif choice == '3':
                clear_screen()
                PasswordManager.edit_password(conn, fernet)
            elif choice == '4':
                clear_screen()
                PasswordManager.delete_password(conn, fernet)
            elif choice == '5':
                clear_screen()
                PasswordManager.generate_random_password(conn, fernet)
            elif choice == '6':
                Banner.exit_animation()
                break
            else:
                print("Invalid choice.")
                input("Press Enter...")