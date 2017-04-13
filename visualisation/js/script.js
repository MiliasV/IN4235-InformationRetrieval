/* jshint esversion: 6, asi: true */

// Mapbox access token
L.mapbox.accessToken = 'pk.eyJ1Ijoiam9pbmVkIiwiYSI6ImNqMGdoNHJvODAwMXkycW1qNno5Nmh0ZDUifQ.umfdxK36OL4yvBpYNTyrGA'

// Global constants
const amsCenterCoords = [52.3702, 4.8952] // Coordinates of the center of Amsterdam
const mapBounds = [[52.2781742, 4.7292418], [52.4310638, 5.0791622]] // Bounding box of the city of Amsterdam
const initialZoom = 12 // Initial zoom level
const minZoom = 11 // Minimum zoom level
const maxZoom = 17 // Maximum zoom level
const mapContainerId = 'map' // Id of the element where the map should be placed
const positiveColor = '#8BC34A' // Color for the positive tweets
const neutralColor = '#9E9E9E' // Color for the neutral tweets
const negativeColor = '#F44336' // Color for the negative tweets
const positiveTwitterIcon = 'img/green.svg'
const neutralTwitterIcon = 'img/gray.svg'
const negativeTwitterIcon = 'img/red.svg'
const mapStyle = 'mapbox://styles/mapbox/dark-v9'
const clusteringRadius = 70 // Maximum radius for clustering
const clustersFile = 'data/clustering_result_chaiken.geojson'
const tweetsFile = 'data/processed_tweets.geojson'
const tweetMarkerRadius = 8 // Radius of the marker of a single tweet
const wordCloudRadius = 200  // Radius for the word cloud
const maxWordSize = 60 // Size of the biggest word in the word cloud
const maxNumberWords = 75 // Maximum number of words to display in the word cloud
const wordCloudWidth = 400
const wordCloudHeight = 250

// Map creation
const map = L.mapbox.map('map', 'mapbox.streets', {
  container: mapContainerId,
  center: amsCenterCoords,
  zoom: initialZoom,
  minZoom: minZoom,
  maxZoom: maxZoom,
  maxBounds: mapBounds
})

// Add custom style over map
L.mapbox.styleLayer(mapStyle).addTo(map)

/**
 * Given the donut properties, create it
 * and return the rendered HTML
 */
function bakeTheDonut (properties) {
  // Compute the center of the icon
  let center = properties.iconSize / 2
  // Create the SVG element
  let svgElement = document.createElementNS(d3.namespaces.svg, 'svg')

  let svg = d3.select(svgElement)
    .attr('width', properties.iconSize)
    .attr('height', properties.iconSize)

  // Scale Sentiment -> Color
  let color = d3.scaleOrdinal([positiveColor, neutralColor, negativeColor])
    .domain(['positive', 'neutral', 'negative'])

  // Scale for the donut, using the count property of the 
  // sentiments to determine the percentages
  let pie = d3.pie()
    .sort(null)
    .value((d) => d.count)

  let path = d3.arc()
    .outerRadius(properties.outerRadius)
    .innerRadius(properties.innerRadius)

  let g = svg.append('g')
    .attr('transform', `translate(${properties.iconSize / 2},${properties.iconSize / 2})`)

  let arc = g.selectAll('.arc')
    .data(pie(properties.sentiments))
    .enter().append('g')
      .attr('class', 'arc')

  arc.append('path')
    .attr('d', path)
    .attr('fill', (d) => color(d.data.type))

  svg.append('text')
    .attr('x', center)
    .attr('y', center)
    .attr('class', properties.pieLabelClass)
    .attr('text-anchor', 'middle')
    .attr('dy', '.3em')
    .text(properties.pieLabel)

  return svgElement.outerHTML
}

/**
 * Custom icon creator for the cluster markers
 */
function iconCreator (cluster) {
  const childMarkers = cluster.getAllChildMarkers()
  const numberChilds = childMarkers.length
  const radiusMax = 22
  // Dynamic radius basing on the number of childs of the cluster
  const radius = radiusMax - (numberChilds < 10 ? 8 : numberChilds < 100 ? 6 : numberChilds < 1000 ? 4 : 0)
  // Thickness of the ring
  const ringThickness = 6
  const iconSize = radius * 2
  const pieLabelClass = 'marker-cluster-label'

  // Compute number of positive, neutral and negative tweets
  let positive = 0
  let neutral = 0
  let negative = 0

  for (let marker of childMarkers) {
    let sentiment = marker.feature.properties.sentiment
    if (sentiment > 0) { positive++ } else if (sentiment < 0) { negative++ } else { neutral++ }
  }

  let markerHtml = bakeTheDonut({
    sentiments: [
      {'type': 'positive', 'count': positive},
      {'type': 'neutral', 'count': neutral},
      {'type': 'negative', 'count': negative}
    ],
    outerRadius: radius,
    innerRadius: radius - ringThickness,
    pieLabel: numberChilds,
    pieLabelClass: pieLabelClass,
    iconSize: iconSize
  })

  return L.divIcon({
    html: markerHtml,
    iconSize: [iconSize, iconSize],
    className: 'marker-cluster-icon'
  })
}

let circle

// Given a list of strings, computes a dictionary containing
// the frequency of occurrency of each string in the list
function computeFrequencies(list) {
  let wordsMap = {}
  list.forEach((token) => {
    if (wordsMap.hasOwnProperty(token)) {
      wordsMap[token]++
    } else {
      wordsMap[token] = 1
    }
  })
  return wordsMap
}

