"""Damned Tail (Guest 666): one hide segment (tapered, scaled per joint in Roblox) with overlapping blackened
dorsal plates, a band of scales at the joint and small side spines; and a barbed obsidian arrowhead tip."""
from kit import *
KEY = "tail"
PREVIEW = {"main": {"elev": 20, "azim": -40, "dist": 0.9}}

def build():
    hide = mat_leather("tail_hide", base=(0.16, 0.015, 0.02), dark=(0.03, 0.002, 0.005), scale=2.2, rough=0.55)
    plate = mat_obsidian("tail_plate", vein=(1.0, 0.04, 0.04), vein_scale=5, vein_w=0.006, k=2.5, base=(0.02, 0.01, 0.012))
    L, r0, r1 = 0.5, 0.135, 0.112
    # hide body along +X, slight bulge in the middle, a waist at the joint
    prof = []
    for i in range(9):
        t = i / 8
        r = r0 + (r1 - r0) * t
        r *= 1 + 0.08 * math.sin(t * math.pi) - (0.1 if i in (0, 8) else 0)
        prof.append((r, -L / 2 + L * t))
    body = lathe(prof, 20, "body"); body.rotation_euler = (0, math.pi / 2, 0); bake_xform(body)
    body.scale = (1, 1, 0.88); bake_xform(body); smooth(body, 60); assign(body, hide)
    parts = [body]
    # three overlapping dorsal plates along the top (+Z), each a curved shell with a centre ridge
    for k in range(3):
        x = -L / 2 + 0.1 + k * 0.15
        pl = sphere(1, (0, 0, 0), 14, 8, "plate"); pl.scale = (0.12, r0 * 0.95, 0.05); bake_xform(pl)
        bm = bmesh.new(); bm.from_mesh(pl.data)
        for v in bm.verts:
            if v.co.z < 0: v.co.z *= 0.2
            v.co.z += -abs(v.co.y) * 0.35 + 0.012
            v.co.x += -v.co.z * 0.6
        bm.to_mesh(pl.data); bm.free()
        pl.location = (x, 0, r0 * 0.82 - k * 0.008); pl.rotation_euler = (0, math.radians(-14), 0); bake_xform(pl)
        assign(pl, plate); parts.append(pl)
        sp = cone(0.022, 0.08, (x + 0.02, 0, r0 * 0.82 + 0.06), (0, math.radians(-50), 0), 5, "dorsal"); assign(sp, plate); parts.append(sp)
    # scale band at the joint end + side spines
    for i in range(14):
        a = i / 14 * TAU
        sc = sphere(1, (0, 0, 0), 8, 5, "scale"); sc.scale = (0.04, 0.03, 0.012); bake_xform(sc)
        sc.matrix_world = Matrix.Translation((L / 2 - 0.03, 0, 0)) @ Matrix.Rotation(a, 4, "X") @ Matrix.Translation((0, 0, r1 * 0.98)) @ Matrix.Rotation(math.radians(-20), 4, "Y")
        bake_xform(sc); assign(sc, plate); parts.append(sc)
    for sy in (-1, 1):
        sp = cone(0.018, 0.07, (0.05, sy * r0 * 0.95, 0.02), (sy * math.radians(-80), math.radians(-30), 0), 5, "side"); assign(sp, plate); parts.append(sp)
    seg = join(parts, "TailSeg")
    # tip: barbed spade arrowhead with a ribbed socket
    tipm = mat_obsidian("tail_tip", vein=(1.0, 0.05, 0.03), vein_scale=3.2, vein_w=0.025, k=8)
    sock = lathe([(0.1, -0.12), (0.115, -0.08), (0.1, -0.06), (0.115, -0.03), (0.1, -0.01), (0.07, 0.04)], 12, "socket")
    sock.rotation_euler = (0, math.pi / 2, 0); bake_xform(sock)
    # spade: a flat lozenge with two backward barbs, thick through the middle
    out = [(0.04, 0), (0.18, 0.09), (0.12, 0.2), (0.26, 0.19), (0.56, 0.0)]
    pts2 = out + [(x, -y) for x, y in reversed(out[1:-1])]
    verts = [(x, 0, y) for x, y in pts2]
    th = 0.06
    vtop = [(x, th * (1 - abs(z) / 0.2) * (1 - x / 0.62) + 0.004, z) for x, _, z in verts]
    vbot = [(x, -yy, z) for x, yy, z in vtop]
    m = len(verts)
    faces = [tuple(range(m)), tuple(range(m, 2 * m))[::-1]] + [(i, (i + 1) % m, m + (i + 1) % m, m + i) for i in range(m)]
    spade = from_pydata(vtop + vbot, faces, "spade")
    sel([spade]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    spade.rotation_euler = (math.pi / 2, 0, 0); bake_xform(spade)
    # ridge down the centre of the spade
    ridge = tube_along([(0.06, 0, 0), (0.3, 0, 0), (0.52, 0, 0)], 0.02, 4, "ridge", radii=[1, 0.8, 0.2]); ridge.scale = (1, 1, 2.2); bake_xform(ridge)
    tip = join([sock, spade, ridge], "TailTip"); flat(tip); assign(tip, tipm)
    tip.location.x = 0.62; bake_xform(tip)
    return {"TailSeg": (seg, 512, True), "TailTip": (tip, 512, True)}
