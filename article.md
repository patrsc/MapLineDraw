# Draw Smooth Curves on Real Maps with MapLineDraw

MapLineDraw lets you sketch corridors of railway lines or roads on an interactive map using smooth spline curves, ready to share with others.

Whether you're a transit enthusiast, a city planner, or just someone who loves to visualize infrastructure, [MapLineDraw](https://maplinedraw.com) is a free and open source web application designed to let you draw smooth curves on a map provided by [OpenStreetMap](https://www.openstreetmap.org/).

![example](example.jpg)

## What Is MapLineDraw?

**MapLineDraw** is a free, open source web application that lets you **draw smooth spline curves** directly on an interactive map (using OpenStreetMap tiles). The tool is ideal for:
* Sketching **railway lines**, **highways**, **race tracks**, or other paths
* Measuring real-world infrastructure curves
* Visualizing concepts for future public transport
* Sharing your ideas with others using simple, link-based projects

Typically line-drawing tools rely on connected straight segments. MapLineDraw uses **cubic B-splines**, which means it can represent curves with **continuous curvature** — an important feature in real-world rail or road design.


## Key Features

The most important features of MapLineDraw are:

* 🎯 **Interactive Spline Drawing**  
  Click to place control points, drag them to adjust, and instantly see the resulting curve update in real time.

* 🧩 **Cubic B-splines (Degree 3)**  
  Smooth paths with continuous curvature.

* 📏 **Automatic Geometry Analysis**  
  The app calculates total curve length, minimum radius, and estimated **maximum speed** using typical comfort-based acceleration thresholds used in railway engineering.

* 🔄 **Open or Closed Curves**  
  Usable for both routes and loops — you can do track modeling, circular paths, and more.

* 📝 **Project Metadata**  
  Add a name, author, and description for your design ideas.

* 📂 **Download and Share**  
  Save your projects to a custom *.json* file, which includes all curve geometry and metadata. Or, use shareable URLs to send your project directly to others.

* 🎨 **Customizable Legends**  
  Color-coded curves, editable via the project JSON file to help clarify your visualizations.

## Use Cases

Infrastructure design is no longer the exclusive domain of specialized, expensive CAD tools. With **MapLineDraw**, anyone can:

* Draft hypothetical **rail corridors** across regions
* Analyze **existing road or rail curves** for speed feasibility
* Trace **real-world routes** for measurement or export
* Sketch **race track concepts**, nature trails, or even fantasy transit systems

It's a tool built for hobbyists, students, planners, or open data advocates.

## Export and Import

While MapLineDraw does not currently export GeoJSON or KML, it allows you to download your project in a custom JSON format. This includes:

* Curve type (open or closed)
* Degree of spline
* Control point coordinates (lat/lon)
* Project metadata and legend

Because the format is clean and structured, it's easy to convert into other formats using a simple script — or fork the project to add that feature.

## Open Source

MapLineDraw is fully open source under the [MIT license](https://github.com/patrsc/MapLineDraw). You can:

* View or contribute on GitHub: https://github.com/patrsc/MapLineDraw
* Suggest features or report bugs via issues
* Fork the project and customize it to your needs

## Known Limitations

MapLineDraw is **not a professional-grade design tool**. Its goal is simplicity, accessibility, and visual clarity, not engineering validation.

* No elevation (height) support (so no tunnels/bridges yet)
* No mobile browser optimization (best used on desktop)
* No built-in export to GIS formats (yet)

## Conclusion

MapLineDraw provides a simple and free drawing tool for curves on a real map. Whether you're mapping out the next high-speed rail link or tracing an existing corridor for fun, it's a tool that helps ideas take shape — smoothly. Go to [maplinedraw.com](https://maplinedraw.com/) and start drawing.

If you like the tool or have suggestions how to improve it, feel free to contribute or open an issue on GitHub: https://github.com/patrsc/MapLineDraw.
