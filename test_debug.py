import zipfile
import json

with zipfile.ZipFile('individual/FreshAnimations_v1.10.5.zip') as z:
    moosh = z.read('assets/minecraft/optifine/cem/mooshroom_animations.jpm').decode('utf-8')
    leg_lines = [line.strip() for line in moosh.splitlines() if any(line.strip().startswith(f'"leg{i}') for i in range(1, 5))]
    print("Leg animations count:", len(leg_lines))
    for l in leg_lines[:6]:
        print(" ", l[:80])
