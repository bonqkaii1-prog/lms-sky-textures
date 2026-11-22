"""Cabin chess scene furniture: a walnut games table (moulded top with boxwood banding, turned vase legs with bun
feet, scalloped aprons that arch up to clear the players' knees, side drawers with brass knobs, an H-stretcher),
a high-back carved chair (turned front legs, raked back legs, shaped crest rail with carved ears, pierced vase
splat, buttoned oxblood leather seat ringed with brass nails), an inlaid chessboard (64 maple / walnut tiles,
brass stringing, brass file and rank letters in a walnut frame) and an analog chess clock (walnut case, two
dials, red flags, plunger buttons). All in studs; the table and chair stand on z = 0, the board sits on z = 0."""
from kit import *
KEY = "cs"
PREVIEW = {"main": {"elev": 22, "azim": -35, "dist": 0.9}, "extra": [{"elev": 30, "azim": -20, "dist": 0.4, "target": None}]}

SQ = 0.21
TOP = 2.5          # table top surface height
TX, TY = 2.6, 2.1  # table top size (x = across, y = between the players)


def walnut(name="walnut", scale=1.0, axis="Z"):
    m = mat_wood(name, base=(0.17, 0.09, 0.048), dark=(0.10, 0.052, 0.028), scale=scale, axis=axis)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.42
    return m


def maple(name="maple", scale=1.0, axis="Z"):
    m = mat_wood(name, base=(0.72, 0.52, 0.30), dark=(0.60, 0.42, 0.22), scale=scale, axis=axis)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.38
    return m


def text_mesh(s, size, loc, rot=(0, 0, 0), extrude=0.002, name="txt"):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.object; t.data.body = s; t.data.size = size; t.data.extrude = extrude
    t.data.align_x = "CENTER"; t.data.align_y = "CENTER"
    bpy.ops.object.convert(target="MESH"); t.name = name
    return t


def turned_leg(h, r=0.085):
    """vase-turned leg with a bun foot; square block at the top for the apron joints"""
    prof = [(0.0, 0.0), (0.06, 0.0), (0.095, 0.03), (0.10, 0.07), (0.085, 0.11), (0.055, 0.14), (0.05, 0.20), (0.065, 0.24),
            (0.07, 0.27), (0.05, 0.31), (0.045, 0.50), (0.055, 0.70), (0.075, 0.95), (0.085, 1.10), (0.075, 1.25), (0.05, 1.40),
            (0.045, 1.50), (0.06, 1.55), (0.07, 1.60), (0.055, 1.65), (0.05, h - 0.42), (0.0, h - 0.42)]
    leg = lathe(prof, 20, "leg")
    blk = box((0.15, 0.15, 0.42), (0, 0, h - 0.21), name="block"); bevel(blk, 0.012, 2); apply_mods(blk)
    return join([leg, blk], "leg")


