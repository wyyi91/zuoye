"""参数校验工具"""

from typing import Optional
from src.config import TempConfig, PIDDefaults


def validate_positive_float(value: str, name: str = "参数") -> tuple[bool, Optional[float], str]:
    """校验正浮点数"""
    try:
        v = float(value)
        if v <= 0:
            return False, None, f"{name}必须大于0"
        return True, v, ""
    except (ValueError, TypeError):
        return False, None, f"{name}必须是有效数字"


def validate_non_negative_float(value: str, name: str = "参数") -> tuple[bool, Optional[float], str]:
    """校验非负浮点数"""
    try:
        v = float(value)
        if v < 0:
            return False, None, f"{name}不能为负数"
        return True, v, ""
    except (ValueError, TypeError):
        return False, None, f"{name}必须是有效数字"


def validate_pid_params(kp: str, ti: str, td: str) -> tuple[bool, dict, str]:
    """校验PID三参数"""
    errors = []

    ok, kp_val, msg = validate_non_negative_float(kp, "Kp")
    if not ok:
        errors.append(msg)

    ok, ti_val, msg = validate_positive_float(ti, "Ti")
    if not ok:
        errors.append(msg)

    ok, td_val, msg = validate_non_negative_float(td, "Td")
    if not ok:
        errors.append(msg)

    if errors:
        return False, {}, "; ".join(errors)

    return True, {"kp": kp_val, "ti": ti_val, "td": td_val}, ""


def validate_sv(value: str) -> tuple[bool, Optional[float], str]:
    """校验设定值"""
    try:
        v = float(value)
        if v < TempConfig.SV_MIN or v > TempConfig.SV_MAX:
            return False, None, f"设定值必须在 {TempConfig.SV_MIN} ~ {TempConfig.SV_MAX} 之间"
        return True, v, ""
    except (ValueError, TypeError):
        return False, None, "设定值必须是有效数字"


def validate_manual_output(value: str,
                           u_min: float = -30.0,
                           u_max: float = 30.0) -> tuple[bool, Optional[float], str]:
    """校验手动输出值"""
    try:
        v = float(value)
        if v < u_min or v > u_max:
            return False, None, f"手动输出必须在 {u_min} ~ {u_max} 之间"
        return True, v, ""
    except (ValueError, TypeError):
        return False, None, "手动输出必须是有效数字"


def validate_disturbance_params(amplitude: str, duration: str) -> tuple[bool, dict, str]:
    """校验干扰参数"""
    errors = []
    ok, amp, msg = validate_positive_float(amplitude, "干扰振幅")
    if not ok:
        errors.append(msg)

    ok, dur, msg = validate_positive_float(duration, "干扰持续时间")
    if not ok:
        errors.append(msg)
    elif dur is not None and dur <= 0:
        errors.append("干扰持续时间必须大于0")

    if errors:
        return False, {}, "; ".join(errors)

    return True, {"amplitude": amp, "duration": dur}, ""
