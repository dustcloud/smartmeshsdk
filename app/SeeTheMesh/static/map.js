//=========================== defines =========================================

//=========================== globals =========================================

var topologygeneration  = ''
var markers             = [];
var lines               = [];
var freezeDrawTopology  = false;
var map;
var infoWindow;

//=========================== helpers =========================================

function addMarker(jsonNode) {
    
    // create marker
    var marker_latlng = new google.maps.LatLng(
        jsonNode['latitude'],
        jsonNode['longitude']
    )
    var marker = new google.maps.Marker({
        position :      marker_latlng,
        title :         jsonNode['title'],
        draggable :     true,
        map :           map
    });
    if (jsonNode.hasOwnProperty('icon')) {
        marker.setIcon(jsonNode['icon']);
    }
    
    // do something when marker is clicked
    google.maps.event.addListener(marker, 'click', (function (marker) {
        return function () {
            infoWindow.setContent("<pre>" + jsonNode['infotext'] + "</pre>");
            infoWindow.open(map, marker);
        }
    })(marker));
    
    // do something when marked is dragged
    google.maps.event.addListener(marker, 'drag', (function (marker) {
        return function () {
            freezeDrawTopology = true;
        }
    })(marker));
    
    // do something when marked stops being dragged
    google.maps.event.addListener(marker, 'dragend', (function (marker) {
        return function () {
            freezeDrawTopology = false;
            var title = marker.title;
            var lat   = marker.getPosition().lat();
            var lng   = marker.getPosition().lng();
            updateMarkerPosition(title,lat,lng);
            topologygeneration = '';
            getMapJson();
        }
    })(marker));
    
    return marker;
}

function addLine(jsonPath) {
    
    // create line
    var source_latlng = new google.maps.LatLng(
        jsonPath['source_latitude'],
        jsonPath['source_longitude']
    )
    var dest_latlng = new google.maps.LatLng(
        jsonPath['dest_latitude'],
        jsonPath['dest_longitude']
    )
    var lineCoordinates = [
        source_latlng,
        dest_latlng,
    ]
    var line = new google.maps.Polyline({
        path:           lineCoordinates,
        geodesic:       true,
        strokeColor:    jsonPath['color'],
        strokeOpacity:  jsonPath['opacity'],
        strokeWeight:   jsonPath['weight'],
    });
    line.setMap(map);
    
    // do something line is clicked
    google.maps.event.addListener(line, 'click', (function (line) {
        return function (event) {
            infoWindow.setPosition(event.latLng);
            infoWindow.setContent("<pre>" + jsonPath['infotext'] + "</pre>");
            infoWindow.open(map, line);
        }
    })(line));
    
    return line;
}

function deleteMarkers() {
    for (var i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    }
    markers = [];
}

function deleteLines() {
    for (var i = 0; i < lines.length; i++) {
        lines[i].setMap(null);
    }
    lines = [];
}

//=========================== main functions ==================================

function initMap() {
    // create map
    var center = {lat: 0, lng: 0};
    map = new google.maps.Map(document.getElementById('map'), {
      zoom:      3,
      center:    center,
      mapTypeId: 'satellite',
      tilt:      0,
    });
    
    // do something when map is dragged
    google.maps.event.addListener(map, 'drag', (function (map) {
        return function () {
            freezeDrawTopology = true;
        }
    })(map));
    
    // do something when map stops being dragged/moved
    google.maps.event.addListener(map, 'idle', (function (map) {
        return function () {
            freezeDrawTopology = false;
            updateMapCenterZoom(
                map.getCenter().lat(),
                map.getCenter().lng(),
                map.getZoom()
            );
        }
    })(map));
    
    // create an infowindow
    infoWindow = new google.maps.InfoWindow();
    
    // load data (now once, then periodically)
    getMapJson();
    setInterval(function() {
        getMapJson()
    }, 2000);
}

function updateMarkerPosition(title,lat,lng) {
    $.ajax({
        type:           "POST",
        url:            'map.json',
        contentType:    'application/json',
        data:           JSON.stringify({
            'title':    title,
            'lat':      lat,
            'lng':      lng
        })
    });
}

function updateMapCenterZoom(centerlat,centerlng,zoom) {
    $.ajax({
        type:           "POST",
        url:            'map.json',
        contentType:    'application/json',
        data:           JSON.stringify({
            'centerlat':     centerlat,
            'centerlng':     centerlng,
            'zoom':          zoom
        })
    });
}

function getMapJson() {
    $.getJSON("map.json", function(topology) {
        drawTopology(topology);
    });
}

function drawTopology(topology) {
    
    // don't draw if disabled
    if (freezeDrawTopology==true) {
        return;
    }
    
    // don't draw if the same topology
    if (topologygeneration==topology['generation']) {
        return;
    }
    
    // remember topology generation
    topologygeneration = topology['generation'];
    
    // adjust map position and zoom
    map.setZoom(topology['map']['zoom']);
    var map_latlng = new google.maps.LatLng(
        topology['map']['centerlat'],
        topology['map']['centerlng']
    )
    map.setCenter(map_latlng);
    
    // delete everything from map
    deleteMarkers();
    deleteLines();
    
    // add markers
    markers = [];
    for (var i = 0; i < topology['nodes'].length; i++) {
        markers.push(addMarker(topology['nodes'][i]));
    };
    
    // lines
    lines = [];
    for (var i = 0; i < topology['links'].length; i++) {
        lines.push(addLine(topology['links'][i]))
    };
}
