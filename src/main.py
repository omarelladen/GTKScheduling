import os
import sys

from .app import App

def main():
    try:
        app = App()

        if "--help" in sys.argv or "-h" in sys.argv:
            print("Usage:")
            print(f"  {app.name_lower} [OPTION…]")
            print("")
            print("Help Options:")
            print("  -h, --help                 Show help options")
            print("")
            print("Application Options:")
            print("  -v, --version              Print version information and exit")
            print("")
            sys.exit(0)
        elif "--version" in sys.argv or "-v" in sys.argv:
            print(f"{app.name} {app.version}")
            sys.exit(0)

        app.run()

    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
