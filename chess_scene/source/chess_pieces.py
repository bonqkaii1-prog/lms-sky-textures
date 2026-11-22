"""Staunton chess set for the cabin chess scene: boxwood (white) and ebony (black) pieces, each turned on a lathe
(plinth, cove, stem, collar, head), with a green baize pad underneath. Rook crenellations and the bishop's mitre
slit are boolean cuts; the knight is a carved horse head (side silhouette, extruded, tapered and smoothed) with
ears, eyes, flared nostrils and a carved mane. One object per piece type and colour; base sits at z = 0."""
from kit import *
KEY = "chess"
PREVIEW = {"main": {"elev": 16, "azim": -20, "dist": 0.95}, "extra": [{"elev": 10, "azim": -90, "dist": 0.3, "target": None}]}

SQ = 0.21  # board square (studs)


def ball(cz, r, a0=-80, a1=90, n=10, squash=1.0):
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        out.append((max(r * math.cos(a), 0.0) if i < n or a1 < 90 else 0.0, cz + r * math.sin(a) * squash))
    return out


def plinth(R, h=0.05):
    """stepped Staunton base: foot, bead, cove, second bead, flowing into the stem"""
    return [(0.0, 0.0), (R, 0.0), (R, 0.10 * h * 1.6), (0.985 * R, 0.24 * h), (0.93 * R, 0.30 * h), (0.80 * R, 0.36 * h),
            (0.78 * R, 0.44 * h), (0.86 * R, 0.52 * h), (0.86 * R, 0.60 * h), (0.74 * R, 0.68 * h), (0.62 * R, 0.80 * h), (0.54 * R, h)]


def felt(R):
    d = cyl(R * 0.93, 0.006, (0, 0, 0.0025), n=40, name="felt")
    return d


def profile_pawn(R=0.056):
    p = plinth(R, 0.045)
    p += [(0.44 * R, 0.065), (0.37 * R, 0.085), (0.33 * R, 0.098), (0.60 * R, 0.102), (0.66 * R, 0.107), (0.62 * R, 0.112), (0.34 * R, 0.116), (0.29 * R, 0.121)]
    p += ball(0.146, 0.029, -62, 90, 14)
    return p


def profile_rook(R=0.064):
    p = plinth(R, 0.05)
    p += [(0.60 * R, 0.07), (0.56 * R, 0.10), (0.56 * R, 0.13), (0.60 * R, 0.146), (0.80 * R, 0.152), (0.84 * R, 0.158), (0.80 * R, 0.163),
          (0.70 * R, 0.166), (0.78 * R, 0.170), (0.80 * R, 0.176), (0.80 * R, 0.205), (0.62 * R, 0.205), (0.60 * R, 0.190), (0.0, 0.190)]
    return p


def profile_bishop(R=0.064):
    p = plinth(R, 0.05)
    p += [(0.46 * R, 0.075), (0.36 * R, 0.11), (0.31 * R, 0.14), (0.30 * R, 0.150), (0.62 * R, 0.155), (0.66 * R, 0.161), (0.62 * R, 0.166),
          (0.36 * R, 0.171), (0.42 * R, 0.178), (0.55 * R, 0.193), (0.60 * R, 0.207), (0.57 * R, 0.222), (0.46 * R, 0.236), (0.30 * R, 0.246), (0.14 * R, 0.251)]
    p += ball(0.262, 0.0125, -55, 90, 8)
    return p


def profile_queen(R=0.072):
    p = plinth(R, 0.055)
    p += [(0.46 * R, 0.08), (0.36 * R, 0.12), (0.29 * R, 0.16), (0.28 * R, 0.180), (0.58 * R, 0.185), (0.63 * R, 0.191), (0.58 * R, 0.197),
          (0.32 * R, 0.201), (0.36 * R, 0.207), (0.52 * R, 0.228), (0.66 * R, 0.250), (0.72 * R, 0.262), (0.70 * R, 0.268), (0.52 * R, 0.266),
          (0.36 * R, 0.270), (0.26 * R, 0.282), (0.10 * R, 0.288)]
    p += ball(0.298, 0.0135, -50, 90, 8)
    return p


