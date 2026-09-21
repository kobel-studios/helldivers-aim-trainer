"""Super Earth Combat Drill - Helldivers 2 aim trainer (GUI app).

Run:  python aim_trainer.py
Click the window to lock the mouse, ESC to release.
"""
import math
import random
import sys

import pygame

pygame.init()
try:
    pygame.mixer.init(22050, -16, 1, 512)
    SND_OK = True
except pygame.error:
    SND_OK = False

W, H = 1600, 900
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("SUPER EARTH // COMBAT DRILL")
clock = pygame.time.Clock()

CAM_H = 1.7
F = H * 0.95
horizon = H * 0.40
fullscreen = False
muted = False


def R(a, b):
    return a + random.uniform(a, b)


def gauss():
    return (random.random() + random.random() + random.random() - 1.5) * 0.7


def proj(x, y, z):
    return (W / 2 + x * F / z, horizon - (y - CAM_H) * F / z)


# ---------- sounds ----------
SNDS = {}


def make_tone(freq, dur, vol=0.3, kind="sq"):
    if not SND_OK:
        return None
    sr, n = 22050, int(22050 * dur)
    buf = bytearray()
    for i in range(n):
        t = i / sr
        ph = (freq * t) % 1.0
        if kind == "sq":
            v = 1.0 if ph < 0.5 else -1.0
        elif kind == "saw":
            v = 2 * ph - 1
        else:
            v = math.sin(2 * math.pi * freq * t)
        buf += int(v * (1 - i / n) * vol * 32767).to_bytes(2, "little", signed=True)
    try:
        return pygame.mixer.Sound(buffer=bytes(buf))
    except pygame.error:
        return None


def init_sounds():
    for name, args in {
        "shot": (200, 0.06, 0.25, "sq"),
        "boom": (55, 0.45, 0.5, "saw"),
        "kill": (760, 0.09, 0.2, "sin"),
        "zap": (90, 0.15, 0.3, "saw"),
        "throw": (300, 0.05, 0.15, "sin"),
        "rail": (50, 0.3, 0.4, "saw"),
        "shell": (120, 0.06, 0.25, "sq"),
    }.items():
        SNDS[name] = make_tone(*args)


def play(name):
    if not muted and SNDS.get(name):
        SNDS[name].play()


# ---------- weapons ----------
WEAPONS = [
    dict(name="AR-23 LIBERATOR", hk="1", mode="auto", rpm=640, dmg=30, spd=380, grav=9.8,
         spread=0.35, pellets=1, mag=45, rel=1.6, col=(255, 210, 74), note="Minimal drop", glen=110),
    dict(name="SG-225 BREAKER", hk="2", mode="auto", rpm=300, dmg=13, spd=320, grav=9.8,
         spread=3.4, pellets=9, mag=13, rel=2.4, falloff=22, col=(255, 176, 74), note="9 pellets, falls off", glen=100),
    dict(name="R-36 ERUPTOR", hk="3", mode="semi", rpm=70, dmg=230, spd=150, grav=9.8,
         spread=0.15, pellets=1, mag=5, rel=3.2, aoe=3.2, col=(255, 122, 60), note="Bolt drops, explodes", glen=120),
    dict(name="JAR-5 DOMINATOR", hk="4", mode="semi", rpm=90, dmg=260, spd=105, grav=12,
         spread=0.2, pellets=1, mag=15, rel=2.6, col=(255, 92, 92), note="Heavy drop - aim high", glen=115),
    dict(name="PLAS-1 SCORCHER", hk="5", mode="semi", rpm=250, dmg=70, spd=210, grav=5,
         spread=0.3, pellets=1, mag=15, rel=2.0, aoe=1.6, col=(124, 242, 255), note="Slight drop, small AoE", glen=105),
    dict(name="AC-8 AUTOCANNON", hk="6", mode="auto", rpm=160, dmg=150, spd=300, grav=9.8,
         spread=0.4, pellets=1, mag=10, rel=2.8, aoe=2.4, col=(255, 226, 122), note="Fast shell, mild drop", glen=140),
    dict(name="GR-8 RECOILLESS", hk="7", mode="semi", rpm=45, dmg=700, spd=190, grav=12,
         spread=0.1, pellets=1, mag=1, rel=3.6, aoe=6, col=(255, 157, 92), note="Arcs at range, huge boom", glen=150),
    dict(name="LAS-16 SICKLE", hk="8", mode="beam", dps=260, spread=0.1, mag=100, rel=2.0,
         col=(255, 77, 109), note="Hitscan beam, no drop", glen=110),
    dict(name="FLAM-40", hk="9", mode="flame", dmg=2.6, spd=20, spread=8, mag=100, rel=2.5,
         col=(255, 140, 46), note="~12m fire cone", glen=95),
    dict(name="ARC-12 BLITZER", hk="0", mode="zap", rpm=55, dmg=130, range=32, chains=3,
         mag=8, rel=2.4, col=(157, 232, 255), note="Instant arc, chains", glen=105),
    dict(name="RS-422 RAILGUN", hk="-", mode="charge", dmg=900, chargeMax=1.2, mag=20,
         rel=1.0, col=(201, 182, 255), note="Hold LMB to charge, pierces", glen=125),
]

