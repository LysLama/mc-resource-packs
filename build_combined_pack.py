import os
import zipfile
import json
import hashlib
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDIVIDUAL_DIR = os.path.join(BASE_DIR, 'individual')
OUTPUT_PACK = os.path.join(BASE_DIR, 'Server_Combined_Pack.zip')
CLIENT_PACK = r'E:\ModrinthApp\profiles\Fabric 26.3\resourcepacks\Server_Combined_Pack.zip'

PACK_ORDER = [
    # 1. Base Layer: Minecraft Reimagined (textures, sounds, models)
    '§aReimagined§0_§8[v1.63.5-fixed]§0.zip',
    # 2. Fusion Enhancement Packs
    'Fusion Connected Blocks v1.1.0 for Minecraft 1.20-26.2.zip',
    'Fusion Connected Glass v1.0.1 for Minecraft 1.20-1.21.8.zip',
    'Fusion 3D Items v1.0.1 for Minecraft 1.20-1.21.8.zip',
    'Fusion Block Transitions v1.0.3 for Minecraft 1.20-1.21.8.zip',
    'Fusion Emissive Ores v1.0.2 for Minecraft 1.20-1.21.8.zip',
    'Fusion Stacking Items v1.0.1 for Minecraft 1.20-1.21.8.zip',
    # 3. Refined Tools (3D tool models)
    'Refined Tools 3.0.zip',
    # 4. Fresh Animations (Base animation logic and rigs)
    'FreshAnimations_v1.10.5.zip',
    # 5. Top Priority: Reimagined Fresh Animations Compatibility Patch
    '§aReimagined§8-§aFA-PATCH§0.zip'
]

MCMETA_OVERLAYS = [
    {"directory": "26.2", "formats": [88, 999], "min_format": 88, "max_format": 999},
    {"directory": "26.1", "formats": [84, 87], "min_format": 84, "max_format": 87},
    {"directory": "1.21.11", "formats": [75, 83], "min_format": 75, "max_format": 83},
    {"directory": "1.21.6", "formats": [60, 74], "min_format": 60, "max_format": 74},
    {"directory": "1.21.5", "formats": [54, 59], "min_format": 54, "max_format": 59},
    {"directory": "1.21.4", "formats": [46, 53], "min_format": 46, "max_format": 53},
    {"directory": "1.21.2", "formats": [36, 45], "min_format": 36, "max_format": 45},
    {"directory": "1.20.5", "formats": [26, 34], "min_format": 26, "max_format": 34},
    {"directory": "1.20.2", "formats": [16, 24], "min_format": 16, "max_format": 24},
    {"directory": "polytone_villager", "formats": [16, 59], "min_format": 16, "max_format": 59},
    {"directory": "polytone_grass", "formats": [16, 999], "min_format": 16, "max_format": 999},
    {"directory": "21-1", "formats": {"min_inclusive": 34, "max_inclusive": 34}, "min_format": 34, "max_format": 34},
    {"directory": "21-4-5", "formats": {"min_inclusive": 43, "max_inclusive": 55}, "min_format": 43, "max_format": 55},
    {"directory": "21-9-11", "formats": {"min_inclusive": 65, "max_inclusive": 75}, "min_format": 65, "max_format": 75},
    {"directory": "21-6-8", "formats": {"min_inclusive": 56, "max_inclusive": 65}, "min_format": 56, "max_format": 65},
    {"directory": "21-5-FA", "formats": {"min_inclusive": 55, "max_inclusive": 99}, "min_format": 55, "max_format": 99},
    {"directory": "21-5-hmi", "formats": {"min_inclusive": 55, "max_inclusive": 64}, "min_format": 55, "max_format": 64},
    {"directory": "26-1", "formats": {"min_inclusive": 82, "max_inclusive": 99}, "min_format": 82, "max_format": 99},
    {"formats": [20, 1000], "min_format": 20, "max_format": 1000, "directory": "pack_format_20"},
    {"formats": [88, 1000], "min_format": 88, "max_format": 1000, "directory": "pack_format_88"},
    {"formats": [24, 1000], "min_format": 24, "max_format": 1000, "directory": "pack_format_24"},
    {"formats": [51, 1000], "min_format": 51, "max_format": 1000, "directory": "pack_format_51"},
    {"formats": [67, 1000], "min_format": 67, "max_format": 1000, "directory": "pack_format_67"},
    {"formats": [40, 1000], "min_format": 40, "max_format": 1000, "directory": "pack_format_40"}
]

