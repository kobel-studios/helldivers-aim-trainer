# Helldivers 2 Aim Trainer

A Helldivers 2 style aim trainer with projectile drop, grenade arcs, and the HD2 weapon roster.

## GUI App (recommended)

Real windowed app — you play as a Helldiver, over-the-shoulder view, tracers come out of the actual gun barrel.

```
pip install pygame
python aim_trainer.py
```

Or double-click the **Helldivers Aim Trainer** desktop shortcut.

## Browser version

Open `index.html` in any browser — no install, no dependencies.

## Features

- **Helldiver character viewmodel** — see your diver, cape, and gun; shots fire from the muzzle
- **Projectile drop** — slow rounds (Dominator, Eruptor, Recoilless) fall over distance, aim above far targets
- **Charged grenades** — hold RMB to cook, dotted arc preview shows the throw, bounce + fuse + AoE
- **HD2 weapon roster** — 11 weapons with different fire modes, drop, spread, AoE, falloff
- **Faction picker** — Terminids, Automatons, or mixed spawns
- **Bug & bot targets** — Scavengers, Hunters, Warriors, Bile Spewers, Shriekers, Troopers, Devastators, Hulks
- **60s drill mode**, score / accuracy / streak tracking
- **Pointer-lock aiming** — mouse never hits the window edge

## Weapons

| Key | Weapon | Style |
|-----|--------|-------|
| 1 | AR-23 Liberator | Auto, minimal drop |
| 2 | SG-225 Breaker | 9-pellet spread, falloff |
| 3 | R-36 Eruptor | Slow bolt, drops, explodes |
| 4 | JAR-5 Dominator | Heavy drop — aim high |
| 5 | PLAS-1 Scorcher | Plasma, slight drop, AoE |
| 6 | AC-8 Autocannon | Fast shell, mild drop |
| 7 | GR-8 Recoilless | Arcs at range, huge boom |
| 8 | LAS-16 Sickle | Hitscan beam, no drop |
| 9 | FLAM-40 | ~12m fire cone |
| 0 | ARC-12 Blitzer | Instant arc, chains |
| - | RS-422 Railgun | Hold to charge, pierces |

## Controls

- **Click window** — lock mouse (FPS aim), **ESC** releases it
- **LMB** — fire (hold for auto/beam/flame, hold to charge railgun)
- **RMB hold** — cook grenade with arc preview, release to throw
- **G** — quick grenade, **R** — reload
- **1-0, -** / scroll wheel / click cards — switch weapon
- **F** — cycle faction, **H** — hide UI, **M** — mute
- **F11** — fullscreen (app version)

For Super Earth.
