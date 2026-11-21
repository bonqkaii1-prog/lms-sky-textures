"""python3 make.py <item> [--bake]
items/<item>.py defines KEY and build() -> {piece_name: (obj, res, emissive)} (+ optional PREVIEW dict)."""
import sys, importlib, time
sys.path.insert(0, "/home/claude/cos"); sys.path.insert(0, "/home/claude/cos/items")
from kit import *
name = sys.argv[1]; do_bake = "--bake" in sys.argv
mod = importlib.import_module(name)
reset()
pieces = mod.build()
objs = [p[0] for p in pieces.values()]
for o in objs:
    if o.modifiers: apply_mods(o)
print("tris", {k: tris(v[0]) for k, v in pieces.items()}, "total", sum(tris(v[0]) for v in pieces.values()))
pv = getattr(mod, "PREVIEW", {})
preview(objs, f"{OUT}/{mod.KEY}_preview.png", res=640, samples=36, **pv.get("main", {}))
for i, extra in enumerate(pv.get("extra", [])):
    preview(objs, f"{OUT}/{mod.KEY}_preview{i+2}.png", res=640, samples=36, **extra)
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/{mod.KEY}.blend")
if do_bake:
    meta = {}
    for pname, (o, res, emis) in pieces.items():
        t = time.time(); uv(o, margin=0.003)
        k = f"{mod.KEY}_{pname}"
        paths = bake(o, k, res=res, samples=8, emissive=emis)
        export_fbx(o, k)
        mn, mx = bounds(o)
        meta[pname] = {"min": list(mn), "max": list(mx), "maps": list(paths.keys()), "tris": tris(o)}
        print(pname, "baked", round(time.time() - t), "s")
    json.dump(meta, open(f"{OUT}/{mod.KEY}_meta.json", "w"), indent=1)
print("DONE", name)
