#!/usr/bin/env python3
"""Generate Apple Log / Log2 → Rec.709 creative look LUTs (.cube).

v2 fixes:
- No Rec.2020→709 matrix (breaks Apple Wide Gamut / Log2 blues → grey-red sky)
- Soft highlight roll-off, hue-preserving
- Much gentler creative tints (previous Blue Mood crushed greens to cyan)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

OUT_DIR = Path(__file__).resolve().parent
SIZE = 33

# Apple Log Profile TF (same curve for Apple Log 2)
R_0 = -0.05641088
R_T = 0.01
SIGMA = 47.28711236
BETA = 0.00964052
GAMMA = 0.08550479
DELTA = 0.69336945
P_T = SIGMA * (R_T - R_0) ** 2


def apple_log_decode(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 0.0, 1.0)
    out = np.empty_like(p)
    hi = p >= P_T
    mid = (p >= 0.0) & (~hi)
    out[hi] = 2.0 ** ((p[hi] - DELTA) / GAMMA) - BETA
    out[mid] = np.sqrt(np.maximum(p[mid], 0.0) / SIGMA) + R_0
    out[~(hi | mid)] = R_0
    return np.maximum(out, 0.0)


def rec709_encode(linear: np.ndarray) -> np.ndarray:
    linear = np.maximum(linear, 0.0)
    return np.where(
        linear <= 0.018,
        4.5 * linear,
        1.099 * np.power(linear, 0.45) - 0.099,
    )


def soft_rolloff(x: np.ndarray, start: float = 0.75, end: float = 1.05) -> np.ndarray:
    """Compress highlights so sky stays neutral instead of clipping per-channel."""
    x = np.maximum(x, 0.0)
    t = np.clip((x - start) / max(end - start, 1e-6), 0.0, 1.0)
    # smoothstep
    t = t * t * (3.0 - 2.0 * t)
    compressed = start + (1.0 - start) * (1.0 - np.exp(-2.2 * (x - start)))
    return np.where(x <= start, x, (1.0 - t) * x + t * np.minimum(compressed, 0.995))


def luma(rgb: np.ndarray) -> np.ndarray:
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def lift_gamma_gain(rgb: np.ndarray, lift=0.0, gamma=1.0, gain=1.0) -> np.ndarray:
    rgb = np.clip(rgb * gain + lift, 1e-6, None)
    return np.power(rgb, 1.0 / max(gamma, 1e-6))


def saturate(rgb: np.ndarray, amount: float) -> np.ndarray:
    y = luma(rgb)[..., None]
    return y + (rgb - y) * amount


def contrast_s_curve(rgb: np.ndarray, amount: float = 0.1) -> np.ndarray:
    x = np.clip(rgb, 0.0, 1.0)
    mid = 0.45
    return mid + (x - mid) * (1.0 + amount * (1.0 - 2.0 * np.abs(x - mid)))


def tint_masked(
    rgb: np.ndarray,
    shadow_tint: np.ndarray,
    mid_tint: np.ndarray,
    highlight_tint: np.ndarray,
    shadow_str: float,
    mid_str: float,
    highlight_str: float,
) -> np.ndarray:
    """Tint by zone; highlights stay nearly neutral so sky doesn't go grey-red."""
    y = luma(rgb)
    # Shadows: 0–0.35, Mids: peak ~0.45, Highlights: only 0.55–0.85 (not pure white)
    shadow = np.clip(1.0 - y / 0.35, 0.0, 1.0)[..., None]
    mid = np.exp(-((y - 0.42) ** 2) / (2 * 0.12**2))[..., None]
    # Avoid tinting brightest sky/specular
    highlight = (np.clip((y - 0.55) / 0.25, 0.0, 1.0) * np.clip((0.92 - y) / 0.12, 0.0, 1.0))[
        ..., None
    ]
    rgb = rgb + shadow * shadow_tint * shadow_str
    rgb = rgb + mid * mid_tint * mid_str
    rgb = rgb + highlight * highlight_tint * highlight_str
    return rgb


