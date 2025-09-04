import sys
from pathlib import Path

# Ensure the project root is on the Python path for imports.
sys.path.append(str(Path(__file__).resolve().parents[1]))
import main

class DummyCanvas:
    def __init__(self):
        self.coords_map = {}
        self.next_id = 1

    def create_oval(self, x1, y1, x2, y2, **kwargs):
        item = self.next_id
        self.next_id += 1
        self.coords_map[item] = [x1, y1, x2, y2]
        return item

    def create_line(self, x1, y1, x2, y2, **kwargs):
        item = self.next_id
        self.next_id += 1
        self.coords_map[item] = [x1, y1, x2, y2]
        return item

    def move(self, item, dx, dy):
        coords = self.coords_map[item]
        self.coords_map[item] = [coords[0] + dx, coords[1] + dy,
                                 coords[2] + dx, coords[3] + dy]

    def coords(self, item, *new_coords):
        if new_coords:
            self.coords_map[item] = list(new_coords)
        return list(self.coords_map[item])

    def find_overlapping(self, x1, y1, x2, y2):
        overlapping = []
        for item, (ix1, iy1, ix2, iy2) in self.coords_map.items():
            if not (ix2 <= x1 or ix1 >= x2 or iy2 <= y1 or iy1 >= y2):
                overlapping.append(item)
        return overlapping

    def delete(self, item):
        self.coords_map.pop(item, None)


def make_app():
    app = object.__new__(main.SwordGameApp)
    app.canvas = DummyCanvas()
    app.base_x = main.WIDTH // 2
    app.base_y = main.HEIGHT // 2
    app.player = app.canvas.create_oval(
        app.base_x - 10, app.base_y - 10, app.base_x + 10, app.base_y + 10,
        fill="blue",
    )
    app.sword = app.canvas.create_line(
        app.base_x, app.base_y, app.base_x, app.base_y - 100,
        width=5, fill="gray",
    )
    return app


def test_move_player_updates_sword():
    app = make_app()
    app.move_player(20, -20)
    assert app.base_x == main.WIDTH // 2 + 20
    assert app.base_y == main.HEIGHT // 2 - 20
    x1, y1, x2, y2 = app.canvas.coords(app.sword)
    assert (x2, y2) == (app.base_x, app.base_y - 100)


def test_move_player_stays_within_bounds():
    app = make_app()
    app.move_player(-1000, -1000)
    assert app.base_x == 10
    assert app.base_y == 10
    assert app.canvas.coords(app.sword) == [10, 10, 10, -90]


def test_move_player_blocked_by_wall():
    app = make_app()
    wall = [app.base_x + 10, app.base_y - 10, app.base_x + 30, app.base_y + 10]
    app.walls = [wall]
    app.move_player(20, 0)
    assert app.base_x == main.WIDTH // 2
    assert app.base_y == main.HEIGHT // 2
