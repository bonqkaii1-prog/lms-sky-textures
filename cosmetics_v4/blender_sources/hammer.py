"""Executioner's Burden (Doombringer) -- colossal war hammer: scorched black iron head with a waffled
striking face, curved beak, crown spike, riveted collar and rune panels burning red; octagonal iron haft
with riveted langets, a leather-wrapped grip, a chain wound round the upper haft with a length hanging free,
and a spiked pommel with a ring."""
import sys; sys.path.insert(0, "/home/claude/cos")
from kit import *
import runes

KEY = "doom_hammer"
reset()
runes.sheet(f"{OUT}/runes_doom.png", seed=7, rows=8, cols=12, w=10, border=False)

DK = dict(base=(0.02, 0.019, 0.02), worn=(0.24, 0.22, 0.21), rust=(0.09, 0.03, 0.015), rust_k=0.07)
iron = mat_iron("iron", pits=0.4, **DK)
iron_rune = mat_iron("iron_rune", rune=f"{OUT}/runes_doom.png", rune_scale=1.0, rune_k=14, rune_col=(1.0, 0.07, 0.02), **DK)
leather = mat_leather("grip", base=(0.07, 0.035, 0.02), scale=1.3)
band = mat_iron("band", base=(0.035, 0.03, 0.028), worn=(0.3, 0.27, 0.25), rust=(0.12, 0.045, 0.02), rust_k=0.18)

parts = []
HX, HY, HZ = 1.0, 0.68, 0.62           # head core (X = length of the head, Z = up the haft)
TOP = 3.4                               # haft length; head sits on top
hz = TOP + HZ / 2