TYPES = [
    dict(n="Scavenger", hp=40, r=0.55, spd=4.5, col=(255, 154, 60), score=10, wt=26, kind="bug"),
    dict(n="Hunter", hp=70, r=0.7, spd=6, col=(255, 194, 60), score=15, wt=18, kind="bug", vz=-1.4, min=15),
    dict(n="Warrior", hp=160, r=1.05, spd=3, col=(255, 122, 46), score=25, wt=18, kind="bug"),
    dict(n="Bile Spewer", hp=420, r=1.7, spd=1.4, col=(157, 255, 92), score=60, wt=9, kind="bug", min=25),
    dict(n="Shrieker", hp=60, r=0.75, spd=11, col=(201, 140, 255), score=30, wt=14, kind="fly"),
    dict(n="Trooper", hp=90, r=0.8, spd=3.6, col=(255, 92, 92), score=20, wt=16, kind="bot"),
    dict(n="Devastator", hp=300, r=1.1, spd=2.2, col=(226, 59, 59), score=45, wt=9, kind="bot", min=20),
    dict(n="Hulk", hp=900, r=1.9, spd=1.1, col=(176, 42, 42), score=120, wt=5, kind="bot", min=40),
]

# ---------- state ----------
st = dict(score=0, kills=0, shots=0, hits=0, streak=0, best=0, time=0.0, drill=False, drillLeft=0.0, drillDone=False)
targets, projs, nades, parts, floats, beams = [], [], [], [], [], []
cx, cy = W / 2, H / 2
grabbed = False
muzzle = 0.0
muzzle_pos = (W / 2, H - 80)
wi = 0
cd = 0.0
reloadT = 0.0
spawnT = 0.5
accT = 0.0
charge = -1.0
nadeT0 = 0.0
rDown = False
flameAcc = 0.0
redFlash = 0.0
bloom = 0.0
faction = "mixed"
sens = 0.9
hudOn = True
ammo = [w["mag"] for w in WEAPONS]
ui = {}  # click rects rebuilt every draw


def cy_t(t):
    return t["y"] if t["fly"] else t["r"] * 0.9


def aim_dir():
    dx, dy = (cx - W / 2) / F, -(cy - horizon) / F
    l = math.sqrt(dx * dx + dy * dy + 1)
    return (dx / l, dy / l, 1 / l)


def ray_targets(d):
    h = []
    for t in targets:
        if t["hp"] <= 0:
            continue
        tt = t["z"] / d[2]
        px, py = d[0] * tt, CAM_H + d[1] * tt
        if math.hypot(px - t["x"], py - cy_t(t)) < t["r"] * 1.15:
            h.append(t)
    h.sort(key=lambda t: t["z"])
    return h


def dmg(t, d):
    if t["hp"] <= 0:
        return
    t["hp"] -= d
    t["flash"] = 1.0
    if t["hp"] <= 0:
        kill(t)


def kill(t):
    st["kills"] += 1
    st["streak"] += 1
    st["best"] = max(st["best"], st["streak"])
    st["score"] += t["type"]["score"]
    sx, sy = proj(t["x"], cy_t(t), t["z"])
    floats.append(dict(x=sx, y=sy, txt="+" + str(t["type"]["score"]), life=1.0, col=(255, 210, 74), size=18))
    for _ in range(14):
        parts.append(dict(x=t["x"], y=cy_t(t), z=t["z"], vx=R(-4, 4), vy=R(0, 6), vz=R(-4, 4),
                          life=R(0.3, 0.7), ml=0.7, col=t["type"]["col"], sz=R(0.05, 0.18), g=9))
    play("kill")


def explode(x, y, z, r, d):
    global redFlash
    beams.append(dict(ring=True, x=x, y=y, z=z, r=r, life=0.35, ml=0.35))
    for i in range(26):
        parts.append(dict(x=x, y=y, z=z, vx=R(-8, 8), vy=R(-2, 10), vz=R(-8, 8),
                          life=R(0.3, 0.8), ml=0.8, col=(255, 176, 74) if i % 3 else (255, 242, 200),
                          sz=R(0.1, 0.3), g=6))
    for t in targets:
        if t["hp"] <= 0:
            continue
        dd = math.dist((t["x"], cy_t(t), t["z"]), (x, y, z))
        if dd < r + t["r"]:
            dmg(t, d * max(0.3, 1 - dd / (r + t["r"])))
    play("boom")
    redFlash = max(redFlash, 0.15)


def start_reload():
    global reloadT
    w = WEAPONS[wi]
    if reloadT <= 0 and ammo[wi] < w["mag"]:
        reloadT = w["rel"]


def fire():
    global muzzle, bloom
    w = WEAPONS[wi]
    if reloadT > 0:
        return
    if ammo[wi] <= 0:
        start_reload()
        return
    ammo[wi] -= 1
    st["shots"] += w["pellets"]
    sp = w.get("spread", 0) * math.pi / 180
    for _ in range(w["pellets"]):
        d = list(aim_dir())
        d[0] += gauss() * sp
        d[1] += gauss() * sp
        l = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
        projs.append(dict(x=0.25, y=CAM_H - 0.25, z=0.4,
                          vx=d[0] / l * w["spd"], vy=d[1] / l * w["spd"], vz=d[2] / l * w["spd"],
                          g=w["grav"], dmg=w["dmg"], aoe=w.get("aoe", 0), life=4,
                          falloff=w.get("falloff", 0), col=w["col"], flame=False, noacc=False, dead=False))
    muzzle, bloom = 1.0, 1.0
    play("shell" if w.get("aoe") else "shot")
    if ammo[wi] <= 0:
        start_reload()


