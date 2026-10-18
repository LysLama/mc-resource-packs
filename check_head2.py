import zipfile
import json

with zipfile.ZipFile('individual/§aReimagined§8-§aFA-PATCH§0.zip') as z:
    d = json.loads(z.read('assets/minecraft/optifine/cem/cow.jem'))
    body = [m for m in d['models'] if m.get('part') == 'body'][0]
    head2 = [s for s in body.get('submodels', []) if s.get('id') == 'head2'][0]
    print("Head2 boxes:")
    for b in head2.get('boxes', []):
        print(" ", b)
    print("\nHead2 children:")
    for c in head2.get('submodels', []):
        print(f"  {c.get('id')}: {len(c.get('boxes', []))} boxes, submodels: {[s.get('id') for s in c.get('submodels', [])]}")
