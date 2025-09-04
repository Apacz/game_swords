import tkinter as tk
from tkinter import messagebox
import random
import json
import os

WIDTH, HEIGHT = 800, 600
START_LIVES = 1000
MOVE_SPEED = 20
DURATION_MS = 60 * 1000  # 1 minute
CELL_SIZE = 40

# map file used for all levels for now
MAP_FILES = {lvl: "maps/example_map" + str(lvl) + ".txt" for lvl in range(1, 21)}

# base vertical speed of falling fruits
FRUIT_BASE_SPEED = 2

# --- simple profile handling -------------------------------------------------

PROFILE_FILE = "user_profile.json"


def load_profile(path: str = PROFILE_FILE):
    """Load profile data from *path* if it exists.

    Returns a dict with at least the key ``highest_level`` indicating the
    highest unlocked level. If the file is missing or invalid, a default profile
    with only level 1 unlocked is returned.
    """

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"highest_level": 1}
    else:
        data = {"highest_level": 1}
    if "highest_level" not in data:
        data["highest_level"] = 1
    return data


def save_profile(data, path: str = PROFILE_FILE):
    """Persist *data* to *path* as JSON."""

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


def unlock_next_level(profile: dict, current_level: int):
    """Unlock the level following *current_level* in ``profile``.

    The ``profile`` dict is modified in place. The highest unlocked level only
    increases when the current level is at least as high as the previously
    unlocked level. Levels above 20 are ignored.
    """

    highest = profile.get("highest_level", 1)
    if current_level >= highest and current_level < 20:
        profile["highest_level"] = current_level + 1