def profile_king(R=0.075):
    p = plinth(R, 0.058)
    p += [(0.46 * R, 0.085), (0.35 * R, 0.13), (0.28 * R, 0.18), (0.27 * R, 0.198), (0.58 * R, 0.203), (0.63 * R, 0.210), (0.58 * R, 0.217),
          (0.32 * R, 0.221), (0.36 * R, 0.227), (0.52 * R, 0.250), (0.64 * R, 0.272), (0.66 * R, 0.283), (0.58 * R, 0.288), (0.44 * R, 0.297),
          (0.24 * R, 0.305), (0.10 * R, 0.309), (0.0, 0.310)]
    return p


def mk_lathe(prof, name, n=40):
    o = lathe(prof, n, name)
    return o


def knight_head(h=0.185, z0=0.055, w=0.074):
    # side silhouette, facing +X, normalised 0..1 in height
    S = [(-0.34, 0.0), (-0.37, 0.18), (-0.38, 0.36), (-0.35, 0.54), (-0.29, 0.69), (-0.21, 0.81), (-0.13, 0.89), (-0.06, 0.93),
         (0.03, 0.92), (0.13, 0.86), (0.25, 0.75), (0.36, 0.62), (0.46, 0.50), (0.53, 0.42), (0.555, 0.36), (0.545, 0.31),
         (0.50, 0.275), (0.42, 0.265), (0.33, 0.285), (0.24, 0.32), (0.16, 0.33), (0.10, 0.28), (0.09, 0.18), (0.14, 0.08), (0.22, 0.0)]
    verts = [(x * h, 0.0, z0 + z * h) for x, z in S]
    o = from_pydata(verts, [tuple(range(len(verts)))], "khead")
    sel([o]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": (0, w, 0)})
    bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    for v in o.data.vertices: v.co.y -= w / 2
    # taper: narrower muzzle and crest, fuller cheeks / neck base
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs(e.verts[0].co.y - e.verts[1].co.y) > w * 0.5], cuts=2, use_grid_fill=True)
    for v in bm.verts:
        x = v.co.x / h; z = (v.co.z - z0) / h
        k = 1.0
        if x > 0.25: k *= 1 - 0.55 * min(1, (x - 0.25) / 0.33)          # muzzle narrows
        if z > 0.78: k *= 1 - 0.45 * min(1, (z - 0.78) / 0.18)          # crest narrows to the ears
        if z < 0.2: k *= 1 + 0.25 * (0.2 - z) / 0.2                    # chest widens into the base
        v.co.y *= k
    bm.to_mesh(o.data); bm.free()
    m = o.modifiers.new("bev", "BEVEL"); m.width = 0.006; m.segments = 2
    subsurf(o, 1); apply_mods(o)
    parts = [o]
    for sy in (-1, 1):
        ear = cone(0.011, 0.034, (0, 0, 0), n=10, name="ear")
        ear.rotation_euler = (sy * 0.25, -0.35, 0); ear.location = (-0.02 * h / 0.185, sy * 0.012, z0 + 0.93 * h); bake_xform(ear)
        parts.append(ear)
        eye = sphere(0.0065, (0.17 * h, sy * w * 0.36, z0 + 0.70 * h), 10, 6, "eye"); parts.append(eye)
        brow = torus(0.008, 0.0022, (0.17 * h, sy * w * 0.355, z0 + 0.705 * h), (math.pi / 2, 0, 0), 12, 4, "brow"); parts.append(brow)
        nos = torus(0.006, 0.002, (0.50 * h, sy * w * 0.17, z0 + 0.40 * h), (math.pi / 2, 0, 0), 10, 4, "nostril"); parts.append(nos)
    # mane: carved locks running down the back of the neck
    for i in range(9):
        t = i / 8
        x = (-0.30 + 0.20 * t * t - 0.07 * t) * h; z = z0 + (0.80 - 0.62 * t) * h
        lock = box((0.018, 0.022 - 0.006 * t, 0.026), (x - 0.04 * h, 0, z), (0, math.radians(-40 + 25 * t), 0), "lock")
        bevel(lock, 0.004, 2, 30); apply_mods(lock); parts.append(lock)
    return join(parts, "khead")