def beam_update(w, dt):
    global accT, muzzle
    ammo[wi] -= dt * 22
    if ammo[wi] <= 0:
        ammo[wi] = 0
        start_reload()
        return
    d = aim_dir()
    ts = ray_targets(d)
    t = ts[0] if ts else None
    accT += dt
    if accT > 0.1:
        st["shots"] += 1
        if t:
            st["hits"] += 1
        accT = 0
    ez = t["z"] if t else 80
    beams.append(dict(pts=[(0.2, CAM_H - 0.2, 0.4), (d[0] * ez / d[2], CAM_H + d[1] * ez / d[2], ez)],
                      life=0.05, ml=0.05, col=w["col"], wide=False))
    if t:
        dmg(t, w["dps"] * dt)
    muzzle = 1.0


def flame_update(w, dt):
    global flameAcc, muzzle
    flameAcc += dt * 80
    ammo[wi] -= dt * 20
    if ammo[wi] <= 0:
        ammo[wi] = 0
        start_reload()
        return
    sp = w["spread"] * math.pi / 180
    while flameAcc >= 1:
        flameAcc -= 1
        d = list(aim_dir())
        d[0] += gauss() * sp
        d[1] += gauss() * sp
        l = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
        projs.append(dict(x=0.25, y=CAM_H - 0.3, z=0.4,
                          vx=d[0] / l * w["spd"], vy=d[1] / l * w["spd"] + 1.5, vz=d[2] / l * w["spd"],
                          g=-3, dmg=w["dmg"], aoe=0, life=0.55, falloff=0,
                          col=w["col"], flame=True, noacc=True, dead=False))
    muzzle = 1.0


def zap():
    global muzzle, cd
    w = WEAPONS[wi]
    if reloadT > 0:
        return
    if ammo[wi] <= 0:
        start_reload()
        return
    ammo[wi] -= 1
    st["shots"] += 1
    cd = 60 / w["rpm"]
    muzzle = 1.0
    play("zap")
    d = aim_dir()
    first, best = None, 1e9
    for t in ray_targets(d):
        tt = t["z"] / d[2]
        dd = math.hypot(d[0] * tt - t["x"], CAM_H + d[1] * tt - cy_t(t))
        if t["z"] < w["range"] and dd < best:
            best, first = dd, t
    if not first:
        beams.append(dict(pts=[(0, CAM_H, 0.5), (d[0] * w["range"], CAM_H + d[1] * w["range"], w["range"])],
                          life=0.12, ml=0.12, col=w["col"], wide=False))
    else:
        st["hits"] += 1
        cur = first
        hit = [cur]
        dmg(cur, w["dmg"])
        for _ in range(1, w["chains"]):
            nx, nd = None, 1e9
            for t in targets:
                if t["hp"] <= 0 or t in hit:
                    continue
                dd = math.dist((t["x"], cy_t(t), t["z"]), (cur["x"], cy_t(cur), cur["z"]))
                if dd < 12 and dd < nd:
                    nd, nx = dd, t
            if not nx:
                break
            dmg(nx, w["dmg"] * 0.8)
            hit.append(nx)
            cur = nx
        pts = [(0, CAM_H, 0.5)] + [(t["x"], cy_t(t), t["z"]) for t in hit]
        beams.append(dict(pts=pts, life=0.15, ml=0.15, col=w["col"], wide=False))
    if ammo[wi] <= 0:
        start_reload()


def rail(p):
    global muzzle
    w = WEAPONS[wi]
    if reloadT > 0:
        return
    if ammo[wi] <= 0:
        start_reload()
        return
    ammo[wi] -= 1
    st["shots"] += 1
    d = aim_dir()
    ts = ray_targets(d)
    end = 90
    beams.append(dict(pts=[(0, CAM_H, 0.5), (d[0] * end / d[2], CAM_H + d[1] * end / d[2], end)],
                      life=0.25, ml=0.25, col=w["col"], wide=True))
    if ts:
        st["hits"] += 1
        for t in ts:
            dmg(t, w["dmg"] * (0.4 + 0.6 * p))
    muzzle = 1.0
    play("rail")
    if ammo[wi] <= 0:
        start_reload()


def throw_nade(power):
    d = aim_dir()
    s = 9 + 16 * power
    nades.append(dict(x=0.3, y=CAM_H - 0.2, z=0.5, vx=d[0] * s, vy=d[1] * s + 2, vz=d[2] * s,
                      fuse=2.4, dead=False))
    play("throw")


def fac_ok(t):
    if faction == "bugs":
        return t["kind"] != "bot"
    if faction == "bots":
        return t["kind"] == "bot"
    return True


def set_faction(f):
    global faction, spawnT
    faction = f
    targets.clear()
    spawnT = 0.4


def spawn():
    pool = [t for t in TYPES if st["time"] >= t.get("min", 0) and fac_ok(t)]
    tw = sum(t["wt"] for t in pool)
    r = random.random() * tw
    typ = pool[0]
    for t in pool:
        r -= t["wt"]
        if r <= 0:
            typ = t
            break
    z = R(18, 55)
    fly = typ["kind"] == "fly"
    targets.append(dict(type=typ, x=R(-z * 0.55, z * 0.55), y=R(4, 11) if fly else 0, z=z,
                        vx=random.choice((-1, 1)) * typ["spd"], vz=typ.get("vz", 0),
                        hp=typ["hp"], r=typ["r"], fly=fly, ph=R(0, 6), life=0, flash=0))


