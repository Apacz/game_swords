import sys
from pathlib import Path

# Ensure the project root is on the Python path for imports.
sys.path.append(str(Path(__file__).resolve().parents[1]))
import main
from test_move_player import DummyCanvas


def test_fruit_speed_increases_with_level():
    canvas = DummyCanvas()
    f1 = main.Fruit(canvas, level=1, x=50, y=0)
    f2 = main.Fruit(canvas, level=5, x=50, y=0)
    assert f1.speed == main.FRUIT_BASE_SPEED + 1
    assert f2.speed == main.FRUIT_BASE_SPEED + 5


def test_fruit_move_uses_speed():
    canvas = DummyCanvas()
    f = main.Fruit(canvas, level=2, x=50, y=0)
    before = canvas.coords(f.id)
    f.move()
    after = canvas.coords(f.id)
    assert after[1] - before[1] == f.speed


def test_spawn_probabilities_level1():
    probs = main.spawn_probabilities(1)
    assert probs == {"black": 1, "red": 3, "purple": 5, "orange": 2, "green": 89}


def test_spawn_probabilities_cap():
    probs = main.spawn_probabilities(30)
    assert probs["green"] == 0
    assert probs["black"] == 30
    assert probs["red"] == 32
    assert probs["purple"] == 38


def test_fruit_requires_multiple_hits():
    canvas = DummyCanvas()
    app = object.__new__(main.SwordGameApp)
    app.canvas = canvas
    app.sword = canvas.create_line(0, 0, 0, 0)
    app.sword_active = True
    fruit = main.Fruit(canvas, level=1, x=0, y=0, color="purple", hits=2)
    assert not app.check_sword_hit(fruit)
    assert fruit.hp == 1
    assert app.check_sword_hit(fruit)
    assert fruit.hp == 0


def test_fruit_has_sword_icon():
    canvas = DummyCanvas()
    f = main.Fruit(canvas, level=1, x=50, y=0)
    assert len(f.icon_ids) == 2


def test_fruit_icon_moves_with_fruit():
    canvas = DummyCanvas()
    f = main.Fruit(canvas, level=1, x=50, y=0)
    before = [canvas.coords(i)[:] for i in f.icon_ids]
    f.move()
    after = [canvas.coords(i)[:] for i in f.icon_ids]
    for b, a in zip(before, after):
        assert a[1] - b[1] == f.speed
        assert a[3] - b[3] == f.speed
