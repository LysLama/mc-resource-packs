import os
import zipfile
import json
import hashlib
import shutil
import io
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDIVIDUAL_DIR = os.path.join(BASE_DIR, 'individual')
OUTPUT_PACK = os.path.join(BASE_DIR, 'Server_Combined_Pack.zip')
CLIENT_PACK = r'D:\ModrinthApp\profiles\Yoel Lezly\resourcepacks\Server_Combined_Pack.zip'
CLIENT_DOWNLOADS = r'D:\ModrinthApp\profiles\Yoel Lezly\downloads\7b9e4ba1-3fda-3d19-a50d-32a39e55fee0'

PACK_ORDER = [
    # 1. Base Layer: Minecraft Reimagined (textures, sounds, models)
    '§aReimagined§0_§8[v1.63.7]§0.zip',
    # 2. Fusion Enhancement Packs
    'Fusion Connected Blocks v1.1.0 for Minecraft 1.20-26.2.zip',
    'Fusion Connected Glass v1.0.1 for Minecraft 1.20-1.21.8.zip',
    'Fusion 3D Items v1.0.1 for Minecraft 1.20-1.21.8.zip',
    'Fusion Block Transitions v1.0.3 for Minecraft 1.20-1.21.8.zip',
    'Fusion Emissive Ores v1.0.2 for Minecraft 1.20-1.21.8.zip',
    # 3. Refined Tools (3D tool models)
    'Refined Tools 3.0.zip',
    # 4. Fresh Animations (Base animation logic and rigs)
    'FreshAnimations_v1.11_26.1+.zip',
    # 5. Top Priority: Reimagined Fresh Animations Compatibility Patch
    '§aReimagined§8-§aFA-PATCH§0.zip',
    # 6. Lively Turtle Helmet (Top Priority - Animated Turtle & Model Override)
    'Lively Turtle Helmet.zip'
]