# ---------- update ----------
def update(dt):
    global spawnT, reloadT, cd, accT, charge, flameAcc, redFlash, bloom, muzzle
    st["time"] += dt
    if st["drill"]:
        st["drillLeft"] -= dt
        if st["drillLeft"] <= 0:
            end_drill()
    w = WEAPONS[wi]
    alive = sum(1 for t in targets if t["hp"] > 0)
    spawnT -= dt
    if spawnT <= 0 and alive < min(5 + st["time"] / 12, 12):
        spawn()
        spawnT = max(0.7, 2.1 - st["time"] * 0.018)
    if reloadT > 0:
        reloadT -= dt
        if reloadT <= 0:
            ammo[wi] = w["mag"]
            reloadT = 0
    cd -= dt
    bloom = max(0, bloom - dt * 4)
    pressed = pygame.mouse.get_pressed()
    if grabbed and pressed[0] and reloadT <= 0:
        if w["mode"] == "auto" and cd <= 0:
            fire()
            cd = 60 / w["rpm"]
        elif w["mode"] == "beam":
            beam_update(w, dt)
        elif w["mode"] == "flame":
            flame_update(w, dt)
    if charge >= 0 and pressed[0]:
        charge = min(1, charge + dt / w["chargeMax"])
    for t in targets:
        if t["hp"] <= 0:
            continue
        t["life"] += dt
        t["flash"] = max(0, t["flash"] - dt * 5)
        t["x"] += t["vx"] * dt
        if abs(t["x"]) > t["z"] * 0.7:
            t["vx"] *= -1
        if t["vz"]:
            t["z"] += t["vz"] * dt
            if t["z"] < 7:
                t["hp"] = 0
                st["streak"] = 0
                redFlash = 0.5
                floats.append(dict(x=W / 2, y=H * 0.5, txt="BREACH!", life=1, col=(255, 92, 92), size=30))
                continue
        if t["fly"]:
            t["y"] += math.sin(st["time"] * 3 + t["ph"]) * dt * 2
            if abs(t["x"]) > t["z"] * 0.75:
                t["vx"] *= -1
    targets[:] = [t for t in targets if t["hp"] > 0]
    for p in projs:
        p["vy"] -= p["g"] * dt
        p["life"] -= dt
        nx, ny, nz = p["x"] + p["vx"] * dt, p["y"] + p["vy"] * dt, p["z"] + p["vz"] * dt
        for t in targets:
            if t["hp"] <= 0 or p["dead"]:
                continue
            if p["z"] < t["z"] <= nz:
                f = (t["z"] - p["z"]) / (nz - p["z"] or 1e-9)
                ix, iy = p["x"] + (nx - p["x"]) * f, p["y"] + (ny - p["y"]) * f
                if math.hypot(ix - t["x"], iy - cy_t(t)) < t["r"] * 1.15:
                    d = p["dmg"]
                    if p["falloff"] and t["z"] > p["falloff"]:
                        d *= max(0.3, 1 - (t["z"] - p["falloff"]) / p["falloff"])
                    if p["aoe"]:
                        explode(ix, iy, t["z"], p["aoe"], d)
                    else:
                        dmg(t, d)
                        if not p["noacc"]:
                            st["hits"] += 1
                            if d >= 5:
                                sx, sy = proj(ix, iy, t["z"])
                                floats.append(dict(x=sx, y=sy, txt=str(round(d)), life=0.6,
                                                   col=(255, 255, 255), size=12))
                    p["dead"] = True
                    break
        if p["dead"]:
            continue
        p["x"], p["y"], p["z"] = nx, ny, nz
        if p["y"] <= 0 and p["vy"] < 0:
            if p["aoe"]:
                explode(p["x"], 0, p["z"], p["aoe"], p["dmg"])
            else:
                parts.append(dict(x=p["x"], y=0.05, z=p["z"], vx=0, vy=1, vz=0, life=0.3, ml=0.3,
                                  col=(138, 147, 166), sz=0.1, g=0))
            p["dead"] = True
        if p["z"] > 130 or p["life"] <= 0:
            p["dead"] = True
    projs[:] = [p for p in projs if not p["dead"]]
    for n in nades:
        n["vy"] -= 9.8 * dt
        n["x"] += n["vx"] * dt
        n["y"] += n["vy"] * dt
        n["z"] += n["vz"] * dt
        n["fuse"] -= dt
        if n["y"] <= 0:
            n["y"] = 0
            if abs(n["vy"]) > 1.5:
                n["vy"] *= -0.42
                n["vx"] *= 0.65
                n["vz"] *= 0.65
            else:
                n["vy"] = 0
                n["vx"] *= 0.9
                n["vz"] *= 0.9
        if n["fuse"] <= 0:
            explode(n["x"], max(n["y"], 0.2), n["z"], 5.5, 420)
            n["dead"] = True
    nades[:] = [n for n in nades if not n["dead"]]
    for p in parts:
        p["vy"] -= p.get("g", 0) * dt
        p["x"] += p["vx"] * dt
        p["y"] += p["vy"] * dt
        p["z"] += p["vz"] * dt
        p["life"] -= dt
    parts[:] = [p for p in parts if p["life"] > 0]
    for f in floats:
        f["y"] -= 40 * dt
        f["life"] -= dt
    floats[:] = [f for f in floats if f["life"] > 0]
    for b in beams:
        b["life"] -= dt
    beams[:] = [b for b in beams if b["life"] > 0]
    muzzle = max(0, muzzle - dt * 8)
    redFlash = max(0, redFlash - dt)


# ---------- drawing ----------
def font(size, bold=False):
    return pygame.font.SysFont("segoeui", size, bold=bold)


def txt(surf, s, x, y, size, col, center=False, bold=False):
    img = font(size, bold).render(str(s), True, col)
    r = img.get_rect()
    r.center = (x, y) if center else r.center
    if not center:
        r.topleft = (x, y)
    surf.blit(img, r)


