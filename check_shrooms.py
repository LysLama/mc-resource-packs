import zipfile
import json
from PIL import Image
import io

with zipfile.ZipFile('individual/§aReimagined§8-§aFA-PATCH§0.zip') as z:
    d = json.loads(z.read('assets/minecraft/optifine/cem/cow.jem'))
    img = Image.open(io.BytesIO(z.read('assets/minecraft/textures/entity/cow/cow.png'))).convert('RGBA')

    # Find mushroom submodels
    body = [m for m in d['models'] if m.get('part') == 'body'][0]
    shrooms = []
    def find_shrooms(sm):
        for s in sm:
            if 'shroom' in s.get('id', '') or 'mushroom' in s.get('id', ''):
                shrooms.append(s)
            find_shrooms(s.get('submodels', []))
    find_shrooms(body.get('submodels', []))
    print(f"Found {len(shrooms)} shroom submodels in cow.jem:")
    for s in shrooms:
        boxes = s.get('boxes', [])
        print(f"  {s.get('id')}: {len(boxes)} boxes")
        for b in boxes:
            print("    box:", b)
