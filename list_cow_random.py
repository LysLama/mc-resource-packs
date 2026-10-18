import zipfile

with zipfile.ZipFile('individual/§aReimagined§0_§8[v1.63.5-fixed]§0.zip') as z_re, \
     zipfile.ZipFile('individual/§aReimagined§8-§aFA-PATCH§0.zip') as z_pa:
    
    print("ALL cow files in Reimagined base:")
    for f in sorted(z_re.namelist()):
        if 'optifine/random/entity/cow' in f:
            print("  RE:", f)

    print("\nALL cow files in Patch:")
    for f in sorted(z_pa.namelist()):
        if 'optifine/random/entity/cow' in f:
            print("  PA:", f)
