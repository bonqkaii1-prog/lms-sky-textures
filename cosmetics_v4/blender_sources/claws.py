"""Predator's Claws (The Rake): a gaunt claw-hand of dirty ivory that sheathes the end of the arm -- a ridged
back-of-hand plate, four long three-jointed fingers with swollen knuckles and a thumb, black hooked talons;
filthy bandages wound round the wrist with torn ends hanging. Exported for the right arm and mirrored for the left."""
from kit import *
KEY = "claws"
PREVIEW = {"main": {"elev": 10, "azim": -30, "dist": 0.85}, "extra": [{"elev": 5, "azim": 70, "dist": 0.9}]}

def finger(base, direction, lengths, r, curl, side, name):
    """a jointed finger: phalanx tubes with knuckle bulges, curling forward (+Y) as it goes down"""
    parts = []
    p = Vector(base); d = Vector(direction).normalized()
    ang = 0
    for i, L in enumerate(lengths):
        ang += curl[i]
        dd = (Matrix.Rotation(ang, 3, "X") @ d).normalized()
        q = p + dd * L
        mid = p.lerp(q, 0.5)
        rr = r * (1 - 0.18 * i)
        pts = [p, p.lerp(q, 0.15), mid, p.lerp(q, 0.85), q]
        parts.append(tube_along(pts, rr, 8, "phal", radii=[1.15, 0.9, 0.75, 0.9, 1.05]))
        parts.append(sphere(rr * 1.25, q, 10, 6, "knuckle"))
        p = q; last = dd
    # hooked talon
    tpts = []
    for j in range(8):
        t = j / 7
        tpts.append(p + last * (0.22 * t) + Vector((0, 0.09 * t * t, 0)))
    talon = tube_along(tpts, r * 0.95, 7, "talon", radii=[1, 0.9, 0.75, 0.6, 0.45, 0.3, 0.15, 0.02])
    return parts, talon

def build():
    bone = mat_bone("rake_bone", base=(0.2, 0.165, 0.11), dark=(0.035, 0.022, 0.012), scale=1.6)
    horn = mat_obsidian("rake_horn", vein=(0.4, 0.05, 0.02), vein_scale=6, vein_w=0.002, k=0.2, base=(0.015, 0.012, 0.01))
    cloth = mat_cloth("rake_bandage", base=(0.15, 0.125, 0.08), dirt=(0.03, 0.02, 0.01), blood=(0.035, 0.002, 0.0), blood_k=0.8, scale=2.0)
    # Roblox R6 arm: 1 x 2 x 1, hand end at z = 0, arm goes up to z = 2; front = -Y
    bones = []; talons = []
    # knuckle bar across the end of the arm (front face = -Y), tendons running up the back of the hand
    for i in range(4):
        x = -0.33 + i * 0.22
        bones.append(sphere(0.1, (x, -0.34, -0.22), 12, 8, "knuckle0"))
        bones.append(tube_along([(x * 0.7, -0.44, 0.35), (x * 0.9, -0.5, 0.05), (x, -0.4, -0.2)], 0.045, 6, "tendon", radii=[0.5, 1, 0.9]))
    pad = sphere(1, (0, -0.2, -0.1), 14, 8, "pad"); pad.scale = (0.46, 0.22, 0.2); bake_xform(pad); bones.append(pad)
    for i in range(4):
        x = -0.33 + i * 0.22
        L = [0.5, 0.42, 0.32] if i in (1, 2) else [0.42, 0.35, 0.27]
        ps, t = finger((x, -0.34, -0.3), (x * 0.3, -0.2, -1), L, 0.062, [0.18, 0.34, 0.4], 1, f"f{i}")
        bones += ps; talons.append(t)
    ps, t = finger((0.46, -0.18, -0.15), (0.6, -0.5, -0.7), [0.26, 0.22], 0.07, [0.25, 0.4], 1, "thumb")
    bones += ps; talons.append(t)
    hand = join(bones, "ClawHand"); smooth(hand, 50); assign(hand, bone)
    tal = join(talons, "Talons"); smooth(tal, 40); assign(tal, horn)
    hand = join([hand, tal], "ClawHand")
    # bandages: overlapping wraps up the forearm, two torn trailing strips
    wraps = []
    gp0 = helix((0, 0, 0.1), (0, 0, 0.85), 1.0, 5.5, n=260)
    gp = []
    for p in gp0:                         # superellipse radius so the wrap hugs the 1x1 square arm
        a_ = math.atan2(p.y, p.x); r_ = 0.54 / (abs(math.cos(a_)) ** 4 + abs(math.sin(a_)) ** 4) ** 0.25
        gp.append(Vector((math.cos(a_) * r_, math.sin(a_) * r_, p.z)))
    w = tube_along(gp, 1.0, 4, "wrap")
    bm = bmesh.new(); bm.from_mesh(w.data)
    for i, v in enumerate(bm.verts):
        c = Vector(gp[min(i // 4, len(gp) - 1)]); d = v.co - c
        radial = Vector((c.x, c.y, 0)).normalized()
        v.co = c + radial * d.dot(radial) * 0.025 + Vector((0, 0, d.z)) * 0.11 + (d - radial * d.dot(radial) - Vector((0, 0, d.z))) * 0.11
    bm.to_mesh(w.data); bm.free(); wraps.append(w)
    rng = random.Random(3)
    for k, (a, L) in enumerate(((0.6, 0.7), (2.4, 0.5))):
        pts = []
        for j in range(10):
            t = j / 9
            pts.append((0.55 * math.cos(a) + 0.04 * math.sin(t * 6), 0.55 * math.sin(a) - 0.06 * t, 0.45 - L * t))
        s = tube_along(pts, 1.0, 4, "strip")
        bm = bmesh.new(); bm.from_mesh(s.data)
        for i, v in enumerate(bm.verts):
            c = Vector(pts[min(i // 4, 9)]); d = v.co - c
            tt = min(i // 4, 9) / 9
            v.co = c + Vector((d.x * 0.07 * (1 - 0.5 * tt), d.y * 0.012, d.z * 0.02))
        bm.to_mesh(s.data); bm.free(); wraps.append(s)
    band = join(wraps, "Bandage"); smooth(band, 60); assign(band, cloth)
    # mirrored copies for the left arm
    def mirror(o, name):
        c = o.copy(); c.data = o.data.copy(); bpy.context.collection.objects.link(c)
        c.scale = (-1, 1, 1); bake_xform(c)
        sel([c]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.flip_normals(); bpy.ops.object.mode_set(mode="OBJECT")
        c.name = name; c.location.x = -1.6; bake_xform(c); return c
    handL = mirror(hand, "ClawHandL"); bandL = mirror(band, "BandageL")
    hand.name = "ClawHandR"; band.name = "BandageR"
    return {"ClawHandR": (hand, 1024, False), "BandageR": (band, 512, False), "ClawHandL": (handL, 1024, False), "BandageL": (bandL, 512, False)}
