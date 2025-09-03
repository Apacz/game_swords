import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import main


def test_profile_load_and_save(tmp_path):
    path = tmp_path / "profile.json"
    data = main.load_profile(path)
    assert data["highest_level"] == 1
    data["highest_level"] = 3
    main.save_profile(data, path)
    loaded = main.load_profile(path)
    assert loaded["highest_level"] == 3


def test_unlock_next_level():
    profile = {"highest_level": 1}
    main.unlock_next_level(profile, 1)
    assert profile["highest_level"] == 2
    # calling again with same level should not change
    main.unlock_next_level(profile, 1)
    assert profile["highest_level"] == 2
    # unlocking higher level updates accordingly
    main.unlock_next_level(profile, 2)
    assert profile["highest_level"] == 3