def thick_line(surf, p1, p2, w, col):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    l = math.hypot(dx, dy) or 1
    ox, oy = -dy / l * w / 2, dx / l * w / 2
    pygame.draw.polygon(surf, col, [(p1[0] + ox, p1[1] + oy), (p2[0] + ox, p2[1] + oy),
                                  (p2[0] - ox, p2[1] - oy), (p1[0] - ox, p1[1] - oy)])


def draw_viewmodel(surf, T):
    global muzzle_pos
    w = WEAPONS[wi]
    bx = W * 0.34
    base = H + 60
    sway = math.sin(T * 1.6) * 5
    arm = (20, 27, 38)
    dark = (14, 18, 27)
    trim = (255, 210, 74)
    # cape
    pygame.draw.polygon(surf, (120, 30, 30),
                        [(bx - 60, base - 260), (bx + 30, base - 250),
                         (bx + 70 + sway, base), (bx - 120 + sway, base)])
    # torso
    pygame.draw.ellipse(surf, arm, (bx - 55, base - 270, 130, 200))
    pygame.draw.rect(surf, trim, (bx - 50, base - 130, 120, 8))
    # shoulder pad
    pygame.draw.ellipse(surf, dark, (bx + 20, base - 265, 70, 55))
    # helmet
    hx, hy = bx - 15, base - 330
    pygame.draw.ellipse(surf, dark, (hx, hy, 70, 75))
    pygame.draw.rect(surf, (200, 230, 255), (hx + 12, hy + 34, 46, 9))  # visor
    pygame.draw.line(surf, trim, (hx + 60, hy + 10), (hx + 75, hy - 25), 3)  # antenna
    # gun aimed at crosshair
    sx, sy = bx + 55, base - 235
    ang = math.atan2(cy - sy, cx - sx)
    glen = w["glen"]
    recoil = muzzle * 14
    gx = sx + math.cos(ang) * -recoil
    gy = sy + math.sin(ang) * -recoil
    mxp = (gx + math.cos(ang) * glen, gy + math.sin(ang) * glen)
    muzzle_pos = mxp
    # arms to grip
    grip = (gx + math.cos(ang) * glen * 0.35, gy + math.sin(ang) * glen * 0.35)
    thick_line(surf, (bx + 30, base - 210), grip, 18, arm)
    thick_line(surf, (bx - 10, base - 190), (gx + math.cos(ang) * 10, gy + math.sin(ang) * 10), 16, arm)
    # gun body + barrel
    thick_line(surf, (gx, gy), mxp, 16, dark)
    thick_line(surf, (gx, gy), (gx + math.cos(ang) * glen * 0.55, gy + math.sin(ang) * glen * 0.55), 24, (24, 32, 45))
    thick_line(surf, (mxp[0] - math.cos(ang) * 14, mxp[1] - math.sin(ang) * 14), mxp, 10, w["col"])
    # mag
    mg = (gx + math.cos(ang) * 25, gy + math.sin(ang) * 25)
    thick_line(surf, mg, (mg[0] + math.sin(ang) * 26, mg[1] - math.cos(ang) * 26), 14, dark)
    # muzzle flash
    if muzzle > 0:
        r = 18 * muzzle
        pts = []
        for i in range(8):
            rr = r if i % 2 == 0 else r * 0.4
            a = ang + i * math.pi / 4
            pts.append((mxp[0] + math.cos(a) * rr, mxp[1] + math.sin(a) * rr))
        pygame.draw.polygon(surf, (255, 230, 150), pts)


def panel(surf, rect):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    s.fill((8, 12, 20, 185))
    surf.blit(s, rect[:2])
    pygame.draw.rect(surf, (255, 210, 74), rect, 1)


