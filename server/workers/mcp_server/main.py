#!/usr/bin/env python3
from utils.setup_path import activate

activate()
from logic.core import main

try:
    main()
except KeyboardInterrupt:
    pass
