import math
import os
from PIL import Image, ImageDraw, ImageFilter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def make_dark_bg(size=64, frame_color=(50, 40, 30)):
    im = Image.new('RGBA', (size, size), (10, 8, 14, 255))
    for y in range(size):
        for x in range(size):
            dx = (x - 31.5) / 32.0
            dy = (y - 31.5) / 32.0
            d = math.sqrt(dx*dx + dy*dy)
            v = max(0.0, 1.0 - d * 0.8)
            noise = ((x * 13 + y * 29) % 7) - 3
            r = int(12 * v + 6 + noise)
            g = int(10 * v + 5 + noise)
            b = int(18 * v + 8 + noise)
            
            # Rounded border frame
            if (x in (2, 61) and 2 <= y <= 61) or (y in (2, 61) and 2 <= x <= 61):
                r, g, b = frame_color
            if (x in (1, 62) and 3 <= y <= 60) or (y in (1, 62) and 3 <= x <= 60):
                r, g, b = int(frame_color[0]*0.4), int(frame_color[1]*0.4), int(frame_color[2]*0.4)
            if x in (0, 63) or y in (0, 63):
                r, g, b = 4, 3, 6

            im.putpixel((x, y), (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))
    return im

# 9x9 sprite from Minecraft Hardcore
HARDCORE_SPRITE = [
    [(0,0,0,0), (26,0,15), (26,0,15), (26,0,15), (0,0,0,0), (26,0,15), (26,0,15), (26,0,15), (0,0,0,0)],
    [(26,0,15), (140,0,40), (230,20,30), (95,0,18), (26,0,15), (140,0,40), (230,20,30), (95,0,18), (26,0,15)],
    [(26,0,15), (255,245,245), (245,35,45), (230,20,30), (45,2,10), (255,245,245), (245,35,45), (140,0,40), (26,0,15)],
    [(15,0,8), (240,25,35), (160,10,25), (40,0,10), (40,0,10), (140,0,40), (40,0,10), (140,0,40), (15,0,8)],
    [(15,0,8), (140,0,40), (95,0,18), (40,0,10), (40,0,10), (40,0,10), (95,0,18), (140,0,40), (15,0,8)],
    [(0,0,0,0), (15,0,8), (95,0,18), (40,0,10), (95,0,18), (95,0,18), (160,10,25), (15,0,8), (0,0,0,0)],
    [(0,0,0,0), (0,0,0,0), (15,0,8), (140,0,40), (95,0,18), (160,10,25), (15,0,8), (0,0,0,0), (0,0,0,0)],
    [(0,0,0,0), (0,0,0,0), (0,0,0,0), (15,0,8), (140,0,40), (15,0,8), (0,0,0,0), (0,0,0,0), (0,0,0,0)],
    [(0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0), (15,0,8), (0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0)]
]

# OPTION 1: Authentic Minecraft Hardcore Heart (Clean, Bold 5x scale)
def create_option_1():
    bg = make_dark_bg(64, frame_color=(100, 20, 35))
    glow = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([8, 8, 56, 56], fill=(220, 20, 45, 55))
    gd.ellipse([14, 14, 50, 50], fill=(255, 35, 60, 75))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=6))
    bg.alpha_composite(glow)

    scale = 5
    ox, oy = (64 - 9 * scale) // 2, (64 - 9 * scale) // 2
    for r in range(9):
        for c in range(9):
            col = HARDCORE_SPRITE[r][c]
            if len(col) == 4 and col[3] == 0:
                continue
            rgba = (col[0], col[1], col[2], 255)
            for dy in range(scale):
                for dx in range(scale):
                    bg.putpixel((ox + c * scale + dx, oy + r * scale + dy), rgba)

    out_path = os.path.join(BASE_DIR, 'icon_option_1.png')
    bg.save(out_path)
    print(f'Created {out_path}')

# OPTION 2: Hardcore Heart + Gold Accent & \"R4\"
def create_option_2():
    bg = make_dark_bg(64, frame_color=(185, 140, 40)) # Gold Frame
    glow = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([12, 6, 52, 46], fill=(230, 25, 45, 65))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=5))
    bg.alpha_composite(glow)

    # 4x scale heart: 36x36 at y=8
    scale = 4
    ox, oy = 14, 8
    for r in range(9):
        for c in range(9):
            col = HARDCORE_SPRITE[r][c]
            if len(col) == 4 and col[3] == 0:
                continue
            rgba = (col[0], col[1], col[2], 255)
            for dy in range(scale):
                for dx in range(scale):
                    bg.putpixel((ox + c * scale + dx, oy + r * scale + dy), rgba)

    # Pixel text 'R4' at bottom centered in Gold (#ffd700) with shadow
    r_mat = [
        '11110',
        '10001',
        '11110',
        '10010',
        '10001'
    ]
    four_mat = [
        '10010',
        '10010',
        '11111',
        '00010',
        '00010'
    ]
    gold = (255, 215, 0, 255)
    shadow = (30, 20, 0, 255)
    
    # R at x=25, y=49
    for y_idx, row in enumerate(r_mat):
        for x_idx, ch in enumerate(row):
            if ch == '1':
                bg.putpixel((25 + x_idx + 1, 49 + y_idx + 1), shadow)
                bg.putpixel((25 + x_idx, 49 + y_idx), gold)
    # 4 at x=33, y=49
    for y_idx, row in enumerate(four_mat):
        for x_idx, ch in enumerate(row):
            if ch == '1':
                bg.putpixel((33 + x_idx + 1, 49 + y_idx + 1), shadow)
                bg.putpixel((33 + x_idx, 49 + y_idx), gold)

    out_path = os.path.join(BASE_DIR, 'icon_option_2.png')
    bg.save(out_path)
    print(f'Created {out_path}')

# OPTION 3: High-Resolution Pixel Art Heart (with subtle fracture/cracks)
def create_option_3():
    bg = make_dark_bg(64, frame_color=(120, 20, 30))
    glow = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([10, 10, 54, 54], fill=(240, 20, 40, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=6))
    bg.alpha_composite(glow)

    # 5x heart with a menacing crack
    scale = 5
    ox, oy = (64 - 9 * scale) // 2, (64 - 9 * scale) // 2
    for r in range(9):
        for c in range(9):
            col = HARDCORE_SPRITE[r][c]
            if len(col) == 4 and col[3] == 0:
                continue
            rgba = (col[0], col[1], col[2], 255)
            for dy in range(scale):
                for dx in range(scale):
                    bg.putpixel((ox + c * scale + dx, oy + r * scale + dy), rgba)

    # Add subtle glowing jagged fracture line across right side
    cracks = [
        (35, 18), (36, 19), (36, 20), (37, 21), (38, 22), (38, 23),
        (37, 24), (37, 25), (38, 26), (39, 27), (39, 28), (40, 29)
    ]
    for cx, cy in cracks:
        bg.putpixel((cx, cy), (15, 0, 5, 255))
        bg.putpixel((cx + 1, cy), (255, 120, 140, 255))

    out_path = os.path.join(BASE_DIR, 'icon_option_3.png')
    bg.save(out_path)
    print(f'Created {out_path}')

if __name__ == '__main__':
    create_option_1()
    create_option_2()
    create_option_3()
