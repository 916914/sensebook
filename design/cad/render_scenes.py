"""Render the SenseBook model with Blender (bpy, Cycles on the CPU).

Reads the meshes and poses that build_model.py wrote to design/cad/build/, then writes
design/renders/*.png and, for labelled views, *.anchors.json (used by annotate.py).
It also exports design/cad/out/sensebook.glb for the web viewer (scene "glb").

Run from design/cad:
    ..\\.venv-render\\Scripts\\python.exe render_scenes.py                 # everything
    ..\\.venv-render\\Scripts\\python.exe render_scenes.py hero front      # chosen scenes
    ..\\.venv-render\\Scripts\\python.exe render_scenes.py --draft hero    # fast preview

These are renders of the CAD model, not photographs. Books, table, pencil, phone and the
mannequin hands are simple stand-ins made here for scale.
"""
import json
import math
import os
import sys

import bpy  # noqa: E402  (must come before bmesh / mathutils)
import bmesh
import numpy as np
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
RENDERS = os.path.normpath(os.path.join(HERE, "..", "renders"))
OUT = os.path.join(HERE, "out")
MM = 0.001
MAN = json.load(open(os.path.join(BUILD, "manifest.json")))
PRM = MAN["params"]
U0 = np.array(MAN["unit_matrix"])
DRAFT = "--draft" in sys.argv
SAMPLES = int(os.environ.get("SB_SAMPLES", 24 if DRAFT else 110))     # SB_SAMPLES=56 halves the time on a slow machine
RES = (900, 600) if DRAFT else (1800, 1200)
LIGHT = 0.11                                    # global light calibration


