import sys
import time
from storage import Storage
from banner import Banner, clear_screen
from termcolor import colored
from master_password import MasterPasswordManager
from security import derive_fernet
from UI import UI

def typewriter(text, color=None, delay=0.03):
    for char in text:
        if color:
            sys.stdout.write(colored(char, color))
        else:
            sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def show_welcome():
    clear_screen()
    Banner.print()
    print(colored("Welcome to Nexa!", "cyan"))
    print()
    typewriter("Nexa is a secure password manager that helps you store, retrieve,")
    typewriter("edit, and manage your credentials safely. All your passwords are")
    typewriter("encrypted and protected by a master password only you know.")
    print()
    typewriter("Your digital life, secured.", "yellow", delay=0.05)
    print()
    # Animated "Let's get started!" spinner
    message = "Let's get started!"
    spinner = ['|', '/', '-', '\\']
    for i in range(16):
        sys.stdout.write('\r' + colored(message, "green") + " " + spinner[i % 4])
        sys.stdout.flush()
        time.sleep(0.12)
    print('\r' + colored(message + " ✔", "green"))
    input("\nPress Enter to continue...")

def main():
    # Show welcome only if master password is not set
    if not MasterPasswordManager.is_set():
        show_welcome()
        MasterPasswordManager.set_master_password()

    # Verify and get master password
    master_pwd = MasterPasswordManager.verify_master_password()
    fernet = derive_fernet(master_pwd)

    # Init DB
    conn = Storage.init_db()

    # Run UI
    UI.main_menu(conn, fernet)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\nERROR:", 'red'),"Keyboard interrupt is disabled while Nexa is running.")