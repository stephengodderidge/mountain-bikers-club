import { loadJS, loadCSS } from '../library/async-loader.js';

export default class Map extends HTMLElement {
    constructor() {
        super();
        this.hasInterface = Boolean(this.dataset.hasInterface);
        this.trail_id = this.dataset.trail;
        this.track_id = this.dataset.track;
    }

    async connectedCallback() {
        await loadCSS('https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/leaflet.css', 'anonymous');
        await loadCSS('https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/leaflet.fullscreen.css', 'anonymous');
        await loadCSS('https://cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.min.css', 'anonymous');
        await loadJS('https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/leaflet.js', 'anonymous');
        await loadJS('https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/Leaflet.fullscreen.min.js', 'anonymous');
        await loadJS('https://cdnjs.cloudflare.com/ajax/libs/leaflet-minimap/3.6.1/Control.MiniMap.min.js', 'anonymous');

        const data = await fetch(`/trail/api/${this.trail_id}/track/${this.track_id}`)
            .then(response => response.json());

        const mapOptions = {
            scrollWheelZoom: false,
        };
        const markerOptions = {
            iconSize: [30, 30],
            iconAnchor: [15, 30],
            shadowUrl: '',
            wptIconUrls: {},
        };

        if (this.hasInterface) {
            mapOptions['dragging'] = !window.L.Browser.mobile;
            markerOptions['startIconUrl'] = ''; // '{% static 'shell/assets/pin_start.svg' %}';
            markerOptions['endIconUrl'] = ''; // '{% static 'shell/assets/pin_end.svg' %}';
            markerOptions['fullscreenControl'] = {
                pseudoFullscreen: true,
            };
        } else {
            mapOptions['zoomControl'] = false;
            mapOptions['attributionControl'] = false;
            mapOptions['dragging'] = false;
            markerOptions['startIconUrl'] = '';
            markerOptions['endIconUrl'] = '';
        }
        const myMap = window.L.map(this, mapOptions);

        const tileLayer = new window.L.tileLayer('https://a.tile.opentopomap.org/{z}/{x}/{y}.png', {
            attribution: false,
            maxZoom: 17,
        });

        new window.L.tileLayer('https://b.tile.opentopomap.org/{z}/{x}/{y}.png', {
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, &copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
            maxZoom: 17,
        }).addTo(myMap);

        if (data.points && data.points.length > 3) {
            const points = data.points.map(p => [p.latitude, p.longitude]);
            const polylineOptionsBack = {
                color: 'white',
                opacity: 0.75,
                weight: 11,
                lineCap: 'round',
            };
            const polylineOptionsFront = {
                color: '#2E73B8',
                weight: 5,
                lineCap: 'round',
            };
            const polylineBack = window.L.polyline(points, polylineOptionsBack).addTo(myMap);
            window.L.polyline(points, polylineOptionsFront).addTo(myMap);

            myMap.fitBounds(polylineBack.getBounds());

            if (this.hasInterface) {
                new window.L.Control.MiniMap(tileLayer, {
                    zoomLevelOffset: -6,
                }).addTo(myMap);
            }
        }
    }
}
