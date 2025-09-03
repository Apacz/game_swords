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
