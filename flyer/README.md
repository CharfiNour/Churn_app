RentTN Flyer Generator

Usage

1. Place your unmodified logo as `flyer/assets/logo.png`.
2. Place the provided phone/screenshot image as `flyer/assets/input.jpg` (JPEG/PNG supported).
3. Run:

```
python3 flyer/make_flyer.py
```

Outputs are written to `flyer/output/renttn_flyer.png` and `.pdf` in A4 size at 300 DPI.

Notes

- The logo is composited exactly as provided (no recolor). Size is only fitted.
- Colors follow the blue gradient visible in your reference.
- Edit text or bullets by changing parameters in `make_flyer()` in `flyer/make_flyer.py`.
- If Pillow is missing, install it with `pip install Pillow --break-system-packages`.

