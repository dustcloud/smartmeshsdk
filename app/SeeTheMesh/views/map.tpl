<!DOCTYPE html>
<html>
    <head>
        <title>{{pagetitle}}</title>
        <meta name="viewport" content="initial-scale=1.0">
        <meta charset="utf-8">
        <script src="/static/jquery-3.1.1.min.js" charset="utf-8"></script>
        <script src="/static/map.js"></script>
        <style>
            html, body {
                height:     100%;
                margin:     0;
                padding:    0;
                overflow:   hidden;
            }
            #map {
                display:    inline-block;
                height:     100%;
                width:      100%;
                padding:    0;
                margin:     0;
                z-index:    0;
            }
            #link_topology {
                position:   absolute;
                top:        10px;
                right:      10px;
                z-index:    999;
            }
        </style>
    </head>
    <body>
        <a id="link_topology" href="/"><img src="../static/logo_topology.png"></a>
        <div id="map"></div>
        <script async defer
            src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAazj5Cac11By3MXPz2-y-aTvK5docw2Ds&callback=initMap&libraries=geometry">
        </script>
    </body>
</html>
