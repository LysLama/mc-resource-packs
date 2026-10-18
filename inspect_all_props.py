import zipfile

with zipfile.ZipFile('individual/§aReimagined§8-§aFA-PATCH§0.zip') as z_pa, \
     zipfile.ZipFile('individual/§aReimagined§0_§8[v1.63.5-fixed]§0.zip') as z_re, \
     zipfile.ZipFile('individual/FreshAnimations_v1.10.5.zip') as z_fa:

    # Check CEM properties across packs
    for name, z in [('FA', z_fa), ('RE', z_re), ('PA', z_pa)]:
        cem_props = [f for f in z.namelist() if f.startswith('assets/minecraft/optifine/cem/') and f.endswith('.properties')]
        print(f"\n{name} CEM properties ({len(cem_props)}):")
        for p in cem_props:
            print(" ", p)

    # Check random entity properties across packs
    for name, z in [('FA', z_fa), ('RE', z_re), ('PA', z_pa)]:
        rand_props = [f for f in z.namelist() if f.startswith('assets/minecraft/optifine/random/entity/') and f.endswith('.properties')]
        print(f"\n{name} Random properties ({len(rand_props)}):")
        for p in rand_props:
            print(" ", p)
