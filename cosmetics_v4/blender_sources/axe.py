"""Butcher's Trophy (Jane Doe): a heavy bearded axe -- chipped, blood-stained blade with a hammer poll and a
wedge through the eye, a slightly curved ash haft, a grip bound in filthy bandage with a tied-off tail, iron
rings, and a torn rag knotted under the head (a separate piece so it can flutter)."""
from kit import *
KEY = "axe"
PREVIEW = {"main": {"elev": 10, "azim": -30, "dist": 0.9}, "extra": [{"elev": 8, "azim": -20, "dist": 0.33, "target": None}]}

def blade_shape(rng):
    # bearded profile (x forward from the haft, z up), with chips knocked out of the edge
    top = [(0.05, 0.16), (0.3, 0.2), (0.55, 0.3), (0.72, 0.38)]
    edge = []
    for i in range(18):
        t = i / 17
        a = math.radians(70 - 150 * t)
        x = 0.42 + 0.33 * math.cos(a); z = -0.05 + 0.45 * math.sin(a) - (0.12 * t ** 2)
        if rng.random() < 0.22 and 1 < i < 16: x -= rng.uniform(0.02, 0.05)       # chips
        edge.append((x, z))
    beard = [(0.36, -0.62), (0.22, -0.4), (0.12, -0.2), (0.05, -0.14)]
    return top + edge + beard

