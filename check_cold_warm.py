import zipfile

with zipfile.ZipFile('individual/§aReimagined§0_§8[v1.63.5-fixed]§0.zip') as z_re, \
     zipfile.ZipFile('individual/§aReimagined§8-§aFA-PATCH§0.zip') as z_pa:
    
    for prefix in ['cold', 'warm']:
        print(f"\n--- {prefix} cow ---")
        for f in sorted(z_re.namelist()):
            if prefix in f and 'cow' in f:
                print("  RE:", f)
        for f in sorted(z_pa.namelist()):
            if prefix in f and 'cow' in f:
                print("  PA:", f)
