"""python3 rebake_color.py <item>
Re-bake only the colour map of an already-imported cosmetic, onto the exact UVs of its exported FBX, using the
fixed base-colour bake (the old DIFFUSE/COLOR bake multiplied by 1 - metallic, so every metal part came out black)."""
import sys, importlib, os
sys.path.insert(0, "/home/claude/cos"); sys.path.insert(0, "/home/claude/cos/items")
from kit import *
name = sys.argv[1]
mod = importlib.import_module(name)
reset()
pieces = mod.build()
for o, _, _ in pieces.values():
    if o.modifiers: apply_mods(o)
os.makedirs(f"{OUT}/colorfix", exist_ok=True)
sc = bpy.context.scene
for pname, (o, res, emis) in pieces.items():
    key = f"{mod.KEY}_{pname}"
    fbx = f"{OUT}/{key}.fbx"
    if not os.path.exists(fbx):
        print("SKIP no fbx", key); continue
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=fbx)
    imp = [x for x in bpy.data.objects if x not in before and x.type == "MESH"][0]
    # bake from the procedural source (o) onto the imported mesh (exact exported UVs) with selected-to-active
    import mathutils
    def wb(ob):
        mw = ob.matrix_world; vs = [mw @ v.co for v in ob.data.vertices]
        return mathutils.Vector([min(v[i] for v in vs) for i in range(3)]), mathutils.Vector([max(v[i] for v in vs) for i in range(3)])
    a0, a1 = wb(o); b0, b1 = wb(imp)
    if (a0 - b0).length > 0.01 or (a1 - b1).length > 0.01:
        print("SKIP bounds mismatch", key, a0, b0, a1, b1); bpy.data.objects.remove(imp); continue
    sc.cycles.samples = 8; sc.render.bake.margin = 6
    im = bpy.data.images.new(f"{key}_color", res, res, alpha=False, float_buffer=False); im.colorspace_settings.name = "sRGB"
    imp.data.materials.clear()
    tm = bpy.data.materials.new("tgt"); tm.use_nodes = True
    tn = tm.node_tree.nodes.new("ShaderNodeTexImage"); tn.image = im; tm.node_tree.nodes.active = tn
    imp.data.materials.append(tm)
    from kit import _swap_to_emit, _restore
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); imp.select_set(True); bpy.context.view_layer.objects.active = imp
    s = _swap_to_emit(o, "color")
    bpy.ops.object.bake(type="EMIT", use_selected_to_active=True, cage_extrusion=0.004, max_ray_distance=0.02)
    _restore(s)
    bpy.data.objects.remove(imp)
    p = f"{OUT}/colorfix/{key}_color.png"; im.filepath_raw = p; im.file_format = "PNG"; im.save()
    print("REBAKED", key)
print("DONE", name)
