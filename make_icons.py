"""Generate SHAIK-AI app icons using only stdlib (no Pillow needed)"""
import os, struct, zlib, base64

ICONS_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(ICONS_DIR, exist_ok=True)

# Simple blue robot emoji rendered as PNG via HTML canvas data
# We'll create a solid blue square PNG programmatically
def make_png(size: int, path: str):
    def chunk(name: bytes, data: bytes) -> bytes:
        c = zlib.crc32(name + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", c)

    # RGBA: dark background + blue circle
    pixels = []
    cx = cy = size // 2
    r1 = size * 0.42
    r2 = size * 0.28
    for y in range(size):
        row = []
        for x in range(size):
            dx, dy = x - cx, y - cy
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < r1:
                if dist < r2:
                    # inner white circle (face)
                    row += [255, 255, 255, 255]
                else:
                    # blue ring
                    row += [88, 166, 255, 255]
            else:
                # dark background
                row += [13, 17, 23, 255]
        pixels.append(bytes(row))

    raw = b"".join(b"\x00" + row for row in pixels)
    compressed = zlib.compress(raw, 9)

    png  = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
                 .replace(struct.pack(">BBB", 2,0,0), struct.pack(">BBBBB", 2,0,0,0,0)))

    # Rebuild IHDR properly
    ihdr_data = struct.pack(">II", size, size) + bytes([8, 6, 0, 0, 0])
    png2  = b"\x89PNG\r\n\x1a\n"
    png2 += chunk(b"IHDR", ihdr_data)
    png2 += chunk(b"IDAT", compressed)
    png2 += chunk(b"IEND", b"")

    with open(path, "wb") as f:
        f.write(png2)
    print(f"[Icon] Created {path} ({size}x{size})")

make_png(192, os.path.join(ICONS_DIR, "icon-192.png"))
make_png(512, os.path.join(ICONS_DIR, "icon-512.png"))
print("Icons created!")
