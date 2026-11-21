"""Forgotten Relic v2 (John Doe): an eight-pointed sigil of tarnished gold over a crimson-enamelled star, rays
tipped with red gems, a ring of burning red runes, a faceted blood-crystal heart held in four gold claws --
hung on a heavy gold chain that runs up over the chest, round the shoulders and behind the neck.

Coordinates are pendant-local (Blender, studs): the pendant faces -Y, +Y points into the chest.
The pendant is worn at Torso CF(0, -0.2, -0.68), so in this space the torso centre is (0, 0.68, 0.2),
the torso top (shoulders/neck base) is z = 1.2, its front face y = 0.18 and its back face y = 1.18."""
from kit import *
import runes
KEY = "relic2"
PREVIEW = {"main": {"elev": 8, "azim": -18, "dist": 1.1}, "extra": [{"elev": 25, "azim": 60, "dist": 1.3}]}
RED = (1.0, 0.07, 0.03)


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


def catmull(ctrl, per=8, closed=False):
    P = [Vector(c) for c in ctrl]
    out = []
    n = len(P)
    rng_ = range(n) if closed else range(n - 1)
    for i in rng_:
        p0 = P[(i - 1) % n] if closed or i > 0 else P[0]
        p1, p2 = P[i], P[(i + 1) % n]
        p3 = P[(i + 2) % n] if closed or i + 2 < n else P[-1]
        for k in range(per):
            t = k / per; t2 = t * t; t3 = t2 * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed: out.append(P[-1])
    return out


def build():
    runes.sheet(f"{OUT}/runes_relic.png", seed=21, rows=4, cols=14, w=12, border=False)
    gold = mat_gold("r2_gold", base=(0.36, 0.2, 0.06), worn=(1.0, 0.78, 0.4))
    enamel = mat_glow("r2_enamel", col=RED, base=(0.42, 0.015, 0.01), k=1.5, crack=10)
    rune = mat_iron("r2_rune", rune=f"{OUT}/runes_relic.png", rune_scale=1.7, rune_col=RED, rune_k=22, base=(0.08, 0.01, 0.008), worn=(0.3, 0.08, 0.05), rust_k=0.0)
    heart = mat_glow("r2_heart", col=(1.0, 0.06, 0.04), base=(0.5, 0.01, 0.01), k=14, crack=7)
    gem = mat_glow("r2_gem", col=RED, base=(0.45, 0.01, 0.0), k=8)
    parts = []
    s1 = star(8, 0.58, 0.3, 0.07, "star1"); bevel(s1, 0.014, 2, 30); assign(s1, gold); parts.append(s1)
    s2 = star(8, 0.44, 0.25, 0.06, "star2", z=-0.05); s2.rotation_euler = (0, math.radians(22.5), 0); bake_xform(s2)
    bevel(s2, 0.012, 2, 30); assign(s2, enamel); parts.append(s2)
    for i in range(8):
        a = i / 8 * TAU + math.pi / 2
        rid = box((0.026, 0.022, 0.24), (0, 0, 0), name="ridge")
        rid.matrix_world = Matrix.Rotation(-(a - math.pi / 2), 4, "Y") @ Matrix.Translation((0, -0.048, 0.39)); bake_xform(rid)
        bevel(rid, 0.006, 1); assign(rid, gold); parts.append(rid)
        # a red gem set near each ray tip, in a little gold bezel
        gx, gz = math.cos(a) * 0.5, math.sin(a) * 0.5
        bz = torus(0.036, 0.011, (gx, -0.04, gz), (math.pi / 2, 0, 0), 12, 5, "bezel"); assign(bz, gold); parts.append(bz)
        g = ico(0.034, (gx, -0.045, gz), 1, "gem"); g.scale = (1, 0.55, 1); bake_xform(g); assign(g, gem); parts.append(g)
    ring = lathe([(0.17, -0.02), (0.25, -0.02), (0.26, 0.0), (0.25, 0.02), (0.17, 0.02)], 48, "runering")
    ring.rotation_euler = (math.pi / 2, 0, 0); ring.location.y = -0.1; bake_xform(ring); assign(ring, rune); parts.append(ring)
    for R_ in (0.165, 0.262):
        t_ = torus(R_, 0.018, (0, -0.1, 0), (math.pi / 2, 0, 0), 48, 8, "trim"); assign(t_, gold); parts.append(t_)
    # four claws gripping the heart
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        pts = [(math.cos(a) * 0.17, -0.1, math.sin(a) * 0.17), (math.cos(a) * 0.15, -0.2, math.sin(a) * 0.15), (math.cos(a) * 0.075, -0.27, math.sin(a) * 0.075)]
        pr = tube_along(pts, 0.024, 6, "claw", radii=[1, 0.8, 0.4]); assign(pr, gold); parts.append(pr)
    # bail on the top point + a drop tip and dangling gem at the bottom
    bail = torus(0.07, 0.024, (0, 0, 0.64), (math.pi / 2, 0, 0), 20, 8, "bail"); assign(bail, gold); parts.append(bail)
    cap = lathe([(0.0, 0.6), (0.05, 0.58), (0.06, 0.55), (0.0, 0.5)], 8, "bailcap"); assign(cap, gold); parts.append(cap)
    tip = cone(0.04, 0.12, (0, 0, -0.65), (math.pi, 0, 0), 6, "droptip"); assign(tip, gold); parts.append(tip)
    dg = lathe([(0.0, -0.69), (0.045, -0.76), (0.05, -0.78), (0.0, -0.9)], 8, "dropgem"); flat(dg); assign(dg, gem); parts.append(dg)
    frame = join(parts, "R2Sigil"); smooth(frame, 35)
    h = lathe([(0.0, -0.2), (0.11, -0.03), (0.12, 0.0), (0.11, 0.03), (0.0, 0.2)], 8, "heart")
    h.rotation_euler = (math.pi / 2, 0, 0); h.location.y = -0.2; h.scale = (1, 0.75, 1); bake_xform(h)
    flat(h); assign(h, heart); h.name = "R2Heart"
    # --- the necklace: from the bail up over the chest, over the shoulders, round behind the neck, and back
    left = [(0.0, 0.0, 0.71), (-0.07, 0.03, 0.86), (-0.17, 0.08, 1.0), (-0.29, 0.13, 1.13), (-0.42, 0.22, 1.24),
            (-0.55, 0.45, 1.27), (-0.6, 0.72, 1.27), (-0.53, 0.98, 1.25), (-0.33, 1.17, 1.23)]
    back = [(0.0, 1.24, 1.22)]
    right = [(-x, y, z) for (x, y, z) in reversed(left)]
    ctrl = left + back + right
    pts = catmull(ctrl, per=10)
    ch = chain_along(pts, 0.11, 0.066, 0.014, "R2Necklace")
    assign(ch, mat_gold("r2_chain", base=(0.3, 0.16, 0.05), worn=(0.95, 0.72, 0.36)))
    smooth(ch, 35)
    return {"Sigil": (frame, 1024, True), "Heart": (h, 256, True), "Necklace": (ch, 512, False)}
