<!doctype html>

<meta charset="utf-8">
<title>{{pagetitle}}</title>

<link   rel="stylesheet" href="/static/style.css">
<script src="/static/d3.v3.min.js" charset="utf-8"></script>
<script src="/static/dagre-d3.js"></script>
<script src="/static/jquery-3.1.1.min.js" charset="utf-8"></script>

<style id="css">
    text {
        font-weight:    300;
        font-family:    "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size:      14px;
    }

    .node rect {
        stroke:         #999;
        fill:           #fff;
        stroke-width:   1.5px;
    }

    .edgePath path {
        stroke:         #333;
        stroke-width:   1.5px;
    }

    #link_map {
        position:       absolute;
        top:            10px;
        right:          10px;
    }
</style>

<h1 class="pagetitle" id="pagetitle">{{pagetitle}}</h1>

<div class="version" id="version">
    <p>{{version}}</p>
</div>

<div class="logo" id="logo">
  <img src="/static/logo_dust.png" alt="logo" />
</div>

<svg id="svg-canvas"></svg>

<a id="link_map" href="/map"><img src="../static/logo_map.png"></a>

<script id="js">

    var currentTopology = ''

    function positionStuff() {
        // svg-canvas
        $('#svg-canvas').offset(
            {
                top:  0,
                left: 0
            }
        );
        $('#svg-canvas').attr('width',  $(window).width()-5);
        $('#svg-canvas').attr('height', $(window).height()-5);
        // pagetitle
        $('#pagetitle').offset(
            {
                top:  20,
                left: 20
            }
        );
        // version
        $('#version').offset(
            {
                top:  $(window).height()-60,
                left: 20
            }
        );
        // logo
        $('#logo').offset(
            {
                top:  $(window).height()-80-20,
                left: $(window).width()-200-20
            }
        );
        $('#logo').css('z-index',-1);
    }
    function getTopologyJson() {
        $.getJSON( "/topology.json", function( topology ) {
            drawTopology(topology);
        });
    }
    function drawTopology(topology) {

        // don't draw if the same topology
        if (JSON.stringify(topology)==JSON.stringify(currentTopology)) {
            return;
        }

        // remember topology
        currentTopology = topology;

        // clear the canvas
        $('#svg-canvas').empty();

        // don't populate canvas if empty topology
        if (topology.nodes.length==0 && topology.links.length==0) {
            return;
        }

        // Create the input graph
        var g = new dagreD3.graphlib.Graph()
                .setGraph({})
                .setDefaultEdgeLabel(function() { return {}; });

        // Nodes
        for (var i = 0; i < topology['nodes'].length; i++) {
            if (topology['nodes'][i]['title']=="box") {
                continue;
            }
            g.setNode(
                i,
                {
                    label: topology['nodes'][i]['title'],
                    style: topology['nodes'][i]['style']
                }
            );
        };

        // Edges
        for (var i = 0; i < topology['links'].length; i++) {
            g.setEdge(
                topology['links'][i]['sourceidx'], topology['links'][i]['destidx'],
                {
                    style: topology['links'][i]['style'],
                    lineInterpolate: 'basis'
                }
            );
        };

        // Create the renderer
        var render = new dagreD3.render();

        // Set up an SVG group so that we can translate the final graph.
        var svg = d3.select("svg"),
                svgGroup = svg.append("g");

        // Set up zoom support
        var zoom = d3.behavior.zoom().on("zoom", function() {
            svgGroup.attr("transform", "translate(" + d3.event.translate + ")" +
                                        "scale(" + d3.event.scale + ")");
        });
        svg.call(zoom);

        // Run the renderer. This is what draws the final graph.
        render(d3.select("svg g"), g);

        // Center the graph
        var initialScale = 0.75;
        zoom
          .translate([(svg.attr("width") - g.graph().width * initialScale) / 2, 20])
          .scale(initialScale)
          .event(svg);
    }
    $(document).ready(function() {
        positionStuff();
        getTopologyJson();
        // periodicall refresh
        setInterval(function() {
            getTopologyJson()
        }, 2000);
    });
</script>
