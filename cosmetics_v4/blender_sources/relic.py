"""Forgotten Relic (John Doe): an ancient eight-pointed sigil of charred iron, embers smouldering in its cracks,
a ring of burning runes, and a faceted crystal heart held in four prongs; a bail and a snapped length of chain."""
from kit import *
import runes
KEY = "relic"
PREVIEW = {"main": {"elev": 8, "azim": -18, "dist": 0.85}, "extra": [{"elev": 30, "azim": 40, "dist": 0.8}]}
RED = (1.0, 0.18, 0.04)

def star(n, ro, ri, th, name, z=0.0):
    verts = []
    for i in range(2 * n):
        r = ro if i % 2 == 0 else ri
        a = i / (2 * n) * TAU + math.pi / 2
        verts.append((r * math.cos(a), 0, r * math.sin(a)))
    top = [(x, -th / 2 + z, zz) for x, _, zz in verts]; bot = [(x, th / 2 + z, zz) for x, _, zz in verts]
    m = len(verts)
    faces = [tuple(range(m))[::-1], tuple(range(m, 2 * m))]
    for i in range(m):
        j = (i + 1) % m
        faces.append((i, j, m + j, m + i))
    o = from_pydata(top + bot, faces, name)
    sel([o]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    return o

def build():
    runes.sheet(f"{OUT}/runes_relic.png", seed=21, rows=4, cols=14, w=12, border=False)
    iron = mat_iron("relic_iron", base=(0.022, 0.018, 0.016), worn=(0.26, 0.22, 0.18), rust=(0.1, 0.035, 0.015), rust_k=0.12, ember=0.5, ember_col=(1.0, 0.16, 0.03), pits=0.55)
    trim = mat_iron("relic_trim", base=(0.05, 0.04, 0.03), worn=(0.42, 0.34, 0.22), rust_k=0.1, metal=1.0, rough=0.45)
    rune = mat_iron("relic_rune", rune=f"{OUT}/runes_relic.png", rune_scale=1.7, rune_col=RED, rune_k=14, base=(0.02, 0.017, 0.015), rust_k=0.05)
    heart = mat_glow("relic_heart", col=(1.0, 0.28, 0.06), base=(0.25, 0.03, 0.0), k=9, crack=7)
    parts = []
    s1 = star(8, 0.58, 0.3, 0.07, "star1"); bevel(s1, 0.012, 2, 30); assign(s1, iron); parts.append(s1)
    s2 = star(8, 0.42, 0.24, 0.06, "star2", z=-0.05); s2.rotation_euler = (0, math.radians(22.5), 0); bake_xform(s2)
    bevel(s2, 0.01, 2, 30); assign(s2, trim); parts.append(s2)
    # raised rim lines on each big ray (two thin ridges per ray give it a forged, layered look)
    for i in range(8):
        a = i / 8 * TAU + math.pi / 2
        rid = box((0.025, 0.02, 0.26), (0, -0.045, 0), name="ridge")
        rid.matrix_world = Matrix.Rotation(-(a - math.pi / 2), 4, "Y") @ Matrix.Translation((0, -0.045, 0.4)); bake_xform(rid)
        bevel(rid, 0.006, 1); assign(rid, iron); parts.append(rid)
    # rune ring: a lathe band facing forward (axis = Y)
    ring = lathe([(0.17, -0.02), (0.25, -0.02), (0.26, 0.0), (0.25, 0.02), (0.17, 0.02)], 48, "runering")
    ring.rotation_euler = (math.pi / 2, 0, 0); ring.location.y = -0.1; bake_xform(ring); assign(ring, rune); parts.append(ring)
    inner = torus(0.165, 0.018, (0, -0.1, 0), (math.pi / 2, 0, 0), 40, 8, "inner"); assign(inner, trim); parts.append(inner)
    outer = torus(0.262, 0.016, (0, -0.1, 0), (math.pi / 2, 0, 0), 48, 8, "outer"); assign(outer, trim); parts.append(outer)
    # four prongs gripping the heart
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        pts = [(math.cos(a) * 0.17, -0.1, math.sin(a) * 0.17), (math.cos(a) * 0.14, -0.2, math.sin(a) * 0.14), (math.cos(a) * 0.07, -0.25, math.sin(a) * 0.07)]
        pr = tube_along(pts, 0.022, 6, "prong", radii=[1, 0.8, 0.45]); assign(pr, trim); parts.append(pr)
    # bail + jump ring on the top point
    bail = torus(0.07, 0.022, (0, 0, 0.66), (0, 0, 0), 20, 8, "bail"); assign(bail, trim); parts.append(bail)
    tip = cone(0.035, 0.12, (0, 0, -0.66), (math.pi, 0, 0), 6, "droptip"); assign(tip, trim); parts.append(tip)
    frame = join(parts, "SigilFrame"); smooth(frame, 35)
    # the crystal heart: an elongated octagonal bipyramid with a bevelled girdle
    h = lathe([(0.0, -0.2), (0.11, -0.03), (0.12, 0.0), (0.11, 0.03), (0.0, 0.2)], 8, "heart")
    h.rotation_euler = (math.pi / 2, 0, 0); h.location.y = -0.2; h.scale = (1, 0.75, 1); bake_xform(h)
    flat(h); assign(h, heart)
    # a snapped length of chain hanging from the bail
    pts = [Vector((0, 0, 0.72)) + Vector((0.012 * i, 0.0, 0.13 * i)) for i in range(5)]
    ch = chain_along(pts, 0.12, 0.07, 0.014, "SigilChain")
    assign(ch, mat_iron("relic_chain", base=(0.03, 0.026, 0.022), worn=(0.3, 0.27, 0.22), rust_k=0.2))
    return {"SigilFrame": (frame, 1024, True), "SigilHeart": (h, 256, True), "SigilChain": (ch, 256, False)}
