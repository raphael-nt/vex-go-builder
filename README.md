# VEX GO Builder

A browser-based 3D builder for VEX GO. Parts come from the official VEX GO STEP CAD files.
Click a part, click a hole on the model, and it snaps into place.

## Features

- **Builder**: part library with thumbnails and colors, snap to holes, rotate (R), change hole (T), tilt (F), Undo, parts used vs. quantity in the kit, save and load as JSON
- **Instructions**: step-by-step playback with parts flying in, orbit camera, parts list per step, link to the official VEX instructions
- Built-in models: Competition Base (55 parts, 28 steps) and Competition Advanced (131 parts), built from VEX instructions 269-8115-010 and 269-8115-040
- Thai and English UI

## Run locally

The app is plain static files in `docs/`. Any static server works:

```
cd docs
python3 -m http.server 8000
```

Open http://localhost:8000. three.js loads from the jsDelivr CDN, so the first load needs internet.

## Deploy

- **GitHub Pages**: Settings, Pages, deploy from branch `main`, folder `/docs`
- **Cloudflare Pages / Netlify**: set the output directory to `docs`, no build command

Saving to a shared database only works inside Claude artifacts. On a normal host, Save keeps the model in the browser, and File exports JSON.

## Layout

```
docs/    the web app (index.html, parts.json, models, m/ meshes, t/ thumbnails)
tools/   STEP to mesh pipeline: conv, batch, export, holes, connectors, catalog, trim
build/   scripted models (lib.py, base.py, adv.py) that write the model JSON
```

The pipeline needs `cadquery-ocp`, `trimesh`, `fast-simplification` and `gltfpack`. Paths inside the scripts point to the original working folders, so adjust them before rerunning.

## Parts data

Parts are identified by VEX part number (for example 228-2500-001). `parts.json` also carries the matching name from the VEX IQ Legal Parts list where the numbers overlap. Some part names are inferred, and a few parts (LED Bumper, Electromagnet, Slide Beam) have no connectors yet.