COMBINED_MCMETA = {
    "pack": {
        "description": "§6§lServer Combined Pack§r\n§7Reimagined + Refined Tools + Fresh Animations (Patched) + Fusion",
        "pack_format": 34,
        "supported_formats": [15, 999],
        "min_format": 15,
        "max_format": 999
    },
    "fusion": {
        "min_version": "1.2.12"
    },
    "overlays": {
        "entries": MCMETA_OVERLAYS
    }
}

IGNORE_PREFIXES = ('.', '__MACOSX')
IGNORE_EXACT = {'pack.mcmeta', 'credits.txt', 'Discord Server.txt', 'desktop.ini', 'Thumbs.db'}

def main():
    print("Building Server Combined Pack...")
    file_registry = {} # arcname -> (pack_filename, zip_name)
    pack_icon_bytes = None

    for pack_name in PACK_ORDER:
        pack_path = os.path.join(INDIVIDUAL_DIR, pack_name)
        if not os.path.exists(pack_path):
            raise FileNotFoundError(f"Missing pack: {pack_path}")
        
        print(f"Indexing {pack_name}...")
        with zipfile.ZipFile(pack_path, 'r') as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                name = info.filename
                
                # Check ignores
                parts = name.split('/')
                if any(p.startswith(IGNORE_PREFIXES) for p in parts):
                    continue
                if name in IGNORE_EXACT:
                    continue
                if name == 'pack.png':
                    if pack_icon_bytes is None:
                        pack_icon_bytes = zf.read(name)
                    continue
                
                # Store or overwrite based on priority
                file_registry[name] = (pack_path, name)

    print(f"Total unique files to package: {len(file_registry)}")
    
    # Verify critical patch files
    cow_jem_source = file_registry.get('assets/minecraft/optifine/cem/cow.jem')
    print(f"assets/minecraft/optifine/cem/cow.jem source: {cow_jem_source[0] if cow_jem_source else 'None'}")
    assert cow_jem_source and 'FA-PATCH' in cow_jem_source[0], "Error: cow.jem not provided by FA patch!"

    # Write output zip
    temp_output = OUTPUT_PACK + '.tmp'
    if os.path.exists(temp_output):
        os.remove(temp_output)

    print(f"Writing to {OUTPUT_PACK}...")
    # Cache open zipfiles to avoid reopening thousands of times
    open_zips = {}
    try:
        for pack_name in PACK_ORDER:
            open_zips[os.path.join(INDIVIDUAL_DIR, pack_name)] = zipfile.ZipFile(os.path.join(INDIVIDUAL_DIR, pack_name), 'r')

        with zipfile.ZipFile(temp_output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out_zf:
            # 1. Write pack.mcmeta
            out_zf.writestr('pack.mcmeta', json.dumps(COMBINED_MCMETA, indent=2))
            
            # 2. Write pack.png
            if pack_icon_bytes:
                out_zf.writestr('pack.png', pack_icon_bytes)

            # 3. Write all mapped files
            count = 0
            total = len(file_registry)
            for arcname, (src_zip_path, src_entry) in file_registry.items():
                data = open_zips[src_zip_path].read(src_entry)
                out_zf.writestr(arcname, data)
                count += 1
                if count % 2000 == 0 or count == total:
                    print(f"  Packaged {count}/{total} files ({count*100//total}%)...")

    finally:
        for z in open_zips.values():
            z.close()

    if os.path.exists(OUTPUT_PACK):
        os.remove(OUTPUT_PACK)
    os.rename(temp_output, OUTPUT_PACK)

    file_size = os.path.getsize(OUTPUT_PACK)
    sha1 = hashlib.sha1()
    with open(OUTPUT_PACK, 'rb') as f:
        while chunk := f.read(65536):
            sha1.update(chunk)
    pack_hash = sha1.hexdigest()

    print(f"\nSuccessfully generated {OUTPUT_PACK}!")
    print(f"File Size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    print(f"SHA-1 Hash: {pack_hash}")

    # Copy to client profile
    shutil.copy2(OUTPUT_PACK, CLIENT_PACK)
    print(f"Copied to client: {CLIENT_PACK}")

    return pack_hash, file_size

if __name__ == '__main__':
    main()
