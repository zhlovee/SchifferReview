# Apple Log / Log2 创意 LUT（v2）

**v2 修复**：去掉错误的 Rec.2020→709 矩阵（Log2 宽色域下天空易发灰红），
高光分区染色更克制，蓝调不再把树叶子染成死青。

## 重要

- 必须在 **Apple Log / Apple Log 2** 色彩空间下使用
- 若摄影机已是 Rec.709 / HDR，不要套这套（会发灰、发假）
- Blackmagic：**Display LUT 开**，**Record LUT 关**

## 风格

| 文件 | 风格 |
|---|---|
| `01_Neutral_Rec709.cube` | 干净中性 Log→709，调色起点 |
| `02_Dreamy_Soft.cube` | 梦幻柔光，轻抬阴影、轻微降饱和 |
| `03_Blue_Mood.cube` | 蓝调情绪，阴影轻冷、天空保持干净 |
| `04_Moonlight_Cyan.cube` | 月光青感，偏冷但不染红高光 |
| `05_Fuji_Provia.cube` | 富士 Provia 感，清透自然 |
| `06_Fuji_Classic_Chrome.cube` | 富士 Classic Chrome，低饱和纪实 |
| `07_Fuji_Velvia.cube` | 富士 Velvia，浓郁但不过曝天空 |
| `08_Teal_Orange.cube` | 轻电影青橙（比 v1 克制很多） |
| `09_Warm_Film.cube` | 暖调胶片，日落感（高光轻暖） |
| `10_Pastel_Dream.cube` | 粉彩梦幻，柔和低对比 |
| `11_Bleach_Bypass.cube` | 漂白旁路，银调偏低饱和 |
| `12_Arctic_Cold.cube` | 极地冷调，干净冰蓝 |

重新下载覆盖旧文件后再导入；手机里旧 LUT 请先删掉再导一次。
