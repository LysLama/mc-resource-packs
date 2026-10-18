import zipfile
import json

def load_cow(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        if 'assets/minecraft/optifine/cem/cow.jem' in z.namelist():
            return json.loads(z.read('assets/minecraft/optifine/cem/cow.jem').decode('utf-8'))
    return None

c_re = load_cow('individual/§aReimagined§0_§8[v1.63.5-fixed]§0.zip')
c_fa = load_cow('individual/FreshAnimations_v1.10.5.zip')
c_pa = load_cow('individual/§aReimagined§8-§aFA-PATCH§0.zip')

print("1. Reimagined models:")
for m in c_re['models']:
    print(f"  part: {m.get('part')}, id: {m.get('id')}, boxes: {len(m.get('boxes', []))}, submodels: {len(m.get('submodels', []))}")

print("\n2. Fresh Animations models:")
for m in c_fa['models']:
    print(f"  part: {m.get('part')}, id: {m.get('id')}, model: {m.get('model')}, boxes: {len(m.get('boxes', []))}, submodels: {len(m.get('submodels', []))}")

print("\n3. Patch models:")
for m in c_pa['models']:
    print(f"  part: {m.get('part')}, id: {m.get('id')}, model: {m.get('model')}, boxes: {len(m.get('boxes', []))}, submodels: {len(m.get('submodels', []))}")
