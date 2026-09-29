import os
import zipfile
import json
import hashlib
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDIVIDUAL_DIR = os.path.join(BASE_DIR, 'individual')
OUTPUT_PACK = os.path.join(BASE_DIR, 'Server_Combined_Pack.zip')
CLIENT_PACK = r'E:\ModrinthApp\profiles\Fabric 26.3\resourcepacks\Server_Combined_Pack.zip'
CLIENT_DOWNLOADS = r'E:\ModrinthApp\profiles\Fabric 26.3\downloads\7b9e4ba1-3fda-3d19-a50d-32a39e55fee0'

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

# Problematic files from FreshAnimations or Reimagined base that break CEM / ETF when FA Patch is active
EXCLUDE_EXACT = {
    # 1. Problematic FreshAnimations CEM properties (cause grazing/block rule mismatch on non-grass)
    'assets/minecraft/optifine/cem/cow.properties',
    'assets/minecraft/optifine/cem/cold_cow.properties',
    'assets/minecraft/optifine/cem/warm_cow.properties',
    'assets/minecraft/optifine/cem/pig.properties',
    'assets/minecraft/optifine/cem/cold_pig.properties',
    'assets/minecraft/optifine/cem/warm_pig.properties',
    'assets/minecraft/optifine/cem/cold_chicken.properties',
    'assets/minecraft/optifine/cem/warm_chicken.properties',
    'assets/minecraft/optifine/cem/mooshroom.properties',
    
    # 2. 64x64 FreshAnimations textures that conflict with 512x256 patch textures
    'assets/minecraft/textures/entity/cow/cow_temperate.png',
    'assets/minecraft/textures/entity/cow/cow_cold.png',
    'assets/minecraft/textures/entity/cow/cow_warm.png',
    'assets/minecraft/textures/entity/cow/mooshroom_brown.png',
    'assets/minecraft/textures/entity/cow/mooshroom_red.png',
    'assets/minecraft/textures/entity/pig/pig_temperate.png',
    'assets/minecraft/textures/entity/chicken/chicken_temperate.png',
    
    # 3. 138-byte transparent placeholder from patch that hides cow if referenced
    'assets/minecraft/textures/entity/reimagined_cow/cow.png',
    
    # 4. Old uncolored / unneeded sheep files from RE base
    'assets/minecraft/optifine/random/entity/sheep/sheep2.png',
    'assets/minecraft/optifine/random/entity/sheep/sheep3.png',
    'assets/minecraft/optifine/random/entity/sheep/fix_eye.png',
    'assets/minecraft/optifine/random/entity/reimagined_sheep/sheep_colors.pdn',
}

