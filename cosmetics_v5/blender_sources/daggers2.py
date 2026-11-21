"""Hacker's Arsenal v2 (C00lkid): two big crimson combat blades -- a long, broad, hooked blade of red-lacquered
steel with chipped edges, a saw-toothed spine, glowing red code etched down the flat, a white-hot red edge,
a spiked red guard with a glowing core, a black grip under red wraps and a jagged glitch-cube pommel --
and a red-and-black X harness: spiked shoulder plates, a glowing skull-visor emblem with circuit traces,
studded straps and two blade loops."""
from kit import *
import runes
KEY = "daggers2"
PREVIEW = {"main": {"elev": 8, "azim": -25, "dist": 1.0}, "extra": [{"elev": 8, "azim": -10, "dist": 0.5}]}
RED = (1.0, 0.04, 0.03)


def build():
    runes.code_sheet(f"{OUT}/code_red.png", seed=31, rows=14, cols=18)
    paint = mat_paint("k2_paint", paint=(0.2, 0.006, 0.005), metal_col=(0.4, 0.37, 0.36), chip=0.3, dirt=(0.02, 0.003, 0.003))
    code = mat_iron("k2_code", rune=f"{OUT}/code_red.png", rune_scale=2.2, rune_col=RED, rune_k=16, base=(0.16, 0.01, 0.008),
                    worn=(0.5, 0.2, 0.18), rust_k=0.0, metal=0.9, rough=0.32, pits=0.1)
    edge = mat_glow("k2_edge", col=RED, base=(0.6, 0.02, 0.0), k=14)
    steel = mat_iron("k2_steel", base=(0.03, 0.026, 0.028), worn=(0.45, 0.42, 0.42), rust_k=0.0, rough=0.35, metal=1.0, pits=0.1)
    wrapm = mat_leather("k2_wrap", base=(0.3, 0.015, 0.01), dark=(0.06, 0.003, 0.002), scale=2.0, rough=0.5)
    L = 1.75
    side = []
    for i in range(18):
        t = i / 17
        w = 0.24 * math.sin(math.pi * min(1, t * 1.15 + 0.08)) ** 0.6 * (1 - t ** 2.5) + 0.012
        side.append((w, t * L))
    right = list(side)
    left = []
    for i, (w, z) in enumerate(side):                       # saw-toothed spine
        ww = w * 0.55 + (0.085 if i % 2 == 0 and 2 < i < 14 else 0.0)
        left.append((-ww, z))
    # hooked, upswept tip: push the last few points toward the spine side
    def hook(x, z):
        t = z / L
        return x - 0.12 * max(0, t - 0.7) ** 2 / 0.09, z
    prof = [hook(x, z) for x, z in right] + [hook(x, z) for x, z in list(reversed(left))[1:]]
    def thick(x, z): return 0.045 * (1 - z / L * 0.7) * (1 - min(1, abs(x) / 0.26) ** 2) + 0.005
    vf = [(x, -thick(x, z), z) for x, z in prof]; vb = [(x, thick(x, z), z) for x, z in prof]
    m = len(prof)
    faces = [tuple(range(m)), tuple(range(m, 2 * m))[::-1]] + [(i, (i + 1) % m, m + (i + 1) % m, m + i) for i in range(m)]
    blade = from_pydata(vf + vb, faces, "blade")
    sel([blade]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    bevel(blade, 0.005, 1, 20); assign(blade, paint)
    # code-etched inlay panels on both flats + a fuller groove
    inl = []
    for sy in (-1, 1):
        pl = box((0.11, 0.01, L * 0.5), (0.02, sy * 0.042, L * 0.33), name="inlay"); bevel(pl, 0.003, 1); assign(pl, code); inl.append(pl)
        fr = box((0.13, 0.008, L * 0.52), (0.02, sy * 0.038, L * 0.33), name="inlayframe"); bevel(fr, 0.003, 1); assign(fr, steel); inl.append(fr)
    ep = [(hook(w + 0.006, z)[0], 0, z) for w, z in side]
    ed = tube_along(ep, 0.011, 4, "edge", radii=[0.5] + [1] * 14 + [0.7, 0.4, 0.15]); ed.scale = (1, 0.6, 1); bake_xform(ed); assign(ed, edge)
    # spiked guard: thick bar with forward horns and four spikes, glowing core
    gpts = [(t * 0.4, -0.07 * t * t, -0.04 + 0.16 * abs(t) ** 3) for t in [(i / 16) * 2 - 1 for i in range(17)]]
    guard = tube_along(gpts, 0.055, 8, "guard", radii=[0.25, 0.5, 0.75, 0.9, 1, 1, 1.05, 1.15, 1.3, 1.15, 1.05, 1, 1, 0.9, 0.75, 0.5, 0.25]); assign(guard, paint)
    spikes = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            sp = cone(0.03, 0.2, (0, 0, 0.1), n=4, name="gspike"); sp.rotation_euler = (sy * 0.9, sx * 0.5, 0); sp.location = (sx * 0.15, sy * 0.03, -0.02); bake_xform(sp)
            assign(sp, steel); spikes.append(sp)
    core = ico(0.07, (0, 0, -0.03), 2, "core"); core.scale = (1, 1.2, 1); bake_xform(core); assign(core, edge)
    cring = torus(0.07, 0.016, (0, -0.06, -0.03), (math.pi / 2, 0, 0), 16, 6, "coreRing"); assign(cring, steel)
    cring2 = torus(0.07, 0.016, (0, 0.06, -0.03), (math.pi / 2, 0, 0), 16, 6, "coreRing"); assign(cring2, steel)
    g = lathe([(0.05, -0.07), (0.062, -0.1), (0.056, -0.2), (0.064, -0.32), (0.056, -0.44), (0.062, -0.55), (0.05, -0.58)], 12, "grip"); assign(g, steel)
    wr = tube_along(helix((0, 0, -0.1), (0, 0, -0.55), 0.062, 6, n=160), 0.016, 5, "wrap"); assign(wr, wrapm)
    pom = box((0.13, 0.13, 0.13), (0, 0, -0.66), (0.6, 0.6, 0.2), name="pommel"); bevel(pom, 0.012, 1); assign(pom, paint)
    pk = cone(0.045, 0.16, (0, 0, -0.78), (math.pi, 0, 0), n=4, name="pommelSpike"); assign(pk, steel)
    pc = []
    rng = random.Random(2)
    for i in range(9):
        s = rng.uniform(0.025, 0.05)
        c = box((s, s, s), (rng.uniform(-0.11, 0.11), rng.uniform(-0.11, 0.11), -0.66 + rng.uniform(-0.12, 0.12)), (rng.random(), rng.random(), rng.random()), "glitch")
        assign(c, edge); pc.append(c)
    dagger = join([blade, ed, guard, core, cring, cring2, g, wr, pom, pk] + inl + spikes + pc, "K2Blade"); smooth(dagger, 30)
    dagger.location.x = -0.9; bake_xform(dagger)
    # --- harness
    leather = mat_leather("k2_harness", base=(0.035, 0.01, 0.008), dark=(0.008, 0.002, 0.002), scale=1.5, rough=0.5)
    hp = []
    for s in (-1, 1):
        st = box((0.18, 0.04, 2.35), (0, 0.6, 0), (0, s * math.radians(38), 0), name="strap"); bevel(st, 0.01, 1); assign(st, leather); hp.append(st)
        # red trim stripe + studs along each strap
        tr = box((0.05, 0.012, 2.2), (0, 0.575, 0), (0, s * math.radians(38), 0), name="stripe"); assign(tr, paint); hp.append(tr)
        for k in range(-5, 6):
            if abs(k) < 2: continue
            d = k * 0.19
            stud = cone(0.025, 0.05, (0, 0, 0), n=4, name="stud"); stud.rotation_euler = (math.pi / 2, 0, 0)
            stud.location = (math.sin(s * math.radians(38)) * d, 0.55, math.cos(s * math.radians(38)) * d); bake_xform(stud); assign(stud, steel); hp.append(stud)
        lp = box((0.3, 0.08, 0.34), (s * 0.4, 0.62, s * -0.55), (0, s * math.radians(38), 0), name="loop"); bevel(lp, 0.015, 2); assign(lp, paint); hp.append(lp)
        bk = torus(0.08, 0.014, (s * -0.45, 0.57, 0.6), (math.pi / 2, s * math.radians(38), 0), 4, 4, "buckle"); assign(bk, steel); hp.append(bk)
        # spiked pauldron-plate where each strap goes over the shoulder
        sh = box((0.42, 0.09, 0.3), (s * 0.68, 0.62, 0.86), (0, s * math.radians(38), 0), name="shoulder"); bevel(sh, 0.03, 2); assign(sh, paint); hp.append(sh)
        for k in range(3):
            sp = cone(0.045, 0.24 - k * 0.04, (0, 0, 0.12), n=4, name="sspike")
            sp.rotation_euler = (-0.25, s * (0.35 + 0.2 * k), 0); sp.location = (s * (0.55 + k * 0.12), 0.6, 0.97 - k * 0.04); bake_xform(sp)
            assign(sp, steel); hp.append(sp)
    # chest emblem: octagonal plate, glowing skull-visor, circuit traces
    plate = cyl(0.27, 0.06, (0, 0.55, 0), (math.pi / 2, 0, 0), 8, "plate"); bevel(plate, 0.012, 1); assign(plate, paint); hp.append(plate)
    rim = torus(0.27, 0.022, (0, 0.52, 0), (math.pi / 2, 0, 0), 8, 4, "rim"); assign(rim, steel); hp.append(rim)
    skull = ico(0.13, (0, 0.5, 0.03), 2, "skull"); skull.scale = (1, 0.55, 1.05); bake_xform(skull); assign(skull, steel); hp.append(skull)
    jaw = box((0.13, 0.06, 0.08), (0, 0.47, -0.1), name="jaw"); bevel(jaw, 0.015, 2); assign(jaw, steel); hp.append(jaw)
    visor = box((0.22, 0.04, 0.05), (0, 0.415, 0.04), name="visor"); bevel(visor, 0.012, 2); assign(visor, edge); hp.append(visor)
    for k in range(8):
        a = k / 8 * TAU
        pts = [(math.cos(a) * 0.2, 0.505, math.sin(a) * 0.2), (math.cos(a) * 0.24, 0.505, math.sin(a) * 0.24 + 0.03 * (1 if k % 2 else -1))]
        tr = tube_along(pts, 0.009, 4, "trace"); assign(tr, edge); hp.append(tr)
        nd = ico(0.016, pts[-1], 1, "node"); assign(nd, edge); hp.append(nd)
    harness = join(hp, "K2Harness"); smooth(harness, 30)
    return {"Blade": (dagger, 1024, True), "Harness": (harness, 1024, True)}
