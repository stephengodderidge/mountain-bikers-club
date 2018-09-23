import { Browser, tileLayer, polyline, map } from '../leaflet/leaflet.min.js';
import '../leaflet/fullscreen.js';

export default class Map extends HTMLElement {
    constructor() {
        super();
    }

    async connectedCallback() {
        this.hasInterface = Boolean(this.dataset.hasInterface);
        this.trail_id = this.dataset.trail;
        this.track_id = this.dataset.track;

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
            mapOptions['dragging'] = !Browser.mobile;
            mapOptions['fullscreenControl'] = true;
            markerOptions['startIconUrl'] = ''; // '{% static 'shell/assets/pin_start.svg' %}';
            markerOptions['endIconUrl'] = ''; // '{% static 'shell/assets/pin_end.svg' %}';
        } else {
            mapOptions['zoomControl'] = false;
            mapOptions['attributionControl'] = false;
            mapOptions['dragging'] = false;
            markerOptions['startIconUrl'] = '';
            markerOptions['endIconUrl'] = '';
        }
        const myMap = map(this, mapOptions);

        tileLayer('/trail/api/tile/{z}/{x}/{y}.png', {
            attribution:
                '&copy; <a href="https://www.openstreetmap.org">OpenStreetMap</a> contributors, &copy; <a href="https://opentopomap.org">OpenTopoMap</a>, &copy; <a href="https://opencyclemap.org">OpenCycleMap</a>',
            // maxZoom: 17,
        }).addTo(myMap);

        if (data.points && data.points.length > 3) {
            const points = data.points.map(p => [p.latitude, p.longitude]);
            const polylineOptionsBack = {
                color: 'white',
                opacity: 0.65,
                weight: 11,
                lineCap: 'round',
            };
            const polylineBack = polyline(points, polylineOptionsBack).addTo(myMap);

            let uphillParts = [];
            let downhillParts = [];
            let uphill = true;
            let currentParts = [];
            let previousElevation = 0;

            for (let i = 0, s = data.points.length; i < s; i += 1) {
                const currentPoint = data.points[i];
                const currentElevation = currentPoint.elevation;

                if (i === 0) {
                    previousElevation = currentElevation;
                    continue;
                }

                const previousPoint = data.points[i - 1];
                currentParts.push(previousPoint);

                const lastDistance = currentParts[currentParts.length - 1].total_distance;
                const firstDistance = currentParts[0].total_distance;

                // if (lastDistance - firstDistance > 0.01) {
                    if (currentElevation >= previousElevation) {
                        // uphill
                        if (!uphill && lastDistance - firstDistance > 0.01) {
                            currentParts.push(currentPoint);
                            downhillParts.push(currentParts);
                            currentParts = [];
                        }
                    } else {
                        // downhill
                        if (uphill && lastDistance - firstDistance > 0.005) {
                            currentParts.push(currentPoint);
                            uphillParts.push(currentParts);
                            currentParts = [];
                        }
                    }

                    uphill = currentElevation >= previousElevation;
                //}

                previousElevation = currentPoint.elevation;
            }

            if (uphill) {
                uphillParts.push(currentParts);
            } else {
                downhillParts.push(currentParts);
            }

            const polylineOptions = {
                color: '#f0484e',
                weight: 5,
                lineCap: 'round',
            };

            for (const p of uphillParts) {
                const p1 = p.map(p => [p.latitude, p.longitude]);
                polyline(p1, polylineOptions).addTo(myMap);
            }

            polylineOptions['color'] = '#3d85cc';

            for (const p of downhillParts) {
                const p2 = p.map(p => [p.latitude, p.longitude]);
                polyline(p2, polylineOptions).addTo(myMap);
            }

            myMap.fitBounds(polylineBack.getBounds());
        }
    }
}