def build():
    rng = random.Random(8)
    steel = mat_iron("axe_steel", base=(0.03, 0.029, 0.028), worn=(0.6, 0.58, 0.55), rust=(0.05, 0.014, 0.005), rust_k=0.35, rough=0.5, metal=1.0, pits=0.45)
    wood = mat_wood("axe_haft", base=(0.09, 0.045, 0.02), dark=(0.018, 0.008, 0.003), scale=1.0)
    cloth = mat_cloth("axe_bandage", base=(0.14, 0.115, 0.075), dirt=(0.03, 0.02, 0.01), blood=(0.035, 0.002, 0.0), blood_k=1.0, scale=2.0)
    rag = mat_cloth("axe_rag", base=(0.06, 0.006, 0.005), dirt=(0.015, 0.003, 0.002), blood=(0.025, 0.0, 0.0), blood_k=0.8, scale=1.5)
    H = 3.0
    # blade: extrude the profile, taper thickness toward the edge
    prof = blade_shape(rng)
    def thick(x): return max(0.01, 0.095 * (1 - (x - 0.05) / 0.8) ** 1.1)
    vf = [(x, -thick(x), z) for x, z in prof]; vb = [(x, thick(x), z) for x, z in prof]
    m = len(prof)
    faces = [tuple(range(m)), tuple(range(m, 2 * m))[::-1]] + [(i, (i + 1) % m, m + (i + 1) % m, m + i) for i in range(m)]
    blade = from_pydata(vf + vb, faces, "blade")
    sel([blade]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    bevel(blade, 0.006, 1, 30)
    edge_pts = [(px - 0.012, 0, pz) for px, pz in prof[4:22]]
    edgebev = tube_along(edge_pts, 0.016, 4, "edgebev"); edgebev.scale = (1, 0.55, 1); bake_xform(edgebev)
    blade = join([blade, edgebev], "blade")
    eye = box((0.2, 0.17, 0.36), (0, 0, 0.0), name="eye"); bevel(eye, 0.02, 2)
    poll = box((0.2, 0.19, 0.2), (-0.18, 0, 0.02), name="poll"); bevel(poll, 0.025, 2)
    face = cyl(0.11, 0.05, (-0.29, 0, 0.02), (0, math.pi / 2, 0), 8, "face"); bevel(face, 0.01, 1)
    wedge = box((0.05, 0.04, 0.08), (0, 0, 0.2), name="wedge")
    head = join([blade, eye, poll, face, wedge], "head"); head.location.z = H - 0.2; bake_xform(head)
    assign(head, steel)
    # forged grind line: a low ridge following the edge a little way in, on both faces
    for sy in (-1, 1):
        gl = [(px - 0.09, sy * (thick(px - 0.09) + 0.002), pz * 0.92) for px, pz in prof[5:21]]
        g = tube_along(gl, 0.009, 4, "grind"); g.scale = (1, 0.5, 1); bake_xform(g); g.location.z = H - 0.2; bake_xform(g)
        g.data.materials.append(steel); head = join([head, g], "head")
    # haft: lathe with a slight swell at the grip and a flared knob, then bent a touch
    hp = [(0.0, 0.0), (0.085, 0.0), (0.1, 0.06), (0.075, 0.18), (0.068, 1.0), (0.072, 1.6), (0.064, 2.6), (0.07, H - 0.05), (0.0, H - 0.05)]
    haft = lathe(hp, 12, "haft"); haft.scale = (1, 0.8, 1); bake_xform(haft)
    bm = bmesh.new(); bm.from_mesh(haft.data)
    for v in bm.verts: v.co.x += 0.06 * math.sin(v.co.z / H * math.pi)
    bm.to_mesh(haft.data); bm.free(); smooth(haft, 50); assign(haft, wood)
    rings = []
    for z in (0.2, H - 0.42):
        r = lathe([(0.07, -0.03), (0.085, -0.02), (0.085, 0.02), (0.07, 0.03)], 12, "ring"); r.location = (0.06 * math.sin(z / H * math.pi), 0, z); bake_xform(r); rings.append(r)
    ring = join(rings, "rings"); assign(ring, steel)
    # bandage grip with a tied tail
    gp = helix((0.02, 0, 0.3), (0.05, 0, 1.15), 0.085, 8, n=320)
    w = tube_along(gp, 1.0, 4, "grip")
    bm = bmesh.new(); bm.from_mesh(w.data)
    for i, v in enumerate(bm.verts):
        c = Vector(gp[min(i // 4, len(gp) - 1)]); d = v.co - c
        rad = Vector((c.x - 0.03, c.y, 0)).normalized()
        dr = d.dot(rad); dz = d.z; side = d - rad * dr - Vector((0, 0, dz))
        v.co = c + rad * dr * 0.02 + Vector((0, 0, dz * 0.1)) + side * 0.1
    bm.to_mesh(w.data); bm.free()
    tpts = [Vector(gp[-1]) + Vector((0.03 * j, -0.05 * j, -0.12 * j)) for j in range(7)]
    tl = tube_along(tpts, 1.0, 4, "gtail")
    bm = bmesh.new(); bm.from_mesh(tl.data)
    for i, v in enumerate(bm.verts):
        c = tpts[min(i // 4, 6)]; d = v.co - c; v.co = c + Vector((d.x * 0.05, d.y * 0.012, d.z * 0.05))
    bm.to_mesh(tl.data); bm.free()
    grip = join([w, tl], "grip"); assign(grip, cloth)
    axe = join([head, haft, ring, grip], "Axe"); smooth(axe, 35)
    # torn rag knotted under the head: a cloth strip subdivided and displaced, ragged at the end
    knot = ico(0.07, (0.07, 0, H - 0.6), 1, "knot"); knot.scale = (1.1, 1.3, 0.8); bake_xform(knot)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=8, y_subdivisions=16, size=1, location=(0, 0, 0))
    r = bpy.context.object; r.scale = (0.2, 0.7, 1); bake_xform(r)
    bm = bmesh.new(); bm.from_mesh(r.data)
    for v in bm.verts:
        t = (0.35 - v.co.y) / 0.7
        v.co = Vector((v.co.x + 0.08 * math.sin(t * 5), 0.06 * math.sin(v.co.x * 20 + t * 8) + 0.1 * t, -t * 0.7))
        if t > 0.85: v.co.z += rng.uniform(0, 0.08)
    bm.to_mesh(r.data); bm.free()
    sol = r.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.012
    r.location = (0.12, 0, H - 0.6); bake_xform(r)
    ragp = join([knot, r], "Rag"); smooth(ragp, 70); assign(ragp, rag)
    PREVIEW["extra"][0]["target"] = Vector((0.3, 0, H - 0.25))
    return {"Axe": (axe, 1024, False), "Rag": (ragp, 512, False)}
