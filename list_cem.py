import zipfile

with zipfile.ZipFile('Server_Combined_Pack.zip') as z:
    cem_files = [f for f in z.namelist() if f.startswith('assets/minecraft/optifine/cem/')]
    print(f"Total files in assets/minecraft/optifine/cem/: {len(cem_files)}")
    for f in sorted(cem_files):
        print(" ", f)
