import os
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


def load_font(font_size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Try several common fonts, fallback to PIL default if none found."""
    candidate_fonts = [
        # DejaVu fonts are usually present in many Linux environments
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", True),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", False),
        # Fallbacks
        ("/System/Library/Fonts/Supplemental/Arial.ttf", False),
        ("/Library/Fonts/Arial.ttf", False),
    ]

    if bold:
        preferred = [p for p in candidate_fonts if p[1]] + [p for p in candidate_fonts if not p[1]]
    else:
        preferred = [p for p in candidate_fonts if not p[1]] + [p for p in candidate_fonts if p[1]]

    for path, _is_bold in preferred:
        try:
            return ImageFont.truetype(path, font_size)
        except Exception:
            continue

    return ImageFont.load_default()


def draw_vertical_gradient(draw: ImageDraw.ImageDraw, box: Tuple[int, int, int, int], top_color: Tuple[int, int, int], bottom_color: Tuple[int, int, int]):
    x0, y0, x1, y1 = box
    height = y1 - y0
    for i in range(height):
        ratio = i / max(1, height - 1)
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))


def rounded_rectangle(draw: ImageDraw.ImageDraw, xy: Tuple[int, int, int, int], radius: int, fill: Tuple[int, int, int, int]):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def fit_image(img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    img = img.copy()
    img.thumbnail(target_size, Image.LANCZOS)
    canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
    x = (target_size[0] - img.width) // 2
    y = (target_size[1] - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def make_flyer(
    background_top: Tuple[int, int, int] = (2, 86, 148),
    background_bottom: Tuple[int, int, int] = (0, 160, 204),
    title: str = "RentTN",
    tagline: str = "Find and rent homes across Tunisia. Fast, safe, simple.",
    bullets=None,
    input_image_path: str = "./assets/input.jpg",
    logo_image_path: str = "./assets/logo.png",
    output_basename: str = "./output/renttn_flyer",
):
    if bullets is None:
        bullets = [
            "Verified listings and landlords",
            "Smart filters: price, type, amenities",
            "In-app chat and appointments",
            "Map view and saved favorites",
        ]

    # A4 at 300 DPI
    dpi = 300
    width_in, height_in = 8.27, 11.69
    width_px, height_px = int(width_in * dpi), int(height_in * dpi)

    base = Image.new("RGBA", (width_px, height_px), (255, 255, 255, 255))
    draw = ImageDraw.Draw(base)

    # Background gradient
    draw_vertical_gradient(draw, (0, 0, width_px, height_px), background_top, background_bottom)

    # Content layout
    margin = int(0.06 * width_px)
    top_margin = int(0.07 * height_px)

    # Header: logo square and title
    logo_target_size = int(0.11 * width_px)
    logo_box = (margin, top_margin, margin + logo_target_size, top_margin + logo_target_size)
    if os.path.exists(logo_image_path):
        logo = Image.open(logo_image_path).convert("RGBA")
        # Keep logo exactly as provided (no color change); just fit within square
        logo = fit_image(logo, (logo_target_size, logo_target_size))
        base.alpha_composite(logo, (logo_box[0], logo_box[1]))

    # Title and tagline
    title_font = load_font(int(0.09 * width_px), bold=True)
    subtitle_font = load_font(int(0.03 * width_px))

    title_x = logo_box[2] + int(0.03 * width_px)
    title_y = logo_box[1] + int(0.01 * height_px)
    draw.text((title_x, title_y), title, fill=(255, 255, 255), font=title_font)

    taglines = [tagline]
    t_y = title_y + int(0.12 * width_px)
    for t in taglines:
        draw.text((title_x, t_y), t, fill=(230, 247, 255), font=subtitle_font)
        t_y += int(0.04 * width_px)

    # Phone mockup container card
    card_top = logo_box[3] + int(0.05 * height_px)
    card_height = int(0.52 * height_px)
    card = (margin, card_top, width_px - margin, card_top + card_height)
    rounded_rectangle(draw, card, radius=int(0.02 * width_px), fill=(255, 255, 255, 30))

    # App screenshot/device image
    if os.path.exists(input_image_path):
        app_img = Image.open(input_image_path).convert("RGBA")
    else:
        # Placeholder
        app_img = Image.new("RGBA", (900, 1800), (240, 240, 240, 255))
        d = ImageDraw.Draw(app_img)
        ph_font = load_font(int(0.05 * app_img.width), bold=True)
        d.text((app_img.width // 6, app_img.height // 2 - 40), "Your App Image", fill=(120, 120, 120), font=ph_font)

    app_zone_w = int(0.42 * width_px)
    app_zone_h = int(card_height * 0.92)
    app_zone_x = card[0] + int(0.05 * width_px)
    app_zone_y = card[1] + (card_height - app_zone_h) // 2
    app_fitted = fit_image(app_img, (app_zone_w, app_zone_h))
    base.alpha_composite(app_fitted, (app_zone_x, app_zone_y))

    # Benefit list on the right side
    list_x = app_zone_x + app_zone_w + int(0.05 * width_px)
    list_y = app_zone_y + int(0.02 * height_px)
    bullet_font = load_font(int(0.038 * width_px))
    bullet_color = (255, 255, 255)
    check_color = (102, 239, 197)

    for line in bullets:
        # Draw a check circle
        r = int(0.016 * width_px)
        draw.ellipse((list_x, list_y, list_x + 2 * r, list_y + 2 * r), fill=check_color)
        draw.text((list_x + 2 * r + int(0.012 * width_px), list_y - int(0.006 * width_px)), line, fill=bullet_color, font=bullet_font)
        list_y += int(0.065 * height_px)

    # CTA band at bottom
    cta_height = int(0.16 * height_px)
    cta_y0 = height_px - cta_height - margin
    cta = (margin, cta_y0, width_px - margin, cta_y0 + cta_height)
    rounded_rectangle(draw, cta, radius=int(0.02 * width_px), fill=(255, 255, 255, 38))

    # CTA text
    cta_title_font = load_font(int(0.06 * width_px), bold=True)
    cta_sub_font = load_font(int(0.032 * width_px))
    cta_text_x = cta[0] + int(0.04 * width_px)
    cta_text_y = cta[1] + int(0.18 * cta_height)
    draw.text((cta_text_x, cta_text_y), "Download the app", fill=(255, 255, 255), font=cta_title_font)
    draw.text((cta_text_x, cta_text_y + int(0.33 * cta_height)), "Scan to get RentTN on iOS & Android", fill=(230, 247, 255), font=cta_sub_font)

    # Optional: QR placeholder area (kept simple to avoid external deps)
    qr_box_size = int(0.18 * width_px)
    qr_x = cta[2] - qr_box_size - int(0.04 * width_px)
    qr_y = cta[1] + (cta_height - qr_box_size) // 2
    rounded_rectangle(draw, (qr_x, qr_y, qr_x + qr_box_size, qr_y + qr_box_size), radius=int(0.02 * width_px), fill=(255, 255, 255, 220))
    qr_text_font = load_font(int(0.028 * width_px), bold=True)
    draw.text((qr_x + int(0.08 * qr_box_size), qr_y + int(0.4 * qr_box_size)), "QR", fill=(2, 86, 148), font=qr_text_font)

    # Ensure output dir exists
    os.makedirs(os.path.dirname(output_basename), exist_ok=True)
    png_path = f"{output_basename}.png"
    pdf_path = f"{output_basename}.pdf"

    base_rgb = base.convert("RGB")
    base_rgb.save(png_path, "PNG")
    base_rgb.save(pdf_path, "PDF", resolution=dpi)

    return png_path, pdf_path


if __name__ == "__main__":
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    input_img = os.path.join(assets_dir, "input.jpg")
    logo_img = os.path.join(assets_dir, "logo.png")
    output_base = os.path.join(os.path.dirname(__file__), "output", "renttn_flyer")

    png, pdf = make_flyer(
        input_image_path=input_img,
        logo_image_path=logo_img,
        output_basename=output_base,
    )
    print("Saved:", png)
    print("Saved:", pdf)