def draw():
    screen.fill((10, 18, 32))
    pygame.draw.rect(screen, (13, 21, 34), (0, horizon, W, H - horizon))
    th = (255, 150, 60) if faction == "bugs" else (130, 180, 255) if faction == "bots" else (255, 210, 74)
    pygame.draw.line(screen, tuple(int(c * 0.6) for c in th), (0, horizon), (W, horizon))
    grid_col = tuple(int(c * 0.35) for c in th)
    z = 6
    while z <= 100:
        y = proj(0, 0, z)[1]
        pygame.draw.line(screen, grid_col, (0, y), (W, y))
        z += 4 if z < 30 else 8
    for x in range(-40, 45, 5):
        a, b = proj(x, 0, 6), proj(x, 0, 110)
        pygame.draw.line(screen, grid_col, a, b)
    # targets far -> near
    for t in sorted(targets, key=lambda t: -t["z"]):
        s = t["r"] * F / t["z"]
        px, py = proj(t["x"], cy_t(t), t["z"])
        gy = proj(t["x"], 0, t["z"])[1]
        pygame.draw.ellipse(screen, (0, 0, 0), (px - s * 1.1, gy - s * 0.28, s * 2.2, s * 0.56))
        col = (255, 255, 255) if t["flash"] > 0 else t["type"]["col"]
        if t["type"]["kind"] == "bot":
            pygame.draw.rect(screen, col, (px - s, py - s, s * 2, s * 2))
            pygame.draw.rect(screen, (0, 0, 0), (px - s, py - s, s * 2, s * 2), max(1, int(s * 0.06)))
            pygame.draw.rect(screen, (255, 42, 42), (px - s * 0.4, py - s * 0.4, s * 0.8, s * 0.25))
        else:
            pygame.draw.circle(screen, col, (px, py), s)
            pygame.draw.circle(screen, (0, 0, 0), (px, py), s, max(1, int(s * 0.06)))
            pygame.draw.circle(screen, (26, 15, 5), (px - s * 0.3, py - s * 0.2), s * 0.12)
            pygame.draw.circle(screen, (26, 15, 5), (px + s * 0.3, py - s * 0.2), s * 0.12)
        if t["fly"]:
            wob = math.sin(st["time"] * 20 + t["ph"]) * s * 0.5
            pygame.draw.line(screen, col, (px - s, py), (px - s * 2, py - s * 0.4 + wob), max(1, int(s * 0.12)))
            pygame.draw.line(screen, col, (px + s, py), (px + s * 2, py - s * 0.4 - wob), max(1, int(s * 0.12)))
        pygame.draw.rect(screen, (0, 0, 0), (px - s, py - s - 10, s * 2, 4))
        hpc = (125, 255, 92) if t["hp"] / t["type"]["hp"] > 0.4 else (255, 92, 92)
        pygame.draw.rect(screen, hpc, (px - s, py - s - 10, s * 2 * max(0, t["hp"] / t["type"]["hp"]), 4))
        if s > 14:
            txt(screen, t["type"]["n"], px, py - s - 24, 11, (200, 210, 220), center=True)
    # projectiles: tracer from gun muzzle to bullet
    for p in projs:
        b = proj(p["x"], p["y"], p["z"])
        if p["flame"]:
            pygame.draw.circle(screen, p["col"], (int(b[0]), int(b[1])), max(2, int(0.12 * F / p["z"])))
        else:
            pygame.draw.line(screen, p["col"], muzzle_pos, b, 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(b[0]), int(b[1])), 2)
    # grenades
    for n in nades:
        px, py = proj(n["x"], n["y"], n["z"])
        pygame.draw.circle(screen, (30, 30, 34), (int(px), int(py)), max(2, int(0.15 * F / n["z"])))
        if n["fuse"] < 0.8 and int(n["fuse"] * 10) % 2 == 0:
            pygame.draw.circle(screen, (255, 59, 59), (int(px), int(py)), max(2, int(0.1 * F / n["z"])))
    # particles
    for p in parts:
        sx, sy = proj(p["x"], p["y"], p["z"])
        r = max(1, p["sz"] * F / p["z"])
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        s.fill((*p["col"], int(255 * max(0, p["life"] / p["ml"]))))
        screen.blit(s, (sx - r, sy - r))
    # beams / explosion rings
    for b in beams:
        al = max(0, b["life"] / b["ml"])
        if b.get("ring"):
            px, py = proj(b["x"], b["y"], b["z"])
            rr = b["r"] * F / b["z"] * (1 - al)
            pygame.draw.circle(screen, (255, 176, 74), (int(px), int(py)), max(1, int(rr)), 4)
            pygame.draw.circle(screen, (255, 220, 150), (int(px), int(py)), max(1, int(rr * 0.6)), 2)
        else:
            pts = []
            for i, q in enumerate(b["pts"]):
                sx, sy = proj(*q)
                if i:
                    sx += R(-3, 3)
                    sy += R(-3, 3)
                pts.append((sx, sy))
            col = tuple(int(c * (0.5 + 0.5 * al)) for c in b["col"])
            pygame.draw.lines(screen, col, False, pts, 4 if b.get("wide") else 2)
    # floating text
    for f in floats:
        img = font(f["size"], True).render(f["txt"], True, f["col"])
        img.set_alpha(int(255 * max(0, f["life"])))
        screen.blit(img, img.get_rect(center=(f["x"], f["y"])))
    # character + gun
    draw_viewmodel(screen, st["time"])
    # grenade arc preview
    if rDown:
        power = min(1, (pygame.time.get_ticks() - nadeT0) / 1200)
        d = aim_dir()
        s = 9 + 16 * power
        x, y, z = 0.3, CAM_H - 0.2, 0.5
        vx, vy, vz = d[0] * s, d[1] * s + 2, d[2] * s
        for _ in range(40):
            vy -= 9.8 * 0.05
            x += vx * 0.05
            y += vy * 0.05
            z += vz * 0.05
            if y < 0:
                break
            px, py = proj(x, y, z)
            pygame.draw.rect(screen, (255, 210, 74), (px - 1.5, py - 1.5, 3, 3))
        pygame.draw.rect(screen, (255, 210, 74), (cx - 30, cy + 24, 60, 7), 2)
        pygame.draw.rect(screen, (255, 210, 74), (cx - 30, cy + 24, 60 * power, 7))
    if redFlash > 0:
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        s.fill((255, 40, 40, int(redFlash * 100)))
        screen.blit(s, (0, 0))
    # crosshair
    w = WEAPONS[wi]
    cr = 9 + w.get("spread", 0) * 4 + bloom * 10
    pygame.draw.circle(screen, (255, 210, 74), (cx, cy), cr, 1)
    pygame.draw.rect(screen, (255, 210, 74), (cx - 1, cy - 1, 2, 2))
    pygame.draw.line(screen, (255, 210, 74), (cx - cr - 6, cy), (cx - cr, cy))
    pygame.draw.line(screen, (255, 210, 74), (cx + cr, cy), (cx + cr + 6, cy))
    pygame.draw.line(screen, (255, 210, 74), (cx, cy - cr - 6), (cx, cy - cr))
    pygame.draw.line(screen, (255, 210, 74), (cx, cy + cr), (cx, cy + cr + 6))
    if charge >= 0:
        rect = pygame.Rect(cx - cr - 8, cy - cr - 8, (cr + 8) * 2, (cr + 8) * 2)
        pygame.draw.arc(screen, w["col"], rect, math.pi / 2 - charge * math.pi * 2, math.pi / 2, 3)
    if hudOn:
        draw_hud()
    else:
        txt(screen, "H = SHOW UI", 12, H - 24, 11, (255, 210, 74))
    if st["drillDone"]:
        draw_overlay()


