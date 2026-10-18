import zipfile

with zipfile.ZipFile('individual/§aReimagined§8-§aFA-PATCH§0.zip') as zp:
    print("Patch random cow files:")
    for f in sorted(zp.namelist()):
        if 'random/entity/cow' in f:
            print(" ", f)

    print("\nPatch texture cow files:")
    for f in sorted(zp.namelist()):
        if 'textures/entity/cow' in f:
            print(" ", f)
