from __future__ import annotations

"""Tkinter application implementing the sword game.

The class in this module coordinates all other parts of the program.  Keeping
the game logic separate from the helper modules makes it easier for learners
to follow the flow of the program and experiment with changes.
"""

import random
import tkinter as tk
from tkinter import messagebox

from fruit import Fruit, spawn_probabilities
from map_loader import load_map, CELL_SIZE
from profile_utils import load_profile, save_profile, unlock_next_level

# ---------------------------------------------------------------------------
# Configuration values
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 800, 600
START_LIVES = 1000
MOVE_SPEED = 20
DURATION_MS = 60 * 1000  # 1 minute

# Map file used for all levels for now
MAP_FILES = {lvl: f"maps/example_map{lvl}.txt" for lvl in range(1, 21)}


class SwordGameApp(tk.Tk):
    """Main application window.

    ``SwordGameApp`` handles the game loop, user interaction and ties together
    the helper modules.  For brevity only a subset of the original game's
    behaviour is implemented here, but the structure mirrors that of a larger
    Tkinter program.
    """

    def __init__(self) -> None:
        super().__init__()
        # Use the whole screen so there is plenty of space to move around.
        self.attributes("-fullscreen", True)
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = self.winfo_screenwidth(), self.winfo_screenheight()
        self.title("Sword Levels")
        self.resizable(False, False)

        self.level: int | None = None
        self.lives = START_LIVES
        self.base_x = WIDTH // 2
        self.base_y = HEIGHT - 20

        # Load player profile for level unlocking
        self.profile = load_profile()

        # Start screen with level selection ---------------------------------
        self.start_frame = tk.Frame(self)
        self.start_frame.pack()
        tk.Label(self.start_frame, text="Select Level").pack(pady=10)

        level_buttons = tk.Frame(self.start_frame)
        level_buttons.pack()
        self.level_buttons = []
        for i in range(1, 21):
            btn = tk.Button(level_buttons, text=str(i), width=3,
                            command=lambda lvl=i: self.start_game(lvl))
            btn.grid(row=(i - 1) // 10, column=(i - 1) % 10, padx=2, pady=2)
            self.level_buttons.append(btn)

        self.update_level_buttons()

        # These attributes are created when a level starts
        _game_attrs = [
            "game_frame", "canvas", "sword", "player",
            "lives_label", "fruits", "sword_active",
        ]
        for name in _game_attrs:
            setattr(self, name, None)

    # ------------------------------------------------------------------
    # Menu handling
    # ------------------------------------------------------------------
    def update_level_buttons(self) -> None:
        """Enable only the levels that have been unlocked."""
        highest = self.profile.get("highest_level", 1)
        for idx, btn in enumerate(self.level_buttons, start=1):
            state = tk.NORMAL if idx <= highest else tk.DISABLED
            btn.config(state=state)

    # ------------------------------------------------------------------
    # Game setup
    # ------------------------------------------------------------------
    def start_game(self, level: int) -> None:
        """Begin the selected level."""
        self.level = level
        self.start_frame.pack_forget()
        self.running = True

        # reset lives and player position
        self.lives = START_LIVES
        self.base_x = WIDTH // 2
        self.base_y = HEIGHT - 20

        self.game_frame = tk.Frame(self)
        self.game_frame.pack()

        # top bar showing lives and remaining time
        info_frame = tk.Frame(self.game_frame)
        info_frame.pack(fill="x")
        self.lives_label = tk.Label(info_frame, text=f"Lives: {self.lives}")
        self.lives_label.pack(side="left")
        self.timer_label = tk.Label(info_frame, text="Time: 01:00")
        self.timer_label.pack(side="right")

        self.canvas = tk.Canvas(self.game_frame, width=WIDTH, height=HEIGHT,
                                bg="white")
        self.canvas.pack()

        # draw level obstacles from map file
        start_pos, end_pos, self.walls = load_map(
            self.canvas, MAP_FILES.get(level, f"maps/example_map{level}.txt")
        )
        self.end_pos = end_pos
        if start_pos:
            self.base_x, self.base_y = start_pos

        # player represented as circle
        self.player = self.canvas.create_oval(
            self.base_x - 10, self.base_y - 10, self.base_x + 10, self.base_y + 10,
            fill="blue",
        )

        # sword represented as line from base to mouse
        self.sword = self.canvas.create_line(
            self.base_x, self.base_y, self.base_x, self.base_y - 100, width=5,
            fill="gray",
        )
        # Bind input events
        self.bind("<Motion>", self.move_sword)
        self.bind("<Button-1>", self.swing_sword)
        self.bind("<Left>", lambda e: self.move_player(-MOVE_SPEED, 0))
        self.bind("<Right>", lambda e: self.move_player(MOVE_SPEED, 0))
        self.bind("<Up>", lambda e: self.move_player(0, -MOVE_SPEED))
        self.bind("<Down>", lambda e: self.move_player(0, MOVE_SPEED))
        self.bind("<space>", lambda e: self.lose_life())
        self.bind("<Escape>", lambda e: self.end_game("quit"))

        self.fruits: list[Fruit] = []
        self.sword_active = False
        self.spawn_fruit()
        self.remaining_ms = DURATION_MS
        self.update_timer()

    # ------------------------------------------------------------------
    # Timer and status updates
    # ------------------------------------------------------------------
    def update_timer(self) -> None:
        """Update the countdown timer displayed on screen."""
        if not self.__dict__.get("running", True):
            return
        if self.remaining_ms <= 0:
            self.end_game()
            return
        total_seconds = self.remaining_ms // 1000
        mins, secs = divmod(total_seconds, 60)
        self.timer_label.config(text=f"Time: {mins:02d}:{secs:02d}")
        self.remaining_ms -= 1000
        self.after(1000, self.update_timer)

    # ------------------------------------------------------------------
    # Player movement
    # ------------------------------------------------------------------
    def move_player(self, dx: int, dy: int) -> None:
        """Move the player and keep the sword aligned."""
        if not self.__dict__.get("running", True):
            return

        # Calculate new base position with margins so the whole player stays
        margin = 10
        old_x, old_y = self.base_x, self.base_y
        new_x = max(margin, min(WIDTH - margin, self.base_x + dx))
        new_y = max(margin, min(HEIGHT - margin, self.base_y + dy))

        # Collision detection against walls
        walls = self.__dict__.get("walls", [])
        new_bbox = [new_x - 10, new_y - 10, new_x + 10, new_y + 10]
        for x1, y1, x2, y2 in walls:
            if not (new_bbox[2] <= x1 or new_bbox[0] >= x2 or
                    new_bbox[3] <= y1 or new_bbox[1] >= y2):
                return

        self.base_x, self.base_y = new_x, new_y

        # Determine the actual distance moved (may be less than dx/dy at edges)
        actual_dx = self.base_x - old_x
        actual_dy = self.base_y - old_y
        self.canvas.move(self.player, actual_dx, actual_dy)

        # Move sword tip by the same amount to keep orientation
        x1, y1, x2, y2 = self.canvas.coords(self.sword)
        self.canvas.coords(
            self.sword,
            self.base_x,
            self.base_y,
            x2 + actual_dx,
            y2 + actual_dy,
        )

        self.check_level_complete()

    def check_level_complete(self) -> None:
        """Check whether the player reached the end of the level."""
        end_pos = self.__dict__.get("end_pos")
        if not end_pos:
            return
        ex, ey = end_pos
        if (abs(self.base_x - ex) <= CELL_SIZE // 2 and
                abs(self.base_y - ey) <= CELL_SIZE // 2):
            self.complete_level()

    def complete_level(self) -> None:
        """Handle level completion: unlock the next level and return to menu."""
        self.running = False
        messagebox.showinfo("Level Complete", f"Level {self.level} complete!")
        unlock_next_level(self.profile, self.level)
        save_profile(self.profile)
        if self.game_frame:
            self.game_frame.destroy()
        self.start_frame.pack()
        self.update_level_buttons()

    # ------------------------------------------------------------------
    # Sword interaction
    # ------------------------------------------------------------------
    def move_sword(self, event: tk.Event) -> None:
        """Update sword line to point towards the mouse."""
        self.canvas.coords(self.sword, self.base_x, self.base_y, event.x, event.y)

    def swing_sword(self, event: tk.Event) -> None:
        """Activate the sword briefly when clicked."""
        self.sword_active = True
        self.canvas.itemconfig(self.sword, fill="red")
        self.after(100, self.deactivate_sword)

    def deactivate_sword(self) -> None:
        self.sword_active = False
        self.canvas.itemconfig(self.sword, fill="gray")

    # ------------------------------------------------------------------
    # Player health
    # ------------------------------------------------------------------
    def lose_life(self) -> None:
        if self.lives <= 0:
            return
        self.lives -= 1
        self.lives_label.config(text=f"Lives: {self.lives}")
        if self.lives <= 0:
            self.end_game(reason="out of lives")

    # ------------------------------------------------------------------
    # Fruit mechanics
    # ------------------------------------------------------------------
    def spawn_fruit(self) -> None:
        """Create a new fruit at the finish point and schedule the next spawn."""
        if not self.__dict__.get("running", True):
            return
        remaining = self.__dict__.get("remaining_ms", DURATION_MS)
        if remaining < 10_000:
            return
        if self.end_pos:
            x, y = self.end_pos
        else:
            x, y = WIDTH // 2, 0
        color, hits = self.choose_fruit_type()
        fruit = Fruit(self.canvas, self.level, x, y, color=color, hits=hits)
        self.fruits.append(fruit)
        self.move_fruit(fruit)
        # spawn frequency increases with level but never faster than every 200ms
        interval = max(1000 - self.level * 50, 200)
        self.after(interval, self.spawn_fruit)

    def move_fruit(self, fruit: Fruit) -> None:
        """Move fruit toward the player and handle collisions."""
        if not self.__dict__.get("running", True):
            return
        fruit.move(self.base_x, self.base_y)
        if self.check_sword_hit(fruit):
            fruit.delete()
            if fruit in self.fruits:
                self.fruits.remove(fruit)
            return
        x1, y1, x2, y2 = self.canvas.coords(fruit.id)
        overlapping = self.canvas.find_overlapping(x1, y1, x2, y2)
        if self.player in overlapping:
            fruit.delete()
            if fruit in self.fruits:
                self.fruits.remove(fruit)
            self.lose_life()
            return
        if (x2 < 0 or x1 > WIDTH or y2 < 0 or y1 > HEIGHT):
            fruit.delete()
            if fruit in self.fruits:
                self.fruits.remove(fruit)
            return
        self.after(50, lambda: self.move_fruit(fruit))

    def check_sword_hit(self, fruit: Fruit) -> bool:
        """Return ``True`` if the sword hits the fruit and it is destroyed."""
        if not self.sword_active:
            return False
        x1, y1, x2, y2 = self.canvas.coords(fruit.id)
        overlapping = self.canvas.find_overlapping(x1, y1, x2, y2)
        if self.sword in overlapping:
            fruit.hp -= 1
            if fruit.hp <= 0:
                return True
        return False

    def choose_fruit_type(self) -> tuple[str, int]:
        probs = spawn_probabilities(self.level)
        roll = random.uniform(0, 100)
        cumulative = 0
        for color in ("black", "red", "purple", "orange"):
            cumulative += probs.get(color, 0)
            if roll < cumulative:
                hits = {"black": 5, "red": 3, "purple": 2, "orange": 2}[color]
                return color, hits
        return "green", 1

    # ------------------------------------------------------------------
    # Game termination
    # ------------------------------------------------------------------
    def end_game(self, reason: str = "time") -> None:
        if not self.__dict__.get("running", True):
            return
        self.running = False
        if reason == "out of lives":
            msg = f"Out of lives! Level {self.level} over."
        else:
            msg = f"Time's up! Level {self.level} over."
        messagebox.showinfo("Game Over", msg)
        self.destroy()
