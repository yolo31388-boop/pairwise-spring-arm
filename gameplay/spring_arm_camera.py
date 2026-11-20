import math

_EPSILON = 1e-9
_MIN_NEAR = 1e-3


def _sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def _scale(v, s):
    return tuple(x * s for x in v)


def sweep_distance(origin, target):
    """扫掠距离：相机理想位置到角色的整段射线长度。"""
    return math.sqrt(sum((t - o) ** 2 for o, t in zip(origin, target)))


def nearest_hit(hits):
    """最近命中：沿整段扫掠取距离最小的命中，而不是只看理想位置。"""
    if not hits:
        return None
    return min(hits, key=lambda hit: hit[0])


def clamp_near(near, arm_length, min_distance):
    """近平面收缩：相机贴墙时 near 随可用臂长收缩，但不大于原始 near。"""
    # 近平面必须落在碰撞点之前，并留出 min_distance 安全边距；
    # 夹到正的极小值，避免 near <= 0 造成退化投影。
    safe_near = arm_length - min_distance
    if safe_near <= _MIN_NEAR:
        return min(near, _MIN_NEAR)
    return min(near, safe_near)


def smooth_state_key(camera_id, side):
    """平滑状态键：每个相机（分屏左右）各自持有独立的弹簧臂平滑状态。"""
    return "%s:%s" % (camera_id, side)


def damping_for_dt(damping, dt, reference):
    """阻尼时间步归一：把按参考帧时长配置的阻尼换算到当前 dt，避免帧率影响手感。"""
    if reference <= _EPSILON:
        return damping
    # 指数衰减保证不同帧率下每秒的平滑量一致。
    return 1.0 - (1.0 - damping) ** (dt / reference)


def shake_before_sweep(position, shake):
    """震动前位置：碰撞扫掠使用未叠加屏幕震动的相机位置。"""
    return _sub(position, shake)


def follow_offset(target, crosshair):
    """跟随偏移：相机跟随目标点与准星分离，避免击退时准星被拖走。"""
    return _sub(target, crosshair)


def replay_arm_length(position, pivot):
    """回放臂长：补记弹簧臂长度，重放时才能复现贴墙收缩。"""
    return sweep_distance(position, pivot)


def collision_layer_allowed(layer, mask):
    """碰撞层过滤：layer 为单 bit 层值，只有落在 mask 内才参与扫掠。"""
    return bool(layer & mask)


def teleport_reset(old_position, new_position, threshold):
    """传送重置：位移超过阈值时丢弃旧插值，避免画面从旧位置飞过来。"""
    return sweep_distance(old_position, new_position) > threshold


def blend_clear(cut, returning):
    """过场切回清理：cut 切回 gameplay 时清掉 blend 里的抖动/震动偏移。"""
    return bool(cut and returning)


def spring_length(ideal, hit_distance, margin):
    """弹簧臂长度：命中距离减去安全边距，并与理想长度取小，且不为负。"""
    return min(ideal, max(0.0, hit_distance - margin))


def fov_for_distance(base_fov, distance, base_distance):
    """距离 FOV：按距离反比调整 FOV，贴墙时避免透视突变。"""
    if distance <= _EPSILON:
        return base_fov
    return base_fov * base_distance / distance


def camera_matrix_translation(shake, offset):
    """相机平移：震动与偏移叠加为最终矩阵的平移分量。"""
    return _add(shake, offset)


def trigger_excluded(layer, trigger_mask):
    """触发器排除：该层不属于触发器掩码，因此不会被草丛等触发器弹开。"""
    return not bool(layer & trigger_mask)
