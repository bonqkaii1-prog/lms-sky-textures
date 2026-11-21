"""Executioner's Burden v2 (Doombringer): the war hammer taken further -- black iron head split by molten
cracks, a red-hot waffled striking face and beak, brass collars studded with glowing red gems, burning rune
panels, ram horns curling off the head, a crown of iron thorns, a crimson leather grip with brass rings, a
bronze chain wound round the haft with a weighted length, and two tattered crimson war banners."""
from kit import *
import runes
KEY = "doom2"
PREVIEW = {"main": {"elev": 10, "azim": -35, "dist": 1.0}, "extra": [{"elev": 14, "azim": -28, "dist": 0.34, "target": None}]}
RED = (1.0, 0.09, 0.02)


def build():
    runes.sheet(f"{OUT}/runes_doom.png", seed=7, rows=8, cols=12, w=10, border=False)
    DK = dict(base=(0.022, 0.02, 0.021), worn=(0.3, 0.27, 0.25), rust=(0.12, 0.03, 0.01), rust_k=0.06)
    iron = mat_iron("d2_iron", pits=0.4, ember=0.55, ember_col=(1.0, 0.16, 0.02), **DK)
    haftm = mat_iron("d2_haft", pits=0.3, **DK)
    rune = mat_iron("d2_rune", rune=f"{OUT}/runes_doom.png", rune_scale=1.0, rune_k=20, rune_col=RED, **DK)
    heat_face = mat_heat("d2_face", axis="X", start=-0.55, end=-0.9, k=12)
    heat_beak = mat_heat("d2_beak", axis="X", start=0.75, end=1.35, k=14)
    brass = mat_gold("d2_brass", base=(0.24, 0.12, 0.035), worn=(0.85, 0.55, 0.25))
    leather = mat_leather("d2_grip", base=(0.22, 0.015, 0.012), dark=(0.05, 0.003, 0.002), scale=1.3, rough=0.55)
    gem = mat_glow("d2_gem", col=RED, base=(0.35, 0.01, 0.0), k=10, crack=9)
    horn = mat_bone("d2_horn", base=(0.1, 0.055, 0.035), dark=(0.02, 0.015, 0.012), scale=2.0)
    parts = []
    HX, HY, HZ = 1.0, 0.68, 0.62
    TOP = 3.4
    hz = TOP + HZ / 2
    core = box((HX, HY, HZ), (0, 0, hz), name="core")
    bm = bmesh.new(); bm.from_mesh(core.data)
    bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs(e.verts[0].co.x - e.verts[1].co.x) > 0.5], cuts=3, use_grid_fill=True)
    for v in bm.verts:
        t = 1 - abs(v.co.x) / (HX / 2); k = 1 - 0.16 * t
        v.co.y *= k; v.co.z = hz + (v.co.z - hz) * k
    bm.to_mesh(core.data); bm.free()
    bevel(core, 0.035, 3, 30); wnormal(core); assign(core, iron); parts.append(core)
    # brass collars with rivets and a glowing gem in a bezel on each broad side
    for sx in (-0.22, 0.22):
        b = box((0.1, HY * 0.95, HZ * 0.95), (sx, 0, hz), name="collar"); bevel(b, 0.02, 2); wnormal(b); assign(b, brass); parts.append(b)
        for k in range(5):
            for sy in (-1, 1):
                r = sphere(0.024, (sx, sy * HY * 0.475, hz - HZ * 0.36 + k * HZ * 0.18), 10, 6, "rivet"); assign(r, brass); parts.append(r)
    for sy in (-1, 1):
        fr = box((0.36, 0.035, HZ * 0.66), (0, sy * HY * 0.42, hz), name="frame"); bevel(fr, 0.01, 2); assign(fr, brass); parts.append(fr)
        pl = box((0.3, 0.012, HZ * 0.54), (0, sy * HY * 0.445, hz), name="runeplate"); assign(pl, rune); parts.append(pl)
        for sx in (-0.22, 0.22):
            bz = torus(0.055, 0.018, (sx, sy * (HY * 0.5 + 0.01), hz + HZ * 0.33), (math.pi / 2, 0, 0), 14, 6, "bezel"); assign(bz, brass); parts.append(bz)
            g = ico(0.05, (sx, sy * (HY * 0.5 + 0.02), hz + HZ * 0.33), 1, "gem"); g.scale = (1, 0.6, 1); bake_xform(g); assign(g, gem); parts.append(g)
    # striking face: octagonal boss, brass rim, red-hot waffle pyramids
    fx = -HX / 2
    boss = cyl(0.37, 0.24, (fx - 0.1, 0, hz), (0, math.pi / 2, 0), n=8, name="boss", r2=0.4); bevel(boss, 0.03, 3, 30); wnormal(boss); assign(boss, heat_face); parts.append(boss)
    rim = torus(0.37, 0.04, (fx - 0.23, 0, hz), (0, math.pi / 2, 0), 24, 6, "rim"); assign(rim, brass); parts.append(rim)
    for iy in range(-2, 3):
        for iz in range(-2, 3):
            if iy * iy + iz * iz > 6: continue
            p = cone(0.058, 0.08, (fx - 0.26, iy * 0.11, hz + iz * 0.11), (0, -math.pi / 2, math.pi / 4), n=4, name="waffle"); assign(p, heat_face); parts.append(p)
    # beak: red-hot toward the point, brass ridge
    pts, radii = [], []
    for i in range(15):
        t = i / 14
        pts.append((HX / 2 - 0.05 + 0.95 * t, 0, hz + 0.05 - 0.5 * t ** 1.8)); radii.append((1 - t) ** 0.9 + 0.03)
    beak = tube_along(pts, 0.21, n=6, name="beak", radii=radii); beak.scale = (1, 0.75, 1); bake_xform(beak)
    bevel(beak, 0.008, 1, 40); assign(beak, heat_beak); parts.append(beak)
    ridge = tube_along([(p[0], 0, p[2] + 0.18 * r) for p, r in zip(pts, radii)][:-3], 0.032, n=4, name="ridge", radii=radii[:-3]); assign(ridge, brass); parts.append(ridge)
    # crown of thorns on top
    sp = cone(0.14, 0.6, (0, 0, hz + HZ / 2 + 0.3), n=6, name="crown"); bevel(sp, 0.01, 1); assign(sp, iron); parts.append(sp)
    for i in range(10):
        a = i / 10 * TAU
        x, y = math.cos(a) * 0.42, math.sin(a) * 0.27
        h_ = 0.26 if i % 2 else 0.18
        th = cone(0.045, h_, (0, 0, h_ / 2), n=4, name="thorn")
        th.rotation_euler = (-y * 1.4, x * 1.1, 0); th.location = (x, y, hz + HZ / 2 - 0.02); bake_xform(th); assign(th, iron); parts.append(th)
    # ram horns: curling out from the top of each collar, sweeping back and down
    for sy in (-1, 1):
        hp, hr = [], []
        for i in range(26):
            t = i / 25
            ang = t * 4.2
            r = 0.42 * (1 - 0.5 * t)
            hp.append((0.12 - 0.2 * t + r * math.sin(ang) * 0.6, sy * (HY * 0.42 + 0.42 * t), hz + HZ * 0.3 + r * math.cos(ang) - 0.1 + 0.15 * t))
            hr.append((1 - t) ** 0.8 + 0.08)
        hn = tube_along(hp, 0.14, 10, "horn", radii=hr)
        # ridged rings along the horn
        for i in range(2, 22, 3):
            ring = torus(0.14 * hr[i] * 1.02, 0.014, (0, 0, 0), (0, 0, 0), 12, 4, "hornring")
            t_ = (Vector(hp[i + 1]) - Vector(hp[i - 1])).normalized()
            ring.matrix_world = Matrix.Translation(hp[i]) @ t_.to_track_quat("Z", "Y").to_matrix().to_4x4(); bake_xform(ring)
            hn = join([hn, ring], "horn")
        assign(hn, horn); parts.append(hn)
    # haft
    haft = cyl(0.088, TOP, (0, 0, TOP / 2), n=8, name="haft"); bevel(haft, 0.01, 1, 30); assign(haft, haftm); parts.append(haft)
    for sy in (-1, 1):
        lg = box((0.055, 0.022, 0.9), (0, sy * 0.095, TOP - 0.42), name="langet"); bevel(lg, 0.006, 1); assign(lg, brass); parts.append(lg)
        tip = cone(0.038, 0.13, (0, sy * 0.095, TOP - 0.93), (math.pi, 0, 0), n=4, name="ltip"); assign(tip, brass); parts.append(tip)
        for k in range(4):
            r = sphere(0.017, (0, sy * 0.108, TOP - 0.15 - k * 0.22), 8, 5, "rivet"); assign(r, brass); parts.append(r)
    for z in (TOP - 1.05, 1.25, 0.32):
        ring = lathe([(0.088, -0.045), (0.12, -0.028), (0.124, 0.028), (0.088, 0.045)], 16, "ring"); ring.location.z = z; bake_xform(ring); assign(ring, brass); parts.append(ring)
    gp = helix((0, 0, 0.36), (0, 0, 1.2), 0.1, 14, n=560)
    grip = tube_along(gp, 0.036, n=6, name="grip"); assign(grip, leather); parts.append(grip)
    pom = lathe([(0.0, -0.4), (0.06, -0.34), (0.14, -0.2), (0.17, -0.1), (0.15, -0.02), (0.1, 0.02), (0.088, 0.06)], 8, "pommel"); bevel(pom, 0.008, 1, 25); assign(pom, brass); parts.append(pom)
    for a in range(4):
        pg = ico(0.045, (math.cos(a * math.pi / 2 + math.pi / 4) * 0.155, math.sin(a * math.pi / 2 + math.pi / 4) * 0.155, -0.1), 1, "pgem"); assign(pg, gem); parts.append(pg)
    for a in range(4):
        th = cone(0.035, 0.16, (math.cos(a * math.pi / 2) * 0.17, math.sin(a * math.pi / 2) * 0.17, -0.12), (0, math.pi / 2, a * math.pi / 2), n=4, name="pthorn"); assign(th, iron); parts.append(th)
    body = join(parts, "HammerBody"); smooth(body, 35)
    # chain (dark bronze) wound round the haft + a weighted free length
    cmat = mat_gold("d2_chain", base=(0.07, 0.035, 0.015), worn=(0.55, 0.32, 0.14), grime=(0.015, 0.008, 0.004))
    cp = helix((0, 0, 1.5), (0, 0, TOP - 1.1), 0.135, 3.2, n=200, phase=0.3)
    wound = chain_along(cp, 0.15, 0.085, 0.017, "ChainWound"); assign(wound, cmat); smooth(wound, 35)
    start = Vector(cp[-1])
    hang_pts = [start + Vector((0.03 * i, -0.02 * i, -0.13 * i)) + Vector((0, 0, -0.004 * i * i)) for i in range(12)]
    hang = chain_along(hang_pts, 0.15, 0.085, 0.017, "ChainHang")
    weight = lathe([(0.0, -0.18), (0.08, -0.14), (0.1, -0.05), (0.09, 0.02), (0.045, 0.05), (0.0, 0.06)], 8, "weight")
    weight.location = hang_pts[-1] + Vector((0, 0, -0.1)); bake_xform(weight)
    for a in range(4):
        th = cone(0.025, 0.1, weight.location + Vector((math.cos(a * math.pi / 2) * 0.1, math.sin(a * math.pi / 2) * 0.1, -0.06)), (0, math.pi / 2, a * math.pi / 2), n=4, name="wthorn")
        weight = join([weight, th], "weight")
    hang = join([hang, weight], "ChainHang"); assign(hang, cmat); smooth(hang, 35)
    # two tattered crimson war banners hanging from the lower collar ring (one piece so it can flutter)
    rng = random.Random(6)
    cloth = mat_cloth("d2_banner", base=(0.32, 0.012, 0.01), dirt=(0.06, 0.003, 0.002), blood=(0.08, 0.0, 0.0), blood_k=0.6, scale=1.4)
    strips = []
    for k, (sy, L, w) in enumerate(((-1, 1.15, 0.26), (1, 0.85, 0.2))):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=6, y_subdivisions=18, size=1, location=(0, 0, 0))
        s = bpy.context.object; s.scale = (w, L, 1); bake_xform(s)
        bm = bmesh.new(); bm.from_mesh(s.data)
        kill = []
        for v in bm.verts:
            t = (L / 2 - v.co.y) / L                       # 0 at top, 1 at the bottom
            x0 = v.co.x
            v.co = Vector((x0 * (1 - 0.15 * t), sy * (0.12 + 0.05 * math.sin(t * 6 + k) + 0.08 * t), -t * L))
            v.co.y += sy * 0.03 * math.sin(x0 * 30 + t * 9)
            if t > 0.8 and rng.random() < 0.35: kill.append(v)              # ragged, torn hem
        bmesh.ops.delete(bm, geom=kill, context="VERTS")
        bm.to_mesh(s.data); bm.free()
        sol = s.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.014; apply_mods(s)
        s.location = (0.0, 0, TOP - 1.0); bake_xform(s)
        strips.append(s)
        tie = torus(0.1, 0.022, (0, 0, TOP - 1.0), (0, 0, 0), 14, 6, "tie"); tie.data.materials.append(brass); strips.append(tie)
    for s in strips:
        if not s.data.materials: s.data.materials.append(cloth)
    banner = join(strips, "Banners"); smooth(banner, 70)
    PREVIEW["extra"][0]["target"] = Vector((0.15, 0, TOP + 0.3))
    body.name, wound.name, hang.name, banner.name = "D2Hammer", "D2ChainWound", "D2ChainHang", "D2Banners"
    return {"Hammer": (body, 1024, True), "ChainWound": (wound, 512, False), "ChainHang": (hang, 512, False), "Banners": (banner, 512, False)}
