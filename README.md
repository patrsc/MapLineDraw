# MapLineDraw

Sketch corridors of railway lines or roads on an interactive map. Draw smooth spline curves on real maps.
Show properties like length and maximum speed.
Free and open source. [maplinedraw.com](https://maplinedraw.com)

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

## References

* [maplinedraw.com](https://maplinedraw.com/)
* [Draw Smooth Curves on Real Maps with MapLineDraw](https://medium.com/@patrsc/introducing-maplinedraw-draw-smooth-curves-on-real-maps-free-and-open-source-e1e6a6f9d39e) ([source file](article.md))
* [Future Ideas](ideas.md)
