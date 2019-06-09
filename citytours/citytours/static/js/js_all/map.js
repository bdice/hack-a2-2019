$(document).on('turbolinks:load', function() {
  let CartoDB_Voyager = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
  });
  var mymap = L.map('mapid').setView([42.2808, -83.7430], 13);
  CartoDB_Voyager.addTo(mymap);
});
