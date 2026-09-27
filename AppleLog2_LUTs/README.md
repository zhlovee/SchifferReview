# Apple Log / Log2 现成免费 LUT 合集

全部为网上作者发布的现成 `.cube`（非自写）。版权归属原作者，仅作搬运方便下载。

## 手机 / Blackmagic Camera 建议优先

拍 **Apple Log 2** 时：

1. `alessio-cinematic/AppleLog2_Cinematic.cube` — 电影感一体 LUT  
2. `tobia-kodak-d65/AppleLog2_33x/...cube` — Kodak 2383 胶片感（33 点，适合 App 监视）  
3. `joey-lj-fuji-gfx/FUJI-*.cube` — 富士风格（Velvia / Provia / Classic Chrome 等）  
4. `rodrigo-polo/AppleLog2_to_Rec709_33_Grid.cube` — 干净中性转换（无风格）  
5. `cinecolor/CINECOLOR_APPLE_LOG2_*.cube` — Log2→709 变体  

## 目录与来源

| 目录 | 内容 | 来源 |
|---|---|---|
| `rodrigo-polo/` | Log2→Rec.709 转换 | [Rodrigo Polo](https://rodrigopolo.com/2025/11/04/apple-log-2-to-rec-709-conversion-lut/) |
| `alessio-cinematic/` | Log1 / Log2 电影感 | [Alessio Gumroad](https://alessiolr.gumroad.com/l/FreeAppleLogLUT) |
| `tobia-kodak-d65/` | Kodak 2383 D65（含 Log 与 Log2） | [Tobia / Logflow](https://logflowtools.gumroad.com/l/applelogfilmiclooksluts) |
| `joey-lj-fuji-gfx/` | 富士 GFX 风格（Log2） | [Joey-LJ/LUTS](https://github.com/Joey-LJ/LUTS) (MIT) |
| `cinecolor/` | Log2 A/B/C | [CineColor](https://cinecolor.io/products/apple-log2-lut) |
| `sebastian-dylag/` | Log2 免费风格 | [Sebastian Dylag](https://sebastiandylag.com/product/apple-log-2-free-lut/) |

## 用法

1. 色彩空间选 **Apple Log 2**（或对应 Log）  
2. Blackmagic Camera → 设置 → LUT → 导入对应 `.cube`  
3. 开 **Display LUT**；建议关 **Record LUT**  
4. 手机监视优先用 **33x** 体积小的文件  

## 注意

- Log 与 Log2 不要混用（看文件名 / 文件夹）  
- 原作者条款以各自页面为准  