# Prefixes to remove (outdated 256x128 random textures / properties from Reimagined base)
EXCLUDE_PREFIXES = (
    'assets/minecraft/optifine/random/entity/cow/cow_temperate',
    'assets/minecraft/optifine/random/entity/cow/mooshroom_brown',
    'assets/minecraft/optifine/random/entity/cow/mooshroom_red',
    'assets/minecraft/optifine/random/entity/cow/brown_mooshroom',
    'assets/minecraft/optifine/random/entity/cow/red_mooshroom',
    'assets/minecraft/optifine/random/entity/pig/pig_temperate',
    'assets/minecraft/optifine/random/entity/chicken/chicken_temperate',
    'assets/minecraft/optifine/random/entity/chicken/chicken_warm',
)

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
    print("Building Server Combined Pack (with complete CEM/ETF conflict fixes)...")
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
                
                # Check general ignores
                parts = name.split('/')
                if any(p.startswith(IGNORE_PREFIXES) for p in parts):
                    continue
                if name in IGNORE_EXACT:
                    continue
                if name == 'pack.png':
                    if pack_icon_bytes is None:
                        pack_icon_bytes = zf.read(name)
                    continue

                # Check conflict exclusions
                if name in EXCLUDE_EXACT:
                    continue
                if any(name.startswith(pfx) for pfx in EXCLUDE_PREFIXES):
                    continue
                
                # Store or overwrite based on priority
                file_registry[name] = (pack_path, name)

    print(f"\nTotal indexed unique files: {len(file_registry)}")
    
    # Verify critical patch files
    cow_jem_source = file_registry.get('assets/minecraft/optifine/cem/cow.jem')
    print(f"assets/minecraft/optifine/cem/cow.jem source: {cow_jem_source[0] if cow_jem_source else 'None'}")
    assert cow_jem_source and 'FA-PATCH' in cow_jem_source[0], "Error: cow.jem not provided by FA patch!"

    # Cache open zipfiles to read file contents
    open_zips = {}
    extra_files = {} # arcname -> bytes

    try:
        for pack_name in PACK_ORDER:
            open_zips[os.path.join(INDIVIDUAL_DIR, pack_name)] = zipfile.ZipFile(os.path.join(INDIVIDUAL_DIR, pack_name), 'r')

        patch_zip_path = os.path.join(INDIVIDUAL_DIR, '§aReimagined§8-§aFA-PATCH§0.zip')
        reimagined_zip_path = os.path.join(INDIVIDUAL_DIR, '§aReimagined§0_§8[v1.63.5-fixed]§0.zip')
        patch_zf = open_zips[patch_zip_path]
        re_zf = open_zips[reimagined_zip_path]

        # 1. Alias cow textures and random properties (512x256)
        temperate_cow_bytes = patch_zf.read('assets/minecraft/textures/entity/cow/temperate_cow.png')
        extra_files['assets/minecraft/textures/entity/cow/cow_temperate.png'] = temperate_cow_bytes
        extra_files['assets/minecraft/textures/entity/cow/cow_cold.png'] = patch_zf.read('assets/minecraft/textures/entity/cow/cold_cow.png')
        extra_files['assets/minecraft/textures/entity/cow/cow_warm.png'] = patch_zf.read('assets/minecraft/textures/entity/cow/warm_cow.png')
        extra_files['assets/minecraft/textures/entity/cow/mooshroom_brown.png'] = patch_zf.read('assets/minecraft/textures/entity/cow/brown_mooshroom.png')
        extra_files['assets/minecraft/textures/entity/cow/mooshroom_red.png'] = patch_zf.read('assets/minecraft/textures/entity/cow/red_mooshroom.png')
        extra_files['assets/minecraft/textures/entity/reimagined_cow/cow.png'] = temperate_cow_bytes # Avoid transparent dummy!

        # Alias cow_temperate*.png to temperate_cow*.png (all 512x256)
        for i in range(2, 11):
            src_name = f'assets/minecraft/optifine/random/entity/cow/temperate_cow{i}.png'
            dst_name = f'assets/minecraft/optifine/random/entity/cow/cow_temperate{i}.png'
            if src_name in patch_zf.namelist():
                extra_files[dst_name] = patch_zf.read(src_name)

        cow_temperate_prop = "skins.2=2 3 4 5 6 7 8 9 10\nweights.2= 1 1 1 1 1 1 1 1 1\n"
        extra_files['assets/minecraft/optifine/random/entity/cow/cow_temperate.properties'] = cow_temperate_prop.encode('utf-8')

        # 2. Alias pig textures and properties
        if 'assets/minecraft/textures/entity/pig/temperate_pig.png' in re_zf.namelist():
            temperate_pig_bytes = re_zf.read('assets/minecraft/textures/entity/pig/temperate_pig.png')
            extra_files['assets/minecraft/textures/entity/pig/pig_temperate.png'] = temperate_pig_bytes

        for suffix in ['2', '10', '11', '12', '780']:
            src_name = f'assets/minecraft/optifine/random/entity/pig/temperate_pig{suffix}.png'
            dst_name = f'assets/minecraft/optifine/random/entity/pig/pig_temperate{suffix}.png'
            if src_name in patch_zf.namelist():
                extra_files[dst_name] = patch_zf.read(src_name)
        
        extra_files['assets/minecraft/optifine/random/entity/pig/pig_temperate.properties'] = patch_zf.read('assets/minecraft/optifine/random/entity/pig/temperate_pig.properties')

        # 3. Alias chicken textures and properties
        temperate_chicken_bytes = patch_zf.read('assets/minecraft/textures/entity/chicken/temperate_chicken.png')
        extra_files['assets/minecraft/textures/entity/chicken/chicken_temperate.png'] = temperate_chicken_bytes
        for suffix in ['3', '4', '11', '12', '16', '20', '101', '404']:
            src_name = f'assets/minecraft/optifine/random/entity/chicken/temperate_chicken{suffix}.png'
            dst_name = f'assets/minecraft/optifine/random/entity/chicken/chicken_temperate{suffix}.png'
            if src_name in patch_zf.namelist():
                extra_files[dst_name] = patch_zf.read(src_name)

        extra_files['assets/minecraft/optifine/random/entity/chicken/chicken_temperate.properties'] = patch_zf.read('assets/minecraft/optifine/random/entity/chicken/temperate_chicken.properties')

        # 4. Map sheep properties and textures from reimagined_sheep to sheep
        sheep_props = patch_zf.read('assets/minecraft/optifine/random/entity/reimagined_sheep/sheep.properties')
        extra_files['assets/minecraft/optifine/random/entity/sheep/sheep.properties'] = sheep_props
        
        for name in patch_zf.namelist():
            if name.startswith('assets/minecraft/optifine/random/entity/reimagined_sheep/') and name.endswith('.png'):
                filename = os.path.basename(name)
                extra_files[f'assets/minecraft/optifine/random/entity/sheep/{filename}'] = patch_zf.read(name)

        # Fix sheep_wool_undercoat.jem animation model reference (typo in patch: undercoat_animations.jpm -> sheep_animations.jpm)
        undercoat_jem_bytes = patch_zf.read('assets/minecraft/optifine/cem/sheep_wool_undercoat.jem')
        undercoat_jem_fixed = undercoat_jem_bytes.decode('utf-8').replace('sheep_wool_undercoat_animations.jpm', 'sheep_animations.jpm')
        extra_files['assets/minecraft/optifine/cem/sheep_wool_undercoat.jem'] = undercoat_jem_fixed.encode('utf-8')

        print(f"Generated {len(extra_files)} compatibility alias files.")

        # Write output zip
        temp_output = OUTPUT_PACK + '.tmp'
        if os.path.exists(temp_output):
            os.remove(temp_output)

        print(f"Writing to {OUTPUT_PACK}...")
        with zipfile.ZipFile(temp_output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out_zf:
            # 1. Write pack.mcmeta
            out_zf.writestr('pack.mcmeta', json.dumps(COMBINED_MCMETA, indent=2))
            
            # 2. Write pack.png
            if pack_icon_bytes:
                out_zf.writestr('pack.png', pack_icon_bytes)

            # 3. Write all mapped files
            count = 0
            files_to_write = {arcname: val for arcname, val in file_registry.items() if arcname not in extra_files}
            total = len(files_to_write) + len(extra_files)
            for arcname, (src_zip_path, src_entry) in files_to_write.items():
                data = open_zips[src_zip_path].read(src_entry)
                out_zf.writestr(arcname, data)
                count += 1
                if count % 2000 == 0:
                    print(f"  Packaged {count}/{total} files ({count*100//total}%)...")

            # 4. Write extra alias files
            for arcname, data in extra_files.items():
                out_zf.writestr(arcname, data)
                count += 1

            print(f"  Finished packaging {count}/{total} files (100%).")

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

    # Copy to client profile resourcepacks if available
    if os.path.exists(os.path.dirname(CLIENT_PACK)):
        shutil.copy2(OUTPUT_PACK, CLIENT_PACK)
        print(f"Copied to client: {CLIENT_PACK}")
    else:
        print(f"Client profile directory not accessible (drive disconnected), skipped local profile copy.")

    # Also update client cache directly!
    if os.path.exists(CLIENT_DOWNLOADS):
        cached_file_path = os.path.join(CLIENT_DOWNLOADS, pack_hash)
        shutil.copy2(OUTPUT_PACK, cached_file_path)
        print(f"Updated client downloads cache: {cached_file_path}")

        # Update log.json in downloads
        log_json_path = os.path.join(os.path.dirname(CLIENT_DOWNLOADS), 'log.json')
        if os.path.exists(log_json_path):
            with open(log_json_path, 'r', encoding='utf-8') as f:
                logs = f.readlines()
            new_log_entry = {
                "id": "7b9e4ba1-3fda-3d19-a50d-32a39e55fee0",
                "url": "https://raw.githubusercontent.com/LysLama/mc-resource-packs/main/Server_Combined_Pack.zip",
                "time": "2026-09-27T07:45:00.000000000Z",
                "hash": pack_hash,
                "file": {
                    "name": f"7b9e4ba1-3fda-3d19-a50d-32a39e55fee0\\{pack_hash}",
                    "size": file_size
                }
            }
            logs.append(json.dumps(new_log_entry) + '\n')
            with open(log_json_path, 'w', encoding='utf-8') as f:
                f.writelines(logs)
            print("Updated client log.json cache record.")

    return pack_hash, file_size

if __name__ == '__main__':
    main()
