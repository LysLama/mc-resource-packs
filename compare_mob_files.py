import zipfile

with zipfile.ZipFile('individual/§aReimagined§0_§8[v1.63.5-fixed]§0.zip') as z_re, \
     zipfile.ZipFile('individual/§aReimagined§8-§aFA-PATCH§0.zip') as z_pa:
    
    re_files = set(z_re.namelist())
    pa_files = set(z_pa.namelist())

    for mob in ['cow', 'pig', 'chicken', 'sheep']:
        print(f"\n=== MOB: {mob} ===")
        re_mob = sorted([f for f in re_files if mob in f and ('random' in f or 'cem' in f or 'textures/entity' in f)])
        pa_mob = sorted([f for f in pa_files if mob in f and ('random' in f or 'cem' in f or 'textures/entity' in f)])
        print(f"Reimagined files ({len(re_mob)}):")
        for f in re_mob[:10]:
            print("  RE:", f)
        print(f"Patch files ({len(pa_mob)}):")
        for f in pa_mob[:10]:
            print("  PA:", f)
