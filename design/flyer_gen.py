import os
from dataclasses import dataclass
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np


# -----------------------------
# Config and utilities
# -----------------------------

@dataclass
class FlyerConfig:
    app_name: str = "RentTN"
    tagline: str = "Find your next home in Tunisia"
    website: Optional[str] = None  # e.g. "rent.tn"
    cta_text: str = "Download the app"
    primary_hex: str = "#0E6AAE"  # deep blue from provided scheme
    secondary_hex: str = "#11A6D6"  # lighter cyan-blue from provided scheme
    gradient_start_hex: str = "#0E6AAE"
    gradient_end_hex: str = "#13B0E6"
    text_on_dark_hex: str = "#FFFFFF"
    accent_hex: str = "#00E0A4"  # mint accent for price/CTA


ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
INPUT_DIR = os.path.join(ASSETS_DIR, "input")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")  # Place exact logo here (won't be altered)
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def ensure_dirs() -> None:
    for path in [ASSETS_DIR, INPUT_DIR, FONTS_DIR, OUTPUT_DIR]:
        os.makedirs(path, exist_ok=True)


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def create_linear_gradient(width: int, height: int, start_hex: str, end_hex: str) -> Image.Image:
    start_rgb = np.array(hex_to_rgb(start_hex), dtype=np.float32)
    end_rgb = np.array(hex_to_rgb(end_hex), dtype=np.float32)
    # vertical gradient -> shape (h, 1, 3) then tile to width
    t = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, None]
    gradient_col = (start_rgb * (1.0 - t) + end_rgb * t).astype(np.uint8)  # (h, 3)
    gradient_col = gradient_col[:, None, :]  # (h, 1, 3)
    gradient = np.tile(gradient_col, (1, width, 1))  # (h, w, 3)
    return Image.fromarray(gradient, mode="RGB")


def load_font(preferred_path: Optional[str], size: int) -> ImageFont.FreeTypeFont:
    try:
        if preferred_path and os.path.exists(preferred_path):
            return ImageFont.truetype(preferred_path, size=size)
        # Try common system fonts
        for name in [
            "Inter-SemiBold.ttf",
            "Inter-Bold.ttf",
            "Montserrat-SemiBold.ttf",
            "Montserrat-Bold.ttf",
            "DejaVuSans.ttf",
        ]:
            fp = os.path.join(FONTS_DIR, name)
            if os.path.exists(fp):
                return ImageFont.truetype(fp, size=size)
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()


def draw_round_rect(draw: ImageDraw.ImageDraw, xy: Tuple[int, int, int, int], radius: int, fill: Optional[Tuple[int, int, int]] = None, outline: Optional[Tuple[int, int, int]] = None, width: int = 2) -> None:
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def paste_centered(background: Image.Image, fg: Image.Image, box: Tuple[int, int, int, int]) -> None:
    bx0, by0, bx1, by1 = box
    bw, bh = bx1 - bx0, by1 - by0
    ratio = min(bw / fg.width, bh / fg.height)
    scaled = fg.resize((int(fg.width * ratio), int(fg.height * ratio)), Image.LANCZOS)
    ox = bx0 + (bw - scaled.width) // 2
    oy = by0 + (bh - scaled.height) // 2
    background.paste(scaled, (ox, oy), scaled if scaled.mode == "RGBA" else None)


def find_first_image(search_dir: str) -> Optional[str]:
    if not os.path.exists(search_dir):
        return None
    for name in os.listdir(search_dir):
        if name.lower().endswith((".png", ".jpg", ".jpeg")):
            return os.path.join(search_dir, name)
    return None


def add_drop_shadow(img: Image.Image, offset: Tuple[int, int] = (0, 8), radius: int = 24, opacity: int = 120) -> Image.Image:
    shadow = Image.new("RGBA", (img.width + abs(offset[0]) * 2, img.height + abs(offset[1]) * 2), (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, opacity))
    shadow.paste(shadow_layer, (abs(offset[0]), abs(offset[1])))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius))
    out = Image.new("RGBA", shadow.size, (0, 0, 0, 0))
    out.paste(shadow, (0, 0))
    out.paste(img, (abs(offset[0]), abs(offset[1])), img)
    return out


