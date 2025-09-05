"""Entry point for the sword game.

The bulk of the implementation now lives in dedicated modules such as
:mod:`game`, :mod:`fruit` and :mod:`profile`.  Keeping this file tiny makes it
clear where new programmers should look for the actual logic.
"""

import tkinter as tk

from game import SwordGameApp


if __name__ == "__main__":
    try:
        app = SwordGameApp()
        app.mainloop()
    except tk.TclError as exc:
        print("Unable to start the graphical interface:", exc)
