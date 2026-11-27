"""Render the SenseBook v2 proposal model with Blender (bpy, Cycles on the CPU), the same tool the build chat uses.

Reads out/sensebook_v2.glb (written by build_v2.py) and writes out/renders/*.png. These are renders of the CAD
model, not photographs; the book is a simple stand-in for scale.

Run from the repository root with the build chat's render environment:
    design\\.venv-render\\Scripts\\python.exe docs\\validation\\hardware_v2\\cad\\render_v2.py [--draft] [scene ...]
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
GLB = os.path.join(HERE, "..", "out", "sensebook_v2.glb")
OUT = os.path.join(HERE, "..", "out", "renders")          # full-size PNG; make_site.py writes web JPGs to web/renders
os.makedirs(OUT, exist_ok=True)
DRAFT = "--draft" in sys.argv
RES = (900, 600) if DRAFT else (1600, 1066)
SAMPLES = 16 if DRAFT else 64


def lin(h):
    h = h.lstrip("#")
    return tuple(((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.image_settings.file_format = "PNG"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    w = bpy.data.worlds.new("w"); w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = lin("#DADBD6") + (1.0,)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3
    sc.world = w
    bpy.ops.import_scene.gltf(filepath=GLB)
    # table under the book
    bpy.ops.mesh.primitive_plane_add(size=3.0, location=(0, 0.1, -0.0122))
    t = bpy.context.active_object
    m = bpy.data.materials.new("table"); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = lin("#B9B2A6") + (1.0,)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
    t.data.materials.append(m)
    fix_materials()
    return sc


def setin(node, names, value):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return


def fix_materials():
    """Clear windows read as dark tinted glass (so the lenses show through), not as frosted white."""
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        b = m.node_tree.nodes.get("Principled BSDF")
        if b is None:
            continue
        if m.name.startswith("glass"):
            setin(b, ["Base Color"], lin("#2A3439") + (1.0,))
            setin(b, ["Transmission Weight", "Transmission"], 1.0)
            setin(b, ["Roughness"], 0.04)
            setin(b, ["Alpha"], 1.0)
            setin(b, ["IOR"], 1.49)
        if m.name.startswith("led_warm"):
            setin(b, ["Emission Strength"], 2.0)


def objs():
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name != "Plane"]


def prop(o, k, d=""):
    try:
        return o.get(k, d)
    except Exception:
        return d


def show(option="A", hide_prefix=(), hide_groups=("views",)):
    """Show one option (A or B); hide the other option's parts, the given groups and names starting with hide_prefix."""
    for o in objs():
        opt, grp = prop(o, "option", ""), prop(o, "group", "")
        hide = opt not in ("", option) or grp in hide_groups or (bool(hide_prefix) and o.name.startswith(tuple(hide_prefix)))
        o.hide_render = bool(hide)


def light(loc, energy, size=0.6, color="#FFF4E6"):
    d = bpy.data.lights.new("L", "AREA"); d.energy = energy; d.size = size; d.color = lin(color)
    o = bpy.data.objects.new("L", d); bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector((0, 0, 0.09)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, lens=50):
    c = bpy.data.cameras.new("C"); c.lens = lens
    o = bpy.data.objects.new("C", c); bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = o


def render(name):
    light((-0.6, 0.9, 1.1), 70); light((0.9, 0.3, 0.7), 28, 0.4, "#E8F0FF"); light((0.0, -0.8, 0.6), 18, 0.5)
    bpy.context.scene.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("render", name)


SCENES = {
    # device on an open textbook, seen from the reader's side
    "v2_hero_A": lambda: (show("A"), camera((-0.30, 0.52, 0.34), (0.0, 0.03, 0.06), 62)),
    # the lens facet: four camera windows, two light bars, the ToF window
    "v2_facet_A": lambda: (show("A"), camera((0.06, 0.20, 0.03), (0.0, -0.035, 0.105), 70)),
    # Option B: keys on the hub wings at the book's top edge, and the pocket clicker on the table
    "v2_hero_B": lambda: (show("B"), camera((-0.46, 0.46, 0.36), (-0.09, 0.03, 0.04), 42)),
    # inside the head: shell and cover hidden
    "v2_inside_A": lambda: (show("A", hide_prefix=("shell_front_tub", "shell_back_cover", "book_", "zone_", "view_")),
                            camera((-0.12, 0.11, 0.045), (0.0, -0.04, 0.105), 58)),
    # what each camera reads: the page areas and the view lines to their corners
    "v2_zones": lambda: (show("A", hide_groups=()), camera((-0.04, 0.50, 0.50), (0.0, 0.10, 0.02), 30)),
    # front, side and top
    "v2_front_A": lambda: (show("A"), camera((0.0, 0.60, 0.27), (0.0, -0.03, 0.105), 95)),
    "v2_side_A": lambda: (show("A", hide_groups=()), camera((0.66, 0.09, 0.30), (0.0, 0.085, 0.06), 45)),
    "v2_top_A": lambda: (show("A"), camera((0.0, 0.05, 0.62), (0.0, -0.035, 0.11), 80)),
    # pulled apart (each part moved by its own explode offset from the model)
    "v2_exploded_A": lambda: (show("A", hide_prefix=("book_",)), explode(1.0), camera((-0.30, 0.33, 0.28), (0.0, -0.03, 0.105), 58)),
    # inside from the back: cover hidden, main board and cells
    "v2_inside_back_A": lambda: (show("A", hide_prefix=("shell_back_cover", "thermal_pad", "heat_spreader", "cover_screw")),
                                 camera((0.10, -0.34, 0.24), (0.0, -0.04, 0.105), 62)),
    # Option B close-up: hub wings and keys at the top edge of the book
    "v2_wings_B": lambda: (show("B"), camera((-0.13, 0.13, 0.11), (0.0, -0.045, 0.0), 50)),
}


def explode(k):
    for o in objs():
        e = prop(o, "explode", None)
        if e is not None and len(e) == 3 and not o.hide_render:
            o.location = Vector((e[0], e[1], e[2])) * k

if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")] or list(SCENES)
    for nm in want:
        reset()
        SCENES[nm]()
        render(nm)
