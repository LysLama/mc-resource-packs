import zipfile
from PIL import Image
import io

with zipfile.ZipFile('individual/§aReimagined§8-§aFA-PATCH§0.zip') as z:
    for name in ['assets/minecraft/textures/entity/cow/temperate_cow.png', 
                 'assets/minecraft/optifine/random/entity/cow/temperate_cow2.png',
                 'assets/minecraft/textures/entity/cow/cow.png']:
        img = Image.open(io.BytesIO(z.read(name))).convert('RGBA')
        print(f"=== {name} ({img.size}) ===")
        # Body: 464, 8
        crop_body = img.crop((464, 8, 508, 36))
        a_body = [a for r,g,b,a in crop_body.getdata()]
        print(f"  Body (464,8): opaque={a_body.count(255)} / {len(a_body)}")
        # Head: 23, 113
        crop_head = img.crop((23, 113, 51, 127))
        a_head = [a for r,g,b,a in crop_head.getdata()]
        print(f"  Head (23,113): opaque={a_head.count(255)} / {len(a_head)}")
        # Leg: 0, 112
        crop_leg = img.crop((0, 112, 16, 128))
        a_leg = [a for r,g,b,a in crop_leg.getdata()]
        print(f"  Leg (0,112): opaque={a_leg.count(255)} / {len(a_leg)}")
