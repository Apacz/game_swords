from __future__ import annotations

"""Utility helpers for loading ASCII maps.

Each map is a simple text file where ``#`` denotes a wall, ``S`` the player
start position and ``E`` the exit.  The function returns both coordinates and a
list of rectangles representing the walls so that the game can perform
collision checks.
"""

from typing import List, Tuple
import tkinter as tk

# Size of a single map cell in pixels.  Using a constant makes it easy to
# tweak the map scale later and keeps this module self contained.
CELL_SIZE = 40


def load_map(canvas: tk.Canvas, path: str) -> Tuple[Tuple[int, int] | None,
                                                    Tuple[int, int] | None,
                                                    List[Tuple[int, int, int, int]]]:
    """Draw the map from ``path`` onto ``canvas``.

    Returns a tuple ``(start, end, walls)`` where ``start`` and ``end`` are the
    player start and exit positions in canvas coordinates.  ``walls`` is a list
    of rectangles (``x1, y1, x2, y2``) representing impassable areas.
    """

    start = end = None
    walls: List[Tuple[int, int, int, int]] = []
    with open(path) as f:
        for row, line in enumerate(f):
            for col, char in enumerate(line.rstrip("\n")):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                if char == "#":
                    canvas.create_rectangle(x1, y1, x2, y2, fill="lightgray")
                    walls.append((x1, y1, x2, y2))
                elif char == "S":
                    canvas.create_rectangle(x1, y1, x2, y2, fill="lightgreen")
                    start = (x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2)
                elif char == "E":
                    canvas.create_rectangle(x1, y1, x2, y2, fill="pink")
                    end = (x1 + CELL_SIZE // 2, y1 + CELL_SIZE // 2)
    return start, end, walls
