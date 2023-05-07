import bpy
import os
import platform
from random import randint
from bpy.types import Object


# USER INPUTS
import_path: str = "/Your/Path/To/outfit-blocks/" # change this path
batch_export: int = 1 # export many outfits at once
export_type: str = "gltf" # or fbx
# USER INPUTS END

export_path: str = import_path + "export/"
if not os.path.exists(export_path):
    os.mkdir(export_path)


def import_fbx() -> None:
    """Import fbx files into blend file.
    Rename Objects, Meshes (...), etc.
    Parents Objects under one Armature.
    Setup Armature Modifier.
    Cleanup blend file.
    """
    if bpy.data.objects.get("Armature"):
        return

    # collect fbx files
    import_files: list[str] = []
    for root, _dirs, files in os.walk(import_path, topdown=True):
        for name in files:
            if ".fbx" in name:
                import_files.append(os.path.join(root, name))

    # import fbx files
    for e_file in import_files:
        bpy.ops.import_scene.fbx(filepath=e_file,
                                 ignore_leaf_bones=True)
        new_name = "Body"
        if not "body" in e_file:
            path_separator: str = "/" if not "Windows" in platform.system() else "\\"
            filename: list[str] = e_file.split(path_separator)[-1].split(".")[0].split("-")
            # new name is <category>_Outfit_<outfit_variant> -> Bottom_Outfit_Office
            new_name: str = (f"{filename[5].capitalize()}_{filename[0].capitalize()}_"
                             f"{filename[2].capitalize()}")
        # object edits
        for e_object in bpy.data.objects:
            if "Wolf3D_" in e_object.name:
                e_object.name: str = new_name
                e_object.parent: Object = bpy.data.objects["Armature"]
            if "Wolf3D_" in e_object.data.name:
                e_object.data.name: str = e_object.name
            for e_modifier in e_object.modifiers:
                if not "Armature.001" in e_modifier.name:
                    continue
                e_modifier.name: str = "Armature"
                e_modifier.object: Object = bpy.data.objects["Armature"]
            if not e_object.active_material:
                continue
            if "Wolf3D_" in e_object.active_material.name:
                e_object.active_material.name: str = f"{e_object.name}_Mat"
        # cleanup old Armatures
        if bpy.data.objects.get("Armature.001"):
            bpy.data.objects.remove(bpy.data.objects["Armature.001"], do_unlink=True)
        if bpy.data.armatures.get("Armature.001"):
            bpy.data.armatures.remove(bpy.data.armatures["Armature.001"], do_unlink=True)
    # cleanup new blend files
    if bpy.data.objects.get("Cube"):
        bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)


def prepare_outfits() -> tuple[dict, list]:
    """Sort all outfits into categories"""
    outfit_table: dict = {}
    # get categories from folder names
    outfit_categories: list[str] = [dir.capitalize() for dir in os.listdir(import_path)
                                    if not dir.lower() in [".ds_store", "body", "export"]]
    outfit_objects: list[Object] = [obj for obj in bpy.data.objects if "Outfit" in obj.name]
    # sort objects into categories
    for e_category in outfit_categories:
        outfit_variants: list[Object] = []
        for e_outfit in outfit_objects:
            if not e_category in e_outfit.name:
                continue
            outfit_variants.append(e_outfit)
        outfit_table.update({e_category:outfit_variants})

    return outfit_table, outfit_objects


def export(batch: int, outfit_table: dict, outfit_objects: list) -> None:
    """Randomize outfits and (batch) export.
    Only visible objects will be exported.
    """
    for e_export in range(1, batch + 1):
        [e.hide_set(True) for e in outfit_objects]
        for e_outfit in outfit_table.values():
            # randomize outfit variants
            e_outfit[randint(0, len(e_outfit)-1)].hide_set(False)
            while os.path.exists(export_path + f"Outfit_Rnd_{e_export:>003}.glb"):
                e_export += 1
            filepath: str = export_path + f"Outfit_Rndm_{e_export:>003}.glb"
        # Armature name same as filename
        bpy.data.objects["Armature"].name = f"Armature_Outfit_Rndm_{e_export:>003}"
        # export
        if "gltf" in export_type:
            bpy.ops.export_scene.gltf(filepath=filepath,
                                    use_visible=True)
        elif "fbx" in export_type:
            bpy.ops.export_scene.fbx(filepath=filepath,
                                    use_visible=True,
                                    add_leaf_bones=False)
        bpy.data.objects[f"Armature_Outfit_Rndm_{e_export:>003}"].name = "Armature"


import_fbx()
outfit_table, outfit_objects = prepare_outfits()
export(batch_export, outfit_table, outfit_objects)