def wood_piece(name, light):
    if light:
        mat = mat_wood(name, base=(0.80, 0.58, 0.32), dark=(0.64, 0.43, 0.21), scale=7.0)
        mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.32
    else:
        mat = mat_wood(name, base=(0.042, 0.026, 0.019), dark=(0.016, 0.010, 0.008), scale=7.0)
        mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.22
    try:
        mat.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value = 0.6
        mat.node_tree.nodes["Principled BSDF"].inputs["Coat Roughness"].default_value = 0.12
    except Exception:
        pass
    return mat


def build():
    baize = mat_cloth("baize", base=(0.03, 0.16, 0.06), dirt=(0.01, 0.06, 0.02), scale=6.0)
    out = {}
    for light in (True, False):
        mat = wood_piece("box" if light else "ebony", light)
        tag = "W" if light else "B"
        made = {}
        made["Pawn"] = (mk_lathe(profile_pawn(), "pawn"), 0.056)
        rook = mk_lathe(profile_rook(), "rook")
        for i in range(3):
            a = i / 3 * math.pi + math.pi / 6
            c = box((0.16, 0.017, 0.03), (0, 0, 0.207), (0, 0, a), "cut")
            b = rook.modifiers.new("bool", "BOOLEAN"); b.operation = "DIFFERENCE"; b.object = c; b.solver = "EXACT"
            apply_mods(rook); bpy.data.objects.remove(c)
        made["Rook"] = (rook, 0.064)
        bish = mk_lathe(profile_bishop(), "bishop")
        slit = box((0.06, 0.007, 0.03), (0.016, 0, 0.222), (0, math.radians(-38), 0), "slit")
        b = bish.modifiers.new("bool", "BOOLEAN"); b.operation = "DIFFERENCE"; b.object = slit; b.solver = "EXACT"
        apply_mods(bish); bpy.data.objects.remove(slit)
        made["Bishop"] = (bish, 0.064)
        q = mk_lathe(profile_queen(), "queen")
        qp = [q]
        for i in range(10):
            a = i / 10 * TAU
            qp.append(sphere(0.0085, (math.cos(a) * 0.70 * 0.072, math.sin(a) * 0.70 * 0.072, 0.271), 10, 6, "qball"))
        made["Queen"] = (join(qp, "queen"), 0.072)
        k = mk_lathe(profile_king(), "king")
        kp = [k, box((0.013, 0.013, 0.052), (0, 0, 0.334), name="kv"), box((0.04, 0.012, 0.012), (0, 0, 0.342), name="kh")]
        for c in kp[1:]: bevel(c, 0.0025, 2, 30); apply_mods(c)
        made["King"] = (join(kp, "king"), 0.075)
        kb = mk_lathe(plinth(0.064, 0.05) + [(0.50 * 0.064, 0.058), (0.0, 0.06)], "kbase")
        made["Knight"] = (join([kb, knight_head()], "knight"), 0.064)
        for nm, (o, R) in made.items():
            smooth(o, 32)
            assign(o, mat)
            f = felt(R); f.data.materials.append(baize)
            for i, ms in enumerate(o.data.materials): pass
            o = join([o, f], f"CS_{nm}{tag}")
            # spread the previews out on a grid
            out[f"{nm}{tag}"] = (o, 256, False)
    xs = {"Pawn": 0, "Rook": 1, "Knight": 2, "Bishop": 3, "Queen": 4, "King": 5}
    for key, (o, _, _) in out.items():
        o.location = (xs[key[:-1]] * 0.2, 0 if key.endswith("W") else 0.22, 0)
    PREVIEW["extra"][0]["target"] = Vector((0.4, 0.0, 0.13))
    return out


def before_bake(pieces):
    for o, _, _ in pieces.values():
        o.location = (0, 0, 0)
