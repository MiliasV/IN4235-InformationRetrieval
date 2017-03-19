mapboxgl.accessToken = 'pk.eyJ1Ijoiam9pbmVkIiwiYSI6ImNqMGdoNHJvODAwMXkycW1qNno5Nmh0ZDUifQ.umfdxK36OL4yvBpYNTyrGA';
var map = new mapboxgl.Map({
    container: 'map', // container id
    style: 'mapbox://styles/mapbox/basic-v9', //stylesheet location
    center: [4.8952, 52.3702],
    zoom: 13,
    minZoom: 12,
    maxZoom: 18,
    maxBounds: [[4.7292418, 52.2781742], [5.0791622, 52.4310638]]
});

map.on('load', function() {
    // Add a new source from our GeoJSON data and set the
    // 'cluster' option to true.
    map.addSource("tweets", {
        type: "geojson",
        // Point to GeoJSON data.
        data: "tweets.ams.geojson",
        cluster: true,
        clusterMaxZoom: 17, // Max zoom to cluster points on
        clusterRadius: 60 // Radius of each cluster when clustering points (defaults to 50)
    });

    // Use the tweets source to create five layers:
    // One for unclustered points, three for each cluster category,
    // and one for cluster labels.
    map.addLayer({
        "id": "unclustered-points",
        "type": "symbol",
        "source": "tweets",
        "filter": ["!has", "point_count"],
        "layout": {
            "icon-image": "post-15"
        }
    });

    // Display the earthquake data in three layers, each filtered to a range of
    // count values. Each range gets a different fill color.
    var layers = [
        [150, '#f28cb1'],
        [20, '#f1f075'],
        [0, '#51bbd6']
    ];

    layers.forEach(function (layer, i) {
        map.addLayer({
            "id": "cluster-" + i,
            "type": "circle",
            "source": "tweets",
            "paint": {
                "circle-color": layer[1],
                "circle-radius": 18
            },
            "filter": i === 0 ?
                [">=", "point_count", layer[0]] :
                ["all",
                    [">=", "point_count", layer[0]],
                    ["<", "point_count", layers[i - 1][0]]]
        });
    });

    // Add a layer for the clusters' count labels
    map.addLayer({
        "id": "cluster-count",
        "type": "symbol",
        "source": "tweets",
        "layout": {
            "text-field": "{point_count}",
            "text-font": [
                "DIN Offc Pro Medium",
                "Arial Unicode MS Bold"
            ],
            "text-size": 12
        }
    });
});