"""Hacker's Arsenal (C00lkid): a pair of black-steel daggers (one mesh, crossed in Roblox) -- a broad
leaf blade with a serrated spine, a fuller, a burning red edge, a horned crossguard, a grip wrapped and
etched with corrupted red code, and a glitch-cube pommel; plus an X harness with two sheath loops and buckles."""
from kit import *
import runes
KEY = "daggers"
PREVIEW = {"main": {"elev": 8, "azim": -25, "dist": 0.85}, "extra": [{"elev": 8, "azim": -10, "dist": 0.4}]}
RED = (1.0, 0.05, 0.03)

def build():
    runes.code_sheet(f"{OUT}/code_red.png", seed=31, rows=14, cols=18)
    steel = mat_iron("dag_steel", base=(0.025, 0.023, 0.025), worn=(0.35, 0.33, 0.33), rust_k=0.02, rough=0.35, metal=1.0, pits=0.15)
    edge = mat_glow("dag_edge", col=RED, base=(0.3, 0.0, 0.0), k=10)
    grip = mat_iron("dag_grip", rune=f"{OUT}/code_red.png", rune_scale=2.6, rune_col=RED, rune_k=9, base=(0.012, 0.01, 0.012), rust_k=0.0, metal=0.2, rough=0.7)
    L = 1.35
    # blade profile (x across, z along). leaf shape: widest a third of the way up
    side = []
    for i in range(14):
        t = i / 13
        w = 0.17 * math.sin(math.pi * min(1, t * 1.25 + 0.05)) ** 0.7 * (1 - t ** 3) + 0.01
        side.append((w, t * L))
    right = [(w, z) for w, z in side]
    left = []
    for i, (w, z) in enumerate(side):          # serrated spine on the left side
        ww = w * 0.8 + (0.06 if i % 2 == 0 and 2 < i < 11 else 0)
        left.append((-ww, z))
    prof = right + list(reversed(left))[1:]
    def thick(x, z): return 0.035 * (1 - z / L * 0.7) * (1 - min(1, abs(x) / 0.2) ** 2) + 0.004
    vf = [(x, -thick(x, z), z) for x, z in prof]; vb = [(x, thick(x, z), z) for x, z in prof]
    m = len(prof)
    faces = [tuple(range(m)), tuple(range(m, 2 * m))[::-1]] + [(i, (i + 1) % m, m + (i + 1) % m, m + i) for i in range(m)]
    blade = from_pydata(vf + vb, faces, "blade")
    sel([blade]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    bevel(blade, 0.004, 1, 20); assign(blade, steel)
    # fuller: a groove strip along the centre (dark recessed bar)
    fuller = box((0.03, 0.074, L * 0.55), (0.0, 0, L * 0.32), name="fuller"); assign(fuller, steel)
    # burning edge: a thin emissive strip along the cutting side
    ep = [(w + 0.004, 0, z) for w, z in side]
    ed = tube_along(ep, 0.008, 4, "edge", radii=[0.5] + [1] * 11 + [0.6, 0.2]); ed.scale = (1, 0.6, 1); bake_xform(ed); assign(ed, edge)
    # crossguard: horned, curling forward like a C
    gpts = []
    for i in range(15):
        t = (i / 14) * 2 - 1
        gpts.append((t * 0.34, -0.06 * t * t, -0.03 + 0.12 * abs(t) ** 3))
    guard = tube_along(gpts, 0.04, 8, "guard", radii=[0.3, 0.6, 0.85, 1, 1, 1, 1.1, 1.2, 1.1, 1, 1, 1, 0.85, 0.6, 0.3]); assign(guard, steel)
    gem = ico(0.045, (0, -0.04, -0.02), 1, "gem"); assign(gem, edge)
    # grip with raised wraps, etched code
    g = lathe([(0.04, -0.06), (0.05, -0.08), (0.046, -0.15), (0.052, -0.25), (0.046, -0.35), (0.05, -0.45), (0.04, -0.47)], 12, "grip"); assign(g, grip)
    wr = tube_along(helix((0, 0, -0.1), (0, 0, -0.43), 0.05, 5, n=140), 0.009, 5, "wrap"); assign(wr, steel)
    pom = box((0.1, 0.1, 0.1), (0, 0, -0.53), (0.6, 0.6, 0.2), name="pommel"); bevel(pom, 0.01, 1); assign(pom, steel)
    pc = []
    rng = random.Random(2)
    for i in range(6):
        s = rng.uniform(0.02, 0.04)
        c = box((s, s, s), (rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08), -0.53 + rng.uniform(-0.09, 0.09)), (rng.random(), rng.random(), rng.random()), "glitch")
        assign(c, edge); pc.append(c)
    dagger = join([blade, fuller, ed, guard, gem, g, wr, pom] + pc, "Dagger"); smooth(dagger, 30)
    # harness: two crossed leather straps, a centre ring plate, buckles and two sheath loops
    leather = mat_leather("harness", base=(0.03, 0.013, 0.007), dark=(0.006, 0.003, 0.002), scale=1.5, rough=0.55)
    hw = mat_iron("harness_hw", base=(0.05, 0.045, 0.045), worn=(0.45, 0.43, 0.42), rust_k=0.05, metal=1.0, rough=0.35)
    hp = []
    for s in (-1, 1):
        st = box((0.14, 0.035, 2.3), (0, 0.6, 0), (0, s * math.radians(38), 0), name="strap"); bevel(st, 0.008, 1); assign(st, leather); hp.append(st)
        lp = box((0.24, 0.07, 0.3), (s * 0.4, 0.62, s * -0.55), (0, s * math.radians(38), 0), name="loop"); bevel(lp, 0.015, 2); assign(lp, leather); hp.append(lp)
        bk = torus(0.07, 0.012, (s * -0.45, 0.58, 0.6), (math.pi / 2, s * math.radians(38), 0), 4, 4, "buckle"); assign(bk, hw); hp.append(bk)
    plate = cyl(0.17, 0.04, (0, 0.56, 0), (math.pi / 2, 0, 0), 8, "plate"); bevel(plate, 0.01, 1); assign(plate, hw); hp.append(plate)
    skull = ico(0.08, (0, 0.52, 0.02), 2, "stud"); assign(skull, edge); hp.append(skull)
    harness = join(hp, "Harness"); smooth(harness, 30)
    dagger.location.x = -0.8; bake_xform(dagger)
    return {"Dagger": (dagger, 1024, True), "Harness": (harness, 1024, True)}