# Problematic files from FreshAnimations or Reimagined base that break CEM / ETF when FA Patch is active
EXCLUDE_EXACT = {
    # 1. Problematic FreshAnimations CEM properties (cause grazing/block rule mismatch on non-grass)
    'assets/minecraft/optifine/cem/cow.properties',
    'assets/minecraft/optifine/cem/cold_cow.properties',
    'assets/minecraft/optifine/cem/warm_cow.properties',
    'assets/minecraft/optifine/cem/cow_baby.properties',
    'assets/minecraft/optifine/cem/cold_cow_baby.properties',
    'assets/minecraft/optifine/cem/warm_cow_baby.properties',
    'assets/minecraft/optifine/cem/mooshroom.properties',
    'assets/minecraft/optifine/cem/mooshroom_baby.properties',
    'assets/minecraft/optifine/cem/pig.properties',
    'assets/minecraft/optifine/cem/cold_pig.properties',
    'assets/minecraft/optifine/cem/warm_pig.properties',
    'assets/minecraft/optifine/cem/pig_baby.properties',
    'assets/minecraft/optifine/cem/cold_pig_baby.properties',
    'assets/minecraft/optifine/cem/warm_pig_baby.properties',
    'assets/minecraft/optifine/cem/chicken.properties',
    'assets/minecraft/optifine/cem/cold_chicken.properties',
    'assets/minecraft/optifine/cem/warm_chicken.properties',
    'assets/minecraft/optifine/cem/chicken_baby.properties',
    'assets/minecraft/optifine/cem/cold_chicken_baby.properties',
    'assets/minecraft/optifine/cem/warm_chicken_baby.properties',
    'assets/minecraft/optifine/cem/goat_baby.properties',
    
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
    {"directory": "26.3", "formats": [97, 999], "min_format": 97, "max_format": 999},
    {"directory": "26.2", "formats": [88, 96], "min_format": 88, "max_format": 96},
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
        reimagined_zip_path = os.path.join(INDIVIDUAL_DIR, '§aReimagined§0_§8[v1.63.7]§0.zip')
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

        # 4. Map sheep properties and textures from reimagined_sheep to sheep (and repair missing pupil / eye UV)
        sheep_props = patch_zf.read('assets/minecraft/optifine/random/entity/reimagined_sheep/sheep.properties')
        extra_files['assets/minecraft/optifine/random/entity/sheep/sheep.properties'] = sheep_props
        
        for name in patch_zf.namelist():
            if (name.startswith('assets/minecraft/optifine/random/entity/reimagined_sheep/') or 
                name.startswith('assets/minecraft/optifine/random/entity/sheep/')) and name.endswith('.png'):
                filename = os.path.basename(name)
                raw_png = patch_zf.read(name)

                # Repair eye UV / pixel alignment for Fresh Animations CEM
                img = Image.open(io.BytesIO(raw_png)).convert('RGBA')
                # Fix right eye (viewer's left): pupil at (1, 6), white sclera at (1, 7) and (2, 7)
                img.putpixel((1, 6), (8, 8, 8, 255))
                img.putpixel((1, 7), (255, 255, 255, 255))
                img.putpixel((2, 7), (255, 255, 255, 255))
                # Fix left eye (viewer's right): pupil at (6, 6), white sclera at (5, 7) and (6, 7)
                img.putpixel((6, 6), (8, 8, 8, 255))
                img.putpixel((5, 7), (255, 255, 255, 255))
                img.putpixel((6, 7), (255, 255, 255, 255))
                # Clear misplaced pixel at (4, 6) if it was erroneously placed there
                if img.getpixel((4, 6)) == (8, 8, 8, 255):
                    img.putpixel((4, 6), (0, 0, 0, 0))

                buf = io.BytesIO()
                img.save(buf, format='PNG')
                fixed_png_bytes = buf.getvalue()

                extra_files[f'assets/minecraft/optifine/random/entity/sheep/{filename}'] = fixed_png_bytes
                extra_files[f'assets/minecraft/optifine/random/entity/reimagined_sheep/{filename}'] = fixed_png_bytes

        # Fix sheep_wool_undercoat.jem animation model reference (typo in patch: undercoat_animations.jpm -> sheep_animations.jpm)
        undercoat_jem_bytes = patch_zf.read('assets/minecraft/optifine/cem/sheep_wool_undercoat.jem')
        undercoat_jem_fixed = undercoat_jem_bytes.decode('utf-8').replace('sheep_wool_undercoat_animations.jpm', 'sheep_animations.jpm')
        extra_files['assets/minecraft/optifine/cem/sheep_wool_undercoat.jem'] = undercoat_jem_fixed.encode('utf-8')

        # 5. Restore mooshroom_animations.jpm (removed in FA v1.11, but required by FA-PATCH cow.jem & mooshroom.jem)
        fa_zip_path = os.path.join(INDIVIDUAL_DIR, 'FreshAnimations_v1.11_26.1+.zip')
        fa_zf = open_zips[fa_zip_path]
        cow_jpm = json.loads(fa_zf.read('assets/minecraft/optifine/cem/cow_animations.jpm').decode('utf-8'))
        cow_jpm['animations'][0] = {
            "varb.21_2_plus": "true",
            "varb.baby_model": "false",
            "varb.is_mooshroom": "true",
            **cow_jpm['animations'][0]
        }
        extra_files['assets/minecraft/optifine/cem/mooshroom_animations.jpm'] = json.dumps(cow_jpm).encode('utf-8')

        # 6. Preserve FA v1.11's native 26.1+ baby CEM models over outdated 1.21.5 baby models in FA-PATCH
        extra_files['assets/minecraft/optifine/cem/chicken_baby.jem'] = fa_zf.read('assets/minecraft/optifine/cem/chicken_baby.jem')
        extra_files['assets/minecraft/optifine/cem/mooshroom_baby.jem'] = fa_zf.read('assets/minecraft/optifine/cem/mooshroom_baby.jem')

        # 7. Merge assets/minecraft/font/default.json from Reimagined and FA-PATCH
        # (Prevent FA-PATCH's single-provider default.json from overwriting Reimagined's 22 custom GUI bitmap fonts & space shifts!)
        re_font = json.loads(re_zf.read('assets/minecraft/font/default.json').decode('utf-8'))
        patch_font = json.loads(patch_zf.read('assets/minecraft/font/default.json').decode('utf-8'))
        merged_font = {
            "providers": re_font.get("providers", []) + patch_font.get("providers", [])
        }
        extra_files['assets/minecraft/font/default.json'] = json.dumps(merged_font, indent=2).encode('utf-8')

        # 8. Fix Villager Trading GUI shopkeeper sprite sheets on 26.2+ / 26.3
        # (In 26.2+, Reimagined disabled core/text.vsh, causing \uE026..\uE031 to draw all 22/88 animation frames as a giant grid.
        #  Cropping each 256x256 sheet to Frame 0 while preserving the 1/255 alpha width marker at (0,0) and (255,0) renders the shopkeeper cleanly!)
        shopkeeper_dirs = [
            'assets/minecraft/textures/gui/sprites/shopkeeper',
            'assets/minecraft/textures/gui/sprites/container/shopkeeper',
            '26.2/assets/minecraft/textures/gui/sprites/shopkeeper',
        ]
        for sdir in shopkeeper_dirs:
            for idx in range(1, 6):
                spath = f'{sdir}/villager_idle{idx}.png'
                if spath in re_zf.namelist():
                    src_im = Image.open(io.BytesIO(re_zf.read(spath))).convert('RGBA')
                    clean_im = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
                    clean_im.paste(src_im.crop((0, 0, 128, 22)), (0, 0))
                    clean_im.putpixel((0, 0), (0, 0, 0, 1))
                    clean_im.putpixel((255, 0), (0, 0, 0, 1))
                    buf = io.BytesIO()
                    clean_im.save(buf, format='PNG')
                    extra_files[spath] = buf.getvalue()
            epath = f'{sdir}/villager_eyes1.png'
            if epath in re_zf.namelist():
                src_im = Image.open(io.BytesIO(re_zf.read(epath))).convert('RGBA')
                clean_im = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
                clean_im.paste(src_im.crop((0, 0, 32, 16)), (0, 0))
                clean_im.putpixel((0, 0), (0, 0, 0, 1))
                clean_im.putpixel((255, 0), (0, 0, 0, 1))
                buf = io.BytesIO()
                clean_im.save(buf, format='PNG')
                extra_files[epath] = buf.getvalue()

        # 9. Book CEM sanitization (Lectern & Enchanting Table):
        #    In vanilla 26.3, BookModel uses RenderTypes::entitySolid which lacks alpha cutout/blending.
        #    Upstream Reimagined defined a flat 2D 'floor' quad (36x36 on lectern, 44x44 on enchanting table)
        #    for a magic floor circle. In 26.3 solid rendering, alpha=0 pixels around the circle render as
        #    an opaque black square (or bluish-gray fog square if forced to translucent).
        #    In fact, upstream Reimagined already blanked out this floor circle in 26.3 overlay texture,
        #    leaving the 'floor' quad as an orphaned artifact.
        #    Here we strip the 'floor' quad and 'scale_circle' from all book .jem models, while preserving
        #    the 3D book model, page animations, and floating rune particles ('symbol1'..'symbol8').
        #    For Lectern (which lacks 'time' in its render state), particle animations are converted from
        #    'time' to 'frame_counter' to eliminate the 20Hz reset jitter.
        #    See knowledge_base/resourcepacks/reimagined/lectern-black-square-fix.md
        def _clean_submodels(submodels):
            cleaned = []
            for s in submodels:
                if s.get("id") in ("floor", "scale_circle"):
                    continue
                if "submodels" in s:
                    s["submodels"] = _clean_submodels(s["submodels"])
                cleaned.append(s)
            return cleaned

        book_jems = [
            "assets/minecraft/optifine/cem/lectern_book.jem",
            "assets/minecraft/optifine/cem/lectern_book2.jem",
            "assets/minecraft/optifine/cem/enchanting_book.jem",
            "assets/minecraft/optifine/cem/enchanting_book2.jem",
            "assets/minecraft/optifine/cem/enchanting_book2_noanim.jem"
        ]

        for jem_name in book_jems:
            if jem_name in re_zf.namelist():
                jem = json.loads(re_zf.read(jem_name).decode("utf-8-sig"))
                is_lectern = "lectern" in jem_name
                for part in jem.get("models", []):
                    if part.get("part") == "book_spine":
                        if "submodels" in part:
                            part["submodels"] = _clean_submodels(part["submodels"])
                        if "animations" in part:
                            new_anims = []
                            for anim in part["animations"]:
                                new_anim = {}
                                for k, expr in anim.items():
                                    if "floor" in k or "circle" in k:
                                        continue
                                    if is_lectern and isinstance(expr, str):
                                        expr = expr.replace("time / 16", "frame_counter / 48")
                                        expr = expr.replace("time * 0.3", "frame_counter * 0.1")
                                        expr = expr.replace("time * 0.1", "frame_counter * 0.0333")
                                        expr = expr.replace("time * 0.25", "frame_counter * 0.0833")
                                        expr = expr.replace("time * 0.2", "frame_counter * 0.0666")
                                        expr = expr.replace("time * 0.05", "frame_counter * 0.0166")
                                        expr = expr.replace("time", "(frame_counter / 3)")
                                    new_anim[k] = expr
                                if new_anim:
                                    new_anims.append(new_anim)
                            part["animations"] = new_anims
                extra_files[jem_name] = json.dumps(jem, indent="\t").encode("utf-8")

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
        for existing_file in os.listdir(CLIENT_DOWNLOADS):
            existing_path = os.path.join(CLIENT_DOWNLOADS, existing_file)
            if os.path.isfile(existing_path):
                try:
                    shutil.copy2(OUTPUT_PACK, existing_path)
                    print(f"Updated active client cache file: {existing_path}")
                except Exception as e:
                    print(f"Could not overwrite {existing_path}: {e}")
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
