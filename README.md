# Prism Path

A **lines slot for the Stake Engine** platform. 5×5 board, 15 paylines. Signature feature:
the rare **Prism Beast** wild lands facing a random direction and fires a path of multiplier-wilds
to the board edge; when two beasts touch the same winning line their multipliers **multiply**.

Architecture is **predetermined / book-driven**: the math (Python) computes every outcome and ships
it to the frontend as an ordered array of book events. The frontend (Svelte 5 + PixiJS 8 + XState)
only choreographs those events — no outcome-affecting logic on the client.

## Repo layout
```
prism-path/
├── math/        # fork of StakeEngine math-sdk; our game lives in games/prism_path
└── frontend/    # fork of StakeEngine web-sdk (pnpm monorepo); our app is apps/prism-path
```
Each half is a faithful monorepo fork — `apps/lines` depends on ~28 workspace packages, so the
only viable fork keeps the monorepo and adds a new app/game.

## Run — math (Python 3.12)
```powershell
cd math
python -m venv env
.\env\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.local.txt   # deps minus the VCS-editable line
python -m pip install -e .
python games\prism_path\run.py                     # Phase 1: optimizer stubbed, flat odds
python games\prism_path\scenario.py --help         # force beast / overlap / whiff / near-max / zero
```
Outputs land in `math/games/prism_path/library/publish_files/` (`index.json`, books, lookup table).

## Run — frontend (Node ≥22.16, pnpm 10.5)
```powershell
cd frontend
pnpm install
pnpm --filter prism-path storybook   # Phase-1 offline dev loop (RGS disabled), plays scenario books
```

## Phase status
**Phase 1 (function/feel)** — full resolver + scenario controller + playable skeleton wired to forced
books; optimizer STUBBED, flat odds. Rules lock after human feel sign-off. Phase 2 (calibration) is gated.
