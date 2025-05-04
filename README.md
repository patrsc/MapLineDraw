# MapLineDraw

Sketch corridors of railway lines or roads on an interactive map.
Show properties like length and maximum speed.
Free and open source.
https://maplinedraw.com

## Develop

### Clone repository

```
git clone https://github.com/patrsc/MapLineDraw.git
cd MapLineDraw
```

### Run API

Change directory:
```
cd api
```

Install dependencies:
```
poetry install
```

Run API:
```
poetry run fastapi dev api.py
```

### Run web site

Change directory:
```
cd web
```

Make sure to install dependencies:

```bash
npm install
```

Start the development server on `http://localhost:3000`:

```bash
npm run dev
```

Build the application for production:

```bash
npm run build
```

Locally preview production build:
```bash
npm run preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.
Look at the [Nuxt documentation](https://nuxt.com/docs/getting-started/introduction) to learn more.

## Deploy

See [Deployment Guide](deploy.md) how to deploy to [maplinedraw.com](https://maplinedraw.com).

## TODO

* publish:
  * save immutable copy on server, link = hash of JSON file (concise JSON)
  * deleted after 1 year
  * re-publish resets timer
  * Open this project (discards current project) | Re-publish | Download | Copy link | Back to your project
  * project can only be accessed by link: `maplinedraw.com/public/{id}`, read-only
  * max file size?
* transfer curve computation to JavaScript
* implement normal mode:
  * click on point selects point
  * point: show lat, lon and "Delete point" button (key Backspace)
  * drag point selects it
  * add intermediate point selects it
  * default selected point: last point
* main tabs:
  * Project: name+author, description, curve list, curve+point Properties, Legend
  * Colors: select colormap and map background tiles
  * Help: help texts
* curvature plot preview over distance with point "sync"
* split curve at selected point
* join curves: select endpoint of one curve, click merge, select endpoint of another curve
* switch curve direction
* altitude:
  * set altitude of control points:
    * value above sea: `float`
    * interpolate: `"auto"` (linear interpolation using altitude from other points)
    * at ground level: `"ground"`
    * value above ground level: `{"ground": float}`
  * pass altitude to API as float value
  * use altitude when generating spline, compute slope
  * get ground level of curve from an elevation API:
    - https://www.opentopodata.org/
    - https://open-elevation.com/
    - https://portal.opentopography.org/datasetMetadata?otCollectionID=OT.032021.4326.1
    - https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM
    - https://portal.opentopography.org/apidocs/#/Public/getGlobalDem
    - https://opentopomap.org/#map=14/48.29402/14.21824
    - https://maplibre.org/news/2022-05-20-terrain3d/#12.02/47.24003/11.30863/-96.8/65
    - https://portal.opentopography.org/raster?opentopoID=OTALOS.112016.4326.2
    - https://observablehq.com/@bert/terrains-with-maplibre
    - https://www.maptoolkit.com/map/#/@14.52534,48.25086,14.2,0,68.5,terrain,3d
    - https://docs.maptiler.com/sdk-js/examples/3d-map/
    - https://sandbox.openglobus.org/
    - https://github.com/felixpalmer/procedural-gl-js
    - https://docs.mapbox.com/mapbox-gl-js/example/add-terrain/
    - https://outragegis.com/gorge/map/#15.86/37.827336/-83.622855/24.8/66
    - https://www.youtube.com/watch?v=CPBUJJ2y_qY
  * compute ground level of resulting curve
  * bridge: curve > 6m over ground (bright blue hairline on right curve side)
  * tunnel: curve > 6m under ground (brown hairline on left curve side)
  * display plot: curve altitude compared to ground altitude over distance