def build_table():
    wal = walnut("tbl_walnut", 1.0); band = maple("tbl_band", 2.0)
    brass = mat_gold("tbl_brass", base=(0.30, 0.18, 0.06), worn=(0.9, 0.7, 0.38))
    parts = []
    th = 0.09
    top = box((TX, TY, th), (0, 0, TOP - th / 2), name="top"); bevel(top, 0.03, 4, 30); assign(top, wal); parts.append(top)
    # moulding under the top
    mould = box((TX - 0.06, TY - 0.06, 0.035), (0, 0, TOP - th - 0.012), name="mould"); bevel(mould, 0.012, 3); assign(mould, wal); parts.append(mould)
    # boxwood banding inlay round the top
    for sx in (-1, 1):
        parts.append(assign(box((0.035, TY - 0.14, 0.004), (sx * (TX / 2 - 0.09), 0, TOP + 0.0005), name="band"), band))
    for sy in (-1, 1):
        parts.append(assign(box((TX - 0.14, 0.035, 0.004), (0, sy * (TY / 2 - 0.09), TOP + 0.0005), name="band"), band))
    lx, ly = TX / 2 - 0.15, TY / 2 - 0.17
    lh = TOP - th - 0.03
    for sx in (-1, 1):
        for sy in (-1, 1):
            l = turned_leg(lh); l.location = (sx * lx, sy * ly, 0); bake_xform(l); assign(l, wal); parts.append(l)
    # side aprons (x ends) with a drawer + knob
    for sx in (-1, 1):
        ap = box((0.05, 2 * ly - 0.14, 0.28), (sx * lx, 0, lh - 0.14), name="apron"); bevel(ap, 0.008, 2); assign(ap, wal); parts.append(ap)
        dr = box((0.02, 0.9, 0.17), (sx * (lx + 0.03), 0, lh - 0.14), name="drawer"); bevel(dr, 0.006, 2); assign(dr, wal); parts.append(dr)
        kn = lathe([(0.0, 0.0), (0.018, 0.0), (0.012, 0.015), (0.028, 0.035), (0.022, 0.05), (0.0, 0.053)], 16, "knob")
        kn.rotation_euler = (0, sx * math.pi / 2, 0); kn.location = (sx * (lx + 0.04), 0, lh - 0.14); bake_xform(kn); assign(kn, brass); parts.append(kn)
        # H-stretcher rails along y, low
        st = cyl(0.03, 2 * ly, (sx * lx, 0, 0.38), (math.pi / 2, 0, 0), 12, "stretch"); assign(st, wal); parts.append(st)
    # central stretcher along x
    st = cyl(0.035, 2 * lx, (0, 0, 0.38), (0, math.pi / 2, 0), 12, "stretchx"); assign(st, wal); parts.append(st)
    ball = sphere(0.07, (0, 0, 0.38), 16, 10, "finial"); assign(ball, wal); parts.append(ball)
    # player-side aprons: scalloped, deep at the legs and arching up to a thin rail in the middle
    for sy in (-1, 1):
        n = 24; verts = []; w = 2 * lx - 0.15
        for i in range(n + 1):
            t = i / n; x = -w / 2 + w * t
            d = 0.05 + 0.20 * (abs(2 * t - 1) ** 2.4)
            verts.append((x, 0, lh)); verts.append((x, 0, lh - d))
        faces = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(n)]
        ap = from_pydata(verts, faces, "scallop")
        sol = ap.modifiers.new("s", "SOLIDIFY"); sol.thickness = 0.05; apply_mods(ap)
        ap.location = (0, sy * ly, 0); bake_xform(ap); bevel(ap, 0.006, 2); assign(ap, wal); parts.append(ap)
    t = join(parts, "CS_Table"); smooth(t, 35)
    return t


