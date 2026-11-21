"""Unholy Eye (Noli): a slit-pupilled eye with a glowing violet iris, held in a shattered obsidian ring whose
shards curl inward like claws, shadow tendrils curling out from its rim."""
from kit import *
from halo import shard
KEY = "eye"
PREVIEW = {"main": {"elev": 6, "azim": -12, "dist": 0.8}, "extra": [{"elev": 25, "azim": 55, "dist": 0.85}]}
VIOLET = (0.6, 0.18, 1.0)

def build():
    eye = sphere(0.36, (0, 0, 0), 40, 24, "Eye"); smooth(eye, 80)
    assign(eye, mat_eye("noli_eye", iris=VIOLET, sclera=(0.012, 0.004, 0.02), vein=(0.3, 0.03, 0.22), k=3.5))
    lid = []                                   # a heavy obsidian socket rim hugging the eye (top + bottom lids)
    obs = mat_obsidian("noli_obsidian", vein=VIOLET, vein_scale=3.0, vein_w=0.016, k=4)
    rng = random.Random(12)
    R = 0.58; pieces = []
    a = 0.3
    while a < TAU - 0.2:
        span = rng.uniform(0.7, 1.05); a1 = min(a + span, TAU + 0.1)
        s = shard(a, a1, R, 0.17, 0.13, rng, "s")
        # claws: hooked thorns curling in toward the eye
        group = [s]
        for _ in range(rng.randint(1, 2)):
            ta = rng.uniform(a + 0.1, a1 - 0.1)
            pts = []
            for i in range(7):
                t = i / 6
                r = R - 0.06 - 0.22 * t; z = 0.05 * math.sin(t * 3) - 0.08 * t
                pts.append((r * math.cos(ta + 0.25 * t), r * math.sin(ta + 0.25 * t), z))
            cl = tube_along(pts, 0.05, 6, "claw", radii=[1, 0.85, 0.7, 0.55, 0.4, 0.25, 0.06]); group.append(cl)
        pieces.append(join(group, "sg"))
        a = a1 + rng.uniform(0.12, 0.22)
    ring = join(pieces, "EyeRing")
    ring.rotation_euler = (math.pi / 2, 0, 0); bake_xform(ring)          # ring faces -Y like the eye
    flat(ring); assign(ring, obs)
    # shadow tendrils curling outward from the rim
    tmat = mat_obsidian("noli_tendril", vein=VIOLET, vein_scale=5.0, vein_w=0.012, k=3, base=(0.01, 0.004, 0.016))
    tens = []
    for i in range(7):
        a0 = i / 7 * TAU + rng.uniform(-0.2, 0.2)
        L = rng.uniform(0.45, 0.75); curl = rng.choice([-1, 1]) * rng.uniform(1.2, 2.4)
        pts, radii = [], []
        for j in range(22):
            t = j / 21
            r = R + 0.05 + L * t
            ang = a0 + curl * t * t * 0.9
            pts.append((r * math.cos(ang), 0.1 + 0.25 * t * t + 0.06 * math.sin(t * 7 + i), r * math.sin(ang)))
            radii.append((1 - t) ** 1.2 * 0.9 + 0.04)
        tens.append(tube_along(pts, 0.065, 7, "tendril", radii=radii))
    ten = join(tens, "Tendrils"); smooth(ten, 60); assign(ten, tmat)
    return {"Eye": (eye, 512, True), "EyeRing": (ring, 1024, True), "Tendrils": (ten, 512, True)}