# ------------------------------------------------------------------ materials
def lin(c):
    return tuple(((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c)


def hexc(h):
    h = h.lstrip("#")
    return lin(tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


MATS = {
    "abs_teal": dict(c="#2B474F", r=0.50, bump=0.15),
    "abs_light": dict(c="#3F5F68", r=0.42),
    "marigold": dict(c="#E8A317", r=0.38),
    "glass": dict(c="#C8D4D8", r=0.02, t=1.0, ior=1.49),
    "blue_ring": dict(c="#9CC4DE", r=0.22, m=1.0),
    "diffuser": dict(c="#F2F0E8", r=0.45, e=("#FFE9C4", 0.9), sss=0.3),
    "dot_white": dict(c="#F5F5F0", r=0.35, e=("#FFFFFF", 0.6)),
    "orange_flag": dict(c="#EE6A1A", r=0.5),
    "pcb_green": dict(c="#0E5C33", r=0.35, coat=0.6), "pcb_green2": dict(c="#1A6B3D", r=0.35, coat=0.6),
    "pcb_black": dict(c="#101214", r=0.35, coat=0.6), "pcb_blue": dict(c="#123385", r=0.35, coat=0.6),
    "pcb_purple": dict(c="#542473", r=0.35, coat=0.6), "pcb_red": dict(c="#9E1A1A", r=0.35, coat=0.6),
    "pcb_white": dict(c="#E6E6E0", r=0.4),
    "ic_black": dict(c="#121214", r=0.45), "plastic_black": dict(c="#17171A", r=0.4),
    "lens_black": dict(c="#0D0D10", r=0.3), "lens_glass": dict(c="#0B1024", r=0.03, coat=1.0, spec=1.0),
    "metal_tin": dict(c="#BDBFC2", r=0.32, m=1.0), "gold": dict(c="#D4A942", r=0.3, m=1.0),
    "aluminium": dict(c="#CDCFD1", r=0.38, m=1.0), "pad_grey": dict(c="#8C99AD", r=0.7),
    "pouch_silver": dict(c="#B4B6BA", r=0.42, m=0.9), "kapton": dict(c="#C7851F", r=0.3, coat=0.5),
    "speaker": dict(c="#1E1E21", r=0.5), "led_warm": dict(c="#FFF0C0", r=0.3, e=("#FFE6B0", 2.0)),
    "wire_multi": dict(c="#B64A3C", r=0.5), "wire_red": dict(c="#B81E1E", r=0.5), "wire_black": dict(c="#1A1A1C", r=0.5),
    "flex_amber": dict(c="#C98A33", r=0.35), "screw_black": dict(c="#1F1F22", r=0.35, m=1.0),
    "screw_steel": dict(c="#B5B7BA", r=0.3, m=1.0), "steel_brushed": dict(c="#C2C4C7", r=0.30, m=1.0, aniso=0.6),
    "spring_steel": dict(c="#A3A7AD", r=0.24, m=1.0), "silicone": dict(c="#D5D8DA", r=0.55),
    "tpu_dark": dict(c="#222427", r=0.8), "foam": dict(c="#2B2C2E", r=0.95),
    # scene props
    "paper_edge": dict(c="#E9E1CE", r=0.8, stripes=True), "cover_cloth": dict(c="#27425C", r=0.85, bump=0.6),
    "cover_card": dict(c="#B9573A", r=0.55), "sweep": dict(c="#DADBD6", r=0.9), "clay": dict(c="#C9B9A6", r=0.7),
    "pencil_wood": dict(c="#D9B26A", r=0.6), "pencil_paint": dict(c="#C9412B", r=0.35, coat=0.4),
    "graphite": dict(c="#2A2A2D", r=0.4), "phone": dict(c="#121316", r=0.25, coat=0.8), "phone_screen": dict(c="#07080A", r=0.05, coat=1.0),
    "cut_face": dict(c="#7FA1AA", r=0.7),
}
_mcache = {}
_meshes = {}


def material(key):
    if key in _mcache:
        return _mcache[key]
    d = MATS[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    col = hexc(d["c"]) + (1.0,)
    b.inputs["Base Color"].default_value = col
    b.inputs["Roughness"].default_value = d.get("r", 0.5)
    b.inputs["Metallic"].default_value = d.get("m", 0.0)
    if "t" in d:
        b.inputs["Transmission Weight"].default_value = d["t"]
        b.inputs["IOR"].default_value = d.get("ior", 1.5)
    if "coat" in d:
        b.inputs["Coat Weight"].default_value = d["coat"]
        b.inputs["Coat Roughness"].default_value = 0.08
    if "e" in d:
        b.inputs["Emission Color"].default_value = hexc(d["e"][0]) + (1.0,)
        b.inputs["Emission Strength"].default_value = d["e"][1]
    if "sss" in d:
        b.inputs["Subsurface Weight"].default_value = d["sss"]
    if "aniso" in d:
        b.inputs["Anisotropic"].default_value = d["aniso"]
    if d.get("bump"):
        n = nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = 2600.0
        n.inputs["Detail"].default_value = 3.0
        bp = nt.nodes.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = d["bump"]
        bp.inputs["Distance"].default_value = 0.00004
        nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    if d.get("stripes"):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        w = nt.nodes.new("ShaderNodeTexWave")
        w.wave_type, w.bands_direction = "BANDS", "Z"
        w.inputs["Scale"].default_value = 5200.0
        w.inputs["Distortion"].default_value = 0.6
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = hexc("#CFC6B0") + (1.0,)
        ramp.color_ramp.elements[1].color = hexc("#F1EADA") + (1.0,)
        nt.links.new(tc.outputs["Object"], w.inputs["Vector"])
        nt.links.new(w.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    _mcache[key] = m
    return m


def image_material(name, path, rough=0.75):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    return m


def wood_material():
    """Calm oak-like desk top: long soft grain, low contrast."""
    m = bpy.data.materials.new("wood")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.6, 46.0, 46.0)
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(4))
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value = 2.4
    n1.inputs["Detail"].default_value = 8.0
    n1.inputs["Roughness"].default_value = 0.55
    n1.inputs["Distortion"].default_value = 0.35
    mp2 = nt.nodes.new("ShaderNodeMapping")
    mp2.inputs["Scale"].default_value = (0.5, 5.0, 5.0)
    n2 = nt.nodes.new("ShaderNodeTexNoise")
    n2.inputs["Scale"].default_value = 1.3
    n2.inputs["Detail"].default_value = 2.0
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MIX"
    mix.inputs["Fac"].default_value = 0.35
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    e = ramp.color_ramp.elements
    e[0].position, e[0].color = 0.30, hexc("#77583A") + (1.0,)
    e[1].position, e[1].color = 0.72, hexc("#A98862") + (1.0,)
    mid = ramp.color_ramp.elements.new(0.52)
    mid.color = hexc("#93714C") + (1.0,)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(tc.outputs["Object"], mp2.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], n1.inputs["Vector"])
    nt.links.new(mp2.outputs["Vector"], n2.inputs["Vector"])
    nt.links.new(n1.outputs["Fac"], mix.inputs["Color1"])
    nt.links.new(n2.outputs["Fac"], mix.inputs["Color2"])
    nt.links.new(mix.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.05
    bp.inputs["Distance"].default_value = 0.0003
    nt.links.new(n1.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.58
    return m


# ------------------------------------------------------------------ scene basics
def reset(res=RES, samples=SAMPLES, transparent=False, bg="#DADBD6", world=0.55):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mcache.clear()
    _meshes.clear()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.render.threads_mode = "AUTO"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = transparent
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    bgn = w.node_tree.nodes["Background"]
    bgn.inputs["Color"].default_value = hexc(bg) + (1.0,)
    bgn.inputs["Strength"].default_value = world
    sc.world = w
    return sc


def link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def mesh_object(name, verts, faces, mat=None, smooth=True, angle=35.0, uvs=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.update()
    if uvs is not None:
        layer = me.uv_layers.new(name="uv")
        for poly in me.polygons:
            for li, vi in zip(poly.loop_indices, poly.vertices):
                layer.data[li].uv = uvs[vi]
    if smooth:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
        me.set_sharp_from_angle(angle=math.radians(angle))
    ob = bpy.data.objects.new(name, me)
    if mat is not None:
        me.materials.append(mat)
    return link(ob)





def body_mesh(key, web=False):
    ck = (key, web)
    if ck in _meshes:
        return _meshes[ck]
    d = np.load(os.path.join(BUILD, "mesh_web" if web else "mesh", key + ".npz"))
    me = bpy.data.meshes.new(key)
    me.from_pydata((d["v"] * MM).tolist(), [], d["f"].tolist())
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=2e-6)
    bm.to_mesh(me)
    bm.free()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.set_sharp_from_angle(angle=math.radians(35))
    _meshes[ck] = me
    return me


def to_m(M):
    M = np.array(M, dtype=float).copy()
    M[:3, 3] *= MM
    return Matrix(M.tolist())


def assemble(pose="table_hardcover", explode=0.0, groups=None, hide=(), extra=None, unit_frame=False, web=False,
             explode_scale=None):
    """Create one object per body. Returns {name: object}."""
    p = MAN["poses"][pose]
    objs = {}
    Ru = (np.array(p["groups"]["unit"]) @ U0)[:3, :3]
    E = Matrix(np.array(extra).tolist()) if extra is not None else Matrix.Identity(4)
    Uinv = np.linalg.inv(np.array(p["groups"]["unit"]) @ U0)
    for b in MAN["bodies"]:
        if b["variant"] != p["variants"].get(b["name"]):
            continue
        if groups is not None and b["group"] not in groups:
            continue
        if any(b["name"].startswith(h) for h in hide):
            continue
        M = np.array(p["groups"][b["group"]])
        if unit_frame:
            M = Uinv @ M
        e = np.array(b["explode"], dtype=float) * explode
        if explode_scale and b["name"] in explode_scale:
            e = e * explode_scale[b["name"]]
        if b["frame"] == "unit" and not unit_frame:
            e = Ru @ e
        T = np.eye(4)
        T[:3, 3] = e
        ob = bpy.data.objects.new(b["name"], body_mesh(b["key"], web))
        if not ob.data.materials:
            ob.data.materials.append(material(b["mat"]))
        ob.matrix_world = E @ to_m(T @ M)
        ob["label"] = b["label"]
        link(ob)
        objs[b["name"]] = ob
    return objs


def area(name, loc, target, size, power, color="#FFFFFF", size_y=None):
    L = bpy.data.lights.new(name, "AREA")
    L.energy = power * LIGHT
    L.color = hexc(color)
    L.shape = "RECTANGLE" if size_y else "SQUARE"
    L.size = size
    if size_y:
        L.size_y = size_y
    ob = link(bpy.data.objects.new(name, L))
    ob.location = loc
    aim(ob, target)
    return ob


def aim(ob, target):
    d = Vector(target) - Vector(ob.location)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(loc, target, lens=60.0, ortho=None, fstop=None, focus=None, shift=(0, 0)):
    c = bpy.data.cameras.new("cam")
    c.lens = lens
    c.clip_start, c.clip_end = 0.005, 20.0
    c.shift_x, c.shift_y = shift
    if ortho:
        c.type = "ORTHO"
        c.ortho_scale = ortho
    ob = link(bpy.data.objects.new("cam", c))
    ob.location = loc
    aim(ob, target)
    if fstop:
        c.dof.use_dof = True
        c.dof.aperture_fstop = fstop
        c.dof.focus_distance = (Vector(focus or target) - Vector(loc)).length
    bpy.context.scene.camera = ob
    return ob


def studio(table_z, warm=False, key=(0.55, 0.45, 0.75), power=1.0):
    """Seamless sweep plus three soft lights."""
    z = table_z * MM
    n, R, far, wide = 16, 0.6, -1.4, 4.0
    prof = [(2.5, z), (far + R, z)]
    for i in range(1, n + 1):
        a = math.pi / 2 * i / n
        prof.append((far + R - R * math.sin(a), z + R - R * math.cos(a)))
    prof.append((far, z + 2.2))
    verts, faces = [], []
    for (y, zz) in prof:
        verts += [(-wide, y, zz), (wide, y, zz)]
    for i in range(len(prof) - 1):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    mesh_object("sweep", verts, faces, material("sweep"))
    t = (0, 0.02, 0.08)
    area("key", key, t, 0.7, 95 * power, "#FFF1DE" if warm else "#FFF8F0")
    area("fill", (-0.75, 0.55, 0.45), t, 1.1, 34 * power, "#EEF3FF")
    area("rim", (-0.15, -0.75, 0.62), t, 0.5, 60 * power, "#FFFFFF")
    area("top", (0.0, 0.05, 1.0), t, 1.2, 40 * power, "#FFFFFF")


def table(table_z, warm=True, power=1.0):
    z = table_z * MM
    ob = mesh_object("table", [(-2.5, -2.0, z), (2.5, -2.0, z), (2.5, 2.5, z), (-2.5, 2.5, z)], [(0, 1, 2, 3)],
                     wood_material(), smooth=False)
    t = (0, 0.05, 0.05)
    area("key", (0.55, 0.20, 0.85), t, 0.9, 120 * power, "#FFE9CF" if warm else "#FFF6EC")
    area("fill", (-0.8, 0.6, 0.5), t, 1.2, 32 * power, "#E6EEFF")
    area("back", (-0.4, -0.5, 0.95), t, 0.9, 40 * power, "#FFF4E4")
    return ob


# ------------------------------------------------------------------ props
def book(page_w, page_d, block, cover, hard=True, left_tex="page_left.png", right_tex="page_right.png",
         cover_mat="cover_cloth", lift=1.0, name="book"):
    """Open book in the book frame: page plane z = 0 at the top edge (y = 0), gutter at x = 0."""
    objs = []
    dip, lam = min(0.42 * block, 5.5), 9.0
    n = 48

    def ztop(x):
        u = x / page_w
        return -dip * math.exp(-x / lam) + 0.9 * math.sin(math.pi * min(u, 1.0)) * (block / 12.0)

    zb = -block + lift
    slant = min(block * 0.55, 7.0)
    # right-handed world: +x is the reader's LEFT (the reader sits at +y and looks toward -y)
    for side, tex in ((1, left_tex), (-1, right_tex)):
        xs = [page_w * (i / n) ** 1.6 for i in range(n + 1)]
        verts, faces, uvs = [], [], []
        for x in xs:                                    # top surface, two rows (y = 0 and y = page_d)
            for y in (0.0, page_d):
                verts.append((side * x * MM, y * MM, ztop(x) * MM))
                u = x / page_w
                uvs.append(((1 - u) if side > 0 else u, 1.0 - y / page_d))
        for i in range(n):
            a, b, c, d = 2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2
            faces.append((a, b, c, d) if side > 0 else (a, d, c, b))
        top = mesh_object(f"{name}_page_{'r' if side > 0 else 'l'}", verts, faces,
                          image_material("pg" + tex, os.path.join(BUILD, "tex", tex)), uvs=uvs)
        objs.append(top)
        # block body (edges of the pages)
        v2, f2 = [], []
        ring = [(x, ztop(x) - 0.02) for x in xs] + [(page_w + slant, zb), (0.0, zb)]
        m = len(ring)
        for (x, z) in ring:
            v2 += [(side * x * MM, 0.0, z * MM), (side * x * MM, page_d * MM, z * MM)]
        for i in range(m):
            j = (i + 1) % m
            q = (2 * i, 2 * j, 2 * j + 1, 2 * i + 1)
            f2.append(q if side > 0 else q[::-1])
        f2.append(tuple(2 * i for i in range(m))[::-1] if side > 0 else tuple(2 * i for i in range(m)))
        f2.append(tuple(2 * i + 1 for i in range(m)) if side > 0 else tuple(2 * i + 1 for i in range(m))[::-1])
        objs.append(mesh_object(f"{name}_block_{'r' if side > 0 else 'l'}", v2, f2, material("paper_edge"), smooth=False))
    ov = 3.0 if hard else 0.0
    zc0, zc1 = -(block + cover), -block
    if hard:
        for x0, x1 in ((5.0, page_w + slant + ov), (-(page_w + slant + ov), -5.0), (-4.2, 4.2)):
            objs.append(boxm(f"{name}_cover", x0, x1, -ov, page_d + ov, zc0, zc1, material(cover_mat), bevel=0.8))
    else:
        objs.append(boxm(f"{name}_cover", -(page_w + slant), page_w + slant, 0, page_d, zc0, zc1, material(cover_mat), bevel=0.0))
    return objs


def boxm(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.0):
    v = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    v = [(a * MM, b * MM, c * MM) for a, b, c in v]
    f = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    ob = mesh_object(name, v, f, mat, smooth=False)
    if bevel:
        m = ob.modifiers.new("b", "BEVEL")
        m.width, m.segments = bevel * MM, 3
    return ob


def cyl_between(name, p0, p1, r0, r1, mat, n=28, cap=True):
    p0, p1 = Vector(p0), Vector(p1)
    ax = (p1 - p0).normalized()
    ref = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(ref).normalized()
    w = ax.cross(u)
    verts, faces = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        d = u * math.cos(a) + w * math.sin(a)
        verts += [tuple(p0 + d * r0), tuple(p1 + d * r1)]
    for i in range(n):
        j = (i + 1) % n
        faces.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    if cap:
        faces.append(tuple(2 * i for i in range(n))[::-1])
        faces.append(tuple(2 * i + 1 for i in range(n)))
    return mesh_object(name, verts, faces, mat, angle=50)


def pencil(p0, direction, length=0.175):
    d = Vector(direction).normalized()
    p0 = Vector(p0)
    cyl_between("pencil", p0, p0 + d * (length - 0.022), 0.0036, 0.0036, material("pencil_paint"), n=6)
    cyl_between("pencil_wood", p0 + d * (length - 0.022), p0 + d * (length - 0.004), 0.0036, 0.0011, material("pencil_wood"), n=18)
    cyl_between("pencil_tip", p0 + d * (length - 0.004), p0 + d * length, 0.0011, 0.0001, material("graphite"), n=12)


def phone(x, y, z, rot=0.0):
    ob = boxm("phone", -35.5, 35.5, -73, 73, 0, 7.8, material("phone"), bevel=3.0)
    sc = boxm("phone_screen", -33, 33, -70, 70, 7.8, 7.9, material("phone_screen"))
    for o in (ob, sc):
        o.matrix_world = Matrix.Translation((x, y, z)) @ Matrix.Rotation(rot, 4, "Z")


def hand(side, E, page_w=185.0, page_d=245.0):
    """Plain mannequin hand holding the lower corner of the book (a stand-in for scale, not a person).
    side: -1 = reader's right hand (x < 0), +1 = reader's left hand. Coordinates in the book frame (mm)."""
    bm = bmesh.new()

    def sph(c, r, scale=(1, 1, 1), rot=None):
        M = Matrix.Translation(Vector(c) * MM)
        if rot is not None:
            M = M @ rot
        M = M @ Matrix.Diagonal((scale[0], scale[1], scale[2], 1.0))
        bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=18, radius=r * MM, matrix=M)

    def cap(p0, p1, r0, r1=None):
        r1 = r1 or r0
        p0, p1 = Vector(p0) * MM, Vector(p1) * MM
        d = p1 - p0
        rotq = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        M = Matrix.Translation((p0 + p1) / 2) @ rotq
        bmesh.ops.create_cone(bm, cap_ends=True, segments=28, radius1=r0 * MM, radius2=r1 * MM, depth=d.length, matrix=M)
        bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=r0 * MM, matrix=Matrix.Translation(p0))
        bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=r1 * MM, matrix=Matrix.Translation(p1))

    X = lambda x: side * x                      # mirror for the other hand
    w, d = page_w, page_d
    zt = 9.0                                    # thumb rests on the page
    cap((X(w - 36), d - 52, zt), (X(w - 20), d - 30, zt + 1.5), 9.0, 9.8)             # thumb tip segment
    cap((X(w - 20), d - 30, zt + 1.5), (X(w + 4), d - 6, zt - 1.0), 9.8, 11.5)        # thumb base segment
    sph((X(w + 12), d + 8, -9.0), 24.0, (1.0, 1.25, 0.72))                           # thenar mound
    sph((X(w - 16), d - 10, -29.0), 40.0, (1.0, 1.0, 0.30))                          # palm, under the book
    for k, (dx, dy, L) in enumerate(((-52, -40, 78), (-36, -48, 86), (-18, -50, 80), (-2, -42, 62))):   # fingers under the book
        p0 = (X(w + dx), d + dy, -27.0)
        p1 = (X(w + dx - 20), d + dy - L, -26.0)
        cap(p0, p1, 9.0, 8.0)
    cap((X(w + 18), d + 34, -20.0), (X(w + 62), d + 200, -105.0), 25.0, 33.0)        # wrist and forearm
    me = bpy.data.meshes.new("hand")
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new("hand", me))
    rm = ob.modifiers.new("remesh", "REMESH")
    rm.mode, rm.voxel_size, rm.use_smooth_shade = "VOXEL", 0.0011, True
    sm = ob.modifiers.new("smooth", "SMOOTH")
    sm.factor, sm.iterations = 0.9, 24
    me.materials.append(material("clay"))
    ob.matrix_world = E
    return ob


