import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from app import App

def main():
    try:
        app = App()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == '__main__':
    main()