# --- head core: tapered block (wider at the faces than the middle) built from a lofted profile
def head_core():
    o = box((HX, HY, HZ), (0, 0, hz), name="core")
    sel([o]); bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(o.data)
    for v in bm.verts:            # waist the middle: pull Y/Z of verts near x=0 inwards
        pass
    bpy.ops.object.mode_set(mode="OBJECT")
    # subdivide along X then pinch the middle for a waisted hammer head
    sel([o]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts": 4, "edge_index": 0}) if False else None
    bpy.ops.object.mode_set(mode="OBJECT")
    return o

core = box((HX, HY, HZ), (0, 0, hz), name="core")
# waist: scale the middle loop in via a lattice-like vertex pass
me = core.data
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.subdivide_edges(bm, edges=[e for e in bm.edges if abs(e.verts[0].co.x - e.verts[1].co.x) > 0.5], cuts=3, use_grid_fill=True)
for v in bm.verts:
    t = 1 - abs(v.co.x) / (HX / 2)          # 1 at centre, 0 at the faces
    k = 1 - 0.16 * t
    v.co.y *= k; v.co.z = hz + (v.co.z - hz) * k
bm.to_mesh(me); bm.free()
bevel(core, 0.035, 3, 30); wnormal(core); assign(core, iron)
parts.append(core)

# raised collar bands with rivets either side of the haft
for sx in (-0.22, 0.22):
    b = box((0.09, HY * 0.93, HZ * 0.93), (sx, 0, hz), name="collar")
    bevel(b, 0.018, 2); wnormal(b); assign(b, band); parts.append(b)
    for k in range(5):
        for sy in (-1, 1):
            r = sphere(0.022, (sx, sy * HY * 0.465, hz - HZ * 0.36 + k * HZ * 0.18), 10, 6, "rivet"); assign(r, band); parts.append(r)
        r = sphere(0.022, (sx, -HY * 0.36 + k * HY * 0.18, hz + HZ * 0.465), 10, 6, "rivet"); assign(r, band); parts.append(r)

# rune panels on both broad sides: recessed frame + burning plate
for sy in (-1, 1):
    fr = box((0.36, 0.03, HZ * 0.62), (0, sy * HY * 0.42, hz), name="frame")
    bevel(fr, 0.01, 2); assign(fr, band); parts.append(fr)
    pl = box((0.3, 0.012, HZ * 0.52), (0, sy * HY * 0.44, hz), name="runeplate")
    assign(pl, iron_rune); parts.append(pl)

# striking face (-X): octagonal boss with a waffled face of pyramids
face_x = -HX / 2
boss = cyl(0.37, 0.24, (face_x - 0.1, 0, hz), (0, math.pi / 2, 0), n=8, name="boss", r2=0.4)
bevel(boss, 0.03, 3, 30); wnormal(boss); assign(boss, iron); parts.append(boss)
rim = torus(0.36, 0.035, (face_x - 0.23, 0, hz), (0, math.pi / 2, 0), maj=24, mnr=6, name="rim"); assign(rim, band); parts.append(rim)
for iy in range(-2, 3):
    for iz in range(-2, 3):
        if iy * iy + iz * iz > 6: continue
        py = cone(0.058, 0.07, (face_x - 0.255, iy * 0.11, hz + iz * 0.11), (0, -math.pi / 2, math.pi / 4), n=4, name="waffle")
        assign(py, iron); parts.append(py)

# beak (+X): curved, faceted spike sweeping down
pts, radii = [], []
for i in range(13):
    t = i / 12
    pts.append((HX / 2 - 0.05 + 0.85 * t, 0, hz + 0.05 - 0.42 * t ** 1.8))
    radii.append((1 - t) ** 0.9 * 1.0 + 0.04)
beak = tube_along(pts, 0.2, n=6, name="beak", radii=radii)
beak.scale = (1, 0.75, 1); bake_xform(beak)
bevel(beak, 0.008, 1, 40); assign(beak, iron); parts.append(beak)
# a ridge along the top of the beak
rpts = [(p[0], 0, p[2] + 0.17 * r) for p, r in zip(pts, radii)]
ridge = tube_along(rpts[:-2], 0.03, n=4, name="ridge", radii=radii[:-2]); assign(ridge, band); parts.append(ridge)

# crown spike on top + four corner thorns
sp = cone(0.13, 0.5, (0, 0, hz + HZ / 2 + 0.25), n=6, name="crown"); bevel(sp, 0.01, 1); assign(sp, iron); parts.append(sp)
for sx in (-1, 1):
    for sy in (-1, 1):
        th = cone(0.05, 0.2, (sx * 0.4, sy * 0.27, hz + HZ / 2 + 0.06), (sy * 0.5, -sx * 0.5, 0), n=4, name="thorn")
        assign(th, iron); parts.append(th)

# --- haft: octagonal iron core, langets from the head, leather grip, flared collar rings
haft = cyl(0.085, TOP, (0, 0, TOP / 2), n=8, name="haft"); bevel(haft, 0.01, 1, 30); assign(haft, iron); parts.append(haft)
for sy in (-1, 1):
    lg = box((0.05, 0.02, 0.9), (0, sy * 0.093, TOP - 0.42), name="langet"); bevel(lg, 0.006, 1); assign(lg, band); parts.append(lg)
    tip = cone(0.035, 0.12, (0, sy * 0.093, TOP - 0.93), (math.pi, 0, 0), n=4, name="langet_tip"); assign(tip, band); parts.append(tip)
    for k in range(4):
        r = sphere(0.016, (0, sy * 0.105, TOP - 0.15 - k * 0.22), 8, 5, "rivet"); assign(r, band); parts.append(r)
for z in (TOP - 1.05, 1.25, 0.32):
    ring = lathe([(0.086, -0.04), (0.115, -0.025), (0.118, 0.025), (0.086, 0.04)], 16, "ring"); ring.location.z = z; bake_xform(ring)
    bevel(ring, 0.004, 1); assign(ring, band); parts.append(ring)
# leather grip: a thick strap wound as a helix with a slight overlap, plus a loose tail end
gp = helix((0, 0, 0.36), (0, 0, 1.2), 0.1, 14, n=560)
grip = tube_along(gp, 0.034, n=6, name="grip"); grip.scale = (1, 1, 1); assign(grip, leather); parts.append(grip)
tail_pts = [Vector(gp[-1]) + Vector((0.02 * i, 0.06 * i, -0.08 * i - 0.01 * i * i)) for i in range(8)]
tail = tube_along(tail_pts, 0.022, n=5, name="gripTail", radii=[1, 1, 0.95, 0.9, 0.85, 0.8, 0.7, 0.6]); assign(tail, leather); parts.append(tail)

# pommel: faceted lathe with a spike and a hanging ring
pom = lathe([(0.0, -0.36), (0.05, -0.32), (0.13, -0.2), (0.16, -0.1), (0.14, -0.02), (0.1, 0.02), (0.085, 0.06)], 8, "pommel")
pom.location.z = 0.0; bake_xform(pom); bevel(pom, 0.008, 1, 25); wnormal(pom); assign(pom, iron); parts.append(pom)
for a in range(4):
    th = cone(0.035, 0.14, (math.cos(a * math.pi / 2) * 0.16, math.sin(a * math.pi / 2) * 0.16, -0.12), (0, math.pi / 2, a * math.pi / 2), n=4, name="pthorn")
    assign(th, iron); parts.append(th)

body = join(parts, "HammerBody")

# --- chain wound round the upper haft, then a free length hanging off the collar
cp = helix((0, 0, 1.5), (0, 0, TOP - 1.1), 0.13, 3.2, n=200, phase=0.3)
wound = chain_along(cp, link_len=0.15, link_w=0.085, wire=0.017, name="ChainWound")
cmat = mat_iron("chain", base=(0.03, 0.028, 0.026), worn=(0.3, 0.28, 0.26), rust=(0.12, 0.045, 0.02), rust_k=0.22)
assign(wound, cmat)
start = Vector(cp[-1])
hang_pts = [start + Vector((0.03 * i, -0.02 * i, -0.13 * i)) + Vector((0, 0, -0.004 * i * i)) for i in range(12)]
hang = chain_along(hang_pts, link_len=0.15, link_w=0.085, wire=0.017, name="ChainHang")
weight = lathe([(0.0, -0.16), (0.07, -0.13), (0.09, -0.05), (0.08, 0.02), (0.04, 0.05), (0.0, 0.06)], 8, "weight")
weight.location = hang_pts[-1] + Vector((0, 0, -0.1)); bake_xform(weight)
hang = join([hang, weight], "ChainHang"); assign(hang, cmat)

for o in (body, wound, hang):
    smooth(o, 35)
print("tris", {o.name: tris(o) for o in (body, wound, hang)})
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/{KEY}.blend")
preview([body, wound, hang], f"{OUT}/{KEY}_preview.png", res=640, elev=10, azim=-35, samples=40, dist=1.0)
sc = bpy.context.scene
preview([body], f"{OUT}/{KEY}_head.png", res=640, elev=14, azim=-28, samples=40, dist=0.32, target=Vector((0.15, 0, TOP + 0.3)))
print("done")
