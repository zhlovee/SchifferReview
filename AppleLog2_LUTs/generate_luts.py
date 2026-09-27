#!/usr/bin/env python3
"""Generate Apple Log 2 → Rec.709 creative look LUTs (.cube).

Transfer function: Apple Log Profile (same curve for Apple Log 2).
Gamut: approximate Rec.2020 → Rec.709 (creative LUTs; not colorimetric AWG).
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np

OUT_DIR = Path(__file__).resolve().parent
SIZE = 33

# Apple Log Profile constants (Apple white paper / colour-science)
R_0 = -0.05641088
R_T = 0.01
SIGMA = 47.28711236
BETA = 0.00964052
GAMMA = 0.08550479
DELTA = 0.69336945
P_T = SIGMA * (R_T - R_0) ** 2

# Rec.2020 → XYZ → Rec.709 (D65), approximate for creative looks
M_2020_TO_709 = np.array(
    [
        [1.660491, -0.587641, -0.072850],
        [-0.124550, 1.132900, -0.008349],
        [-0.018151, -0.100579, 1.118730],
    ],
    dtype=np.float64,
)


def apple_log_decode(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 0.0, 1.0)
    out = np.empty_like(p)
    hi = p >= P_T
    mid = (p >= 0.0) & (~hi)
    out[hi] = 2.0 ** ((p[hi] - DELTA) / GAMMA) - BETA
    out[mid] = np.sqrt(np.maximum(p[mid], 0.0) / SIGMA) + R_0
    out[~ (hi | mid)] = R_0
    return np.maximum(out, 0.0)


def rec709_encode(linear: np.ndarray) -> np.ndarray:
    linear = np.maximum(linear, 0.0)
    return np.where(
        linear <= 0.018,
        4.5 * linear,
        1.099 * np.power(linear, 0.45) - 0.099,
    )


def soft_clip(x: np.ndarray, hi: float = 0.98) -> np.ndarray:
    x = np.clip(x, 0.0, None)
    return np.where(x < hi, x, hi + (1.0 - hi) * (1.0 - np.exp(-(x - hi) / (1.0 - hi))))


def lift_gamma_gain(rgb: np.ndarray, lift=0.0, gamma=1.0, gain=1.0) -> np.ndarray:
    rgb = rgb * gain + lift
    rgb = np.clip(rgb, 1e-6, None)
    return np.power(rgb, 1.0 / max(gamma, 1e-6))


def saturate(rgb: np.ndarray, amount: float) -> np.ndarray:
    luma = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    return luma[..., None] + (rgb - luma[..., None]) * amount


def tint_shadows_highlights(
    rgb: np.ndarray,
    shadow_tint: np.ndarray,
    highlight_tint: np.ndarray,
    shadow_str: float = 0.25,
    highlight_str: float = 0.18,
) -> np.ndarray:
    luma = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    shadow_mask = np.clip(1.0 - luma * 2.2, 0.0, 1.0)[..., None]
    highlight_mask = np.clip((luma - 0.45) * 2.0, 0.0, 1.0)[..., None]
    rgb = rgb + shadow_mask * shadow_tint * shadow_str
    rgb = rgb + highlight_mask * highlight_tint * highlight_str
    return rgb


def contrast_s_curve(rgb: np.ndarray, amount: float = 0.15) -> np.ndarray:
    # Gentle S around mid-gray in display space
    x = np.clip(rgb, 0.0, 1.0)
    mid = 0.5
    return mid + (x - mid) * (1.0 + amount * (1.0 - 2.0 * np.abs(x - mid)))


LOOKS = {
    "01_Neutral_Rec709": {
        "desc": "干净中性转换，调色起点",
        "lift": 0.01,
        "gamma": 1.02,
        "gain": 1.05,
        "sat": 1.02,
        "contrast": 0.08,
        "shadow": np.array([0.0, 0.0, 0.01]),
        "highlight": np.array([0.01, 0.005, 0.0]),
        "ss": 0.05,
        "hs": 0.05,
    },
    "02_Dreamy_Soft": {
        "desc": "梦幻柔光，低对比偏粉青",
        "lift": 0.04,
        "gamma": 1.12,
        "gain": 1.02,
        "sat": 0.88,
        "contrast": -0.05,
        "shadow": np.array([0.02, 0.0, 0.04]),
        "highlight": np.array([0.06, 0.03, 0.05]),
        "ss": 0.22,
        "hs": 0.28,
    },
    "03_Blue_Mood": {
        "desc": "蓝调情绪，阴影冷青",
        "lift": 0.0,
        "gamma": 1.05,
        "gain": 1.0,
        "sat": 0.95,
        "contrast": 0.12,
        "shadow": np.array([-0.02, 0.02, 0.08]),
        "highlight": np.array([0.02, 0.01, 0.04]),
        "ss": 0.35,
        "hs": 0.15,
    },
    "04_Moonlight_Cyan": {
        "desc": "月光青蓝，夜戏感",
        "lift": -0.01,
        "gamma": 1.08,
        "gain": 0.98,
        "sat": 0.85,
        "contrast": 0.18,
        "shadow": np.array([-0.04, 0.03, 0.10]),
        "highlight": np.array([0.0, 0.04, 0.08]),
        "ss": 0.4,
        "hs": 0.22,
    },
    "05_Fuji_Provia": {
        "desc": "富士 Provia 感，清透自然",
        "lift": 0.015,
        "gamma": 1.0,
        "gain": 1.06,
        "sat": 1.08,
        "contrast": 0.1,
        "shadow": np.array([0.01, 0.0, 0.02]),
        "highlight": np.array([0.02, 0.015, 0.0]),
        "ss": 0.12,
        "hs": 0.1,
    },
    "06_Fuji_Classic_Chrome": {
        "desc": "富士 Classic Chrome，低饱和纪实",
        "lift": 0.02,
        "gamma": 1.04,
        "gain": 1.02,
        "sat": 0.78,
        "contrast": 0.14,
        "shadow": np.array([0.02, 0.0, 0.03]),
        "highlight": np.array([0.03, 0.02, 0.01]),
        "ss": 0.18,
        "hs": 0.12,
    },
    "07_Fuji_Velvia": {
        "desc": "富士 Velvia，浓郁风光色",
        "lift": 0.0,
        "gamma": 0.96,
        "gain": 1.08,
        "sat": 1.35,
        "contrast": 0.22,
        "shadow": np.array([0.02, -0.01, 0.04]),
        "highlight": np.array([0.04, 0.02, -0.01]),
        "ss": 0.15,
        "hs": 0.12,
    },
    "08_Teal_Orange": {
        "desc": "电影青橙，阴影青高光橙",
        "lift": 0.0,
        "gamma": 1.02,
        "gain": 1.04,
        "sat": 1.05,
        "contrast": 0.16,
        "shadow": np.array([-0.03, 0.04, 0.08]),
        "highlight": np.array([0.08, 0.03, -0.02]),
        "ss": 0.32,
        "hs": 0.25,
    },
    "09_Warm_Film": {
        "desc": "暖调胶片，日落感",
        "lift": 0.02,
        "gamma": 1.03,
        "gain": 1.05,
        "sat": 1.0,
        "contrast": 0.12,
        "shadow": np.array([0.05, 0.01, -0.02]),
        "highlight": np.array([0.08, 0.04, 0.0]),
        "ss": 0.2,
        "hs": 0.22,
    },
    "10_Pastel_Dream": {
        "desc": "粉彩梦幻，少女感柔调",
        "lift": 0.05,
        "gamma": 1.15,
        "gain": 1.0,
        "sat": 0.82,
        "contrast": -0.08,
        "shadow": np.array([0.04, 0.0, 0.05]),
        "highlight": np.array([0.08, 0.05, 0.06]),
        "ss": 0.25,
        "hs": 0.3,
    },
    "11_Bleach_Bypass": {
        "desc": "漂白旁路，银调高对比",
        "lift": -0.02,
        "gamma": 0.92,
        "gain": 1.1,
        "sat": 0.55,
        "contrast": 0.28,
        "shadow": np.array([0.01, 0.01, 0.02]),
        "highlight": np.array([0.03, 0.03, 0.02]),
        "ss": 0.1,
        "hs": 0.1,
    },
    "12_Arctic_Cold": {
        "desc": "极地冷调，干净冰蓝",
        "lift": 0.01,
        "gamma": 1.06,
        "gain": 1.02,
        "sat": 0.9,
        "contrast": 0.1,
        "shadow": np.array([-0.01, 0.02, 0.07]),
        "highlight": np.array([0.01, 0.03, 0.06]),
        "ss": 0.3,
        "hs": 0.2,
    },
}


def apply_look(linear_rgb: np.ndarray, look: dict) -> np.ndarray:
    # Gamut: Rec.2020-ish linear → Rec.709 linear (approx)
    shaped = linear_rgb @ M_2020_TO_709.T
    shaped = soft_clip(shaped, hi=1.2)

    # Exposure pivot around middle gray (~0.18 linear)
    shaped = shaped * look["gain"]
    display = rec709_encode(shaped)
    display = lift_gamma_gain(display, lift=look["lift"], gamma=look["gamma"], gain=1.0)
    display = contrast_s_curve(display, amount=look["contrast"])
    display = tint_shadows_highlights(
        display,
        look["shadow"],
        look["highlight"],
        shadow_str=look["ss"],
        highlight_str=look["hs"],
    )
    display = saturate(display, look["sat"])
    return np.clip(display, 0.0, 1.0)


def build_lut(look: dict) -> np.ndarray:
    coords = np.linspace(0.0, 1.0, SIZE)
    r, g, b = np.meshgrid(coords, coords, coords, indexing="ij")
    log_rgb = np.stack([r, g, b], axis=-1)
    linear = apple_log_decode(log_rgb)
    out = apply_look(linear, look)
    # .cube order: B changes fastest, then G, then R
    # With indexing ij meshgrid on (r,g,b), flatten in order r,g,b matches:
    # for r in R: for g in G: for b in B
    return out.reshape(-1, 3)


def write_cube(path: Path, data: np.ndarray, title: str, desc: str) -> None:
    lines = [
        f'TITLE "{title}"',
        f"# Apple Log 2 creative look — {desc}",
        "# Input: Apple Log / Apple Log 2 (same TF)",
        "# Output: Rec.709 display-referred (creative, approximate gamut)",
        "# Use as Display LUT in Blackmagic Camera; prefer Record LUT OFF",
        f"LUT_3D_SIZE {SIZE}",
        "DOMAIN_MIN 0.0 0.0 0.0",
        "DOMAIN_MAX 1.0 1.0 1.0",
    ]
    for rgb in data:
        lines.append(f"{rgb[0]:.6f} {rgb[1]:.6f} {rgb[2]:.6f}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    readme_rows = []
    for name, look in LOOKS.items():
        data = build_lut(look)
        cube_path = OUT_DIR / f"{name}.cube"
        write_cube(cube_path, data, name, look["desc"])
        readme_rows.append((name, look["desc"], cube_path.name))
        print(f"Wrote {cube_path.name}")

    readme = OUT_DIR / "README.md"
    lines = [
        "# Apple Log 2 创意风格 LUT 包",
        "",
        "面向 **Apple Log / Apple Log 2** 素材，输出接近 **Rec.709** 的创意风格。",
        "曲线按 Apple Log Profile 官方公式解码；色域为 Rec.2020→709 近似（创意向，非严格 Apple Wide Gamut 校色）。",
        "",
        "## 包含风格",
        "",
        "| 文件 | 风格 |",
        "|---|---|",
    ]
    for name, desc, fname in readme_rows:
        lines.append(f"| `{fname}` | {desc} |")
    lines += [
        "",
        "## Blackmagic Camera 用法",
        "",
        "1. 把 `.cube` 拷到 iPhone「文件」App",
        "2. 打开 Blackmagic Camera → **设置 → LUT**",
        "3. **导入 LUT**，选中要用的风格",
        "4. 打开 **Display LUT**（监视器用）",
        "5. 建议关闭 **Record LUT**，保留干净 Log 后期再套",
        "",
        "## 建议",
        "",
        "- 先锁白平衡、曝光正常再套 LUT",
        "- 梦幻/粉彩类对比偏软，适合人像与窗边逆光",
        "- 蓝调/月光适合阴天、夜景、室内冷光",
        "- 富士三款：Provia 日常、Chrome 街拍、Velvia 风景",
        "- 若觉得过浓，在后期用 Mix/强度拉到 50–80%",
        "",
    ]
    readme.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {readme.name}")


if __name__ == "__main__":
    main()
