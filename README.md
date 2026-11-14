# VEX GO Builder

A browser-based 3D builder for VEX GO. Parts come from the official VEX GO STEP CAD files.
Click a part, click a hole on the model, and it snaps into place.

## Features

- **Builder**: part library with thumbnails and colors, snap to holes, rotate (R), change hole (T), tilt (F), Undo, parts used vs. quantity in the kit, save and load as JSON
- **Showcase**: turn the model and tap a part to see its name, highlight every part of one kind, or switch to 2D and swipe through 10 pictures around the robot
- **Instructions**: step-by-step playback with parts flying in, orbit camera, parts list per step, link to the official VEX instructions
- Built-in models: Competition Base (55 parts, 28 steps) and Competition Advanced (133 parts, 50 steps), built from VEX instructions 269-8115-010 and 269-8115-040
- Thai and English UI, click sounds (can be muted), saved models with preview pictures in Open
- Works on phones, tablets and desktop
- CAD-style tools: undo and redo, copy, paste, duplicate, mirror left-right, groups, hide and isolate,
  parts tree, view cube with fit, X-ray, section view, measure, collision warning, right-click menu,
  library search, PNG and CSV export, shortcut sheet (press ?)
- Drag a part to move it (no Take off needed), Lock (L) keeps parts from moving, Ctrl and drag for box select,
  named groups in a group list, blinking marker on the chosen hole
- Icon toolbar grouped by task (history, part in hand, selection, step) with tooltips that show the shortcut; Ctrl+S saves
- Cloud save to a Supabase project with a room code (see `supabase/vexgo_models.sql`)

## Run locally

The app is plain static files in `docs/`. Any static server works:

```
cd docs
python3 -m http.server 8000
```

Open http://localhost:8000. three.js and three-mesh-bvh load from the jsDelivr CDN, so the first load needs internet.

## Deploy

- **GitHub Pages**: Settings, Pages, deploy from branch `main`, folder `/docs`
- **Cloudflare Pages / Netlify**: set the output directory to `docs`, no build command

Saving to a shared database only works inside Claude artifacts. On a normal host, Save keeps the model in the browser, and File exports JSON.

## Layout

```
docs/    the web app (index.html, parts.json, models, m/ part meshes as .glb, t/ thumbnails)
tools/   step2glb.py turns the VEX GO STEP files into GLB meshes, colors.py writes kit colors into parts.json,
         the rest (holes, connectors, catalog) find the pin and shaft holes
build/   scripted models (lib.py, base.py, adv.py) that write the model JSON. adv.py is plain Python (python build/adv.py)
         and builds Competition Advanced on top of docs/model-base.json
```

Meshes keep the full STEP tessellation (no polygon reduction) and the CAD colors of every face.
Each GLB has one material per color. The largest one is named `main_<hex>`, and a kit color variant
in `parts.json` (`ov`) can replace it, for example the red and green Disk. Electronics cables are removed.

```
python3 tools/step2glb.py "<GO kit STEP folder>" glb      # needs cadquery-ocp, trimesh, gltfpack (npm)
python3 tools/colors.py                                  # after reading mesh bounds and material names
```

Some script paths point to the original working folders, so adjust them before rerunning.

## Parts data

Parts are identified by VEX part number (for example 228-2500-001). `parts.json` also carries the matching name from the VEX IQ Legal Parts list where the numbers overlap. Some part names are inferred, and a few parts (LED Bumper, Electromagnet, Slide Beam) have no connectors yet.
