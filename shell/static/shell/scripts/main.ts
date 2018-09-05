import Wave from './components/section-wave.js';
import Button from './components/single-button.js';
import Map from './components/trail-map.js';

if ('customElements' in window) {
    customElements.define("section-wave", Wave);
    customElements.define("lit-button", Button);
    customElements.define("trail-map", Map);
}
