# MapLineDraw

Sketch corridors of railway lines or roads on an interactive map.
Show properties like length and maximum speed.
Free and open source.
https://maplinedraw.com

![example](example.jpg)

## Introduction

MapLineDraw is a free, open source web application that lets you draw smooth curves on a map.
* It lets hobbyists draw infrastructure corridors,
for example railway lines or highways, and share their ideas with others.
* It can be also used as a measurement or data extraction tool: you can for example draw a curve
over existing objects, such as roads, race tracks, railways, or rivers to get their length or
extract their curve data (control points of a spline).

MapLineDraw allows you to:
* Draw smooth curves and show curve properties such as curve length, minimal radius and its corresponding maximum
  speed (using a typical design value for comfortable lateral acceleration of railways). Curves are
  represented using draggable control points and use B-splines of degree 3, which leads to a continuous curvature.
* Make open or closed (circular) curves. Add, move and remove curve control points as you need.
* Enter project information: Project name, author and description.
* Download your projects as JSON files to save them locally.
* Share projects using sharing links. Those projects can be directly shared with others and open
  directly in the web app.
* Show different colored legends (you can edit them in the saved JSON file with a text editor).

Have fun in drafting your visions for the future of public infrastructure!

Note that this is not a professional program for infrastructure projects and does for example not consider
elevation (bridges or tunnels).

Any project you see on [maplinedraw.com](https://maplinedraw.com) is intended only for discussion and idea sharing and does not mean that what you see is a finalized project that will be built in reality.

## Usage

Go to [maplinedraw.com](https://maplinedraw.com) and try it yourself.

### Keyboard shortcuts

* Press <kbd>d</kbd> to toggle draw mode.
* Press <kbd>backspace</kbd> or <kbd>del</kbd> to delete a curve.
* Press <kbd>esc</kbd> to unselect curve.

### Limitations

The application does not yet work well on mobile devices.

## Feedback

Having problems or need a feature? [Create an issue](https://github.com/patrsc/MapLineDraw/issues/new) in GitHub.

## Contributing

To contribute source code, fork the repository and create a pull request.

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

## License

License is [MIT](LICENSE.md).

## Future ideas

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
