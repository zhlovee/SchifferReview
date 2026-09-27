# Apple Log 2 创意风格 LUT 包

面向 **Apple Log / Apple Log 2** 素材，输出接近 **Rec.709** 的创意风格。
曲线按 Apple Log Profile 官方公式解码；色域为 Rec.2020→709 近似（创意向，非严格 Apple Wide Gamut 校色）。

## 包含风格

| 文件 | 风格 |
|---|---|
| `01_Neutral_Rec709.cube` | 干净中性转换，调色起点 |
| `02_Dreamy_Soft.cube` | 梦幻柔光，低对比偏粉青 |
| `03_Blue_Mood.cube` | 蓝调情绪，阴影冷青 |
| `04_Moonlight_Cyan.cube` | 月光青蓝，夜戏感 |
| `05_Fuji_Provia.cube` | 富士 Provia 感，清透自然 |
| `06_Fuji_Classic_Chrome.cube` | 富士 Classic Chrome，低饱和纪实 |
| `07_Fuji_Velvia.cube` | 富士 Velvia，浓郁风光色 |
| `08_Teal_Orange.cube` | 电影青橙，阴影青高光橙 |
| `09_Warm_Film.cube` | 暖调胶片，日落感 |
| `10_Pastel_Dream.cube` | 粉彩梦幻，少女感柔调 |
| `11_Bleach_Bypass.cube` | 漂白旁路，银调高对比 |
| `12_Arctic_Cold.cube` | 极地冷调，干净冰蓝 |

## Blackmagic Camera 用法

1. 把 `.cube` 拷到 iPhone「文件」App
2. 打开 Blackmagic Camera → **设置 → LUT**
3. **导入 LUT**，选中要用的风格
4. 打开 **Display LUT**（监视器用）
5. 建议关闭 **Record LUT**，保留干净 Log 后期再套

## 建议

- 先锁白平衡、曝光正常再套 LUT
- 梦幻/粉彩类对比偏软，适合人像与窗边逆光
- 蓝调/月光适合阴天、夜景、室内冷光
- 富士三款：Provia 日常、Chrome 街拍、Velvia 风景
- 若觉得过浓，在后期用 Mix/强度拉到 50–80%