# ------------------------------------------------------------------ labels
def anchors(name, items, cam=None):
    """items: list of (label, object or world point). Writes pixel coordinates for annotate.py."""
    sc = bpy.context.scene
    cam = cam or sc.camera
    bpy.context.view_layer.update()
    out = []
    for label, tgt in items:
        if isinstance(tgt, bpy.types.Object):
            bb = [tgt.matrix_world @ Vector(c) for c in tgt.bound_box]
            pt = sum(bb, Vector()) / 8.0
        else:
            pt = Vector(tgt)
        co = world_to_camera_view(sc, cam, pt)
        out.append(dict(label=label, x=round(co.x * sc.render.resolution_x, 1),
                        y=round((1 - co.y) * sc.render.resolution_y, 1)))
    with open(os.path.join(RENDERS, name + ".anchors.json"), "w") as fh:
        json.dump(dict(size=[sc.render.resolution_x, sc.render.resolution_y], items=out), fh, indent=1)


def render(name):
    os.makedirs(RENDERS, exist_ok=True)
    sc = bpy.context.scene
    sc.render.filepath = os.path.join(RENDERS, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("rendered", name, flush=True)


def cut_objects(objs, plane_co, plane_no, cap_mat="cut_face"):
    """Section view: remove everything on the positive side of a plane and cap the cut."""
    for ob in objs:
        me = ob.data.copy()
        ob.data = me
        bm = bmesh.new()
        bm.from_mesh(me)
        inv = ob.matrix_world.inverted()
        co = inv @ Vector(plane_co)
        no = (inv.to_3x3().transposed().inverted() @ Vector(plane_no)).normalized() if False else (ob.matrix_world.to_3x3().transposed() @ Vector(plane_no)).normalized()
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=no, clear_outer=True)
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
        if edges:
            fill = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges, normal=no)
            shell = ob.name.startswith("shell_")
            if shell and len(me.materials) < 2:
                me.materials.append(material(cap_mat))
            for f in fill["geom"]:
                if isinstance(f, bmesh.types.BMFace):
                    f.smooth = False
                    if shell:
                        f.material_index = 1
        bm.to_mesh(me)
        bm.free()
        if len(me.polygons) == 0:
            ob.hide_render = True