def spawn_probabilities(level):
    """Return spawn percentages for each fruit color at a given level.

    The allocation grows with the level while ensuring the total never
    exceeds 100%.  Orange fruits are not available on the very first level,
    so their probability is only allocated from level 2 onwards.  Any
    remaining probability is assigned to green fruits.
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


class Fruit:
    """Simple falling enemy that moves faster on higher levels.

    Fruits can require multiple hits to destroy depending on their color.
    """

    def __init__(self, canvas, level, x, y, color="green", hits=1):
        self.canvas = canvas
        self.color = color
        self.hp = hits
        self.id = canvas.create_oval(
            x - 15, y - 15, x + 15, y + 15, fill=color
        )
        # draw a tiny sword icon on top of the fruit
        blade = canvas.create_line(x, y - 10, x, y + 10, width=2, fill="black")
        guard = canvas.create_line(x - 5, y + 5, x + 5, y + 5, width=2, fill="black")
        self.icon_ids = [blade, guard]
        # speed increases with level
        self.speed = FRUIT_BASE_SPEED + level

    def move(self, target_x, target_y):
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

    def delete(self):
        """Remove the fruit and its sword icon from the canvas."""
        self.canvas.delete(self.id)
        for icon in self.icon_ids:
            self.canvas.delete(icon)


def load_map(canvas, path):
    start = end = None
    walls = []
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


class SwordGameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.attributes("-fullscreen", True)
        global WIDTH, HEIGHT
        WIDTH, HEIGHT = self.winfo_screenwidth(), self.winfo_screenheight()
        self.title("Sword Levels")
        self.resizable(False, False)

        self.level = None
        self.lives = START_LIVES
        self.base_x = WIDTH // 2
        self.base_y = HEIGHT - 20

        # load player profile for level unlocking
        self.profile = load_profile()

        # start screen with level selection
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

        # apply initial locking based on profile
        self.update_level_buttons()

        self.game_frame = None
        self.canvas = None
        self.sword = None
        self.player = None
        self.lives_label = None

    def update_level_buttons(self):
        """Enable only the levels that have been unlocked."""

        highest = self.profile.get("highest_level", 1)
        for idx, btn in enumerate(self.level_buttons, start=1):
            state = tk.NORMAL if idx <= highest else tk.DISABLED
            btn.config(state=state)

    def start_game(self, level):
        self.level = level
        self.start_frame.pack_forget()
        self.running = True

        # reset lives
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

        self.canvas = tk.Canvas(self.game_frame, width=WIDTH, height=HEIGHT, bg="white")
        self.canvas.pack()

        # draw level obstacles from map file
        start_pos, end_pos, self.walls = load_map(
            self.canvas, MAP_FILES.get(level, "maps/example_map" + str(level) + ".txt")
        )
        self.end_pos = end_pos
        if start_pos:
            self.base_x, self.base_y = start_pos

        # player represented as circle
        self.player = self.canvas.create_oval(
            self.base_x - 10, self.base_y - 10, self.base_x + 10, self.base_y + 10,
            fill="blue"
        )

        # sword represented as line from base to mouse
        self.sword = self.canvas.create_line(
            self.base_x, self.base_y, self.base_x, self.base_y - 100, width=5, fill="gray"
        )
        self.bind("<Motion>", self.move_sword)
        self.bind("<Button-1>", self.swing_sword)
        self.bind("<Left>", lambda e: self.move_player(-MOVE_SPEED, 0))
        self.bind("<Right>", lambda e: self.move_player(MOVE_SPEED, 0))
        self.bind("<Up>", lambda e: self.move_player(0, -MOVE_SPEED))
        self.bind("<Down>", lambda e: self.move_player(0, MOVE_SPEED))
        self.bind("<space>", lambda e: self.lose_life())
        self.bind("<Escape>", lambda e: self.end_game("quit"))

        # list of active fruits
        self.fruits = []

        # sword initially inactive; ensure defined before spawning fruits
        self.sword_active = False
        self.spawn_fruit()
        self.remaining_ms = DURATION_MS
        self.update_timer()

    def update_timer(self):
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

    def move_player(self, dx, dy):
        """Move the player and keep the sword aligned.

        The player's base position is restricted to stay fully within the
        canvas. The sword's tip should maintain its relative position to the
        player as the player moves.
        """

        if not self.__dict__.get("running", True):
            return

        # Calculate new base position with margins so the whole player stays
        # inside the canvas bounds.
        margin = 10
        old_x, old_y = self.base_x, self.base_y
        new_x = max(margin, min(WIDTH - margin, self.base_x + dx))
        new_y = max(margin, min(HEIGHT - margin, self.base_y + dy))

        # Collision detection against walls
        walls = self.__dict__.get("walls", [])
        new_bbox = [new_x - 10, new_y - 10, new_x + 10, new_y + 10]
        for x1, y1, x2, y2 in walls:
            if not (new_bbox[2] <= x1 or new_bbox[0] >= x2 or new_bbox[3] <= y1 or new_bbox[1] >= y2):
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

    def check_level_complete(self):
        """Check whether the player reached the end of the level."""

        end_pos = self.__dict__.get("end_pos")
        if not end_pos:
            return
        ex, ey = end_pos
        if (
            abs(self.base_x - ex) <= CELL_SIZE // 2
            and abs(self.base_y - ey) <= CELL_SIZE // 2
        ):
            self.complete_level()

    def complete_level(self):
        """Handle level completion: unlock the next level and return to start."""

        self.running = False
        messagebox.showinfo("Level Complete", f"Level {self.level} complete!")
        unlock_next_level(self.profile, self.level)
        save_profile(self.profile)
        if self.game_frame:
            self.game_frame.destroy()
        self.start_frame.pack()
        self.update_level_buttons()

    def move_sword(self, event):
        # update sword line to point towards mouse
        self.canvas.coords(self.sword, self.base_x, self.base_y, event.x, event.y)

    def swing_sword(self, event):
        """Activate the sword briefly when clicked."""
        self.sword_active = True
        self.canvas.itemconfig(self.sword, fill="red")
        self.after(100, self.deactivate_sword)

    def deactivate_sword(self):
        self.sword_active = False
        self.canvas.itemconfig(self.sword, fill="gray")

    def lose_life(self):
        if self.lives <= 0:
            return
        self.lives -= 1
        self.lives_label.config(text=f"Lives: {self.lives}")
        if self.lives <= 0:
            self.end_game(reason="out of lives")

    # --- fruit/enemy mechanics -------------------------------------------------

    def spawn_fruit(self):
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

    def move_fruit(self, fruit):
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
        if (
            x2 < 0
            or x1 > WIDTH
            or y2 < 0
            or y1 > HEIGHT
        ):
            fruit.delete()
            if fruit in self.fruits:
                self.fruits.remove(fruit)
            return
        self.after(50, lambda: self.move_fruit(fruit))

    def check_sword_hit(self, fruit):
        """Return True if the sword hits the fruit and it is destroyed."""
        if not self.sword_active:
            return False
        x1, y1, x2, y2 = self.canvas.coords(fruit.id)
        overlapping = self.canvas.find_overlapping(x1, y1, x2, y2)
        if self.sword in overlapping:
            fruit.hp -= 1
            if fruit.hp <= 0:
                return True
        return False

    def choose_fruit_type(self):
        probs = spawn_probabilities(self.level)
        roll = random.uniform(0, 100)
        cumulative = 0
        for color in ("black", "red", "purple", "orange"):
            # Use .get so missing colors simply contribute 0 probability
            cumulative += probs.get(color, 0)
            if roll < cumulative:
                hits = {"black": 5, "red": 3, "purple": 2, "orange": 2}[color]
                return color, hits
        # If no special fruit was selected, default to a simple green one
        return "green", 1

    def end_game(self, reason="time"):
        if not self.__dict__.get("running", True):
            return
        self.running = False
        if reason == "out of lives":
            msg = f"Out of lives! Level {self.level} over."
        else:
            msg = f"Time's up! Level {self.level} over."
        messagebox.showinfo("Game Over", msg)
        self.destroy()


if __name__ == "__main__":
    app = SwordGameApp()
    app.mainloop()
