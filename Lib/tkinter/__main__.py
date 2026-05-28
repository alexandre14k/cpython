"""Main entry point"""

import sys
if sys.argv[0].endswith("__main__.py"):
    sys.argv[0] = "myFRpy -m tkinter"
from . import _test as main
main()
