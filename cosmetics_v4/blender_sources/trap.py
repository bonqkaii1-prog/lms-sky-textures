"""Final Catch (ITrapped): a heavy rusted bear trap -- riveted cross base, two leaf springs with eyelets,
a round trigger pan with its dog, two serrated jaws on pivots (exported once; the second is the same mesh
turned 180 degrees), and a chain ending in a ring."""
from kit import *
KEY = "trap"
PREVIEW = {"main": {"elev": 32, "azim": -25, "dist": 0.85}}

def jaw(R, name):
    """half-ring flat bar standing up, teeth along the inner/top edge, pivot lugs at both ends"""
    n = 28; w, t = 0.07, 0.035
    pts = []
    for i in range(n + 1):
        a = math.pi * i / n
        pts.append((R * math.cos(a), 0, R * math.sin(a) * 0.95))
    bar = tube_along(pts, 1.0, 4, "bar", twist=0)
    # rebuild as a flat rectangular bar: scale a 4-sided tube section into w x t
    bm = bmesh.new(); bm.from_mesh(bar.data)
    for i, v in enumerate(bm.verts):
        c = Vector(pts[min(i // 4, n)])
        d = v.co - c
        d.y *= t; rad = Vector((c.x, 0, c.z)).normalized() if c.length > 1e-4 else Vector((1, 0, 0))
        dr = d.dot(rad); dy = d.y
        v.co = c + rad * (dr * w) + Vector((0, dy, 0))
    bm.to_mesh(bar.data); bm.free()
    parts = [bar]
    # teeth on the inside of the arch, pointing inward/down so the jaws interlock
    for i in range(1, 15):
        a = math.pi * i / 15
        c = Vector((R * math.cos(a), 0, R * math.sin(a) * 0.95))
        th = cone(0.038, 0.11, (0, 0, 0), n=4, name="tooth")
        th.matrix_world = Matrix.Translation(c - c.normalized() * 0.05) @ (c.normalized()).to_track_quat("-Z", "Y").to_matrix().to_4x4() @ Matrix.Translation((0, 0, 0.0))
        bake_xform(th); parts.append(th)
    for sx in (-1, 1):
        lug = cyl(0.045, 0.06, (sx * R, 0, 0), (math.pi / 2, 0, 0), 10, "lug"); parts.append(lug)
    o = join(parts, name); return o

def build():
    rust = mat_iron("trap_rust", base=(0.025, 0.018, 0.014), worn=(0.2, 0.18, 0.16), rust=(0.06, 0.018, 0.006), rust_k=0.5, rough=0.78, pits=0.6)
    dark = mat_iron("trap_steel", base=(0.025, 0.022, 0.02), worn=(0.3, 0.28, 0.26), rust=(0.06, 0.018, 0.006), rust_k=0.35)
    parts = []
    base = box((1.5, 0.16, 0.05), (0, 0, 0.025), name="arm"); bevel(base, 0.01, 1); parts.append(base)
    cross = box((0.16, 0.5, 0.05), (0, 0, 0.025), name="cross"); bevel(cross, 0.01, 1); parts.append(cross)
    for sx in (-1, 1):
        # pivot posts the jaws hinge on
        post = box((0.08, 0.2, 0.09), (sx * 0.42, 0, 0.07), name="post"); bevel(post, 0.008, 1); parts.append(post)
        pin = cyl(0.025, 0.24, (sx * 0.42, 0, 0.09), (math.pi / 2, 0, 0), 10, "pin"); parts.append(pin)
        # leaf spring: a long flat strip bent up from the base, eyelet round the jaw ends
        sp = []
        for i in range(12):
            t = i / 11
            sp.append((sx * (0.5 + 0.34 * t), 0, 0.06 + 0.12 * math.sin(t * math.pi * 0.8)))
        spring = tube_along(sp, 1.0, 4, "spring")
        bm = bmesh.new(); bm.from_mesh(spring.data)
        for i, v in enumerate(bm.verts):
            c = Vector(sp[min(i // 4, 11)]); d = v.co - c
            v.co = c + Vector((d.x * 0.03, d.y * 0.1, d.z * 0.03))
        bm.to_mesh(spring.data); bm.free(); parts.append(spring)
        eyelet = torus(0.08, 0.02, (sx * 0.5, 0, 0.1), (0, math.pi / 2, 0), 16, 6, "eyelet"); parts.append(eyelet)
        for k in range(3):
            parts.append(sphere(0.016, (sx * (0.2 + k * 0.4) * 0.9, 0.05, 0.055), 8, 5, "rivet"))
    pan = cyl(0.17, 0.03, (0, 0, 0.07), n=24, name="pan"); bevel(pan, 0.006, 1); parts.append(pan)
    dog = box((0.04, 0.26, 0.025), (0, -0.1, 0.095), (0.15, 0, 0), name="dog"); parts.append(dog)
    ring = torus(0.06, 0.018, (0, 0.27, 0.05), (0, 0, 0), 14, 6, "anchor"); parts.append(ring)
    b = join(parts, "TrapBase"); smooth(b, 35); assign(b, rust)
    j = jaw(0.42, "Jaw"); j.location.z = 0.09; bake_xform(j); smooth(j, 35); assign(j, dark)
    j2 = j.copy(); j2.data = j.data.copy(); bpy.context.collection.objects.link(j2)
    j2.matrix_world = Matrix.Translation((0, 0, 0.09)) @ Matrix.Rotation(math.radians(48), 4, "X") @ Matrix.Translation((0, 0, -0.09)) @ Matrix.Rotation(math.pi, 4, "Z")
    j.matrix_world = Matrix.Translation((0, 0, 0.09)) @ Matrix.Rotation(math.radians(-48), 4, "X") @ Matrix.Translation((0, 0, -0.09)); bake_xform(j)
    pts = [Vector((0, 0.3, 0.05)) + Vector((0.04 * math.sin(i), 0.13 * i, 0.03 * i)) for i in range(9)]
    ch = chain_along(pts, 0.13, 0.075, 0.016, "Chain")
    end = torus(0.1, 0.022, pts[-1] + Vector((0, 0.1, 0)), (math.pi / 2, 0, 0), 18, 6, "endring")
    ch = join([ch, end], "Chain"); assign(ch, rust)
    # only one jaw is exported (the other is the same mesh); keep j2 for the preview only
    PREVIEW["_extra_objs"] = [j2]
    j2.data.materials.clear(); j2.data.materials.append(dark)
    return {"TrapBase": (b, 1024, False), "Jaw": (j, 512, False), "Chain": (ch, 512, False)}
