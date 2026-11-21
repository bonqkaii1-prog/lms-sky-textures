"""Blender (bpy 5.3, headless) toolkit for the Shattered Memories cosmetics.
Model -> join per Roblox MeshPart -> UV -> bake PBR (color, normal, roughness, metalness, emissive mask) -> FBX.
Units: 1 Blender unit = 1 stud. Z up in Blender; exported Y up / -Z forward for Roblox."""
import bpy, bmesh, math, random, os, json
from mathutils import Vector, Matrix, Euler

OUT = "/home/claude/cos/out"
TAU = math.tau


# ---------------------------------------------------------------- scene
def reset(samples=48):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    try:
        sc.cycles.use_denoising = True
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
    w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.03, 0.032, 0.04, 1); bg.inputs[1].default_value = 0.6
    return sc


def sel(objs, active=None):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or objs[0]


def apply_mods(o):
    sel([o])
    for m in list(o.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=m.name)
        except Exception as e:
            print("apply fail", o.name, m.name, e)


def xform(o, loc=(0, 0, 0), rot=(0, 0, 0), scale=None):
    o.location = Vector(loc)
    o.rotation_euler = Euler(rot)
    if scale is not None:
        o.scale = Vector(scale) if hasattr(scale, "__len__") else Vector((scale, scale, scale))
    return o


def bake_xform(o):
    sel([o]); bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o


# ---------------------------------------------------------------- primitives
def box(size, loc=(0, 0, 0), rot=(0, 0, 0), name="box"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = Vector(size)
    bake_xform(o); return o


def cyl(r, h, loc=(0, 0, 0), rot=(0, 0, 0), n=24, name="cyl", r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=n, radius=r, depth=h, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=n, radius1=r, radius2=r2, depth=h, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; return bake_xform(o)


def cone(r, h, loc=(0, 0, 0), rot=(0, 0, 0), n=16, name="cone", r2=0.0):
    bpy.ops.mesh.primitive_cone_add(vertices=n, radius1=r, radius2=r2, depth=h, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; return bake_xform(o)


def sphere(r, loc=(0, 0, 0), seg=16, ring=8, name="sph"):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=ring, radius=r, location=loc)
    o = bpy.context.object; o.name = name; return bake_xform(o)


def ico(r, loc=(0, 0, 0), sub=1, name="ico"):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=loc)
    o = bpy.context.object; o.name = name; return bake_xform(o)


def torus(R, r, loc=(0, 0, 0), rot=(0, 0, 0), maj=16, mnr=8, name="tor"):
    bpy.ops.mesh.primitive_torus_add(major_segments=maj, minor_segments=mnr, major_radius=R, minor_radius=r, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; return bake_xform(o)


def from_pydata(verts, faces, name="mesh"):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); return o


def lathe(profile, n=32, name="lathe", axis="Z"):
    """profile: list of (radius, height). Revolved round Z."""
    verts, faces = [], []
    m = len(profile)
    for i in range(n):
        a = TAU * i / n
        for (r, h) in profile:
            verts.append((r * math.cos(a), r * math.sin(a), h))
    for i in range(n):
        j = (i + 1) % n
        for k in range(m - 1):
            faces.append((i * m + k, j * m + k, j * m + k + 1, i * m + k + 1))
    o = from_pydata(verts, faces, name)
    sel([o]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=1e-5); bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    return o


def tube_along(points, radius, n=10, name="tube", radii=None, twist=0.0, cap=True):
    """sweep a circle along a polyline (list of Vector). radii: per-point radius multipliers."""
    pts = [Vector(p) for p in points]
    verts, faces = [], []
    prev_n = None
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        if prev_n is None:
            up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
            nrm = t.cross(up).normalized()
        else:
            nrm = (prev_n - t * prev_n.dot(t)).normalized()
        prev_n = nrm
        bin_ = t.cross(nrm)
        r = radius * (radii[i] if radii else 1.0)
        for k in range(n):
            a = TAU * k / n + twist * i
            verts.append(p + (nrm * math.cos(a) + bin_ * math.sin(a)) * r)
    for i in range(len(pts) - 1):
        for k in range(n):
            a, b = i * n + k, i * n + (k + 1) % n
            faces.append((a, b, b + n, a + n))
    if cap:
        faces.append(tuple(range(n))[::-1])
        last = (len(pts) - 1) * n
        faces.append(tuple(range(last, last + n)))
    o = from_pydata([tuple(v) for v in verts], faces, name)
    sel([o]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.object.mode_set(mode="OBJECT")
    return o


def chain_along(points, link_len=0.16, link_w=0.09, wire=0.018, name="chain"):
    """real interlocking links laid along a polyline, alternating 90 degrees."""
    pts = [Vector(p) for p in points]
    seg = []
    total = 0
    for i in range(len(pts) - 1):
        d = (pts[i + 1] - pts[i]).length; seg.append(d); total += d
    step = link_len * 0.78
    links = []
    s = 0.0; idx = 0
    def at(sv):
        acc = 0
        for i, d in enumerate(seg):
            if acc + d >= sv:
                u = (sv - acc) / d
                return pts[i].lerp(pts[i + 1], u), (pts[i + 1] - pts[i]).normalized()
            acc += d
        return pts[-1], (pts[-1] - pts[-2]).normalized()
    k = 0
    while s <= total:
        p, t = at(s)
        o = torus(1, wire / (link_w / 2), maj=14, mnr=6, name=f"{name}_{k}")
        # stretch into an oval link: long axis along X, then aim X at the tangent
        o.scale = Vector((link_len / 2, link_w / 2, link_w / 2)); bake_xform(o)
        rot = t.to_track_quat("X", "Z").to_matrix().to_4x4()
        spin = Matrix.Rotation(math.pi / 2 * (k % 2), 4, "X")
        o.matrix_world = Matrix.Translation(p) @ rot @ spin
        bake_xform(o)
        links.append(o); s += step; k += 1
    return join(links, name)


def helix(p0, p1, radius, turns, n=80, phase=0.0):
    a, b = Vector(p0), Vector(p1)
    ax = (b - a).normalized()
    up = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(up).normalized(); v = ax.cross(u)
    out = []
    for i in range(n + 1):
        t = i / n
        ang = phase + TAU * turns * t
        out.append(a.lerp(b, t) + (u * math.cos(ang) + v * math.sin(ang)) * radius)
    return out


def join(objs, name):
    objs = [o for o in objs if o]
    if len(objs) == 1:
        objs[0].name = name; return objs[0]
    for o in objs:
        if o.modifiers: apply_mods(o)
    sel(objs, objs[0]); bpy.ops.object.join()
    o = bpy.context.object; o.name = name; return o


# ---------------------------------------------------------------- modifiers
def bevel(o, w=0.02, seg=2, angle=35, clamp=True):
    m = o.modifiers.new("bevel", "BEVEL"); m.width = w; m.segments = seg; m.limit_method = "ANGLE"
    m.angle_limit = math.radians(angle); m.use_clamp_overlap = clamp; m.harden_normals = False
    return m


def subsurf(o, lv=1):
    m = o.modifiers.new("sub", "SUBSURF"); m.levels = lv; m.render_levels = lv; return m


def wnormal(o):
    m = o.modifiers.new("wn", "WEIGHTED_NORMAL"); m.keep_sharp = True; return m


def displace(o, strength=0.02, scale=0.6, kind="CLOUDS", detail=2):
    tex = bpy.data.textures.new(f"d_{o.name}", type=kind)
    if kind == "CLOUDS":
        tex.noise_scale = scale; tex.noise_depth = detail
    elif kind == "VORONOI":
        tex.noise_scale = scale
    m = o.modifiers.new("disp", "DISPLACE"); m.texture = tex; m.strength = strength; m.texture_coords = "OBJECT"
    return m


def smooth(o, deg=40):
    sel([o])
    for p in o.data.polygons: p.use_smooth = True
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(deg))
    except Exception:
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(deg))
        except Exception:
            pass
    return o


