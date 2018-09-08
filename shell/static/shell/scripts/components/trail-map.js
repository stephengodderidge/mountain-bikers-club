import {loadJS, loadCSS} from '../library/async-loader.js';

export default class Map extends HTMLElement {
    constructor() {
        super();
        this.url = this.dataset.url;
        this.hasInterface = Boolean(this.dataset.hasInterface);
    }

    async connectedCallback() {
        await loadCSS('https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/leaflet.css', 'anonymous');
        await loadJS('https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/leaflet.js', 'anonymous');
        // TODO build our own loader from DB
        await loadJS('https://cdnjs.cloudflare.com/ajax/libs/leaflet-gpx/1.4.0/gpx.min.js', 'anonymous');

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
        } else {
            mapOptions['zoomControl'] = false;
            mapOptions['attributionControl'] = false;
            mapOptions['dragging'] = false;
            markerOptions['startIconUrl'] = '';
            markerOptions['endIconUrl'] = '';
        }
        const myMap = window.L.map(this, mapOptions);

        window.L.tileLayer('https://a.tile.opentopomap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, &copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
            maxZoom: 17,
        }).addTo(myMap);

        new window.L.GPX(
            this.url,
            {
                async: true,
                polyline_options: {
                    color: 'crimson',
                    opacity: 0.75,
                    weight: 4,
                    lineCap: 'round',
                },
                marker_options: markerOptions,
            },
        ).on('loaded', function (e) {
            myMap.fitBounds(e.target.getBounds());
        }).addTo(myMap);
    }
}
