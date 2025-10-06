import os
import time
import pyfiglet
from termcolor import colored
from debug import log_debug, log_error

def clear_screen():
    """Clears the terminal screen in a cross-platform way."""
    os.system('cls' if os.name == 'nt' else 'clear')

class Banner:
    @staticmethod
    def print():
        """
        Displays the Nexa ASCII art banner in magenta using the 'the_edge' font.
        """
        clear_screen()
        ascii_banner = pyfiglet.figlet_format("Nexa", font="the_edge")
        print(colored(ascii_banner, 'magenta'))
        log_debug("Displayed Nexa ASCII banner.")

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
        cycles = max(2, int(duration_seconds / 0.5))
        start = time.time()
        for cycle in range(cycles):
            print(colored(ascii_denied, 'red'))
            for i in range(8):
                elapsed = int(time.time() - start)
                msg = f"\r{spinner[i % 4]} Unauthorized access detected. Locking in {max(0, duration_seconds - elapsed)}s..."
                print(colored(msg, 'red'), end='', flush=True)
                time.sleep(0.12)
            print('\r' + ' ' * 80, end='\r')
            clear_screen()
            time.sleep(0.06)
        clear_screen()
        print(colored(ascii_denied, 'red'))
        print(colored("Too many failed attempts. System locked.", 'red'))
        log_error("Master password access denied animation shown; exiting.")
        time.sleep(2)
        clear_screen()

    @staticmethod
    def access_granted_animation():
        """
        Displays an 'Access Granted' ASCII art animation in green, with a loading spinner.
        """
        clear_screen()
        access_granted = "Access Granted"
        font = "smbraille"
        ascii_access = pyfiglet.figlet_format(access_granted, font=font)
        print(colored(ascii_access, 'green'))
        log_debug("Access granted banner displayed.")
        spinner = ['|', '/', '-', '\\']
        print(colored("Please wait while we unlock your vault...", 'yellow'))
        for i in range(40):
            print(colored(f"\r{spinner[i % 4]} Unlocking...", 'red'), end='', flush=True)
            time.sleep(0.1)
        print(colored("\rVault Unlocked! ✔", 'green'))
        time.sleep(2)
        clear_screen()

    @staticmethod
    def exit_animation():
        """
        Displays an animated 'Exiting...' ASCII art with dots loading.
        """
        clear_screen()
        base_text = "Exiting"
        font = "smbraille"

        # Animate 3 dots (repeat a few times if you want)
        for cycle in range(2):  # repeat the dot animation 2 times
            for dots in range(1, 4):
                closing = base_text + " " + ("." * dots)
                ascii_closing = pyfiglet.figlet_format(closing, font=font)
                clear_screen()
                print(colored(ascii_closing, 'red'))
                log_debug(f"Exit banner displayed with {dots} dots.")
                time.sleep(0.5)

        clear_screen()
        time.sleep(1)
        clear_screen()