# ------------------------------------------------------------------ label sets
SHORT = {
    "shell_front_tub": "Front shell (tub)", "shell_back_cover": "Back cover", "lens_bezel": "Lens bezel", "camera_lens_glass": "Lens front",
    "light_ring_diffuser": "Light-ring diffuser", "light_ring_pcb": "Light-ring LED board", "camera_lens_m12": "M12 ultra-wide lens",
    "camera_holder_m12": "M12 lens holder", "camera_board_imx708": "Camera board (IMX708)", "pi_zero_2w_pcb": "Raspberry Pi Zero 2 W",
    "microsd_card": "microSD card", "heat_spreader": "Heat spreader", "thermal_pad": "Thermal pad", "cell_right": "LiPo cell pack, 800 mAh",
    "cell_left": "LiPo cell pack, 800 mAh", "cell_foam_right": "Foam pad", "light_ring_leds": "Light-ring LEDs", "speaker": "Speaker", "amp_board_max98357a": "Speaker amp (MAX98357A)",
    "dac_board_pcm5102": "Headphone DAC", "mic_right": "Microphone", "mic_left": "Microphone", "charger_board": "Charger + 5 V boost",
    "usb_c_receptacle": "USB-C", "fuel_gauge_max17048": "Fuel gauge (MAX17048)", "status_led_board": "Status LED board",
    "status_dot_pipes": "Status dots", "button_ask": "Ask button", "button_play_pause": "Play / Pause", "button_back": "Back",
    "button_forward": "Forward", "top_bar_board": "Button board", "ask_button_board": "Ask switch board", "button_vol_up": "Volume +", "button_vol_down": "Volume -",
    "volume_board": "Volume switches", "mic_mute_switch": "Mic-mute switch", "dac_jack": "Headphone jack",
    "haptic_motor": "Vibration motor", "harness_left": "Wiring harness", "harness_right": "Wiring harness",
    "battery_leads": "Battery leads", "camera_flex": "Camera flex", "hub_body": "Hub", "stick_outer_tube": "Outer tube",
    "stick_inner_tube": "Inner tube", "stick_collar": "Twist-lock collar", "stick_glide_bush": "Glide bush",
    "tilt_joint_head": "Tilt-joint head", "tilt_pivot_screw": "Pivot screw (M3)", "tilt_thumb_nut": "Thumb nut",
    "hub_cord": "Coiled cord (hub sensor)", "rear_leg": "Rear leg", "rear_leg_pad": "Soft TPU pad", "leg_pin": "Leg hinge pin",
    "torsion_spring_right": "Torsion springs (2)", "hub_sensor_switch": "Hub sensor switch", "blade_right": "Blade (spring steel)",
    "blade_left": "Blade (spring steel)", "blade_coat_right": "Blade coating", "blade_knuckle_right": "Blade knuckle",
    "blade_knuckle_left": "Blade knuckle", "knuckle_pin": "Knuckle pin", "cell_pcm_right": "Cell protection board",
    "speaker_leads": "Speaker leads", "hub_sensor_lead": "Sensor lead (in a groove)", "hub_cord_riser": "Cord through the joint",
    "camera_connector": "Camera connector", "status_leds": "Status LEDs", "cover_screw_1": "Cover screws (4)",
    "camera_screws": "Camera screws", "mic_mute_slider": "Mic-mute slider", "hub_cord_tail": "Hub cord",
    "blade_clamp_screw_right": "Blade clamp screw",
}