LOOKS = {
    "01_Neutral_Rec709": {
        "desc": "干净中性 Log→709，调色起点",
        "exposure": 1.0,
        "lift": 0.0,
        "gamma": 1.0,
        "gain": 1.0,
        "sat": 1.0,
        "contrast": 0.06,
        "shadow": np.array([0.0, 0.0, 0.0]),
        "mid": np.array([0.0, 0.0, 0.0]),
        "highlight": np.array([0.0, 0.0, 0.0]),
        "ss": 0.0,
        "ms": 0.0,
        "hs": 0.0,
    },
    "02_Dreamy_Soft": {
        "desc": "梦幻柔光，轻抬阴影、轻微降饱和",
        "exposure": 1.05,
        "lift": 0.025,
        "gamma": 1.08,
        "gain": 0.98,
        "sat": 0.92,
        "contrast": -0.04,
        "shadow": np.array([0.01, 0.005, 0.015]),
        "mid": np.array([0.01, 0.005, 0.01]),
        "highlight": np.array([0.01, 0.008, 0.012]),
        "ss": 0.12,
        "ms": 0.08,
        "hs": 0.06,
    },
    "03_Blue_Mood": {
        "desc": "蓝调情绪，阴影轻冷、天空保持干净",
        "exposure": 1.0,
        "lift": 0.005,
        "gamma": 1.03,
        "gain": 1.0,
        "sat": 0.95,
        "contrast": 0.08,
        "shadow": np.array([-0.01, 0.01, 0.04]),
        "mid": np.array([-0.005, 0.005, 0.02]),
        "highlight": np.array([0.0, 0.005, 0.015]),  # cool, not warm
        "ss": 0.18,
        "ms": 0.1,
        "hs": 0.08,
    },
    "04_Moonlight_Cyan": {
        "desc": "月光青感，偏冷但不染红高光",
        "exposure": 0.98,
        "lift": 0.0,
        "gamma": 1.05,
        "gain": 0.98,
        "sat": 0.9,
        "contrast": 0.1,
        "shadow": np.array([-0.015, 0.015, 0.045]),
        "mid": np.array([-0.01, 0.01, 0.025]),
        "highlight": np.array([0.0, 0.01, 0.02]),
        "ss": 0.2,
        "ms": 0.12,
        "hs": 0.08,
    },
    "05_Fuji_Provia": {
        "desc": "富士 Provia 感，清透自然",
        "exposure": 1.04,
        "lift": 0.01,
        "gamma": 1.0,
        "gain": 1.02,
        "sat": 1.06,
        "contrast": 0.08,
        "shadow": np.array([0.005, 0.0, 0.01]),
        "mid": np.array([0.005, 0.005, 0.0]),
        "highlight": np.array([0.01, 0.008, 0.0]),
        "ss": 0.08,
        "ms": 0.06,
        "hs": 0.05,
    },
    "06_Fuji_Classic_Chrome": {
        "desc": "富士 Classic Chrome，低饱和纪实",
        "exposure": 1.02,
        "lift": 0.015,
        "gamma": 1.02,
        "gain": 1.0,
        "sat": 0.82,
        "contrast": 0.1,
        "shadow": np.array([0.01, 0.0, 0.015]),
        "mid": np.array([0.008, 0.005, 0.005]),
        "highlight": np.array([0.01, 0.008, 0.005]),
        "ss": 0.1,
        "ms": 0.06,
        "hs": 0.05,
    },
    "07_Fuji_Velvia": {
        "desc": "富士 Velvia，浓郁但不过曝天空",
        "exposure": 1.02,
        "lift": 0.0,
        "gamma": 0.98,
        "gain": 1.03,
        "sat": 1.18,
        "contrast": 0.14,
        "shadow": np.array([0.01, -0.005, 0.015]),
        "mid": np.array([0.01, 0.005, 0.0]),
        "highlight": np.array([0.015, 0.01, 0.0]),
        "ss": 0.1,
        "ms": 0.08,
        "hs": 0.06,
    },
    "08_Teal_Orange": {
        "desc": "轻电影青橙（比 v1 克制很多）",
        "exposure": 1.02,
        "lift": 0.0,
        "gamma": 1.02,
        "gain": 1.02,
        "sat": 1.02,
        "contrast": 0.1,
        "shadow": np.array([-0.015, 0.02, 0.035]),
        "mid": np.array([0.01, 0.005, -0.005]),
        "highlight": np.array([0.025, 0.01, -0.005]),
        "ss": 0.16,
        "ms": 0.08,
        "hs": 0.1,
    },
    "09_Warm_Film": {
        "desc": "暖调胶片，日落感（高光轻暖）",
        "exposure": 1.03,
        "lift": 0.01,
        "gamma": 1.02,
        "gain": 1.02,
        "sat": 1.0,
        "contrast": 0.08,
        "shadow": np.array([0.02, 0.005, -0.01]),
        "mid": np.array([0.02, 0.01, 0.0]),
        "highlight": np.array([0.025, 0.012, 0.0]),
        "ss": 0.12,
        "ms": 0.1,
        "hs": 0.1,
    },
    "10_Pastel_Dream": {
        "desc": "粉彩梦幻，柔和低对比",
        "exposure": 1.06,
        "lift": 0.035,
        "gamma": 1.1,
        "gain": 0.97,
        "sat": 0.88,
        "contrast": -0.06,
        "shadow": np.array([0.015, 0.005, 0.02]),
        "mid": np.array([0.015, 0.01, 0.015]),
        "highlight": np.array([0.012, 0.01, 0.015]),
        "ss": 0.12,
        "ms": 0.08,
        "hs": 0.06,
    },
    "11_Bleach_Bypass": {
        "desc": "漂白旁路，银调偏低饱和",
        "exposure": 1.05,
        "lift": -0.01,
        "gamma": 0.95,
        "gain": 1.05,
        "sat": 0.62,
        "contrast": 0.18,
        "shadow": np.array([0.005, 0.005, 0.01]),
        "mid": np.array([0.005, 0.005, 0.005]),
        "highlight": np.array([0.01, 0.01, 0.008]),
        "ss": 0.06,
        "ms": 0.04,
        "hs": 0.04,
    },
    "12_Arctic_Cold": {
        "desc": "极地冷调，干净冰蓝",
        "exposure": 1.02,
        "lift": 0.008,
        "gamma": 1.04,
        "gain": 1.0,
        "sat": 0.92,
        "contrast": 0.07,
        "shadow": np.array([-0.008, 0.01, 0.03]),
        "mid": np.array([-0.005, 0.008, 0.02]),
        "highlight": np.array([0.0, 0.008, 0.015]),
        "ss": 0.14,
        "ms": 0.08,
        "hs": 0.06,
    },
}