def build_chair():
    wal = walnut("ch_walnut", 1.2); lea = mat_leather("ch_leather", base=(0.22, 0.04, 0.025), dark=(0.06, 0.01, 0.006), scale=1.5, rough=0.45)
    brass = mat_gold("ch_brass", base=(0.30, 0.18, 0.06), worn=(0.9, 0.7, 0.38))
    parts = []
    SW, SD, SH = 1.9, 1.5, 1.35   # seat width, depth (front edge at -y), seat top height (cushion top)
    frame_h = SH - 0.14
    # seat frame
    sf = box((SW, SD, 0.12), (0, 0, frame_h - 0.06), name="seatframe"); bevel(sf, 0.02, 3); assign(sf, wal); parts.append(sf)
    # cushion: domed, buttoned leather
    cu = box((SW - 0.1, SD - 0.1, 0.14), (0, 0, frame_h + 0.07), name="cushion")
    bm = bmesh.new(); bm.from_mesh(cu.data)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=6, use_grid_fill=True)
    for v in bm.verts:
        if v.co.z > frame_h + 0.07:
            u = v.co.x / (SW / 2); w_ = v.co.y / (SD / 2)
            v.co.z += 0.035 * max(0, 1 - u * u) * max(0, 1 - w_ * w_)
    bm.to_mesh(cu.data); bm.free()
    bevel(cu, 0.03, 3, 25); subsurf(cu, 1); assign(cu, lea); parts.append(cu)
    for ix in (-1, 0, 1):
        for iy in (-1, 0, 1):
            b = sphere(0.025, (ix * 0.45, iy * 0.42, SH + 0.022 - 0.01 * (abs(ix) + abs(iy))), 10, 6, "button"); assign(b, lea); parts.append(b)
    # brass nail heads round the seat rail
    per = []
    for i in range(22): per.append((-SW / 2 + SW * (i + 0.5) / 22, -SD / 2 - 0.004))
    for i in range(16): per.append((-SW / 2 - 0.004, -SD / 2 + SD * (i + 0.5) / 16)); per.append((SW / 2 + 0.004, -SD / 2 + SD * (i + 0.5) / 16))
    for (x, y) in per:
        nl = sphere(0.016, (x, y, frame_h - 0.02), 8, 5, "nail"); assign(nl, brass); parts.append(nl)
    # front legs: turned
    fh = frame_h - 0.12
    for sx in (-1, 1):
        prof = [(0.0, 0.0), (0.05, 0.0), (0.07, 0.03), (0.07, 0.06), (0.05, 0.09), (0.045, 0.30), (0.06, 0.45), (0.07, 0.55), (0.05, 0.65),
                (0.045, 0.80), (0.06, 0.86), (0.06, 0.90), (0.075, fh - 0.12), (0.0, fh - 0.12)]
        lg = lathe(prof, 16, "fleg"); lg.location = (sx * (SW / 2 - 0.1), -SD / 2 + 0.1, 0); bake_xform(lg); assign(lg, wal); parts.append(lg)
        bl = box((0.15, 0.15, 0.14), (sx * (SW / 2 - 0.1), -SD / 2 + 0.1, fh - 0.06), name="fblock"); bevel(bl, 0.01, 2); assign(bl, wal); parts.append(bl)
    # back legs: square, tapering, raked, rising into the back posts
    BH = 4.25
    rake = math.radians(9)
    for sx in (-1, 1):
        pts = [(sx * (SW / 2 - 0.09), SD / 2 - 0.09 + 0.12, 0.0), (sx * (SW / 2 - 0.09), SD / 2 - 0.09, frame_h),
               (sx * (SW / 2 - 0.1), SD / 2 - 0.09 + math.tan(rake) * (BH - frame_h), BH)]
        post = tube_along(pts, 0.095, 4, "post", radii=[1.0, 1.0, 0.85]); bevel(post, 0.01, 2); assign(post, wal); parts.append(post)
        fin = lathe([(0.0, 0.0), (0.05, 0.0), (0.065, 0.04), (0.05, 0.08), (0.03, 0.1), (0.04, 0.13), (0.0, 0.17)], 12, "postfin")
        fin.location = pts[-1]; bake_xform(fin); assign(fin, wal); parts.append(fin)
    def back_y(z):
        return SD / 2 - 0.09 + math.tan(rake) * max(0, z - frame_h)
    # crest rail: shaped, bowed, with carved ears
    cz = BH - 0.22
    crest = []
    n = 20
    for i in range(n + 1):
        t = i / n; x = -SW / 2 + 0.1 + (SW - 0.2) * t
        crest.append((x, back_y(cz) + 0.06 * math.sin(math.pi * t), cz + 0.10 * math.sin(math.pi * t) ** 1.5))
    cr = tube_along(crest, 0.12, 8, "crest")
    for v in cr.data.vertices: v.co.y = back_y(cz) + (v.co.y - back_y(cz)) * 0.5
    assign(cr, wal); parts.append(cr)
    for sx in (-1, 1):
        ear = torus(0.07, 0.025, (sx * (SW / 2 - 0.12), back_y(cz) + 0.01, cz + 0.06), (math.pi / 2, 0, 0), 14, 6, "ear"); assign(ear, wal); parts.append(ear)
    # lower back rail
    lr = box((SW - 0.2, 0.07, 0.12), (0, back_y(frame_h + 0.3), frame_h + 0.3), (rake, 0, 0), "lrail"); bevel(lr, 0.012, 2); assign(lr, wal); parts.append(lr)
    # vase splat, pierced: outer vase outline with an inner vase-shaped piercing, filled between, then thickened
    z0, z1 = frame_h + 0.36, cz - 0.08
    m = 22
    def vase(t, k):
        return k * (0.13 + 0.21 * math.sin(math.pi * min(1, t * 1.2)) ** 1.3 + 0.14 * t ** 3)
    bm = bmesh.new()
    outer, inner = [], []
    for side in (-1, 1):
        rng_ = range(m + 1) if side == 1 else range(m, -1, -1)
        for i in rng_:
            t = i / m; z = z0 + (z1 - z0) * t
            outer.append(bm.verts.new((side * vase(t, 1.0), back_y(z), z)))
    zi0, zi1 = z0 + (z1 - z0) * 0.22, z0 + (z1 - z0) * 0.8
    for side in (-1, 1):
        rng_ = range(m + 1) if side == 1 else range(m, -1, -1)
        for i in rng_:
            t = i / m; z = zi0 + (zi1 - zi0) * t
            tt = 0.22 + 0.58 * t
            w = max(0.02, vase(tt, 1.0) - 0.11) * math.sin(math.pi * t) ** 0.5
            inner.append(bm.verts.new((side * w, back_y(z), z)))
    edges = []
    for loop in (outer, inner):
        for i in range(len(loop)):
            a, b = loop[i], loop[(i + 1) % len(loop)]
            if a.co != b.co:
                edges.append(bm.edges.new((a, b)))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bm.edges[:])
    me = bpy.data.meshes.new("splat"); bm.to_mesh(me); bm.free()
    sp = bpy.data.objects.new("splat", me); bpy.context.collection.objects.link(sp)
    so = sp.modifiers.new("s", "SOLIDIFY"); so.thickness = 0.05; so.offset = 0; apply_mods(sp)
    bevel(sp, 0.008, 2, 40); assign(sp, wal); parts.append(sp)
    # side stretchers + front stretcher (turned)
    for sx in (-1, 1):
        s = cyl(0.03, SD - 0.2, (sx * (SW / 2 - 0.1), 0.02, 0.35), (math.pi / 2, 0, 0), 10, "sst"); assign(s, wal); parts.append(s)
    s = cyl(0.03, SW - 0.2, (0, -SD / 2 + 0.1, 0.5), (0, math.pi / 2, 0), 10, "fst"); assign(s, wal); parts.append(s)
    c = join(parts, "CS_Chair"); smooth(c, 35)
    return c


