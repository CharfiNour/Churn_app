Flyer generator for the RentTN mobile app

How it works
- Outputs two sizes in `design/output/`:
  - `flyer_A4_2480x3508.png` (A4 @ 300dpi)
  - `flyer_IG_1080x1350.png` (Instagram portrait)
- Uses your exact logo from `design/assets/logo.png` (not modified).
- If you add a UI screenshot to `design/assets/input/` (PNG/JPG), it will be showcased inside a phone mockup. If not present, a tasteful placeholder is used.

Setup
1. Place your unaltered logo at `design/assets/logo.png` (transparent PNG recommended).
2. Optionally drop a high-res app screenshot into `design/assets/input/`.
3. (Optional) Put any preferred fonts in `design/assets/fonts/` (e.g., Inter or Montserrat). The script will automatically use them if found, otherwise it falls back to system/default fonts.

Run
```bash
pip install -r requirements.txt
python design/flyer_gen.py
```

Customization
- Edit defaults in `FlyerConfig` inside `design/flyer_gen.py` to change texts, gradient colors, and CTA.
- Colors are tuned to match the provided blue scheme; adjust `gradient_start_hex` and `gradient_end_hex` if needed.

Notes
- Your logo is never altered by the script. It is only placed inside a rounded white tile as shown in the preview.
