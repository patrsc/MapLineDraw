<template>
    <main>
        <div class="container" style="max-width: 960px;">
            <div class="row mt-3">
                <div class="col">
                    <NuxtLink to="/" type="button" class="btn btn-sm btn-outline-secondary"><Ico name="fa6-solid:arrow-left"/> Back to project</NuxtLink>
                </div>
            </div>
            <article class="mb-5">
                <div class="px-4 py-5 text-center">
                    <Logo class="mb-3"/>
                    <h1 class="display-5 fw-bold text-body-emphasis">MapLineDraw</h1>
                    <div class="col-md-10 mx-auto">
                        <p class="text-muted lead mb-4 subtitle"><strong>Draw smooth curves on real maps.</strong></p>
                        <p class="lead mb-4">
                        MapLineDraw lets you sketch corridors of railway lines or roads on an interactive map using smooth spline curves, ready to share with others.
                        </p>
                        <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
                            <NuxtLink to="/" type="button" class="btn btn-primary px-4 gap-3">Start your project</NuxtLink>
                            <a href="https://github.com/patrsc/MapLineDraw" target="_blank" type="button" class="btn btn-outline-secondary px-4"><Ico name="fa7-brands:github"/> View on GitHub</a>
                        </div>
                    </div>
                </div>

                <p class="text-center">
                    <img src="/example.jpg" alt="Example of MapLineDraw" class="img-fluid rounded my-3">
                </p>
                <p>
                    Whether you're a transit enthusiast, a city planner, or just someone who loves to visualize infrastructure,
                    <a href="https://maplinedraw.com" target="_blank" rel="noopener">MapLineDraw</a>
                    is a free and open source web application designed to let you draw smooth curves on a map provided by
                    <a href="https://www.openstreetmap.org/" target="_blank" rel="noopener">OpenStreetMap</a>.
                </p>
                <h2>What Is MapLineDraw?</h2>
                <p>
                    <strong>MapLineDraw</strong> is a free, open source web application that lets you
                    <strong>draw smooth spline curves</strong> directly on an interactive map (using OpenStreetMap tiles). The tool is ideal for:
                </p>
                <ul>
                    <li>Sketching <strong>railway lines</strong>, <strong>highways</strong>, <strong>race tracks</strong>, or other paths</li>
                    <li>Measuring real-world infrastructure curves</li>
                    <li>Visualizing concepts for future public transport</li>
                    <li>Sharing your ideas with others using simple, link-based projects</li>
                </ul>
                <p>
                    Typically line-drawing tools rely on connected straight segments. MapLineDraw uses
                    <strong>cubic B-splines</strong>, which means it can represent curved lines with
                    <strong>continuous curvature</strong> — an important feature in real-world railroad or road design.
                </p>

                <h2>Key Features</h2>

                MapLineDraw comes with many useful features, such as the following:

                <div class="row row-cols-1 row-cols-sm-2 g-4 pt-5">

                    <div class="col d-flex align-items-start">
                        <div class="text-primary flex-shrink-0 me-3" style="width: 2rem">
                            <Ico name="fa7-solid:pencil" size="1.5rem" width="1.5rem"/>
                        </div>
                        <div>
                        <h3 class="fw-bold mb-0 fs-4 text-body-emphasis">Interactive Spline Drawing</h3>
                        <p class="text-muted">Click to place control points, drag them to adjust, and instantly see the resulting curve update in real time.</p>
                        </div>
                    </div>

                    <div class="col d-flex align-items-start">
                        <div class="text-primary flex-shrink-0 me-3" style="width: 2rem">
                            <Ico name="fa7-solid:bezier-curve" size="1.5rem"/>
                        </div>
                        <div>
                        <h3 class="fw-bold mb-0 fs-4 text-body-emphasis">Cubic B-splines</h3>
                        <p class="text-muted">Smooth spline paths of degree 3 with continuous curvature for realistic road and rail geometry.</p>
                        </div>
                    </div>

                    <div class="col d-flex align-items-start">
                        <div class="text-primary flex-shrink-0 me-3" style="width: 2rem">
                            <Ico name="fa7-solid:ruler" size="1.5rem"/>
                        </div>
                        <div>
                        <h3 class="fw-bold mb-0 fs-4 text-body-emphasis">Automatic Geometry Analysis</h3>
                        <p class="text-muted">Calculates curve length, minimum radius, and estimated maximum speed using comfort-based acceleration limits.</p>
                        </div>
                    </div>

                    <div class="col d-flex align-items-start">
                        <div class="text-primary flex-shrink-0 me-3" style="width: 2rem">
                            <Ico name="fa7-solid:arrow-rotate-forward" size="1.5rem"/>
                        </div>
                        <div>
                        <h3 class="fw-bold mb-0 fs-4 text-body-emphasis">Open or Closed Curves</h3>
                        <p class="text-muted">Supports both open routes and closed loops — ideal for tracks, circuits, and circular paths.</p>
                        </div>
                    </div>

                    <div class="col d-flex align-items-start">
                        <div class="text-primary flex-shrink-0 me-3" style="width: 2rem">
                            <Ico name="fa7-solid:file-alt" size="1.5rem"/>
                        </div>
                        <div>
                        <h3 class="fw-bold mb-0 fs-4 text-body-emphasis">Project Metadata</h3>
                        <p class="text-muted">Add a project name, author, and description to document your design ideas clearly.</p>
                        </div>
                    </div>

                    <div class="col d-flex align-items-start">
                        <div class="text-primary flex-shrink-0 me-3" style="width: 2rem">
                            <Ico name="fa7-solid:cloud-arrow-down" size="1.5rem"/>
                        </div>
                        <div>
                        <h3 class="fw-bold mb-0 fs-4 text-body-emphasis">Download and Share</h3>
                        <p class="text-muted">Save projects to a JSON file containing geometry and metadata, or share them via link-based URLs.</p>
                        </div>
                    </div>

                    <div class="col d-flex align-items-start">
                        <div class="text-primary flex-shrink-0 me-3" style="width: 2rem">
                            <Ico name="fa7-solid:palette" size="1.5rem"/>
                        </div>
                        <div>
                        <h3 class="fw-bold mb-0 fs-4 text-body-emphasis">Customizable Legends</h3>
                        <p class="text-muted">Color-coded curves editable in the JSON file help clarify and organize your visualizations.</p>
                        </div>
                    </div>

                </div>

                <h2>Use Cases</h2>
                <p>
                    Infrastructure design is no longer the exclusive domain of specialized, expensive CAD tools. With
                    <strong>MapLineDraw</strong>, anyone can:
                </p>
                <ul>
                    <li>Draft hypothetical <strong>rail corridors</strong> across regions</li>
                    <li>Analyze <strong>existing road or rail curves</strong> for speed feasibility</li>
                    <li>Trace <strong>real-world routes</strong> for measurement or export</li>
                    <li>Sketch <strong>race track concepts</strong>, nature trails, or fantasy transit systems</li>
                </ul>
                <p>It's a tool built for hobbyists, students, planners, and open data advocates.</p>

                <h2>Export and Import</h2>
                <p>
                    While MapLineDraw does not currently export GeoJSON or KML, it allows you to download your project in a custom JSON format. This includes:
                </p>
                <ul>
                    <li>Curve type (open or closed)</li>
                    <li>Degree of spline</li>
                    <li>Control point coordinates (lat/lon)</li>
                    <li>Project metadata and legend</li>
                </ul>
                <p>
                    Because the format is clean and structured, it's easy to convert into other formats using a simple script — or fork the project to add that feature.
                </p>

                <h2>Open Source</h2>
                <p>
                    MapLineDraw is fully open source under the
                    <a href="https://github.com/patrsc/MapLineDraw/blob/main/LICENSE.md" target="_blank" rel="noopener">MIT license</a>.
                    You can:
                </p>
                <ul>
                    <li>View or contribute on <a href="https://github.com/patrsc/MapLineDraw" target="_blank" rel="noopener">GitHub</a></li>
                    <li>Suggest features or report bugs via issues</li>
                    <li>Fork the project and customize it to your needs</li>
                </ul>

                <h2>Known Limitations</h2>
                <p>MapLineDraw is <strong>not a professional-grade design tool</strong>. Its goal is simplicity, accessibility, and visual clarity — not engineering validation.</p>
                <ul>
                    <li>No elevation (height) support (no tunnels or bridges yet)</li>
                    <li>No mobile browser optimization (best used on desktop)</li>
                    <li>No built-in export to GIS formats (yet)</li>
                </ul>

                <h2>Conclusion</h2>
                <p>
                    MapLineDraw provides a simple and free drawing tool for curves on a real map. Whether you're mapping the next
                    high-speed rail link or tracing an existing corridor for fun, it's a tool that helps ideas take shape — smoothly.
                    Visit <a href="https://maplinedraw.com/" target="_blank" rel="noopener">maplinedraw.com</a> to start drawing.
                </p>
                <p>
                    If you like the tool or have suggestions for improvement, contribute or open an issue on
                    <a href="https://github.com/patrsc/MapLineDraw/issues" target="_blank" rel="noopener">GitHub</a>.
                </p>
            </article>
        </div>
    </main>
</template>

<style scoped>
h2 {
    margin-top: 3rem;
    margin-bottom: 1.5rem;
    font-weight: bold;
}
.container {
    margin-bottom: 5rem;
}
.subtitle {
    font-size: 1.6rem;
}
</style>

<script setup lang="ts">
useHead({
    title: 'About MapLineDraw',
})
</script>