def build_board():
    frame = walnut("bd_frame", 2.0); light = maple("bd_light", 3.0); dark = walnut("bd_dark", 3.0)
    brass = mat_gold("bd_brass", base=(0.32, 0.2, 0.07), worn=(0.95, 0.75, 0.42))
    parts = []
    play = 8 * SQ
    W = play + 2 * 0.09
    slab = box((W, W, 0.05), (0, 0, 0.025), name="slab"); bevel(slab, 0.012, 3); assign(slab, frame); parts.append(slab)
    lip = 0.065
    for sx in (-1, 1):
        r = box((0.09, W, lip), (sx * (W / 2 - 0.045), 0, lip / 2), name="rail"); bevel(r, 0.012, 3); assign(r, frame); parts.append(r)
    for sy in (-1, 1):
        r = box((W - 0.18, 0.09, lip), (0, sy * (W / 2 - 0.045), lip / 2), name="rail"); bevel(r, 0.008, 2); assign(r, frame); parts.append(r)
    # brass stringing round the play area
    for sx in (-1, 1):
        parts.append(assign(box((0.008, play + 0.016, 0.004), (sx * (play / 2 + 0.008), 0, 0.058)), brass))
    for sy in (-1, 1):
        parts.append(assign(box((play + 0.016, 0.008, 0.004), (0, sy * (play / 2 + 0.008), 0.058)), brass))
    # 64 inlaid tiles, grain alternating direction, a hair's groove between them
    for i in range(8):
        for j in range(8):
            x = -play / 2 + SQ * (i + 0.5); y = -play / 2 + SQ * (j + 0.5)
            t = box((SQ - 0.004, SQ - 0.004, 0.012), (x, y, 0.054), name="tile"); bevel(t, 0.0015, 1)
            assign(t, light if (i + j) % 2 == 1 else dark); parts.append(t)
    # brass file and rank letters (white sits at -y)
    for i, ch in enumerate("abcdefgh"):
        x = -play / 2 + SQ * (i + 0.5)
        for sy, rot in ((-1, 0), (1, math.pi)):
            t = text_mesh(ch, 0.05, (x, sy * (W / 2 - 0.045), lip + 0.0005), (0, 0, rot)); assign(t, brass); parts.append(t)
    for j in range(8):
        y = -play / 2 + SQ * (j + 0.5)
        for sx, rot in ((-1, 0), (1, math.pi)):
            t = text_mesh(str(j + 1), 0.05, (sx * (W / 2 - 0.045), y, lip + 0.0005), (0, 0, rot)); assign(t, brass); parts.append(t)
    b = join(parts, "CS_Board"); smooth(b, 30)
    return b


