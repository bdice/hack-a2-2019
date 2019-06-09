function CityTours(){};

CityTours.prototype.getRoute = function(map, tourname, lat, lon) {
  let points = [];

  $.getJSON('/api/data/'+tourname, function(data) {
    console.log('TOUR RESPONSE:');
    console.log(data);

    data.forEach(row => {
      latlng = {'lat': row.latlng[0], 'lon': row.latlng[1]};
      L.marker(latlng).addTo(map).bindPopup(row.Name);
      points.push(row.latlng);
    });
  });

  $.getJSON('/api/route/'+tourname, {'user_location': [lat, lon]}, function(indices) {
    console.log('ROUTE RESPONSE:');
    console.log(indices);
    let lineverts = [[lat, lon]];
    indices.forEach(ind => {
      lineverts.push(points[ind]);
    });
    console.log(lineverts);
    L.polyline(lineverts).addTo(map);
  });

};

let map;
let citytour = new CityTours();

$(document).on('turbolinks:load', function() {
  // Centered on Ann Arbor downtown by default
  let user_latlon = [42.2808, -83.7430];

  let CartoDB_Voyager = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
  });

  map = L.map('mapid').setView(user_latlon, 15);
  CartoDB_Voyager.addTo(map);

  function onLocationFound(e) {
    var radius = e.accuracy / 2;

    L.marker(e.latlng).addTo(map)
    .bindPopup("You are within " + radius + " meters from this point");

    L.circle(e.latlng, radius).addTo(map);

    console.log('Found location, requesting tour');
    citytour.getRoute(map, 'birthday', e.latlng.lat, e.latlng.lng);
  }

  map.on('locationfound', onLocationFound);
  map.locate({setView: true, maxZoom: 16});
});
