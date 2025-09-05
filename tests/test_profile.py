import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import profile_utils as profile_mod


def test_profile_load_and_save(tmp_path):
    path = tmp_path / "profile.json"
    data = profile_mod.load_profile(path)
    assert data["highest_level"] == 1
    data["highest_level"] = 3
    profile_mod.save_profile(data, path)
    loaded = profile_mod.load_profile(path)
    assert loaded["highest_level"] == 3


def test_unlock_next_level():
    prof = {"highest_level": 1}
    profile_mod.unlock_next_level(prof, 1)
    assert prof["highest_level"] == 2
    # calling again with same level should not change
    profile_mod.unlock_next_level(prof, 1)
    assert prof["highest_level"] == 2
    # unlocking higher level updates accordingly
    profile_mod.unlock_next_level(prof, 2)
    assert prof["highest_level"] == 3
