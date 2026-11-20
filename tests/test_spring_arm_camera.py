import pytest
from gameplay import spring_arm_camera as mod

CASES = [
    ("distance", 'm.sweep_distance((0, 0, 0), (3, 4, 0)) == approx(5.0)'),
    ("hit", 'm.nearest_hit([(5, "wall"), (2, "rock")]) == (2, "rock")'),
    ("near", 'm.clamp_near(0.3, 2.0, 0.5) == approx(0.3)'),
    ("key", 'm.smooth_state_key("L", "A") == "L:A"'),
    ("damping", 'm.damping_for_dt(0.5, 0.016, 0.016) == approx(0.5)'),
    ("shake", 'm.shake_before_sweep((1, 2, 3), (0, 1, 0)) == (1, 1, 3)'),
    ("offset", 'm.follow_offset((1, 2), (3, 5)) == (-2, -3)'),
    ("replay", 'm.replay_arm_length((1, 2, 3), (1, 2, 6)) == approx(3.0)'),
    ("layer", 'm.collision_layer_allowed(1, 0b0010) is False'),
    ("teleport", 'm.teleport_reset((0, 0), (10, 0), 5) is True'),
    ("blend", 'm.blend_clear(True, True) is True'),
    ("spring", 'm.spring_length(5, 2, 0.5) == approx(1.5)'),
    ("fov", 'm.fov_for_distance(60, 2, 1) == approx(30.0)'),
    ("matrix", 'm.camera_matrix_translation((1, 2), (3, 4)) == (4, 6)'),
    ("trigger", 'm.trigger_excluded(1, 0b0100) is True')
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx})