def draw_header(draw: ImageDraw.ImageDraw, cfg: FlyerConfig, canvas: Image.Image, padding: int, logo_max: int) -> int:
    text_color = hex_to_rgb(cfg.text_on_dark_hex)
    # Logo container
    y = padding
    x = padding
    container_size = logo_max
    radius = container_size // 5
    container_box = (x, y, x + container_size, y + container_size)
    draw_round_rect(draw, container_box, radius, fill=(255, 255, 255), outline=None)

    # Paste logo inside container without modification
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            # inset a bit inside container
            inset = container_size // 8
            logo_box = (x + inset, y + inset, x + container_size - inset, y + container_size - inset)
            paste_centered(canvas, logo, logo_box)
        except Exception:
            pass

    # App name
    title_font = load_font(os.path.join(FONTS_DIR, "Inter-SemiBold.ttf"), size=int(container_size * 0.8))
    title_x = x + container_size + padding
    title_y = y + (container_size - title_font.size) // 2
    draw.text((title_x, title_y), cfg.app_name, fill=text_color, font=title_font)

    return y + container_size


def draw_phone_showcase(base: Image.Image, area: Tuple[int, int, int, int], screenshot_path: Optional[str]) -> None:
    x0, y0, x1, y1 = area
    w, h = x1 - x0, y1 - y0
    corner = min(w, h) // 12
    phone_bg = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    mask = Image.new("L", (w, h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, w, h], radius=corner, fill=255)
    phone_bg.putalpha(mask)

    # Screen inset
    screen_inset = max(12, min(w, h) // 18)
    screen_box = (screen_inset, screen_inset, w - screen_inset, h - screen_inset)

    # Paste screenshot or placeholder
    if screenshot_path and os.path.exists(screenshot_path):
        try:
            shot = Image.open(screenshot_path).convert("RGBA")
            # Slightly round the inner screen
            screen = Image.new("RGBA", (screen_box[2] - screen_box[0], screen_box[3] - screen_box[1]), (0, 0, 0, 0))
            mask2 = Image.new("L", screen.size, 0)
            ImageDraw.Draw(mask2).rounded_rectangle([0, 0, screen.size[0], screen.size[1]], radius=corner // 2, fill=255)
            ratio = min(screen.size[0] / shot.width, screen.size[1] / shot.height)
            shot_scaled = shot.resize((int(shot.width * ratio), int(shot.height * ratio)), Image.LANCZOS)
            temp = Image.new("RGBA", screen.size, (0, 0, 0, 0))
            paste_centered(temp, shot_scaled, (0, 0, screen.size[0], screen.size[1]))
            screen.paste(temp, (0, 0), mask2)
            phone_bg.paste(screen, (screen_box[0], screen_box[1]), screen)
        except Exception:
            _draw_placeholder_screen(phone_bg, screen_box)
    else:
        _draw_placeholder_screen(phone_bg, screen_box)

    phone_with_shadow = add_drop_shadow(phone_bg, offset=(0, 18), radius=36, opacity=110)
    base.paste(phone_with_shadow, (x0, y0), phone_with_shadow)


def _draw_placeholder_screen(img: Image.Image, box: Tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(box, radius=16, fill=(237, 243, 247))
    draw.text(((x0 + x1) // 2, (y0 + y1) // 2), "Your app UI here", anchor="mm", fill=(120, 130, 140))


def draw_feature_card(canvas: Image.Image, area: Tuple[int, int, int, int], title: str, bullets: Tuple[str, ...], cfg: FlyerConfig) -> None:
    x0, y0, x1, y1 = area
    draw = ImageDraw.Draw(canvas)
    bg = Image.new("RGBA", (x1 - x0, y1 - y0), (255, 255, 255, 255))
    mask = Image.new("L", bg.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, bg.size[0], bg.size[1]], radius=24, fill=255)
    bg.putalpha(mask)
    bg = add_drop_shadow(bg, offset=(0, 10), radius=20, opacity=100)
    canvas.paste(bg, (x0, y0), bg)

    inner_pad = 36
    text_color = (25, 41, 57)
    title_font = load_font(os.path.join(FONTS_DIR, "Inter-Bold.ttf"), size=44)
    body_font = load_font(os.path.join(FONTS_DIR, "Inter-SemiBold.ttf"), size=30)

    draw.text((x0 + inner_pad, y0 + inner_pad), title, fill=text_color, font=title_font)
    by = y0 + inner_pad + title_font.size + 12
    for bullet in bullets:
        # bullet dot
        dot_r = 6
        dot_x = x0 + inner_pad
        dot_y = by + body_font.size // 2
        draw.ellipse((dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r), fill=hex_to_rgb(cfg.accent_hex))
        draw.text((x0 + inner_pad + 20, by), bullet, fill=text_color, font=body_font)
        by += body_font.size + 12


def draw_cta(draw: ImageDraw.ImageDraw, cfg: FlyerConfig, canvas: Image.Image, center_x: int, y: int, width: int, height: int) -> None:
    btn_box = (center_x - width // 2, y, center_x + width // 2, y + height)
    draw_round_rect(draw, btn_box, radius=height // 2, fill=hex_to_rgb(cfg.accent_hex))
    font = load_font(os.path.join(FONTS_DIR, "Inter-SemiBold.ttf"), size=int(height * 0.45))
    draw.text((center_x, y + height // 2), cfg.cta_text, anchor="mm", fill=(0, 45, 35), font=font)


def render_flyer(size_name: str, width: int, height: int, cfg: FlyerConfig) -> str:
    ensure_dirs()
    bg = create_linear_gradient(width, height, cfg.gradient_start_hex, cfg.gradient_end_hex)
    draw = ImageDraw.Draw(bg)

    padding = int(min(width, height) * 0.04)
    header_h = draw_header(draw, cfg, bg, padding=padding, logo_max=int(min(width, height) * 0.08))

    # Tagline under header
    tagline_font = load_font(os.path.join(FONTS_DIR, "Inter-SemiBold.ttf"), size=int(min(width, height) * 0.035))
    draw.text((padding, header_h + int(padding * 0.5)), cfg.tagline, fill=hex_to_rgb(cfg.text_on_dark_hex), font=tagline_font)

    # Layout: phone on right, features on left (or stacked on small size)
    content_top = header_h + int(padding * 2.2)
    content_bottom = height - padding
    content_left = padding
    content_right = width - padding

    is_narrow = width < 1400

    screenshot_path = find_first_image(INPUT_DIR)

    if is_narrow:
        # Stacked layout
        phone_h = int((content_bottom - content_top) * 0.48)
        phone_box = (content_left, content_top, content_right, content_top + phone_h)
        draw_phone_showcase(bg, phone_box, screenshot_path)

        card_top = phone_box[3] + padding
        card_box = (content_left, card_top, content_right, content_bottom)
        draw_feature_card(
            bg,
            card_box,
            title="Why RentTN?",
            bullets=(
                "Smart search: city, type, price",
                "Clean listings with real photos",
                "Fast contact with owners",
            ),
            cfg=cfg,
        )
        cta_y = card_box[3] - int(padding * 1.6)
        draw_cta(draw, cfg, bg, center_x=width // 2, y=cta_y, width=int(width * 0.4), height=int(min(width, height) * 0.065))
    else:
        # Two-column layout
        mid_x = (content_left + content_right) // 2
        left_box = (content_left, content_top, mid_x - padding // 2, content_bottom)
        right_box = (mid_x + padding // 2, content_top, content_right, content_bottom)

        # Features on left
        draw_feature_card(
            bg,
            (left_box[0], left_box[1], left_box[2], left_box[1] + int((left_box[3] - left_box[1]) * 0.62)),
            title="Find places you love",
            bullets=(
                "Filter by location and budget",
                "Browse verified apartments and studios",
                "See details at a glance",
            ),
            cfg=cfg,
        )
        draw_cta(draw, cfg, bg, center_x=(left_box[0] + left_box[2]) // 2, y=left_box[3] - int(min(width, height) * 0.11), width=int((left_box[2] - left_box[0]) * 0.8), height=int(min(width, height) * 0.065))

        # Phone on right
        draw_phone_showcase(bg, right_box, screenshot_path)

    # Website footer
    if cfg.website:
        foot_font = load_font(os.path.join(FONTS_DIR, "Inter-SemiBold.ttf"), size=int(min(width, height) * 0.028))
        draw.text((width - padding, height - padding // 2), cfg.website, anchor="rs", fill=hex_to_rgb(cfg.text_on_dark_hex), font=foot_font)

    out_name = f"flyer_{size_name}.png"
    out_path = os.path.join(OUTPUT_DIR, out_name)
    bg.save(out_path)
    return out_path


def main() -> None:
    cfg = FlyerConfig()
    # A4 at 300 DPI: 2480 x 3508
    a4_path = render_flyer("A4_2480x3508", 2480, 3508, cfg)
    # Instagram portrait 1080 x 1350
    ig_path = render_flyer("IG_1080x1350", 1080, 1350, cfg)
    print("Saved:")
    print(a4_path)
    print(ig_path)


if __name__ == "__main__":
    ensure_dirs()
    main()