def label_items(objs, names):
    return [(SHORT[n], objs[n]) for n in names if n in objs]


# ------------------------------------------------------------------ scenes
HARD = dict(page_w=185.0, page_d=245.0, block=PRM["block_hard"], cover=PRM["cover_hard"])
TABLE_HARD = PRM["table_hard"]


def soft_lights(c, power=1.0, front=(0.4, 0.5, 0.5)):
    area("key", front, c, 0.8, 34 * power)
    area("fill", (-front[0] * 1.2, front[1] * 0.7, 0.3), c, 1.0, 16 * power)
    area("back", (0.0, -front[1] * 1.2, 0.45), c, 0.8, 18 * power)
    area("top", (0.0, 0.0, 0.7), c, 0.9, 14 * power)


def sc_hero():
    reset(world=0.5)
    studio(TABLE_HARD, warm=True)
    assemble("table_hardcover")
    book(**HARD)
    camera((-0.245, 0.400, 0.255), (0.010, 0.012, 0.062), lens=56, fstop=7.0, focus=(0.0, -0.02, 0.12))
    render("01_hero")


def world_bbox(objs):
    lo, hi = Vector((1e9, 1e9, 1e9)), Vector((-1e9, -1e9, -1e9))
    for o in objs:
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            lo = Vector((min(lo.x, p.x), min(lo.y, p.y), min(lo.z, p.z)))
            hi = Vector((max(hi.x, p.x), max(hi.y, p.y), max(hi.z, p.z)))
    return lo, hi