// Computes the words in the tweets in a certain radius from a specified point
function wordsInRadius(geoJsonLayer, position, radius) {
  let wordsList = []
  Object.keys(geoJsonLayer._layers).forEach((key) => {
      const layer = geoJsonLayer._layers[key]
      const tweetPosition = layer._latlng

      if (position.distanceTo(tweetPosition) < wordCloudRadius) {
        wordsList = wordsList.concat(layer.feature.properties.tokens)
      }
  })
  return wordsList
}

// Draw a word cloud
function drawCloud(position, frequencyList) {
  var color = d3.scaleOrdinal(d3.schemeDark2);

  function draw(words) {
    let svgElement = document.createElementNS(d3.namespaces.svg, 'svg')

    d3.select(svgElement)
      .attr('width', wordCloudWidth)
      .attr('height', wordCloudHeight)
      .attr('class', 'wordcloud')
    .append('g')
      .attr('transform', `translate(${wordCloudWidth/2},${wordCloudHeight/2})`)
      .selectAll('text')
      .data(words)
    .enter().append('text')
      .style('font-family', 'Roboto Slab')
      .style('font-size', (d) => `${d.size}px`)
      .style('fill', (d, i) => color(i))
      .attr('text-anchor', 'middle')
      .attr('transform', (d) => `translate(${d.x}, ${d.y})`)
      .text((d) => d.text)

    openPopup(position, svgElement.outerHTML)
  }

  d3.cloud()
    .size([wordCloudWidth, wordCloudHeight])
    .words(frequencyList)
    .padding(1)
    .rotate(0)
    .text((d) => d.text)
    .font('Roboto Slab')
    .fontSize((d) => d.size)
    .on('end', draw)
    .start()
}

// Compute normalized sizes for the words in the cloud basing on the frequency
function computeWordSizes(frequencyList) {
  let wordSizeList = []

  let freqArray = frequencyList.map((wordFreq) => wordFreq.frequency)
  let maxFrequency = Math.max(...freqArray)

  frequencyList.forEach((wordFreq) =>
    wordSizeList.push({
      text: wordFreq.word,
      size: Math.sqrt(wordFreq.frequency / maxFrequency) * maxWordSize
    })
  )

  return wordSizeList
}

// Remove the circle representing the radius when the word cloud
// popup is closed
map.on('popupclose', () => {
  if (typeof circle !== 'undefined') {
    map.removeLayer(circle)
  }
})

// Opens a popup in the map at a given position with the given content
function openPopup(position, content) {
  L.popup({className: 'wcPopup', maxWidth: wordCloudWidth})
    .setLatLng(position)
    .setContent(content)
    .openOn(map)
}

let clusters
let clustersLayer

let drawClusters = (filterFunc)  => {
  clustersLayer = L.geoJson(clusters, {
    filter: filterFunc,
    style: (feature) => ({stroke: false, color: d3.interpolateRdYlGn(1 - feature.properties.order / 101), fillOpacity: 0.6 })
  })
  map.addLayer(clustersLayer)
}

$.getJSON(clustersFile, (loadedClusters) => {
  clusters = loadedClusters
  drawClusters((feature) => true)
})

// Load the tweets asynchronously and add them to the map
$.getJSON(tweetsFile, (tweets) => {
  const geoJsonLayer = L.geoJson(tweets, {
    pointToLayer: (feature, latlng) => {
      const sentiment = feature.properties.sentiment

      var iconType
      if (sentiment > 0) { iconType = positiveTwitterIcon } else if (sentiment < 0) { iconType = negativeTwitterIcon } else { iconType = neutralTwitterIcon }

      return L.marker(latlng, {
        icon: L.icon({
          iconUrl: iconType,
          iconSize: [25, 20],
          iconAnchor: [15, 12]
        })
      })
    },
    // onEachFeature: (feature, layer) => layer.bindPopup(feature.properties.text)
  })

  // Marker clustering
  const markers = new L.MarkerClusterGroup({
    maxClusterRadius: clusteringRadius,
    showCoverageOnHover: true,
    iconCreateFunction: iconCreator
  })

  markers.addLayer(geoJsonLayer)
  map.addLayer(markers)

  // Register Popup on click callback
  map.on('click', (e) => {
    const clickedPosition = e.latlng

    // Get the list of words in the radius around the position clicked
    let wordsList = wordsInRadius(geoJsonLayer, clickedPosition, wordCloudRadius)

    // If there is at least one word in the radius considered, open the popup
    // with the word cloud
    if (wordsList.length > 0) {
      circle = L.circle(clickedPosition, wordCloudRadius).addTo(map)

      // Compute the frequency of each word
      let wordsMap = computeFrequencies(wordsList)

      // Flatten frequency dictionary and sort it by frequency of the words
      let flatWordsMap = []
      Object.keys(wordsMap).forEach((token) => {
        flatWordsMap.push({'word': token, 'frequency': wordsMap[token]})
      })
      flatWordsMap.sort((a, b) => b.frequency - a.frequency)

      // Compute normalized word sizes
      let wordSizeList = computeWordSizes(flatWordsMap.slice(0, maxNumberWords))

      // Draw the word cloud
      drawCloud(clickedPosition, wordSizeList)
    }
  })
})

$('#sliderPriceIn')
  .slider({id: 'sliderPrice', min: 0, max: 164, range: true, value: [0, 164]})
  .on('slideStop', (sliderValue) => { 
    let [minVal, maxVal] = sliderValue.value
    // console.log(sliderValue)
    clustersLayer.remove()
    drawClusters((feature) => (feature.properties.mean_price > minVal && feature.properties.mean_price < maxVal))
  })