def build_clock():
    wal = walnut("ck_walnut", 3.0)
    face = mat_cloth("ck_face", base=(0.82, 0.78, 0.68), dirt=(0.5, 0.45, 0.35), scale=4.0)
    ink = mat_cloth("ck_ink", base=(0.02, 0.02, 0.02), dirt=(0.01, 0.01, 0.01), scale=4.0)
    red = mat_paint("ck_red", paint=(0.55, 0.02, 0.02), chip=0.2)
    brass = mat_gold("ck_brass", base=(0.32, 0.2, 0.07), worn=(0.95, 0.75, 0.42))
    glass = mat_cloth("ck_glass", base=(0.06, 0.07, 0.07), dirt=(0.03, 0.03, 0.03), scale=2.0)
    parts = []
    L, D, H = 0.56, 0.2, 0.26   # length along y (between the players), depth along x, height
    # case: front (dial side, -x) leans back 12 degrees
    lean = math.radians(12)
    verts = [(-D / 2, -L / 2, 0), (D / 2, -L / 2, 0), (D / 2, L / 2, 0), (-D / 2, L / 2, 0),
             (-D / 2 + math.tan(lean) * H, -L / 2, H), (D / 2, -L / 2, H), (D / 2, L / 2, H), (-D / 2 + math.tan(lean) * H, L / 2, H)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    case = from_pydata(verts, faces, "case")
    sel([case]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    bevel(case, 0.012, 3, 30); assign(case, wal); parts.append(case)
    plinth = box((D + 0.03, L + 0.03, 0.025), (0, 0, 0.0125), name="plinth"); bevel(plinth, 0.008, 2); assign(plinth, wal); parts.append(plinth)
    n = Vector((-math.cos(lean), 0, math.sin(lean)))
    for sy in (-1, 1):
        c = Vector((-D / 2 + math.tan(lean) * H * 0.5, sy * L / 4, H * 0.5)) + n * 0.002
        rot = (0, -math.pi / 2 - lean, 0)
        bez = torus(0.085, 0.012, c, rot, 32, 8, "bezel"); assign(bez, brass); parts.append(bez)
        dial = cyl(0.083, 0.004, c - n * 0.002, rot, 32, "dial"); assign(dial, face); parts.append(dial)
        for k in range(12):
            a = k / 12 * TAU
            tick = box((0.003, 0.004, 0.018 if k % 3 == 0 else 0.010), (0, 0, 0), name="tick")
            local = Vector((0, math.sin(a) * 0.066, math.cos(a) * 0.066))
            tick.rotation_euler = (a, 0, 0); tick.location = local; bake_xform(tick)
            tick.rotation_euler = rot; tick.location = c + n * 0.0015; bake_xform(tick)
            assign(tick, ink); parts.append(tick)
        # red flag hanging near 12 o'clock
        fl = box((0.004, 0.02, 0.028), (0, 0, 0), name="flag"); fl.location = c + Vector((0, 0.012, 0.055)) + n * 0.004; bake_xform(fl); assign(fl, red); parts.append(fl)
        # glass ring cap
        gl = torus(0.08, 0.004, c + n * 0.008, rot, 32, 4, "glass"); assign(gl, glass); parts.append(gl)
    # brass name plate
    pl = box((0.004, 0.09, 0.02), Vector((-D / 2 + math.tan(lean) * H * 0.12, 0, H * 0.12)) + n * 0.003, (0, -lean, 0), "plate"); assign(pl, brass); parts.append(pl)
    ck = join(parts, "CS_Clock"); smooth(ck, 30)
    # one plunger button (cloned twice in Roblox)
    btn = join([assign(lathe([(0.0, 0.0), (0.02, 0.0), (0.02, 0.05), (0.035, 0.055), (0.04, 0.065), (0.035, 0.075), (0.0, 0.078)], 20, "btn"), red)], "CS_ClockBtn")
    smooth(btn, 30)
    return ck, btn


def build():
    t = build_table()
    c = build_chair(); c.rotation_euler = (0, 0, math.pi); bake_xform(c)
    c.location = (0, -2.0 + 0.05, 0); bake_xform(c)
    b = build_board(); b.location = (0, 0, TOP); bake_xform(b)
    ck, btn = build_clock(); ck.location = (TX / 2 - 0.2, 0, TOP); bake_xform(ck)
    btn.location = (TX / 2 - 0.2, -0.14, TOP + 0.26); bake_xform(btn)
    PREVIEW["extra"][0]["target"] = Vector((0.3, 0, TOP + 0.1))
    return {"Table": (t, 1024, False), "Chair": (c, 1024, False), "Board": (b, 1024, False), "Clock": (ck, 512, False), "ClockBtn": (btn, 128, False)}


def before_bake(pieces):
    for o, _, _ in pieces.values():
        sel([o]); bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
