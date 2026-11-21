"""Corrupted Crown (1x1x1x1): blackened iron circlet split at the front, gothic blade spikes (two snapped),
riveted plaques of glowing green code, a green gem in a claw setting, and voxel corruption erupting from the split."""
from kit import *
import runes
KEY = "crown"
PREVIEW = {"main": {"elev": 22, "azim": -20, "dist": 0.9}, "extra": [{"elev": 55, "azim": 160, "dist": 0.95}]}
GREEN = (0.25, 1.0, 0.35)

def build():
    runes.code_sheet(f"{OUT}/code_green.png", seed=11, rows=10, cols=14)
    DK = dict(base=(0.018, 0.02, 0.019), worn=(0.22, 0.24, 0.22), rust=(0.03, 0.06, 0.03), rust_k=0.1)
    iron = mat_iron("crown_iron", pits=0.45, **DK)
    plaque = mat_iron("crown_code", rune=f"{OUT}/code_green.png", rune_scale=3.2, rune_col=GREEN, rune_k=16, **DK)
    gold = mat_iron("crown_trim", base=(0.06, 0.055, 0.04), worn=(0.4, 0.38, 0.3), rust=(0.05, 0.08, 0.04), rust_k=0.15, metal=1.0, rough=0.4)
    gem = mat_glow("crown_gem", col=GREEN, base=(0.02, 0.15, 0.04), k=12, crack=6)
    vox = mat_glow("crown_vox", col=GREEN, base=(0.01, 0.05, 0.015), k=7, crack=10)
    body = []
    R, H = 0.64, 0.3
    gap = math.radians(26)                      # the split at the front (-Y)
    n = 64
    # band: thick lathe profile, then cut the split by deleting verts in the gap
    band = lathe([(R, 0.0), (R + 0.075, 0.0), (R + 0.09, 0.03), (R + 0.06, 0.06), (R + 0.06, H - 0.06), (R + 0.095, H - 0.03), (R + 0.08, H), (R, H)], n, "band")
    bm = bmesh.new(); bm.from_mesh(band.data)
    kill = [v for v in bm.verts if abs(math.atan2(v.co.x, -v.co.y)) < gap / 2]
    bmesh.ops.delete(bm, geom=kill, context="VERTS")
    # jag the split edges
    rng = random.Random(4)
    for v in bm.verts:
        a = abs(math.atan2(v.co.x, -v.co.y))
        if a < gap / 2 + 0.12:
            v.co.x += rng.uniform(-0.03, 0.03); v.co.z += rng.uniform(-0.02, 0.02)
    # cap only the two cut ends of the split (not the crown's inner/outer openings)
    bnd = [e for e in bm.edges if e.is_boundary and all(abs(math.atan2(v.co.x, -v.co.y)) < gap / 2 + 0.2 for v in e.verts)]
    bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
    bm.to_mesh(band.data); bm.free()
    bevel(band, 0.006, 1, 40); assign(band, iron); body.append(band)
    # plaques + studs
    for i in range(8):
        a = (i + 0.5) / 8 * TAU
        if abs((a + math.pi) % TAU - math.pi - 0) < 0.01: pass
        ang_from_front = abs(math.atan2(math.sin(a), -math.cos(a)))
        if ang_from_front < gap: continue
        p = box((0.2, 0.03, 0.16), (0, 0, 0), name="plaque"); bevel(p, 0.006, 1)
        p.matrix_world = Matrix.Rotation(a, 4, "Z") @ Matrix.Translation((0, -(R + 0.075), H / 2)); bake_xform(p)
        assign(p, plaque); body.append(p)
        for dz in (-1, 1):
            s = sphere(0.016, (0, 0, 0), 8, 5, "stud"); s.matrix_world = Matrix.Rotation(a + math.radians(12.5), 4, "Z") @ Matrix.Translation((0, -(R + 0.075), H / 2 + dz * 0.07)); bake_xform(s); assign(s, gold); body.append(s)
    # spikes: flat diamond blades leaning out; tall/short alternating; two snapped
    for i in range(12):
        a = i / 12 * TAU
        front = abs(math.atan2(math.sin(a), -math.cos(a)))
        if front < gap * 0.9: continue
        tall = 0.62 if i % 2 == 0 else 0.36
        if i in (3, 8): tall *= 0.45                # snapped
        w = 0.15 if i % 2 == 0 else 0.11
        prof = [(0, 0, 0), (w / 2, 0, tall * 0.25), (0, 0, tall), (-w / 2, 0, tall * 0.25)]
        verts = []
        for x, _, z in prof:
            verts += [(x, -0.03, z), (x, 0.03, z)]
        verts = [(x, y * (1 - z / (tall + 1e-3) * 0.9), z) for x, y, z in verts]
        faces = [(0, 2, 4, 6), (1, 7, 5, 3), (0, 1, 3, 2), (2, 3, 5, 4), (4, 5, 7, 6), (6, 7, 1, 0)]
        sp = from_pydata(verts, faces, "spike")
        if i in (3, 8):                             # jagged snapped top
            bm = bmesh.new(); bm.from_mesh(sp.data)
            for v in bm.verts:
                if v.co.z > tall * 0.9: v.co.z -= 0.04; v.co.x += 0.03
            bm.to_mesh(sp.data); bm.free()
        bevel(sp, 0.004, 1, 30)
        sp.matrix_world = Matrix.Rotation(a, 4, "Z") @ Matrix.Translation((0, -(R + 0.05), H - 0.02)) @ Matrix.Rotation(math.radians(-12), 4, "X")
        bake_xform(sp); assign(sp, iron); body.append(sp)
        cap = cyl(0.035, 0.03, (0, 0, 0), n=8, name="cap"); cap.matrix_world = Matrix.Rotation(a, 4, "Z") @ Matrix.Translation((0, -(R + 0.05), H - 0.01)); bake_xform(cap); assign(cap, gold); body.append(cap)
    # front: claw setting holding the gem at the edge of the split
    gx = math.radians(32)
    setting = []
    gpos = Matrix.Rotation(gx, 4, "Z") @ Vector((0, -(R + 0.12), H * 0.55))
    for k in range(4):
        cl = cone(0.02, 0.12, (0, 0, 0), n=4, name="claw")
        cl.matrix_world = Matrix.Translation(gpos) @ Matrix.Rotation(gx, 4, "Z") @ Matrix.Rotation(k * math.pi / 2, 4, "Y") @ Matrix.Translation((0, 0, 0.07)) @ Matrix.Rotation(math.radians(160), 4, "X")
        bake_xform(cl); assign(cl, gold); body.append(cl)
    crown = join(body, "CrownBody")
    smooth(crown, 32)
    g = ico(0.075, gpos, 1, "gem"); g.scale = (1, 0.7, 1.35); g.rotation_euler = (0, 0, gx); bake_xform(g)
    # voxel corruption erupting from the split, climbing like a broken spike
    rng = random.Random(9); cubes = [g]
    for i in range(30):
        t = rng.random() ** 0.8
        z = H * 0.2 + t * 0.85
        spread = 0.04 + 0.1 * t
        a = rng.uniform(-gap * 0.6, gap * 0.6) + rng.uniform(-0.1, 0.1) * t
        r = R + 0.05 + rng.uniform(-0.03, 0.06) + rng.uniform(0, spread) * 0.6
        s = rng.uniform(0.04, 0.11) * (1.15 - t * 0.6)
        c = box((s, s, s), (math.sin(a) * r + rng.uniform(-spread, spread) * 0.5, -math.cos(a) * r, z), (rng.uniform(0, 0.6), rng.uniform(0, 0.6), rng.uniform(0, 0.6)), "vox")
        bevel(c, s * 0.06, 1); cubes.append(c)
    corrupt = join(cubes, "Corruption")
    for p in corrupt.data.polygons: p.use_smooth = False
    assign(corrupt, vox); corrupt.data.materials.append(gem)
    return {"CrownBody": (crown, 1024, True), "Corruption": (corrupt, 512, True)}