def _ortho(name, loc, target, scale, pose="table_hardcover"):
    reset(transparent=True, world=0.9, res=(1500, 1500) if not DRAFT else (750, 750))
    objs = assemble(pose)
    c = (0, -0.02, 0.07)
    area("key", (0.5, 0.6, 0.8), c, 0.9, 60)
    area("fill", (-0.6, 0.4, 0.4), c, 1.2, 25)
    area("back", (0.0, -0.8, 0.5), c, 0.8, 30)
    cam = camera(loc, target, ortho=scale)
    names = {b["name"]: b["group"] for b in MAN["bodies"]}
    ulo, uhi = world_bbox([o for n, o in objs.items() if names[n] == "unit"])
    alo, ahi = world_bbox(objs.values())
    llo, lhi = world_bbox([objs["camera_lens_glass"]])
    blo, bhi = world_bbox([objs["blade_left"], objs["blade_right"]])
    plo, phi = world_bbox([objs["rear_leg_pad"]])
    pts = [("unit_lo", ulo), ("unit_hi", uhi), ("all_lo", alo), ("all_hi", ahi), ("lens", (llo + lhi) / 2),
           ("blade_lo", blo), ("blade_hi", bhi), ("pad_lo", plo), ("pad_hi", phi),
           ("origin", (0, 0, 0)), ("hub_top", (0, PRM["stick_y"] * MM, PRM["hub_top_z"] * MM)),
           ("stick_top", (0, PRM["stick_y"] * MM, (PRM["hub_top_z"] + 90.0) * MM)), ("table", (0, 0, TABLE_HARD * MM))]
    anchors(name, pts, cam)
    render(name)


def sc_front():
    _ortho("02_front", (0, 1.0, 0.068), (0, 0, 0.068), 0.215)


def sc_side():
    _ortho("03_side", (1.0, -0.022, 0.068), (0, -0.022, 0.068), 0.215)


def sc_top():
    _ortho("04_top", (0, -0.022, 1.0), (0, -0.022, 0), 0.215)


def sc_exploded_unit():
    reset(transparent=True, world=1.0, res=(2000, 1500) if not DRAFT else (1000, 750))
    objs = assemble("table_hardcover", explode=1.0, groups=("unit",), unit_frame=True, hide=("hub_cord_tail",))
    c = (0, -0.006, -0.015)
    soft_lights(c, power=1.25, front=(0.5, 0.5, 0.5))
    cam = camera((0.47, 0.50, 0.36), c, lens=106)
    names = ["shell_front_tub", "shell_back_cover", "lens_bezel", "light_ring_diffuser", "light_ring_pcb",
             "camera_lens_m12", "camera_holder_m12", "camera_board_imx708", "pi_zero_2w_pcb", "microsd_card", "heat_spreader",
             "thermal_pad", "cell_right", "cell_left", "speaker", "amp_board_max98357a", "dac_board_pcm5102", "mic_right",
             "charger_board", "usb_c_receptacle", "fuel_gauge_max17048", "status_led_board", "status_dot_pipes", "button_ask",
             "button_play_pause", "button_back", "button_forward", "top_bar_board", "button_vol_up",
             "volume_board", "mic_mute_switch", "dac_jack", "haptic_motor", "harness_left", "camera_flex",
             "cover_screw_1"]
    anchors("05_exploded_unit", label_items(objs, names), cam)
    render("05_exploded_unit")


