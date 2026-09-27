# Fuji GFX Look LUT for Apple Log 2 / Apple Log Gamut

A professional, single-stage Creative & Transform 3D LUT designed specifically for iPhone 17 Pro series and Final Cut Camera 2.0 footage. 

This LUT features a precision mathematical bridge that inputs **Apple Log 2 Gamma** paired with the **Apple Log Gamut **, and outputs a fully normalized, broadcast-ready **Rec.709 / Gamma 2.4** image—infused with the iconic color science, rich micro-contrast, and organic film-like look of **Fujifilm GFX medium-format cameras**.

---

## Technical Specifications

| Parameter | Specification |
| :--- | :--- |
| **Input Gamma** | Apple Log 2 (The latest ultra-flat log curve) |
| **Input Gamut** | Apple Log Gamut |
| **Output Color Space** | Rec.709 (Standard SDR Delivery) |
| **Output Gamma** | Gamma 2.4 / Rec.709 Standard |
| **LUT Format** | .cube (High-density 33x33x33 or 65x65x65 precision) |
| **Function** | Unified Transform + Creative Look (All-in-One) |

---

## Workflow Integration

### 1. DaVinci Resolve (Non-Managed / Standard YRGB)
Since this LUT handles both color space normalization and the creative look, use a simple 2-node serial pipeline:
* **Node 1 (Primary / Exposure Adjustment):** Do NOT apply the LUT here. Use this node to adjust *Offset*, *Contrast*, or *Exposure*. Since Apple Log 2 curves are exceptionally flat, compensate for any ETTR (Exposure Thoughts to the Right) variations here.
* **Node 2 (The Film Look):** Apply this **Fuji GFX Look LUT**. It will mathematically ingest the adjusted Apple Log 2 / Rec.2020 data and output the final, graded Rec.709 Fuji aesthetic.

### 2. Final Cut Pro X
1. Select your Apple Log 2 clips in the timeline.
2. Go to the **Inspector** window -> **Info** tab -> Change Metadata View to **Extended**.
3. In the **Camera LUT** dropdown, select **Add Custom Camera LUT...** and load this `.cube` file.
4. *Recommendation:* If the image appears too bright or dark under the LUT, apply the *Color Wheels* effect **before/above** the Custom LUT effect to manipulate the underlying log exposure.

### 3. Adobe Premiere Pro
1. Open the **Lumetri Color** panel.
2. Go to the **Basic Correction** tab.
3. Click the **Input LUT** dropdown menu, select **Browse...**, and choose this file. 
4. Because this LUT maps directly from Apple Log 2 to Rec.709, placing it as an Input LUT allows you to use the *Exposure* and *Contrast* sliders immediately below it to non-destructively tweak the image mapping.

---

## Grading Notes & Best Practices

* **The Apple Log 2 Advantage:** Apple Log 2 reallocates mid-tone and highlight values to lower IRE levels compared to V1. This LUT preserves that extended highlight headroom, giving you smooth, unclipped roll-offs in bright areas (like skies or window backlights) provided your exposure is balanced in Node 1.
* **Gamut Accuracy:** By mapping from the native Rec.2020 Apple Log Gamut to Rec.709, this LUT prevents common conversion artifacts such as oversaturating primary colors or tearing in high-luminance neon lights.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