def draw_hud():
    ui.clear()
    # title
    txt(screen, "SUPER EARTH COMBAT DRILL", W / 2, 20, 15, (255, 210, 74), center=True, bold=True)
    # stats
    acc = round(100 * st["hits"] / st["shots"]) if st["shots"] else 0
    panel(screen, (12, 12, 170, 96))
    txt(screen, f"SCORE  {st['score']}", 22, 20, 13, (255, 255, 255))
    txt(screen, f"KILLS  {st['kills']}", 22, 38, 13, (255, 255, 255))
    txt(screen, f"ACC    {acc}%", 22, 56, 13, (255, 255, 255))
    txt(screen, f"STREAK {st['streak']}  (best {st['best']})", 22, 74, 13, (255, 255, 255))
    if st["drill"]:
        txt(screen, f"{math.ceil(st['drillLeft'])}s", W / 2, 48, 22, (255, 255, 255), center=True, bold=True)
    else:
        txt(screen, f"TIME   {int(st['time'])}s", 22, 90, 12, (159, 179, 200))
    # help + faction + sens + drill button
    hp = pygame.Rect(W - 250, 12, 238, 150)
    panel(screen, hp)
    txt(screen, "CLICK = lock mouse   ESC = free", hp.x + 10, hp.y + 8, 11, (159, 179, 200))
    txt(screen, "LMB fire   RMB hold = cook nade", hp.x + 10, hp.y + 24, 11, (159, 179, 200))
    txt(screen, "G nade  R reload  1-0/wheel gun", hp.x + 10, hp.y + 40, 11, (159, 179, 200))
    txt(screen, "H hide UI   M mute   F faction", hp.x + 10, hp.y + 56, 11, (159, 179, 200))
    txt(screen, "FIGHTING:", hp.x + 10, hp.y + 76, 11, (255, 210, 74))
    bx = hp.x + 76
    for label, f in (("BUGS", "bugs"), ("BOTS", "bots"), ("MIXED", "mixed")):
        r = pygame.Rect(bx, hp.y + 74, 50, 16)
        ui["fac_" + f] = r
        on = faction == f
        pygame.draw.rect(screen, (60, 50, 20) if on else (20, 26, 36), r)
        pygame.draw.rect(screen, (255, 210, 74) if on else (80, 90, 105), r, 1)
        txt(screen, label, r.centerx, r.centery - 1, 10, (255, 210, 74) if on else (159, 179, 200), center=True)
        bx += 54
    txt(screen, "SENS", hp.x + 10, hp.y + 98, 11, (255, 210, 74))
    sr = pygame.Rect(hp.x + 50, hp.y + 99, 130, 12)
    ui["sens"] = sr
    pygame.draw.rect(screen, (20, 26, 36), sr)
    pygame.draw.rect(screen, (80, 90, 105), sr, 1)
    kx = sr.x + (sens - 0.3) / 1.7 * sr.w
    pygame.draw.circle(screen, (255, 210, 74), (int(kx), sr.centery), 6)
    dr = pygame.Rect(hp.x + 10, hp.y + 120, 120, 20)
    ui["drill"] = dr
    pygame.draw.rect(screen, (60, 50, 20), dr)
    pygame.draw.rect(screen, (255, 210, 74), dr, 1)
    txt(screen, "START 60s DRILL", dr.centerx, dr.centery - 1, 10, (255, 210, 74), center=True)
    # ammo
    w = WEAPONS[wi]
    txt(screen, "RELOADING" if reloadT > 0 else f"{max(0, math.ceil(ammo[wi]))} / {w['mag']}",
        W - 24, H - 220, 30, (255, 255, 255), center=False, bold=True)
    txt(screen, w["name"], W - 24, H - 186, 12, (159, 179, 200))
    # weapon cards
    cw, gap = 104, 6
    total = len(WEAPONS) * (cw + gap) - gap
    x0 = max(8, (W - total) / 2)
    y0 = H - 64
    ui["cards"] = []
    for i, wp in enumerate(WEAPONS):
        r = pygame.Rect(x0 + i * (cw + gap), y0, cw, 54)
        ui["cards"].append(r)
        on = i == wi
        pygame.draw.rect(screen, (50, 42, 16) if on else (16, 21, 30), r)
        pygame.draw.rect(screen, (255, 210, 74) if on else (60, 70, 85), r, 2 if on else 1)
        txt(screen, wp["hk"].upper(), r.x + 5, r.y + 4, 10, (255, 210, 74))
        txt(screen, wp["name"], r.x + 5, r.y + 16, 10, (255, 255, 255))
        txt(screen, wp["note"], r.x + 5, r.y + 28, 9, (159, 179, 200))
        txt(screen, f"AMMO {max(0, math.ceil(ammo[i]))}", r.x + 5, r.y + 40, 9, (124, 242, 255))