def apply_look(linear_rgb: np.ndarray, look: dict) -> np.ndarray:
    # Keep working in camera RGB — do NOT apply Rec.2020 matrix (breaks Log2 AWG blues).
    rgb = linear_rgb * look["exposure"]
    rgb = soft_rolloff(rgb, start=0.72, end=1.15)
    display = rec709_encode(rgb)
    display = lift_gamma_gain(
        display, lift=look["lift"], gamma=look["gamma"], gain=look["gain"]
    )
    display = contrast_s_curve(display, amount=look["contrast"])
    display = tint_masked(
        display,
        look["shadow"],
        look["mid"],
        look["highlight"],
        look["ss"],
        look["ms"],
        look["hs"],
    )
    display = saturate(display, look["sat"])
    return np.clip(display, 0.0, 1.0)


def build_lut(look: dict) -> np.ndarray:
    coords = np.linspace(0.0, 1.0, SIZE)
    r, g, b = np.meshgrid(coords, coords, coords, indexing="ij")
    log_rgb = np.stack([r, g, b], axis=-1)
    linear = apple_log_decode(log_rgb)
    out = apply_look(linear, look)
    return out.reshape(-1, 3)


def write_cube(path: Path, data: np.ndarray, title: str, desc: str) -> None:
    lines = [
        f'TITLE "{title}"',
        f"# Apple Log / Log2 creative look v2 — {desc}",
        "# Input: Apple Log or Apple Log 2 (same transfer function)",
        "# Output: Rec.709 display-referred",
        "# v2: no Rec.2020 matrix; highlight-safe tints (fixes grey-red sky)",
        "# Blackmagic Camera: Display LUT ON, Record LUT OFF recommended",
        f"LUT_3D_SIZE {SIZE}",
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
    ]
    for rgb in data:
        lines.append(f"{rgb[0]:.6f} {rgb[1]:.6f} {rgb[2]:.6f}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = []
    for name, look in LOOKS.items():
        data = build_lut(look)
        cube = OUT_DIR / f"{name}.cube"
        write_cube(cube, data, name, look["desc"])
        rows.append((name, look["desc"], cube.name))
        print(f"Wrote {cube.name}")

    readme = OUT_DIR / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Apple Log / Log2 创意 LUT（v2）",
                "",
                "**v2 修复**：去掉错误的 Rec.2020→709 矩阵（Log2 宽色域下天空易发灰红），",
                "高光分区染色更克制，蓝调不再把树叶子染成死青。",
                "",
                "## 重要",
                "",
                "- 必须在 **Apple Log / Apple Log 2** 色彩空间下使用",
                "- 若摄影机已是 Rec.709 / HDR，不要套这套（会发灰、发假）",
                "- Blackmagic：**Display LUT 开**，**Record LUT 关**",
                "",
                "## 风格",
                "",
                "| 文件 | 风格 |",
                "|---|---|",
            ]
            + [f"| `{f}` | {d} |" for _, d, f in rows]
            + [
                "",
                "重新下载覆盖旧文件后再导入；手机里旧 LUT 请先删掉再导一次。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("Wrote README.md")


if __name__ == "__main__":
    main()
