import { Control, Map, DomUtil, DomEvent, bind, control } from './leaflet.min.js';

Control.Fullscreen = Control.extend({
    options: {
        position: 'topleft',
        title: {
            'false': 'View Fullscreen',
            'true': 'Exit Fullscreen',
        },
    },

    onAdd: function(map) {
        var container = DomUtil.create('div', 'leaflet-control-fullscreen leaflet-bar leaflet-control');

        this.link = DomUtil.create('a', 'leaflet-control-fullscreen-button leaflet-bar-part', container);
        this.link.href = '#';

        this._map = map;
        this._map.on('fullscreenchange', this._toggleTitle, this);
        this._toggleTitle();

        DomEvent.on(this.link, 'click', this._click, this);

        return container;
    },

    _click: function(e) {
        DomEvent.stopPropagation(e);
        DomEvent.preventDefault(e);
        this._map.toggleFullscreen(this.options);
    },

    _toggleTitle: function() {
        this.link.title = this.options.title[this._map.isFullscreen()];
    },
});

Map.include({
    isFullscreen: function() {
        return this._isFullscreen || false;
    },

    toggleFullscreen: function() {
        var container = this.getContainer();

        if (this.isFullscreen()) {
            this._disablePseudoFullscreen(container);
        } else {
            this._enablePseudoFullscreen(container);
        }

    },

    _enablePseudoFullscreen: function(container) {
        DomUtil.addClass(container, 'leaflet-pseudo-fullscreen');
        this._setFullscreen(true);
        this.fire('fullscreenchange');
    },

    _disablePseudoFullscreen: function(container) {
        DomUtil.removeClass(container, 'leaflet-pseudo-fullscreen');
        this._setFullscreen(false);
        this.fire('fullscreenchange');
    },

    _setFullscreen: function(fullscreen) {
        var container = this.getContainer();

        this._isFullscreen = fullscreen;

        if (fullscreen) {
            DomUtil.addClass(container, 'leaflet-fullscreen-on');
        } else {
            DomUtil.removeClass(container, 'leaflet-fullscreen-on');
        }

        this.invalidateSize();
    },
});

Map.mergeOptions({
    fullscreenControl: false,
});

Map.addInitHook(function() {
    if (this.options.fullscreenControl) {
        this.fullscreenControl = new Control.Fullscreen(this.options.fullscreenControl);
        this.addControl(this.fullscreenControl);
    }
});

control.fullscreen = function(options) {
    return new Control.Fullscreen(options);
};
