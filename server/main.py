#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

if __name__ == "__main__":
    # UTF-8 console so the block banner prints on Windows terminals
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    # Initializes the launcher, not the server.
    try:
        from launcher.menu import main_menu
        main_menu()
    except KeyboardInterrupt:
        os._exit(0)
