import zipfile
import json

with zipfile.ZipFile('individual/FreshAnimations_v1.10.5.zip') as z:
    moosh_data = json.loads(z.read('assets/minecraft/optifine/cem/mooshroom_animations.jpm'))
    print("Mooshroom animations keys:")
    for a in moosh_data.get('animations', []):
        for k, v in a.items():
            if 'visible' in k or 'scale' in k or 'render' in k or 'head' in k or 'body' in k:
                print(f"  {k} = {v[:80]}")
