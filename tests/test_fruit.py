import sys
from pathlib import Path

# Ensure the project root is on the Python path for imports.
sys.path.append(str(Path(__file__).resolve().parents[1]))

import fruit
import game
from test_move_player import DummyCanvas


def test_fruit_speed_increases_with_level():
    canvas = DummyCanvas()
    f1 = fruit.Fruit(canvas, level=1, x=50, y=0)
    f2 = fruit.Fruit(canvas, level=5, x=50, y=0)
    assert f1.speed == fruit.FRUIT_BASE_SPEED + 1
    assert f2.speed == fruit.FRUIT_BASE_SPEED + 5


def test_fruit_move_uses_speed():
    canvas = DummyCanvas()
    f = fruit.Fruit(canvas, level=2, x=0, y=0)
    before = canvas.coords(f.id)
    f.move(100, 0)
    after = canvas.coords(f.id)
    dx = after[0] - before[0]
    dy = after[1] - before[1]
    dist = (dx ** 2 + dy ** 2) ** 0.5
    assert abs(dist - f.speed) < 1e-6


def test_spawn_probabilities_level1():
    probs = fruit.spawn_probabilities(1)
    assert probs == {"black": 1, "red": 3, "purple": 5, "green": 91}


def test_spawn_probabilities_cap():
    probs = fruit.spawn_probabilities(30)
    assert probs["green"] == 0
    assert probs["black"] == 30
    assert probs["red"] == 32
    assert probs["purple"] == 38


def test_fruit_requires_multiple_hits():
    canvas = DummyCanvas()
    app = object.__new__(game.SwordGameApp)
    app.canvas = canvas
    app.sword = canvas.create_line(0, 0, 0, 0)
    app.sword_active = True
    fruit_obj = fruit.Fruit(canvas, level=1, x=0, y=0, color="purple", hits=2)
    assert not game.SwordGameApp.check_sword_hit(app, fruit_obj)
    assert fruit_obj.hp == 1
    assert game.SwordGameApp.check_sword_hit(app, fruit_obj)
    assert fruit_obj.hp == 0


def test_fruit_has_sword_icon():
    canvas = DummyCanvas()
    f = fruit.Fruit(canvas, level=1, x=50, y=0)
    assert len(f.icon_ids) == 2


def test_fruit_icon_moves_with_fruit():
    canvas = DummyCanvas()
    f = fruit.Fruit(canvas, level=1, x=0, y=0)
    before = [canvas.coords(i)[:] for i in f.icon_ids]
    f.move(50, 0)
    after = [canvas.coords(i)[:] for i in f.icon_ids]
    for b, a in zip(before, after):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5
        assert abs(dist - f.speed) < 1e-6
        dx2 = a[2] - b[2]
        dy2 = a[3] - b[3]
        dist2 = (dx2 ** 2 + dy2 ** 2) ** 0.5
        assert abs(dist2 - f.speed) < 1e-6


def test_spawn_fruit_stops_when_time_low():
    app = object.__new__(game.SwordGameApp)
    app.canvas = DummyCanvas()
    app.level = 1
    app.fruits = []
    app.running = True
    app.remaining_ms = 9000
    app.after_called = False

    def dummy_after(self, interval, callback):
        self.after_called = True

    app.after = dummy_after.__get__(app, game.SwordGameApp)
    game.SwordGameApp.spawn_fruit(app)
    assert app.fruits == []
    assert not app.after_called


class DummyLabel:
    def config(self, **kwargs):
        self.kwargs = kwargs


def test_fruit_collision_loses_life():
    app = object.__new__(game.SwordGameApp)
    app.canvas = DummyCanvas()
    app.base_x = 50
    app.base_y = 50
    app.player = app.canvas.create_oval(40, 40, 60, 60)
    app.sword = app.canvas.create_line(0, 0, 0, 0)
    app.sword_active = False
    app.lives = 2
    app.lives_label = DummyLabel()
    app.fruits = []
    app.running = True
    fruit_obj = fruit.Fruit(app.canvas, level=1, x=50, y=50)
    app.fruits.append(fruit_obj)
    game.SwordGameApp.move_fruit(app, fruit_obj)
    assert app.lives == 1
    assert fruit_obj not in app.fruits
