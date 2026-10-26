"""Regenerate the site favicons from the real logo (the existing ones were 40-byte placeholder files)."""
import os
from PIL import Image

STATIC_IMG = os.path.join("btre", "static", "img")
LOGO = os.path.join(STATIC_IMG, "logo.png")

img = Image.open(LOGO).convert("RGBA")
print("logo.png:", img.size, img.format)

for size in (192, 512):
    out = os.path.join(STATIC_IMG, f"favicon-{size}.png")
    resized = img.resize((size, size), Image.LANCZOS)
    resized.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")

# also a plain favicon.ico at both common locations used by browsers
ico_32 = img.resize((32, 32), Image.LANCZOS)
ico_32.save(os.path.join(STATIC_IMG, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
print("favicon.ico written")
