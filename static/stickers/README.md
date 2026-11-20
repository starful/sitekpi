# Metric stickers (glossary mascot)

Optional cute loops on 指標辞典 `/glossary`. Missing file = layout unchanged.
Language-agnostic: one set for `ja` / `en` / `ko`. Grow one HELP id at a time; a full set is not required.

Served from opaque URLs (`/stk/<hash>.gif`) via `sitekpi/stickers.py` so ad blockers do not drop paths that look like analytics (`pageviews.gif`, …). Do **not** link cards to `/static/stickers/<id>.gif` in production HTML.

## Files

| Path | Role |
|------|------|
| `{HELP_id}.png` | Still (frame 1) |
| `{HELP_id}.gif` | 2-frame loop |
| `mascot-base.png` | Canonical pink-hair girl (reference only; not shown on cards) |
| `mascot-boy.png` | Alternate base (reference only) |

`stickers.py` skips stems that start with `mascot` or end with `-base`.

`HELP_id` must match a key in `sitekpi/metrics/help.py`.

## Character lock (do not redesign)

Default reference: `mascot-base.png`.

- Long wavy pastel pink hair
- Cream beret with beige bow + tiny blue flower
- Cream cable-knit cardigan, white collar, light blue plaid skirt
- White socks, brown Mary Jane shoes
- Brown satchel with tiny orange fox charm
- Flat vector LINE-sticker art, soft pastel, clean outlines, chibi proportions

Hair / outfit / colors stay fixed. Only pose and metric props change. Older stickers may use the brown-bob girl (`pageviews.png`); prefer pink `mascot-base` for new work.

## GenerateImage (Cursor)

Tool: `GenerateImage` · `aspect_ratio`: `1:1` · `reference_image_paths`: absolute path to reference · `filename`: stem only (no directory). Outputs land under the Cursor project `assets/` folder as `.jpg` / `.png`.

### Frame 1 — copy template

Replace `[POSE]` with the metric action (one clear prop + gesture).

```text
Same chibi sticker girl as the reference image: exact same face, long wavy pastel pink hair, cream beret with a beige bow and tiny blue flower, cream cable-knit cardigan, white collar, light blue plaid skirt, white socks, brown Mary Jane shoes, brown satchel with a tiny orange fox charm. Flat vector LINE-sticker art, soft pastel, clean outlines.

Pose for [METRIC / POSE]: [POSE]. Soft cream or soft lilac background, tiny floor shadow. No text, no numbers, no logos, no watermark, not realistic, not 3D.
```

Short form (when the reference already locks the design):

```text
Same character as the reference: exact same face, hair, outfit, colors, proportions, and flat sticker art style.
Only change the pose / action to: [POSE].
Keep chibi cute look, plain cream/lilac background, no text, no new character design.
```

### Frame 2 — motion for the GIF

Reference **frame 1** (the asset just generated), not only `mascot-base`. Motion must read at **~56px** on the glossary card — tiny blinks disappear. Prefer props jumping, arms rising, chart dots shifting, papers floating.

```text
Animation frame 2 of the exact same sticker as the reference. Keep the same girl, same outfit, same background, same framing, same main prop.
Only large readable motion: [MOTION]. Flat vector LINE sticker, no text, no logos, no watermark, no new objects.
```

### Pose ideas (examples)

| HELP id | Pose sketch |
|---------|-------------|
| `exit_rate` | Walking out a simple door / leaving |
| `cart_abandonment` | Leaving a cart behind |
| `utm` | Holding a small tag / labeled path prop (no readable letters) |
| `avg_session_duration` | Holding a round analog clock (no numbers) |
| `device_mobile` | Tall phone in both hands |
| `trend_8w` | Presenting a soft rising curve with eight dots |

## Pillow → `static/stickers/`

GenerateImage is still-only. Build a Chrome-friendly GIF from two RGB frames:

1. Resize both frames to **512×512**, convert to **RGB** (no alpha).
2. Save frame 1 as `{id}.png`.
3. Quantize each frame independently to **P mode, adaptive, 128 colors**.
4. `save_all` GIF: duration **500–650** ms, `loop=0`, `disposal=2`, **no transparency** on frame 0.

```python
from pathlib import Path
from PIL import Image

def to_rgb512(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    return im.resize((512, 512), Image.Resampling.LANCZOS)

def save_sticker(help_id: str, frame1: Path, frame2: Path, out_dir: Path, duration_ms: int = 650) -> None:
    f1 = to_rgb512(frame1)
    f2 = to_rgb512(frame2)
    f1.save(out_dir / f"{help_id}.png")
    p1 = f1.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    p2 = f2.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    p1.save(
        out_dir / f"{help_id}.gif",
        save_all=True,
        append_images=[p2],
        duration=duration_ms,
        loop=0,
        disposal=2,
        optimize=False,
    )
```

### Pitfalls

- Do **not** leave a transparency index on frame 0 (speckled face / freeze in Chrome).
- Subtle blink-only loops look frozen at card size — exaggerate motion.
- Screenshot tools often freeze on one GIF frame; verify by opening the raw `/stk/…gif` URL.
- Character drift between GenerateImage frames is normal; always reference frame 1 for frame 2.

## Checklist for a new metric

1. HELP entry exists (`help.py` + l10n if needed).
2. Frame 1 with `mascot-base.png` → Frame 2 with frame 1.
3. Write `{id}.png` + `{id}.gif` under this directory.
4. Confirm glossary card uses `/stk/…` and the loop is visible at card size.
