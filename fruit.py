from __future__ import annotations

"""Definitions related to the falling fruit enemies.

Separating the :class:`Fruit` class and spawn logic from the rest of the
application keeps the main game code shorter and easier to understand.  The
module also exposes :func:`spawn_probabilities` which describes how the
difficulty ramps up with higher levels.
"""

from dataclasses import dataclass
import tkinter as tk

# base vertical speed of falling fruits
FRUIT_BASE_SPEED = 2


def spawn_probabilities(level: int) -> dict:
    """Return spawn percentages for each fruit color at ``level``.

    The allocation grows with the level while ensuring the total never exceeds
    ``100``.  Orange fruits are not available on the very first level so their
    probability is only allocated from level 2 onwards.  Any remaining
    probability is assigned to green fruits.
    """

    remaining = 100

    # Always allocate in order of the more challenging fruit first
    black = min(1 + (level - 1) * 1, remaining)
    remaining -= black

    red = min(3 + (level - 1) * 1, remaining)
    remaining -= red

    purple = min(5 + (level - 1) * 2, remaining)
    remaining -= purple

    # Orange fruits appear only from level 2 upwards
    orange = 0
    if level > 1 and remaining > 0:
        orange = min(2 + (level - 2) * 2, remaining)
        remaining -= orange

    # Whatever probability is left goes to the basic green fruit
    green = remaining

    probs = {"black": black, "red": red, "purple": purple, "green": green}
    if orange:
        probs["orange"] = orange
    return probs


@dataclass
class Fruit:
    """Simple falling enemy that moves faster on higher levels.

    Fruits can require multiple hits to destroy depending on their colour.  The
    class is intentionally small so that beginners can easily grasp how it
    works.  Each fruit draws a tiny sword icon on top for visual flair.
    """

    canvas: tk.Canvas
    level: int
    x: int
    y: int
    color: str = "green"
    hits: int = 1

    def __post_init__(self) -> None:
        self.hp = self.hits
        self.id = self.canvas.create_oval(
            self.x - 15, self.y - 15, self.x + 15, self.y + 15, fill=self.color
        )
        # draw a tiny sword icon on top of the fruit
        blade = self.canvas.create_line(self.x, self.y - 10, self.x, self.y + 10,
                                       width=2, fill="black")
        guard = self.canvas.create_line(self.x - 5, self.y + 5, self.x + 5,
                                       self.y + 5, width=2, fill="black")
        self.icon_ids = [blade, guard]
        # speed increases with level
        self.speed = FRUIT_BASE_SPEED + self.level

    # -- movement -------------------------------------------------------------
    def move(self, target_x: float, target_y: float) -> None:
        """Move the fruit towards a target position."""
        x1, y1, x2, y2 = self.canvas.coords(self.id)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        dx = target_x - cx
        dy = target_y - cy
        dist = (dx ** 2 + dy ** 2) ** 0.5 or 1
        move_x = dx / dist * self.speed
        move_y = dy / dist * self.speed
        self.canvas.move(self.id, move_x, move_y)
        for icon in self.icon_ids:
            self.canvas.move(icon, move_x, move_y)

    def delete(self) -> None:
        """Remove the fruit and its sword icon from the canvas."""
        self.canvas.delete(self.id)
        for icon in self.icon_ids:
            self.canvas.delete(icon)