def draw_overlay():
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    s.fill((3, 5, 9, 220))
    screen.blit(s, (0, 0))
    box = pygame.Rect(W / 2 - 220, H / 2 - 110, 440, 220)
    pygame.draw.rect(screen, (10, 15, 24), box)
    pygame.draw.rect(screen, (255, 210, 74), box, 2)
    acc = round(100 * st["hits"] / st["shots"]) if st["shots"] else 0
    txt(screen, "DRILL COMPLETE", W / 2, box.y + 34, 24, (255, 210, 74), center=True, bold=True)
    txt(screen, f"SCORE: {st['score']}", W / 2, box.y + 80, 16, (207, 224, 240), center=True)
    txt(screen, f"KILLS: {st['kills']}   |   BEST STREAK: {st['best']}", W / 2, box.y + 106, 14, (207, 224, 240), center=True)
    txt(screen, f"ACCURACY: {acc}%", W / 2, box.y + 130, 14, (207, 224, 240), center=True)
    br = pygame.Rect(W / 2 - 60, box.y + 160, 120, 32)
    ui["continue"] = br
    pygame.draw.rect(screen, (255, 210, 74), br)
    txt(screen, "CONTINUE", br.centerx, br.centery - 1, 12, (0, 0, 0), center=True, bold=True)


def reset_stats():
    global spawnT, reloadT, charge
    st.update(score=0, kills=0, shots=0, hits=0, streak=0, time=0.0, drillDone=False)
    targets.clear(); projs.clear(); nades.clear(); parts.clear(); floats.clear(); beams.clear()
    for i, w in enumerate(WEAPONS):
        ammo[i] = w["mag"]
    reloadT = 0
    spawnT = 0.5
    charge = -1


def start_drill():
    reset_stats()
    st["drill"] = True
    st["drillLeft"] = 60.0


def end_drill():
    st["drill"] = False
    st["drillDone"] = True


def set_grab(on):
    global grabbed
    grabbed = on
    pygame.event.set_grab(on)
    pygame.mouse.set_visible(not on)


def select_weapon(i):
    global wi, reloadT, charge
    wi = i % len(WEAPONS)
    reloadT = 0
    charge = -1


def hud_click(pos):
    if st["drillDone"] and ui.get("continue") and ui["continue"].collidepoint(pos):
        st["drillDone"] = False
        reset_stats()
        return True
    if not hudOn:
        return False
    for f in ("bugs", "bots", "mixed"):
        if ui.get("fac_" + f) and ui["fac_" + f].collidepoint(pos):
            set_faction(f)
            return True
    if ui.get("sens") and ui["sens"].collidepoint(pos):
        global sens
        r = ui["sens"]
        sens = 0.3 + max(0, min(1, (pos[0] - r.x) / r.w)) * 1.7
        return True
    if ui.get("drill") and ui["drill"].collidepoint(pos):
        start_drill()
        return True
    for i, r in enumerate(ui.get("cards", [])):
        if r.collidepoint(pos):
            select_weapon(i)
            return True
    return False


def toggle_fullscreen():
    global screen, fullscreen, W, H, F, horizon
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((1600, 900), pygame.RESIZABLE)
    W, H = screen.get_size()
    F, horizon = H * 0.95, H * 0.40


def main():
    global cx, cy, charge, nadeT0, rDown, accT, W, H, F, horizon, muted, hudOn, sens
    init_sounds()
    for _ in range(3):
        spawn()
    while True:
        dt = min(0.033, clock.tick(120) / 1000)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.VIDEORESIZE and not fullscreen:
                W, H = e.size
                F, horizon = H * 0.95, H * 0.40
                screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
            if e.type == pygame.MOUSEMOTION:
                if grabbed:
                    cx = max(0, min(W, cx + e.rel[0] * sens))
                    cy = max(0, min(H, cy + e.rel[1] * sens))
                else:
                    cx, cy = e.pos
                if not grabbed and pygame.mouse.get_pressed()[0] and ui.get("sens") and ui["sens"].collidepoint(e.pos):
                    r = ui["sens"]
                    sens = 0.3 + max(0, min(1, (e.pos[0] - r.x) / r.w)) * 1.7
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    if grabbed:
                        w = WEAPONS[wi]
                        if reloadT <= 0:
                            if w["mode"] == "semi" and cd <= 0:
                                fire()
                                cd = 60 / w["rpm"]
                            elif w["mode"] == "zap" and cd <= 0:
                                zap()
                            elif w["mode"] == "charge":
                                charge = 0
                    elif not hud_click(e.pos):
                        set_grab(True)
                elif e.button == 3:
                    if grabbed:
                        rDown = True
                        nadeT0 = pygame.time.get_ticks()
                elif e.button in (4, 5):
                    select_weapon(wi + (1 if e.button == 4 else -1))
            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    if charge >= 0:
                        if charge >= 0.35:
                            rail(charge)
                        charge = -1
                    accT = 0
                elif e.button == 3 and rDown:
                    throw_nade(min(1, (pygame.time.get_ticks() - nadeT0) / 1200))
                    rDown = False
            if e.type == pygame.KEYDOWN:
                k = e.key
                if k == pygame.K_ESCAPE and grabbed:
                    set_grab(False)
                elif k == pygame.K_F11:
                    toggle_fullscreen()
                elif k == pygame.K_r:
                    start_reload()
                elif k == pygame.K_g:
                    throw_nade(0.55)
                elif k == pygame.K_m:
                    muted = not muted
                elif k == pygame.K_f:
                    set_faction({"mixed": "bugs", "bugs": "bots", "bots": "mixed"}[faction])
                elif k == pygame.K_h:
                    hudOn = not hudOn
                elif k == pygame.K_RETURN and st["drillDone"]:
                    st["drillDone"] = False
                    reset_stats()
                else:
                    name = pygame.key.name(k)
                    for i, wp in enumerate(WEAPONS):
                        if wp["hk"] == name:
                            select_weapon(i)
        update(dt)
        draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
