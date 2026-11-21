"""Fractured Halo (Ellernate): a halo of black obsidian shattered into faceted shards with jagged breaks,
crimson veins burning through them, chips drifting in the gaps. Three shard groups so they can drift apart."""
from kit import *
KEY = "halo"
PREVIEW = {"main": {"elev": 25, "azim": -15, "dist": 0.8}, "extra": [{"elev": 70, "azim": 0, "dist": 0.85}]}

def shard(a0, a1, R, w, h, rng, name):
    """arc segment with a lens/diamond cross-section and jagged broken ends"""
    n = max(6, int((a1 - a0) / math.radians(5)))
    prof = [(w / 2, 0), (w * 0.3, h / 2), (-w * 0.25, h * 0.42), (-w / 2, 0.0), (-w * 0.25, -h * 0.42), (w * 0.3, -h / 2)]   # faceted hexagonal crystal section (radial, z)
    verts, faces = [], []
    for i in range(n + 1):
        t = i / n; a = a0 + (a1 - a0) * t
        end = min(t, 1 - t) * n
        k = 1.0 if end > 1.5 else 0.55 + 0.3 * end
        for (dr, dz) in prof:
            jag = rng.uniform(-0.03, 0.03) if end < 1 else 0
            r = R + dr * k + jag
            verts.append((r * math.cos(a), r * math.sin(a), dz * k + (rng.uniform(-0.03, 0.03) if end < 1 else 0)))
    m = len(prof)
    for i in range(n):
        for j in range(m):
            jj = (j + 1) % m
            faces.append((i * m + j, i * m + jj, (i + 1) * m + jj, (i + 1) * m + j))
    faces.append(tuple(range(m))[::-1]); faces.append(tuple(range(n * m, n * m + m)))
    o = from_pydata(verts, faces, name)
    sel([o]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    # break-face detail: subdivide and roughen the ends a touch
    displace(o, 0.012, 0.15)
    return o

def build():
    obs = mat_obsidian("halo_obsidian", vein=(1.0, 0.02, 0.04), vein_scale=2.6, vein_w=0.022, k=6)
    rng = random.Random(5)
    R = 0.95
    groups = [[], [], []]
    a = 0.0; i = 0
    while a < TAU - 0.15:
        span = rng.uniform(math.radians(28), math.radians(44))
        a1 = min(a + span, TAU - 0.12)
        s = shard(a, a1, R + rng.uniform(-0.03, 0.03), 0.2, 0.15, rng, f"shard{i}")
        # crystalline thorns breaking out of some shards, raking outward and up
        thorns = [s]
        for _ in range(rng.randint(1, 3)):
            ta = rng.uniform(a + 0.08, a1 - 0.08); tl = rng.uniform(0.14, 0.3)
            th = cone(0.045, tl, (0, 0, 0), n=5, name="thorn")
            th.matrix_world = Matrix.Rotation(ta, 4, "Z") @ Matrix.Translation((R + 0.06, 0, 0.03)) @ Matrix.Rotation(math.radians(rng.uniform(25, 70)), 4, "Y") @ Matrix.Translation((0, 0, tl / 2))
            bake_xform(th); thorns.append(th)
        s = join(thorns, f"shard{i}")
        s.rotation_euler = (rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06), 0); bake_xform(s)
        groups[i % 3].append(s)
        a = a1 + rng.uniform(math.radians(4), math.radians(9)); i += 1
    # chips in the gaps
    chips = []
    for k in range(16):
        aa = rng.uniform(0, TAU); r = R + rng.uniform(-0.12, 0.12)
        c = ico(rng.uniform(0.02, 0.045), (r * math.cos(aa), r * math.sin(aa), rng.uniform(-0.09, 0.09)), 1, "chip")
        c.scale = (1, rng.uniform(0.5, 1), rng.uniform(1.2, 2)); c.rotation_euler = (rng.uniform(0, 3), rng.uniform(0, 3), rng.uniform(0, 3)); bake_xform(c)
        chips.append(c)
    out = {}
    for gi, g in enumerate(groups):
        o = join(g, f"Shards{gi + 1}"); flat(o); assign(o, obs); out[f"Shards{gi + 1}"] = (o, 512, True)
    ch = join(chips, "Chips"); flat(ch); assign(ch, obs); out["Chips"] = (ch, 256, True)
    return out
