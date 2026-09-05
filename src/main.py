# Copyright 2025-2026 Omar Zagonel El Laden
# SPDX-License-Identifier: GPL-3.0-only

from .app import App


def main():
    try:
        app = App()
        app.parse_args()
        app.run()

    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()
