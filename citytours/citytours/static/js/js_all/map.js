function CityTours(){};

CityTours.prototype.getTour = function(map, tourname) {
  $.getJSON('/api/data/'+tourname, function(data) {
    console.log('TOUR RESPONSE:');
    console.log(data);
    data.forEach(row => {
      latlng = {'lat': row.latlng[0], 'lon': row.latlng[1]};
      L.marker(latlng).addTo(map).bindPopup(row.Name);
    });
  });
};

CityTours.prototype.getRoute = function(map, tourname, lat, lon) {
  $.getJSON('/api/route/'+tourname, {'user_location': [lat, lon]}, function(data) {
    console.log('ROUTE RESPONSE:');
    console.log(data);
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
    citytour.getTour(map, 'birthday');
    citytour.getRoute(map, 'birthday', e.latlng.lat, e.latlng.lng);
  }

  map.on('locationfound', onLocationFound);
  map.locate({setView: true, maxZoom: 16});
});