def flat(o):
    for p in o.data.polygons: p.use_smooth = False
    return o


def remesh_voxel(o, size=0.02):
    m = o.modifiers.new("rm", "REMESH"); m.mode = "VOXEL"; m.voxel_size = size; return m


def decimate(o, ratio):
    m = o.modifiers.new("dec", "DECIMATE"); m.ratio = ratio; return m


def tris(o):
    dg = bpy.context.evaluated_depsgraph_get(); e = o.evaluated_get(dg); me = e.to_mesh()
    n = sum(len(p.vertices) - 2 for p in me.polygons); e.to_mesh_clear(); return n


# ---------------------------------------------------------------- materials (procedural, baked later)
def _nt(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (900, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (600, 0)
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return nt, bsdf, out


def _tex_coord(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord"); return tc


def _noise(nt, scale=6.0, detail=6.0, rough=0.55, coord=None, dim="3D"):
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    if coord is not None: nt.links.new(coord, n.inputs["Vector"])
    return n


def _ramp(nt, src, stops):
    r = nt.nodes.new("ShaderNodeValToRGB"); nt.links.new(src, r.inputs[0])
    els = r.color_ramp.elements
    while len(els) > 1: els.remove(els[-1])
    for i, (pos, col) in enumerate(stops):
        e = els[0] if i == 0 else els.new(pos)
        e.position = pos; e.color = col if len(col) == 4 else (*col, 1)
    return r


def _math(nt, op, a, b=None, clamp=False):
    m = nt.nodes.new("ShaderNodeMath"); m.operation = op; m.use_clamp = clamp
    for i, v in enumerate([a, b]):
        if v is None: continue
        if isinstance(v, (int, float)): m.inputs[i].default_value = v
        else: nt.links.new(v, m.inputs[i])
    return m.outputs[0]


def _mix(nt, fac, a, b):
    m = nt.nodes.new("ShaderNodeMix"); m.data_type = "RGBA"
    if isinstance(fac, (int, float)): m.inputs["Factor"].default_value = fac
    else: nt.links.new(fac, m.inputs["Factor"])
    for sock, v in ((m.inputs[6], a), (m.inputs[7], b)):
        if isinstance(v, tuple): sock.default_value = v if len(v) == 4 else (*v, 1)
        else: nt.links.new(v, sock)
    return m.outputs[2]


def _bump(nt, h, strength=0.4, dist=0.02, normal=None):
    b = nt.nodes.new("ShaderNodeBump"); b.inputs["Strength"].default_value = strength; b.inputs["Distance"].default_value = dist
    nt.links.new(h, b.inputs["Height"])
    if normal is not None: nt.links.new(normal, b.inputs["Normal"])
    return b.outputs[0]


def _edges(nt, lo=0.53, k=5.0):
    """worn-edge mask from a bevel-normal difference (reliable on game-res meshes, unlike pointiness)"""
    bv = nt.nodes.new("ShaderNodeBevel"); bv.samples = 6; bv.inputs["Radius"].default_value = 0.012
    g = nt.nodes.new("ShaderNodeNewGeometry")
    dp = nt.nodes.new("ShaderNodeVectorMath"); dp.operation = "DOT_PRODUCT"
    nt.links.new(bv.outputs[0], dp.inputs[0]); nt.links.new(g.outputs["Normal"], dp.inputs[1])
    d = _math(nt, "SUBTRACT", 1.0, dp.outputs["Value"])
    return _math(nt, "MULTIPLY", d, 14.0, clamp=True)


def _ao(nt, dist=0.15):
    a = nt.nodes.new("ShaderNodeAmbientOcclusion"); a.inputs["Distance"].default_value = dist; a.samples = 8
    return a.outputs["AO"]


def _img(nt, path, coord, proj="BOX", blend=0.2):
    im = bpy.data.images.load(path, check_existing=True)
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = im; t.projection = proj; t.projection_blend = blend
    nt.links.new(coord, t.inputs["Vector"]); return t


def _set_emit(nt, bsdf, mask, color, strength):
    """emission = mask * color; the mask socket is tagged so the bake can find it"""
    bsdf.inputs["Emission Color"].default_value = (*color, 1)
    s = _math(nt, "MULTIPLY", mask, strength)
    nt.links.new(s, bsdf.inputs["Emission Strength"])
    tag = nt.nodes.new("ShaderNodeMath"); tag.operation = "ADD"; tag.name = "EMASK"; tag.label = "EMASK"
    nt.links.new(mask, tag.inputs[0]); tag.inputs[1].default_value = 0.0


def mat_iron(name="iron", base=(0.028, 0.026, 0.026), worn=(0.3, 0.285, 0.27), rust=(0.16, 0.06, 0.03), rust_k=0.25,
             scorch=0.6, ember=0.0, ember_col=(1.0, 0.25, 0.04), rune=None, rune_col=(1.0, 0.16, 0.05), rune_k=18.0, rune_scale=1.0, rough=0.62, metal=0.9, pits=0.35):
    mat = bpy.data.materials.new(name); nt, bsdf, out = _nt(mat)
    tc = _tex_coord(nt)
    obj = tc.outputs["Object"]
    big = _noise(nt, 2.2, 4, 0.5, obj)
    fine = _noise(nt, 38, 8, 0.65, obj)
    edge = _edges(nt)
    ao = _ao(nt)
    # scorched base with soot variation, rust in crevices, polished worn edges
    soot = _ramp(nt, big.outputs["Fac"], [(0.35, (base[0] * 0.6, base[1] * 0.6, base[2] * 0.6)), (0.7, (base[0] * 1.8, base[1] * 1.7, base[2] * 1.6))])
    cav = _math(nt, "SUBTRACT", 1.0, ao)
    rmask = _math(nt, "MULTIPLY", _math(nt, "ADD", _math(nt, "MULTIPLY", cav, 1.6), _math(nt, "SUBTRACT", fine.outputs["Fac"], 0.45)), rust_k * 2.2, clamp=True)
    col = _mix(nt, rmask, soot.outputs[0], rust)
    wear = _math(nt, "MULTIPLY", edge, _math(nt, "ADD", _math(nt, "MULTIPLY", fine.outputs["Fac"], 0.9), -0.05), clamp=True)
    col = _mix(nt, wear, col, worn)
    if rune:
        rt = _img(nt, rune, _math_vec_scale(nt, obj, rune_scale), "BOX", 0.15)
        rmk = _math(nt, "GREATER_THAN", rt.outputs["Color"], 0.5)
        # engraved: darken around the glyph, glow inside
        col = _mix(nt, rmk, col, (0.05, 0.01, 0.0))
        _set_emit(nt, bsdf, rmk, rune_col, rune_k)
        hgt = _math(nt, "SUBTRACT", _math(nt, "MULTIPLY", fine.outputs["Fac"], pits), _math(nt, "MULTIPLY", rmk, 0.6))
    else:
        hgt = _math(nt, "MULTIPLY", fine.outputs["Fac"], pits)
        if ember > 0:
            # charred: embers smouldering in the crevices and cracks
            cr = nt.nodes.new("ShaderNodeTexVoronoi"); cr.feature = "DISTANCE_TO_EDGE"; cr.inputs["Scale"].default_value = 9
            nt.links.new(obj, cr.inputs["Vector"])
            crk = _math(nt, "LESS_THAN", cr.outputs["Distance"], 0.014)
            emk = _math(nt, "MAXIMUM", _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", cav, 0.55), 2.0, clamp=True),
                        _math(nt, "MULTIPLY", crk, _math(nt, "MULTIPLY", big.outputs["Fac"], 1.6, clamp=True)))
            emk = _math(nt, "MULTIPLY", emk, 1.0)
            emk = _math(nt, "MULTIPLY", emk, ember, clamp=True)
            col = _mix(nt, emk, col, (ember_col[0] * 0.3, ember_col[1] * 0.3, ember_col[2] * 0.3))
            _set_emit(nt, bsdf, emk, ember_col, 10.0)
            hgt = _math(nt, "SUBTRACT", hgt, _math(nt, "MULTIPLY", crk, 0.5))
    nt.links.new(col, bsdf.inputs["Base Color"])
    r = _math(nt, "ADD", _math(nt, "MULTIPLY", big.outputs["Fac"], 0.25), rough - 0.12)
    r = _math(nt, "SUBTRACT", r, _math(nt, "MULTIPLY", wear, 0.35))
    r = _math(nt, "ADD", r, _math(nt, "MULTIPLY", rmask, 0.3), clamp=True)
    nt.links.new(r, bsdf.inputs["Roughness"])
    mt = _math(nt, "SUBTRACT", metal, _math(nt, "MULTIPLY", rmask, 0.8), clamp=True)
    nt.links.new(mt, bsdf.inputs["Metallic"])
    nt.links.new(_bump(nt, hgt, 0.35, 0.01), bsdf.inputs["Normal"])
    return mat


def _math_vec_scale(nt, vec, s):
    m = nt.nodes.new("ShaderNodeVectorMath"); m.operation = "SCALE"; m.inputs[3].default_value = s
    nt.links.new(vec, m.inputs[0]); return m.outputs[0]


def mat_leather(name="leather", base=(0.09, 0.045, 0.025), dark=(0.025, 0.012, 0.008), scale=1.0, rough=0.7, wrap=True):
    mat = bpy.data.materials.new(name); nt, bsdf, out = _nt(mat)
    tc = _tex_coord(nt); obj = tc.outputs["Object"]
    n1 = _noise(nt, 14 * scale, 8, 0.7, obj)
    cell = nt.nodes.new("ShaderNodeTexVoronoi"); cell.inputs["Scale"].default_value = 60 * scale; nt.links.new(obj, cell.inputs["Vector"])
    ao = _ao(nt, 0.08)
    col = _ramp(nt, n1.outputs["Fac"], [(0.3, dark), (0.75, base)]).outputs[0]
    col = _mix(nt, _math(nt, "SUBTRACT", 1.0, ao), col, dark)
    edge = _edges(nt)
    col = _mix(nt, _math(nt, "MULTIPLY", edge, 0.18), col, (base[0] * 1.6, base[1] * 1.6, base[2] * 1.5))
    nt.links.new(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough; bsdf.inputs["Metallic"].default_value = 0.0
    h = _math(nt, "ADD", _math(nt, "MULTIPLY", cell.outputs["Distance"], 0.5), _math(nt, "MULTIPLY", n1.outputs["Fac"], 0.5))
    nt.links.new(_bump(nt, h, 0.45, 0.006), bsdf.inputs["Normal"])
    return mat


def mat_cloth(name="cloth", base=(0.55, 0.5, 0.42), dirt=(0.16, 0.11, 0.07), blood=None, blood_k=0.0, scale=1.0):
    mat = bpy.data.materials.new(name); nt, bsdf, out = _nt(mat)
    tc = _tex_coord(nt); obj = tc.outputs["Object"]
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.inputs["Scale"].default_value = 90 * scale
    wv.inputs["Distortion"].default_value = 1.5; nt.links.new(obj, wv.inputs["Vector"])
    wv2 = nt.nodes.new("ShaderNodeTexWave"); wv2.wave_type = "BANDS"; wv2.bands_direction = "Y"; wv2.inputs["Scale"].default_value = 90 * scale; nt.links.new(obj, wv2.inputs["Vector"])
    n1 = _noise(nt, 5 * scale, 6, 0.6, obj)
    ao = _ao(nt, 0.06)
    col = _mix(nt, _math(nt, "ADD", _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", 1.0, ao), 1.3), _math(nt, "SUBTRACT", n1.outputs["Fac"], 0.35), clamp=True), base, dirt)
    if blood:
        bn = _noise(nt, 3.5 * scale, 4, 0.5, obj)
        bm = _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", bn.outputs["Fac"], 0.55), 8.0 * blood_k, clamp=True)
        col = _mix(nt, bm, col, blood)
    nt.links.new(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    h = _math(nt, "ADD", wv.outputs["Fac"], wv2.outputs["Fac"])
    nt.links.new(_bump(nt, h, 0.3, 0.004), bsdf.inputs["Normal"])
    return mat


def mat_bone(name="bone", base=(0.62, 0.55, 0.42), dark=(0.18, 0.13, 0.08), scale=1.0):
    mat = bpy.data.materials.new(name); nt, bsdf, out = _nt(mat)
    tc = _tex_coord(nt); obj = tc.outputs["Object"]
    n1 = _noise(nt, 9 * scale, 8, 0.6, obj); ao = _ao(nt, 0.1)
    st = nt.nodes.new("ShaderNodeTexWave"); st.inputs["Scale"].default_value = 18 * scale; st.inputs["Distortion"].default_value = 6
    nt.links.new(obj, st.inputs["Vector"])
    col = _ramp(nt, n1.outputs["Fac"], [(0.3, (base[0] * 0.75, base[1] * 0.72, base[2] * 0.66)), (0.7, base)]).outputs[0]
    col = _mix(nt, _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", 1.0, ao), 1.5, clamp=True), col, dark)
    nt.links.new(col, bsdf.inputs["Base Color"])
    nt.links.new(_math(nt, "ADD", _math(nt, "MULTIPLY", n1.outputs["Fac"], 0.2), 0.42), bsdf.inputs["Roughness"])
    nt.links.new(_bump(nt, _math(nt, "ADD", st.outputs["Fac"], n1.outputs["Fac"]), 0.25, 0.006), bsdf.inputs["Normal"])
    return mat


def mat_glow(name="glow", col=(1, 0.2, 0.05), base=(0.2, 0.02, 0.0), k=25.0, crack=None):
    """emissive core: crystal / energy. crack: (scale) voronoi crack glow over dark glass"""
    mat = bpy.data.materials.new(name); nt, bsdf, out = _nt(mat)
    tc = _tex_coord(nt); obj = tc.outputs["Object"]
    bsdf.inputs["Base Color"].default_value = (*base, 1)
    bsdf.inputs["Roughness"].default_value = 0.15; bsdf.inputs["Metallic"].default_value = 0.0
    if crack:
        v = nt.nodes.new("ShaderNodeTexVoronoi"); v.feature = "DISTANCE_TO_EDGE"; v.inputs["Scale"].default_value = crack; nt.links.new(obj, v.inputs["Vector"])
        m = _math(nt, "LESS_THAN", v.outputs["Distance"], 0.045)
        n = _noise(nt, 4, 3, 0.5, obj)
        mask = _math(nt, "MAXIMUM", m, _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", n.outputs["Fac"], 0.5), 2.5, clamp=True))
    else:
        n = _noise(nt, 3, 4, 0.5, obj)
        mask = _math(nt, "ADD", _math(nt, "MULTIPLY", n.outputs["Fac"], 0.5), 0.6, clamp=True)
    _set_emit(nt, bsdf, mask, col, k)
    return mat


def mat_obsidian(name="obsidian", vein=(1.0, 0.05, 0.1), vein_scale=3.0, vein_w=0.03, k=20.0, base=(0.012, 0.01, 0.014)):
    mat = bpy.data.materials.new(name); nt, bsdf, out = _nt(mat)
    tc = _tex_coord(nt); obj = tc.outputs["Object"]
    v = nt.nodes.new("ShaderNodeTexVoronoi"); v.feature = "DISTANCE_TO_EDGE"; v.inputs["Scale"].default_value = vein_scale
    nz = _noise(nt, 2.5, 4, 0.5, obj)
    warp = nt.nodes.new("ShaderNodeVectorMath"); warp.operation = "ADD"
    nt.links.new(obj, warp.inputs[0]); nt.links.new(nz.outputs["Color"], warp.inputs[1])
    nt.links.new(warp.outputs[0], v.inputs["Vector"])
    vm = _math(nt, "LESS_THAN", v.outputs["Distance"], vein_w)
    n2 = _noise(nt, 20, 6, 0.6, obj)
    edge = _edges(nt)
    col = _mix(nt, _math(nt, "MULTIPLY", edge, 0.35), base, (0.03, 0.028, 0.034))
    col = _mix(nt, vm, col, (vein[0] * 0.35, vein[1] * 0.35, vein[2] * 0.35))
    nt.links.new(col, bsdf.inputs["Base Color"])
    nt.links.new(_math(nt, "ADD", _math(nt, "MULTIPLY", n2.outputs["Fac"], 0.25), 0.12), bsdf.inputs["Roughness"])
    bsdf.inputs["Metallic"].default_value = 0.0
    _set_emit(nt, bsdf, vm, vein, k)
    nt.links.new(_bump(nt, _math(nt, "SUBTRACT", n2.outputs["Fac"], _math(nt, "MULTIPLY", vm, 0.8)), 0.3, 0.01), bsdf.inputs["Normal"])
    return mat


def mat_wood(name="wood", base=(0.22, 0.12, 0.06), dark=(0.07, 0.035, 0.018), scale=1.0, axis="Z"):
    mat = bpy.data.materials.new(name); nt, bsdf, out = _nt(mat)
    tc = _tex_coord(nt); obj = tc.outputs["Object"]
    mp = nt.nodes.new("ShaderNodeMapping"); nt.links.new(obj, mp.inputs[0])
    mp.inputs["Scale"].default_value = (12 * scale, 12 * scale, 0.6 * scale) if axis == "Z" else (0.6 * scale, 12 * scale, 12 * scale)
    nz = _noise(nt, 3, 6, 0.6, mp.outputs[0])
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "RINGS"; wv.inputs["Scale"].default_value = 1.2; wv.inputs["Distortion"].default_value = 4
    nt.links.new(mp.outputs[0], wv.inputs["Vector"])
    ao = _ao(nt, 0.08)
    col = _ramp(nt, _math(nt, "ADD", _math(nt, "MULTIPLY", wv.outputs["Fac"], 0.6), _math(nt, "MULTIPLY", nz.outputs["Fac"], 0.4)), [(0.25, dark), (0.8, base)]).outputs[0]
    col = _mix(nt, _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", 1.0, ao), 1.4, clamp=True), col, dark)
    nt.links.new(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.72
    nt.links.new(_bump(nt, wv.outputs["Fac"], 0.25, 0.006), bsdf.inputs["Normal"])
    return mat


def assign(o, mat):
    o.data.materials.clear(); o.data.materials.append(mat); return o


# ---------------------------------------------------------------- bake + export
def uv(o, margin=0.004, angle=60):
    sel([o]); bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle), island_margin=margin, area_weight=1.0, scale_to_bounds=False)
    try:
        bpy.ops.uv.pack_islands(margin=margin, rotate=True)
    except Exception:
        pass
    bpy.ops.object.mode_set(mode="OBJECT")


def _bake_img(name, res, color=True):
    im = bpy.data.images.new(name, res, res, alpha=False, float_buffer=False)
    im.colorspace_settings.name = "sRGB" if color else "Non-Color"
    return im


def _with_target(o, im):
    for ms in o.material_slots:
        nt = ms.material.node_tree
        t = nt.nodes.get("BAKE_TARGET") or nt.nodes.new("ShaderNodeTexImage")
        t.name = "BAKE_TARGET"; t.image = im
        for n in nt.nodes: n.select = False
        t.select = True; nt.nodes.active = t


def _swap_to_emit(o, which):
    """route a channel into an emission shader for baking; returns undo info"""
    saved = []
    for ms in o.material_slots:
        nt = ms.material.node_tree
        out = [n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"][0]
        bsdf = [n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"][0]
        em = nt.nodes.new("ShaderNodeEmission"); em.name = "BAKE_EMIT"; em.inputs[1].default_value = 1.0
        if which == "metal":
            src = bsdf.inputs["Metallic"]
        elif which == "color":
            src = bsdf.inputs["Base Color"]
        else:
            tag = nt.nodes.get("EMASK")
            src = tag.inputs[0] if tag else None
        if src is not None and src.is_linked:
            nt.links.new(src.links[0].from_socket, em.inputs[0])
        else:
            v = src.default_value if src is not None else 0.0
            em.inputs[0].default_value = tuple(v) if hasattr(v, "__len__") else (v, v, v, 1)
        old = out.inputs[0].links[0].from_socket
        nt.links.new(em.outputs[0], out.inputs[0])
        saved.append((nt, out, old, em))
    return saved


def _restore(saved):
    for nt, out, old, em in saved:
        nt.links.new(old, out.inputs[0]); nt.nodes.remove(em)


def bake(o, key, res=1024, samples=16, emissive=False):
    sc = bpy.context.scene
    sc.cycles.samples = samples
    sc.render.bake.margin = 6
    sel([o])
    paths = {}
    def do(kind, name, color, **kw):
        im = _bake_img(f"{key}_{name}", res, color)
        _with_target(o, im)
        bpy.ops.object.bake(type=kind, **kw)
        p = f"{OUT}/{key}_{name}.png"; im.filepath_raw = p; im.file_format = "PNG"; im.save()
        paths[name] = p
    # base colour via an emission swap: a DIFFUSE/COLOR bake multiplies by (1 - metallic), so metal came out black
    s = _swap_to_emit(o, "color"); do("EMIT", "color", True); _restore(s)
    do("NORMAL", "normal", False, normal_space="TANGENT")
    do("ROUGHNESS", "rough", False)
    s = _swap_to_emit(o, "metal"); do("EMIT", "metal", False); _restore(s)
    if emissive:
        s = _swap_to_emit(o, "emask"); do("EMIT", "emask", False); _restore(s)
    return paths


def export_fbx(o, key):
    sel([o])
    p = f"{OUT}/{key}.fbx"
    bpy.ops.export_scene.fbx(filepath=p, use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                             axis_forward="-Z", axis_up="Y", mesh_smooth_type="OFF", use_mesh_modifiers=True, add_leaf_bones=False,
                             bake_anim=False, use_tspace=True, path_mode="STRIP")
    return p


def bounds(o):
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    mn = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    mx = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    return mn, mx


# ---------------------------------------------------------------- preview
def preview(objs, path, res=720, dist=1.0, elev=18, azim=35, target=None, samples=48, ground=True, lights=None):
    sc = bpy.context.scene
    sc.cycles.samples = samples
    sc.render.resolution_x = res; sc.render.resolution_y = res
    mn = Vector((1e9,) * 3); mx = Vector((-1e9,) * 3)
    for o in objs:
        a, b = bounds(o)
        mn = Vector((min(mn.x, a.x), min(mn.y, a.y), min(mn.z, a.z))); mx = Vector((max(mx.x, b.x), max(mx.y, b.y), max(mx.z, b.z)))
    c = target or (mn + mx) / 2
    rad = (mx - mn).length / 2
    cam_d = bpy.data.cameras.new("C"); cam_d.lens = 70
    cam = bpy.data.objects.new("C", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    d = rad * 3.1 * dist
    e, a = math.radians(elev), math.radians(azim)
    cam.location = c + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * d
    cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
    made = [cam]
    for (loc, energy, col, size) in (lights or [((d, -d, d * 1.2), 560, (1, 0.95, 0.9), 2.5), ((-d, -d * 0.3, d * 0.6), 300, (0.6, 0.7, 1.0), 3.0), ((0, d * 1.2, d), 600, (1, 0.85, 0.8), 2.0)]):
        ld = bpy.data.lights.new("L", "AREA"); ld.energy = energy * rad * rad * 0.6; ld.color = col; ld.size = size * rad
        lo = bpy.data.objects.new("L", ld); sc.collection.objects.link(lo); lo.location = c + Vector(loc) * (rad / max(rad, 1e-3))
        lo.rotation_euler = (c - lo.location).to_track_quat("-Z", "Y").to_euler(); made.append(lo)
    if ground:
        bpy.ops.mesh.primitive_plane_add(size=rad * 30, location=(c.x, c.y, mn.z - 0.002))
        g = bpy.context.object; gm = bpy.data.materials.new("ground"); gm.use_nodes = True
        gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.05, 0.06, 1)
        gm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.5
        g.data.materials.append(gm); made.append(g)
    sc.render.filepath = path; sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    for o in made: bpy.data.objects.remove(o, do_unlink=True)
    return path


def mat_paint(name="paint", paint=(0.5, 0.03, 0.02), metal_col=(0.45, 0.43, 0.4), chip=0.55, dirt=(0.06, 0.04, 0.03), scale=1.0):
    """painted steel: chipped edges and scratches showing bare metal, grime in the crevices"""
    mat = bpy.data.materials.new(name); nt, bsdf, out = _nt(mat)
    tc = _tex_coord(nt); obj = tc.outputs["Object"]
    n1 = _noise(nt, 9 * scale, 8, 0.7, obj); n2 = _noise(nt, 2.5 * scale, 4, 0.5, obj)
    edge = _edges(nt); ao = _ao(nt, 0.1)
    sc = nt.nodes.new("ShaderNodeTexWave"); sc.inputs["Scale"].default_value = 30 * scale; sc.inputs["Distortion"].default_value = 18; sc.inputs["Detail"].default_value = 2
    nt.links.new(obj, sc.inputs["Vector"])
    scratch = _math(nt, "GREATER_THAN", sc.outputs["Fac"], 0.985)
    chips = _math(nt, "MULTIPLY", _math(nt, "ADD", _math(nt, "MULTIPLY", edge, 1.2), _math(nt, "SUBTRACT", n1.outputs["Fac"], 0.62 - chip * 0.08)), 4.0, clamp=True)
    chips = _math(nt, "GREATER_THAN", _math(nt, "MAXIMUM", chips, _math(nt, "MULTIPLY", scratch, n2.outputs["Fac"])), 0.5)
    pc = _ramp(nt, n2.outputs["Fac"], [(0.3, (paint[0] * 0.7, paint[1] * 0.7, paint[2] * 0.7)), (0.75, paint)]).outputs[0]
    col = _mix(nt, chips, pc, metal_col)
    col = _mix(nt, _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", 1.0, ao), 1.6, clamp=True), col, dirt)
    nt.links.new(col, bsdf.inputs["Base Color"])
    nt.links.new(_math(nt, "ADD", _math(nt, "MULTIPLY", chips, -0.15), 0.5), bsdf.inputs["Roughness"])
    nt.links.new(chips, bsdf.inputs["Metallic"])
    nt.links.new(_bump(nt, _math(nt, "ADD", chips, _math(nt, "MULTIPLY", n1.outputs["Fac"], 0.2)), 0.35, 0.006), bsdf.inputs["Normal"])
    return mat


def mat_eye(name="eye", iris=(0.62, 0.2, 1.0), sclera=(0.035, 0.012, 0.05), vein=(0.5, 0.05, 0.35), iris_deg=34, pupil_w=0.05, k=10.0):
    """eyeball looking down -Y: radial-fibred glowing iris, vertical slit pupil, dark veined sclera"""
    mat = bpy.data.materials.new(name); nt, bsdf, out = _nt(mat)
    tc = _tex_coord(nt); obj = tc.outputs["Object"]
    nv = nt.nodes.new("ShaderNodeVectorMath"); nv.operation = "NORMALIZE"; nt.links.new(obj, nv.inputs[0])
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(nv.outputs[0], sep.inputs[0])
    fwd = _math(nt, "MULTIPLY", sep.outputs["Y"], -1.0)                    # 1 at the front of the eye
    iris_m = _math(nt, "GREATER_THAN", fwd, math.cos(math.radians(iris_deg)))
    ang = _math(nt, "ARCTAN2", sep.outputs["X"], sep.outputs["Z"])
    fib = nt.nodes.new("ShaderNodeTexNoise"); fib.inputs["Scale"].default_value = 40; fib.inputs["Detail"].default_value = 6
    cmb = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(_math(nt, "MULTIPLY", ang, 3.0), cmb.inputs[0]); nt.links.new(_math(nt, "MULTIPLY", fwd, 0.4), cmb.inputs[1])
    nt.links.new(cmb.outputs[0], fib.inputs["Vector"])
    ring = _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", fwd, math.cos(math.radians(iris_deg))), 1.0 / (1 - math.cos(math.radians(iris_deg))), clamp=True)
    pupil = _math(nt, "MULTIPLY", _math(nt, "LESS_THAN", _math(nt, "ABSOLUTE", sep.outputs["X"]), pupil_w), _math(nt, "GREATER_THAN", fwd, math.cos(math.radians(iris_deg * 0.82))))
    irisglow = _math(nt, "MULTIPLY", iris_m, _math(nt, "ADD", _math(nt, "MULTIPLY", fib.outputs["Fac"], 0.9), _math(nt, "MULTIPLY", ring, 0.6)))
    irisglow = _math(nt, "MULTIPLY", irisglow, _math(nt, "SUBTRACT", 1.0, pupil), clamp=True)
    v = nt.nodes.new("ShaderNodeTexVoronoi"); v.feature = "DISTANCE_TO_EDGE"; v.inputs["Scale"].default_value = 16; nt.links.new(_math_vec_scale(nt, obj, 1.0), v.inputs["Vector"])
    vfade = _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", 0.6, fwd), 2.0, clamp=True)
    vm = _math(nt, "MULTIPLY", _math(nt, "MULTIPLY", _math(nt, "LESS_THAN", v.outputs["Distance"], 0.012), _math(nt, "SUBTRACT", 1.0, iris_m)), vfade)
    col = _mix(nt, vm, sclera, vein)
    col = _mix(nt, iris_m, col, (iris[0] * 0.35, iris[1] * 0.35, iris[2] * 0.35))
    col = _mix(nt, pupil, col, (0.0, 0.0, 0.0))
    nt.links.new(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.08; bsdf.inputs["Metallic"].default_value = 0.0
    _set_emit(nt, bsdf, _math(nt, "MAXIMUM", _math(nt, "POWER", irisglow, 1.6), _math(nt, "MULTIPLY", vm, 0.25)), iris, k)
    return mat


def mat_heat(name="heat", base=(0.02, 0.018, 0.018), col=(1.0, 0.2, 0.03), axis="X", start=0.5, end=1.2, k=14.0, crack_scale=7.0):
    """black iron that turns red-hot toward one end (object-space axis from `start` to `end`), with molten cracks"""
    mat = bpy.data.materials.new(name); nt, bsdf, out = _nt(mat)
    tc = _tex_coord(nt); obj = tc.outputs["Object"]
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(obj, sep.inputs[0])
    g = _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", sep.outputs[axis], start), 1.0 / (end - start), clamp=True)
    v = nt.nodes.new("ShaderNodeTexVoronoi"); v.feature = "DISTANCE_TO_EDGE"; v.inputs["Scale"].default_value = crack_scale; nt.links.new(obj, v.inputs["Vector"])
    crk = _math(nt, "LESS_THAN", v.outputs["Distance"], 0.03)
    n = _noise(nt, 6, 5, 0.6, obj)
    edge = _edges(nt)
    mask = _math(nt, "MAXIMUM", _math(nt, "MULTIPLY", g, _math(nt, "ADD", 0.35, _math(nt, "MULTIPLY", n.outputs["Fac"], 0.8)), clamp=True),
                 _math(nt, "MULTIPLY", crk, _math(nt, "ADD", 0.25, g), clamp=True))
    mask = _math(nt, "MAXIMUM", mask, _math(nt, "MULTIPLY", edge, _math(nt, "MULTIPLY", g, 1.2), clamp=True))
    col_ = _mix(nt, mask, base, (col[0] * 0.5, col[1] * 0.4, col[2] * 0.3))
    nt.links.new(col_, bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 0.85; bsdf.inputs["Roughness"].default_value = 0.5
    _set_emit(nt, bsdf, mask, col, k)
    nt.links.new(_bump(nt, _math(nt, "SUBTRACT", n.outputs["Fac"], _math(nt, "MULTIPLY", crk, 0.6)), 0.3, 0.01), bsdf.inputs["Normal"])
    return mat


def mat_gold(name="gold", base=(0.32, 0.17, 0.05), worn=(0.95, 0.7, 0.35), grime=(0.05, 0.03, 0.01)):
    """aged gold / brass: bright worn edges, dark grime in the crevices"""
    mat = bpy.data.materials.new(name); nt, bsdf, out = _nt(mat)
    tc = _tex_coord(nt); obj = tc.outputs["Object"]
    n = _noise(nt, 12, 6, 0.6, obj); ao = _ao(nt, 0.1); edge = _edges(nt)
    col = _ramp(nt, n.outputs["Fac"], [(0.3, (base[0] * 0.8, base[1] * 0.8, base[2] * 0.8)), (0.7, base)]).outputs[0]
    col = _mix(nt, _math(nt, "MULTIPLY", edge, 0.9, clamp=True), col, worn)
    col = _mix(nt, _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", 1.0, ao), 1.8, clamp=True), col, grime)
    nt.links.new(col, bsdf.inputs["Base Color"])
    bsdf.inputs["Metallic"].default_value = 1.0
    nt.links.new(_math(nt, "ADD", _math(nt, "MULTIPLY", n.outputs["Fac"], 0.2), 0.25), bsdf.inputs["Roughness"])
    nt.links.new(_bump(nt, n.outputs["Fac"], 0.2, 0.006), bsdf.inputs["Normal"])
    return mat
