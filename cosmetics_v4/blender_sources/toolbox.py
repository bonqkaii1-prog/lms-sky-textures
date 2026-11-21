"""Administrator's Toolkit (Builderman): a battered red steel toolbox -- rolled-lip body with pressed ribs,
dents, chipped paint showing bare steel, corner guards, two latches and a fold-down handle; the lid (its own
piece, so it can bounce) sits cracked open on its hinge; a combination wrench, a screwdriver, a claw hammer
and a tape measure stick out; a webbing strap with a buckle holds it on."""
from kit import *
KEY = "toolbox"
PREVIEW = {"main": {"elev": 22, "azim": -32, "dist": 0.9}, "extra": [{"elev": 40, "azim": 25, "dist": 0.85}]}

def build():
    paint = mat_paint("tb_paint", paint=(0.42, 0.025, 0.018), chip=0.6)
    steel = mat_iron("tb_steel", base=(0.12, 0.115, 0.11), worn=(0.55, 0.54, 0.52), rust_k=0.15, rough=0.4, metal=1.0)
    yellow = mat_paint("tb_yellow", paint=(0.75, 0.45, 0.02), chip=0.4, metal_col=(0.2, 0.2, 0.2))
    black = mat_leather("tb_rubber", base=(0.03, 0.03, 0.03), dark=(0.01, 0.01, 0.01), scale=2, rough=0.8)
    W, D, H = 1.3, 0.62, 0.55
    body = box((W, D, H), (0, 0, H / 2), name="body"); bevel(body, 0.04, 3, 40)
    # pressed ribs on the front/back + a rolled lip round the top
    parts = [body]
    for sy in (-1, 1):
        for k in range(3):
            rb = box((W * 0.82, 0.02, 0.035), (0, sy * D / 2, 0.12 + k * 0.13), name="rib"); bevel(rb, 0.012, 2); parts.append(rb)
    lip = box((W + 0.03, D + 0.03, 0.05), (0, 0, H - 0.02), name="lip"); bevel(lip, 0.02, 2); parts.append(lip)
    bodyp = join(parts, "bodyp"); displace(bodyp, 0.012, 0.35); assign(bodyp, paint)
    hw = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            g = box((0.14, 0.14, 0.14), (sx * (W / 2 - 0.04), sy * (D / 2 - 0.04), 0.05), name="guard"); bevel(g, 0.03, 2); hw.append(g)
        lt = box((0.12, 0.04, 0.16), (sx * 0.36, -D / 2 - 0.02, H - 0.08), name="latch"); bevel(lt, 0.01, 1); hw.append(lt)
        sh = torus(0.08, 0.018, (sx * (W / 2 + 0.02), 0, H * 0.6), (0, math.pi / 2, 0), 12, 6, "sidehandle"); hw.append(sh)
    for i in range(6):
        hw.append(sphere(0.014, (-W / 2 + 0.1 + i * 0.22, -D / 2 - 0.012, 0.05), 8, 5, "rivet"))
    hwj = join(hw, "hw"); assign(hwj, steel)
    box_ = join([bodyp, hwj], "Box"); smooth(box_, 30)
    # lid: a shallow tray hinged at the back edge, open ~22 degrees, with a fold handle on top
    lidb = box((W + 0.04, D + 0.04, 0.12), (0, 0, 0.06), name="lid"); bevel(lidb, 0.035, 3, 40)
    for k in range(2):
        rb = box((W * 0.7, 0.03, 0.02), (0, -0.12 + k * 0.24, 0.125), name="lrib"); bevel(rb, 0.008, 1); lidb = join([lidb, rb], "lid")
    displace(lidb, 0.008, 0.3); assign(lidb, paint)
    hp = [(-0.3, 0, 0.12), (-0.3, 0, 0.2), (-0.22, 0, 0.26), (0.22, 0, 0.26), (0.3, 0, 0.2), (0.3, 0, 0.12)]
    handle = tube_along(hp, 0.025, 8, "handle"); assign(handle, black)
    grip = cyl(0.04, 0.4, (0, 0, 0.26), (0, math.pi / 2, 0), 10, "hgrip"); assign(grip, black)
    lid = join([lidb, handle, grip], "Lid")
    lid.matrix_world = Matrix.Translation((0, D / 2, H)) @ Matrix.Rotation(math.radians(-22), 4, "X") @ Matrix.Translation((0, -D / 2 - 0.02, 0)); bake_xform(lid); smooth(lid, 30)
    # tools
    tools = []
    # combination wrench
    wb = box((0.06, 0.02, 0.62), (0, 0, 0.31), name="wshaft"); bevel(wb, 0.008, 1)
    ring = torus(0.07, 0.025, (0, 0, 0.66), (math.pi / 2, 0, 0), 12, 6, "wring")
    jaw = cyl(0.075, 0.03, (0, 0, -0.02), (math.pi / 2, 0, 0), 6, "wjaw")
    cut = box((0.06, 0.06, 0.1), (0, 0, -0.07), name="cut")
    bm = jaw.modifiers.new("b", "BOOLEAN"); bm.object = cut; bm.operation = "DIFFERENCE"; apply_mods(jaw); bpy.data.objects.remove(cut)
    wrench = join([wb, ring, jaw], "wrench"); assign(wrench, steel)
    wrench.matrix_world = Matrix.Translation((-0.38, 0.05, H - 0.2)) @ Matrix.Rotation(math.radians(-14), 4, "Y") @ Matrix.Rotation(math.radians(10), 4, "X"); bake_xform(wrench); tools.append(wrench)
    # screwdriver
    sdh = lathe([(0.0, 0.0), (0.05, 0.02), (0.06, 0.08), (0.055, 0.22), (0.045, 0.26), (0.02, 0.27)], 8, "sdh"); assign(sdh, yellow)
    sds = cyl(0.014, 0.42, (0, 0, 0.47), n=8, name="sds"); assign(sds, steel)
    sdt = cone(0.014, 0.05, (0, 0, 0.7), n=4, name="sdt", r2=0.004); assign(sdt, steel)
    sd = join([sdh, sds, sdt], "sd"); sd.matrix_world = Matrix.Translation((-0.1, -0.1, H - 0.15)) @ Matrix.Rotation(math.radians(160), 4, "X") @ Matrix.Rotation(math.radians(-15), 4, "Y")
    bake_xform(sd); tools.append(sd)
    # claw hammer
    hh = lathe([(0.0, 0.0), (0.035, 0.0), (0.032, 0.5), (0.03, 0.62), (0.0, 0.62)], 10, "hh"); assign(hh, black)
    head = box((0.08, 0.06, 0.08), (0, 0, 0.66), name="hhead"); bevel(head, 0.01, 1)
    face = cyl(0.045, 0.1, (-0.1, 0, 0.66), (0, math.pi / 2, 0), 12, "hface")
    claw = tube_along([(0.04, 0, 0.66), (0.14, 0, 0.66), (0.22, 0, 0.6)], 0.03, 6, "claw", radii=[1, 0.8, 0.3]); claw.scale = (1, 1.5, 1); bake_xform(claw)
    hm = join([head, face, claw], "hm"); assign(hm, steel)
    hammer = join([hh, hm], "hammer"); hammer.matrix_world = Matrix.Translation((0.3, 0.02, H - 0.35)) @ Matrix.Rotation(math.radians(18), 4, "Y"); bake_xform(hammer); tools.append(hammer)
    # tape measure
    tape = box((0.18, 0.08, 0.18), (0.0, 0.0, 0.0), name="tape"); bevel(tape, 0.04, 3); assign(tape, yellow)
    blade = box((0.3, 0.02, 0.004), (0.22, -0.03, -0.07), name="tblade"); assign(blade, yellow)
    tp = join([tape, blade], "tape"); tp.matrix_world = Matrix.Translation((0.05, 0.1, H + 0.02)) @ Matrix.Rotation(math.radians(-30), 4, "Z") @ Matrix.Rotation(math.radians(20), 4, "X"); bake_xform(tp); tools.append(tp)
    toolsj = join(tools, "Tools"); smooth(toolsj, 35)
    # webbing strap with a buckle (wraps under and round the box; Roblox puts it against the back)
    strap_m = mat_cloth("tb_strap", base=(0.08, 0.08, 0.09), dirt=(0.03, 0.03, 0.03), scale=3)
    sp = [(-W / 2 - 0.03, D / 2 + 0.02, 0.15), (-W / 2 - 0.03, D / 2 + 0.02, H * 0.7), (-W / 2 - 0.03, 0.0, H + 0.03), (-W / 2 - 0.03, -D / 2 - 0.04, H * 0.7), (-W / 2 - 0.03, -D / 2 - 0.04, 0.1)]
    straps = []
    for sx in (-0.38, 0.38):
        pts = [(sx, p[1], p[2]) for p in sp]
        s = box((0.16, 0.012, 1), (0, 0, 0), name="s"); s.scale = (1, 1, 1)
        st = tube_along(pts, 1.0, 4, "strap")
        bm = bmesh.new(); bm.from_mesh(st.data)
        for i, v in enumerate(bm.verts):
            c = Vector(pts[min(i // 4, 4)]); d = v.co - c; v.co = c + Vector((d.x * 0.08, d.y * 0.01, d.z * 0.01))
        bm.to_mesh(st.data); bm.free(); bpy.data.objects.remove(s); straps.append(st)
        bk = box((0.2, 0.03, 0.12), (sx, -D / 2 - 0.05, H * 0.4), name="buckle"); bevel(bk, 0.01, 1); bk.data.materials.append(steel); straps.append(bk)
    for s in straps:
        if not s.data.materials: s.data.materials.append(strap_m)
    strapj = join(straps, "Straps")
    return {"Box": (box_, 1024, False), "Lid": (lid, 512, False), "Tools": (toolsj, 1024, False), "Straps": (strapj, 512, False)}