def sc_exploded_mech():
    reset(transparent=True, world=1.0, res=(1500, 2000) if not DRAFT else (750, 1000))
    objs = assemble("table_hardcover", explode=1.0, groups=("hub", "stick_outer", "stick_inner", "cord", "leg", "blade_r", "blade_l"))
    c = (0, -0.004, 0.088)
    soft_lights(c, power=2.6, front=(0.6, 0.6, 0.6))
    cam = camera((0.74, 0.74, 0.52), c, lens=88)
    names = ["tilt_joint_head", "tilt_pivot_screw", "tilt_thumb_nut", "stick_inner_tube", "stick_glide_bush", "stick_collar",
             "stick_outer_tube", "hub_cord", "hub_body", "torsion_spring_right", "leg_pin", "hub_sensor_switch", "rear_leg", "rear_leg_pad",
             "blade_knuckle_right", "knuckle_pin", "blade_right", "blade_coat_right", "blade_clamp_screw_right"]
    anchors("06_exploded_tri_grip", label_items(objs, names), cam)
    render("06_exploded_tri_grip")


def sc_cutaway():
    reset(transparent=True, world=1.1, res=(2000, 1500) if not DRAFT else (1000, 750))
    objs = assemble("table_hardcover", groups=("unit",), unit_frame=True, hide=("hub_cord_tail",))
    cut_objects(list(objs.values()), (0.0, 0, 0), (1, 0, 0))
    c = (0, -0.017, 0.017)
    area("key", (0.5, 0.25, 0.30), c, 0.6, 42)
    area("fill", (0.5, -0.35, 0.10), c, 0.8, 22)
    area("top", (0.25, 0.0, 0.5), c, 0.7, 20)
    cam = camera((0.50, 0.075, 0.085), c, ortho=0.086)
    names = ["shell_front_tub", "shell_back_cover", "lens_bezel", "light_ring_diffuser", "light_ring_pcb", "camera_lens_m12",
             "camera_holder_m12", "camera_board_imx708", "pi_zero_2w_pcb", "heat_spreader", "thermal_pad", "cell_right",
             "button_ask", "button_play_pause", "top_bar_board", "fuel_gauge_max17048", "camera_flex", "charger_board",
             "speaker", "mic_right", "harness_right"]
    anchors("07_cutaway_side", label_items(objs, names), cam)
    render("07_cutaway_side")


def sc_internals_front():
    reset(transparent=True, world=1.0, res=(2000, 1300) if not DRAFT else (1000, 650))
    objs = assemble("table_hardcover", groups=("unit",), unit_frame=True,
                    hide=("shell_front_tub", "button_", "status_dot_pipes", "lens_bezel", "light_ring_diffuser",
                          "mic_mute_slider", "mic_mute_flag", "hub_cord_tail"))
    c = (0, -0.016, 0.019)
    soft_lights(c, power=0.9, front=(0.3, 0.6, 0.45))
    cam = camera((0.085, 0.345, 0.155), c, lens=105)
    names = ["shell_back_cover", "pi_zero_2w_pcb", "cell_right", "cell_left", "cell_pcm_right", "camera_lens_m12", "camera_holder_m12",
             "camera_board_imx708", "light_ring_pcb", "speaker", "charger_board", "usb_c_receptacle", "dac_jack",
             "amp_board_max98357a", "dac_board_pcm5102", "haptic_motor", "status_led_board", "volume_board", "mic_mute_switch",
             "mic_right", "mic_left", "top_bar_board", "fuel_gauge_max17048", "harness_left", "battery_leads",
             "speaker_leads"]
    anchors("08_internals_front", label_items(objs, names), cam)
    render("08_internals_front")


def sc_internals_back():
    reset(transparent=True, world=1.0, res=(2000, 1300) if not DRAFT else (1000, 650))
    objs = assemble("table_hardcover", groups=("unit",), unit_frame=True, hide=("shell_back_cover", "cover_screw", "hub_cord_tail"))
    c = (0, -0.018, 0.019)
    area("key", (-0.3, -0.6, 0.45), c, 0.8, 30)
    area("fill", (0.5, -0.5, 0.2), c, 1.0, 14)
    area("top", (0.0, -0.1, 0.6), c, 0.8, 14)
    cam = camera((-0.085, -0.375, 0.150), c, lens=105)
    names = ["shell_front_tub", "pi_zero_2w_pcb", "heat_spreader", "thermal_pad", "microsd_card", "camera_flex", "harness_left",
             "harness_right", "cell_right", "cell_left", "button_ask"]
    anchors("09_internals_back", label_items(objs, names), cam)
    render("09_internals_back")


def sc_on_hardcover():
    reset(world=0.30, bg="#CFC3B2")
    table(TABLE_HARD)
    assemble("table_hardcover")
    book(**HARD)
    pencil((-0.235, 0.215, TABLE_HARD * MM + 0.0036), (0.22, -1.0, 0))
    camera((0.31, 0.60, 0.37), (0.0, 0.080, 0.022), lens=44, fstop=6.3, focus=(0.0, -0.02, 0.11))
    render("10_on_open_hardcover")


