import tkinter as tk
from tkinter import messagebox
import random

WIDTH, HEIGHT = 800, 600
START_LIVES = 3
MOVE_SPEED = 20
DURATION_MS = 5 * 60 * 1000  # 5 minutes
CELL_SIZE = 40

# map file used for all levels for now
MAP_FILES = {lvl: "maps/example_map.txt" for lvl in range(1, 21)}

# base vertical speed of falling fruits
FRUIT_BASE_SPEED = 2


class Fruit:
    """Simple falling enemy that moves faster on higher levels."""

    def __init__(self, canvas, level, x, y):
        self.canvas = canvas
        # represent fruit as orange circle
        self.id = canvas.create_oval(x - 15, y - 15, x + 15, y + 15, fill="orange")
        # speed increases with level
        self.speed = FRUIT_BASE_SPEED + level

    def move(self):
        """Move the fruit vertically based on its speed."""
        self.canvas.move(self.id, 0, self.speed)


def load_map(canvas, path):
    with open(path) as f:
        for row, line in enumerate(f):
            for col, char in enumerate(line.rstrip("\n")):
                if char == "#":
                    x1 = col * CELL_SIZE
                    y1 = row * CELL_SIZE
                    x2 = x1 + CELL_SIZE
                    y2 = y1 + CELL_SIZE
                    canvas.create_rectangle(x1, y1, x2, y2, fill="lightgray")


class SwordGameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sword Levels")
        self.resizable(False, False)

        self.level = None
        self.lives = START_LIVES
        self.base_x = WIDTH // 2
        self.base_y = HEIGHT - 20

        # start screen with level selection
        self.start_frame = tk.Frame(self)
        self.start_frame.pack()
        tk.Label(self.start_frame, text="Select Level").pack(pady=10)

        level_buttons = tk.Frame(self.start_frame)
        level_buttons.pack()
        for i in range(1, 21):
            btn = tk.Button(level_buttons, text=str(i), width=3,
                            command=lambda lvl=i: self.start_game(lvl))
            btn.grid(row=(i - 1) // 10, column=(i - 1) % 10, padx=2, pady=2)

        self.game_frame = None
        self.canvas = None
        self.sword = None
        self.player = None
        self.lives_label = None

    def start_game(self, level):
        self.level = level
        self.start_frame.pack_forget()

        # reset lives and base position
        self.lives = START_LIVES
        self.base_x = WIDTH // 2
        self.base_y = HEIGHT - 20

        self.game_frame = tk.Frame(self)
        self.game_frame.pack()

        self.lives_label = tk.Label(self.game_frame, text=f"Lives: {self.lives}")
        self.lives_label.pack(anchor="nw")

        self.canvas = tk.Canvas(self.game_frame, width=WIDTH, height=HEIGHT, bg="white")
        self.canvas.pack()

        # draw level obstacles from map file
        load_map(self.canvas, MAP_FILES.get(level, "maps/example_map.txt"))

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

        # list of active fruits
        self.fruits = []
        self.spawn_fruit()

        self.after(DURATION_MS, self.end_game)

    def move_player(self, dx, dy):
        """Move the player and keep the sword aligned.

        The player's base position is restricted to stay fully within the
        canvas. The sword's tip should maintain its relative position to the
        player as the player moves.
        """

        # Calculate new base position with margins so the whole player stays
        # inside the canvas bounds.
        margin = 10
        old_x, old_y = self.base_x, self.base_y
        self.base_x = max(margin, min(WIDTH - margin, self.base_x + dx))
        self.base_y = max(margin, min(HEIGHT - margin, self.base_y + dy))

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

    def move_sword(self, event):
        # update sword line to point towards mouse
        self.canvas.coords(self.sword, self.base_x, self.base_y, event.x, event.y)

    def swing_sword(self, event):
        # flash sword color when clicking to simulate swing
        self.canvas.itemconfig(self.sword, fill="red")
        self.after(100, lambda: self.canvas.itemconfig(self.sword, fill="gray"))

    def lose_life(self):
        if self.lives <= 0:
            return
        self.lives -= 1
        self.lives_label.config(text=f"Lives: {self.lives}")
        if self.lives <= 0:
            self.end_game(reason="out of lives")

    # --- fruit/enemy mechanics -------------------------------------------------

    def spawn_fruit(self):
        """Create a new falling fruit and schedule the next spawn."""
        x = random.randint(20, WIDTH - 20)
        fruit = Fruit(self.canvas, self.level, x, 0)
        self.fruits.append(fruit)
        self.move_fruit(fruit)
        # spawn frequency increases with level but never faster than every 200ms
        interval = max(1000 - self.level * 50, 200)
        self.after(interval, self.spawn_fruit)

    def move_fruit(self, fruit):
        """Move fruit down the screen and handle collisions."""
        fruit.move()
        if self.check_sword_hit(fruit):
            self.canvas.delete(fruit.id)
            if fruit in self.fruits:
                self.fruits.remove(fruit)
            return
        x1, y1, x2, y2 = self.canvas.coords(fruit.id)
        if y1 > HEIGHT:
            # fruit escaped -> lose life
            self.canvas.delete(fruit.id)
            if fruit in self.fruits:
                self.fruits.remove(fruit)
            self.lose_life()
        else:
            self.after(50, lambda: self.move_fruit(fruit))

    def check_sword_hit(self, fruit):
        """Return True if the sword overlaps the given fruit."""
        x1, y1, x2, y2 = self.canvas.coords(fruit.id)
        overlapping = self.canvas.find_overlapping(x1, y1, x2, y2)
        return self.sword in overlapping

    def end_game(self, reason="time"):
        if reason == "out of lives":
            msg = f"Out of lives! Level {self.level} over."
        else:
            msg = f"Time's up! Level {self.level} over."
        messagebox.showinfo("Game Over", msg)
        self.destroy()


if __name__ == "__main__":
    app = SwordGameApp()
    app.mainloop()
