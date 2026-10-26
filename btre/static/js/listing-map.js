(function () {
  'use strict';

  function showMapError(container, address) {
    var query = encodeURIComponent(address);
    container.innerHTML =
      '<div class="listing-map-error">' +
      '<i class="fas fa-map-marked-alt fa-2x"></i>' +
      '<p>Unable to load the map preview.</p>' +
      (address ? '<a href="https://www.google.com/maps/search/?api=1&query=' + query + '" target="_blank" rel="noopener">Open in Google Maps</a>' : '<span>Add an address to show the map.</span>') +
      '</div>';
  }

  function renderMap(mapEl, lat, lng, address, title) {
    mapEl.innerHTML = '';
    var map = L.map(mapEl, { scrollWheelZoom: false }).setView([lat, lng], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    L.marker([lat, lng]).addTo(map)
      .bindPopup('<strong>' + title + '</strong><br>' + address)
      .openPopup();

    setTimeout(function () { map.invalidateSize(); }, 250);
  }

  function initListingMap() {
    var mapEl = document.getElementById('listingMap');
    if (!mapEl || typeof L === 'undefined') return;

    var lat = parseFloat(mapEl.dataset.lat);
    var lng = parseFloat(mapEl.dataset.lng);
    var address = mapEl.dataset.address || '';
    var title = mapEl.dataset.title || 'Property location';
    var hasCoords = !isNaN(lat) && !isNaN(lng);

    if (hasCoords) {
      renderMap(mapEl, lat, lng, address, title);
      return;
    }

    if (!address.trim()) {
      showMapError(mapEl, address);
      return;
    }

    fetch('https://nominatim.openstreetmap.org/search?format=json&limit=1&q=' + encodeURIComponent(address), {
      headers: { 'Accept': 'application/json' }
    })
      .then(function (res) { return res.json(); })
      .then(function (results) {
        if (results && results[0]) {
          renderMap(mapEl, parseFloat(results[0].lat), parseFloat(results[0].lon), address, title);
        } else {
          showMapError(mapEl, address);
        }
      })
      .catch(function () {
        showMapError(mapEl, address);
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initListingMap);
  } else {
    initListingMap();
  }
})();