def sc_on_paperback():
    reset(world=0.30, bg="#CFC3B2")
    tz = -(PRM["block_soft"] + PRM["cover_soft"])
    table(tz)
    assemble("table_paperback")
    book(page_w=129.0, page_d=198.0, block=PRM["block_soft"], cover=PRM["cover_soft"], hard=False, left_tex="pb_left.png",
         right_tex="pb_right.png", cover_mat="cover_card", lift=0.9)
    camera((-0.27, 0.46, 0.26), (0.0, 0.05, 0.04), lens=45, fstop=6.3, focus=(0.0, -0.02, 0.12))
    render("11_on_thin_paperback")


def sc_tripod():
    reset(world=0.30, bg="#CFC3B2")
    table(TABLE_HARD)
    assemble("tripod_no_book")
    z = TABLE_HARD * MM + 0.0002
    w, h, y0 = 0.105, 0.297, 0.075
    mesh_object("sheet", [(-w, y0, z), (w, y0, z), (w, y0 + h, z), (-w, y0 + h, z)], [(0, 1, 2, 3)],
                image_material("sheet", os.path.join(BUILD, "tex", "sheet.png")), smooth=False,
                uvs=[(1, 1), (0, 1), (0, 0), (1, 0)])
    camera((0.34, 0.44, 0.27), (0.0, 0.04, 0.045), lens=45, fstop=6.3, focus=(0.0, -0.03, 0.11))
    render("12_table_tripod_no_book")


def sc_in_hand():
    reset(world=0.42, bg="#D6D0C4")
    beta = math.radians(38)
    E = Matrix.Translation((0, 0, 0.30)) @ Matrix.Rotation(-beta, 4, "X")
    assemble("in_hand", extra=np.array(E))
    for ob in book(**HARD):
        ob.matrix_world = E @ ob.matrix_world
    for side in (1, -1):
        hand(side, E)
    t = E @ Vector((0, 0.085, 0.03))
    area("key", (0.6, 0.5, 1.0), t, 0.9, 150, "#FFF0DC")
    area("fill", (-0.8, 0.7, 0.5), t, 1.2, 45, "#E6EEFF")
    area("back", (-0.2, -0.9, 0.7), t, 0.7, 70, "#FFFFFF")
    loc = E @ Vector((-0.20, 0.52, 0.50))
    camera(loc, t, lens=38, fstop=5.6, focus=E @ Vector((0, -0.02, 0.11)))
    render("13_held_in_the_hands")


def sc_stowed():
    reset(world=0.5)
    studio(0.0, warm=True)
    # lie the folded device on its back: unit back face down
    R = Matrix.Rotation(math.radians(90), 4, "X")
    objs = assemble("stowed", extra=np.array(R))
    lo, hi = world_bbox(objs.values())
    shift = Matrix.Translation((-(lo.x + hi.x) / 2, -(lo.y + hi.y) / 2 + 0.01, -lo.z))
    for o in objs.values():
        o.matrix_world = shift @ o.matrix_world
    pencil((0.090, 0.095, 0.0036), (-0.04, -1.0, 0))
    phone(-0.110, 0.012, 0.0, rot=math.radians(-5))
    camera((0.10, 0.40, 0.42), (-0.008, 0.012, 0.012), lens=50, fstop=8.0)
    lo, hi = world_bbox(objs.values())
    anchors("14_folded", [("lo", lo), ("hi", hi)])
    render("14_folded")


def sc_extended():
    reset(world=0.5)
    block, cover = 30.0, 3.0
    tz = -(block + cover)
    studio(tz, warm=True)
    assemble("extended")
    book(page_w=230.0, page_d=300.0, block=block, cover=cover, cover_mat="cover_cloth")
    camera((-0.42, 0.52, 0.36), (0.0, 0.0, 0.085), lens=50, fstop=8.0, focus=(0.0, -0.02, 0.2))
    render("15_stick_extended_small_print")


def sc_glb():
    """Web-viewer model: one node per body, default pose, explode vector and label in the node extras."""
    reset()
    objs = assemble("table_hardcover", web=True)
    p = MAN["poses"]["table_hardcover"]
    Ru = (np.array(p["groups"]["unit"]) @ U0)[:3, :3]
    for b in MAN["bodies"]:
        if b["name"] not in objs or b["variant"] is not None:
            continue
        ob = objs[b["name"]]
        e = np.array(b["explode"], dtype=float)
        if b["frame"] == "unit":
            e = Ru @ e
        ob["explode"] = [float(e[0]) * MM, float(e[1]) * MM, float(e[2]) * MM]
        ob["group"] = b["group"]
        ob["label"] = b["label"]
        ob["mat"] = b["mat"]
    path = os.path.join(OUT, "sensebook.glb")
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_extras=True, export_yup=True, export_apply=True,
                              export_cameras=False, export_lights=False)
    print("glb", round(os.path.getsize(path) / 1e6, 2), "MB", flush=True)


SCENES = {"hero": sc_hero, "front": sc_front, "side": sc_side, "top": sc_top, "exploded_unit": sc_exploded_unit,
          "exploded_mech": sc_exploded_mech, "cutaway": sc_cutaway, "internals_front": sc_internals_front,
          "internals_back": sc_internals_back, "hardcover": sc_on_hardcover, "paperback": sc_on_paperback, "tripod": sc_tripod,
          "in_hand": sc_in_hand, "stowed": sc_stowed, "extended": sc_extended, "glb": sc_glb}


if __name__ == "__main__":
    want = [a for a in sys.argv[1:] if not a.startswith("--")] or list(SCENES)
    for w in want:
        SCENES[w]()
