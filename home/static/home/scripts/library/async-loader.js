const urlList = new Set();
let loadJSPromise = null;
let loadCSSPromise = null;

/**
 * Load JS asynchronously
 * @param {string} src
 * @param {boolean|string} [crossOrigin=false]
 * @param {string} [integrity='']
 * @returns {Promise<*>}
 */
export function loadJS(src, crossOrigin = false, integrity = '') {
    if (urlList.has(src)) {
        return loadJSPromise;
    }

    loadJSPromise = new Promise((resolve, reject) => {
        const script = document.createElement('script');

        script.onload = event => resolve(event);
        script.onerror = event => reject(event);
        script.async = true;
        if (typeof crossOrigin === "string") {
            script.crossOrigin = crossOrigin;
        } else if (crossOrigin === true) {
            script.crossOrigin = "anonymous";
        }
        script.integrity = integrity;
        script.src = src;

        document.head.appendChild(script);
        urlList.add(src);
    });

    return loadJSPromise;
}

/**
 * Load CSS asynchronously
 * @param {string} src
 * @param {boolean} [crossOrigin=false]
 * @param {string} [integrity='']
 * @param {string} [media="screen"]
 * @returns {Promise<*>}
 */
export function loadCSS(
    src,
    crossOrigin = false,
    integrity = '',
    media = 'screen',
) {
    if (urlList.has(src)) {
        return loadCSSPromise;
    }

    loadCSSPromise = new Promise((resolve, reject) => {
        const link = document.createElement('link');

        link.addEventListener('load', event => resolve(event));
        link.addEventListener('error', event => reject(event));
        link.setAttribute('rel', 'stylesheet');
        link.setAttribute('media', media);
        if (typeof crossOrigin === "string") {
            link.crossOrigin = crossOrigin;
        } else if (crossOrigin === true) {
            link.crossOrigin = "anonymous";
        }
        link.integrity = integrity;
        link.setAttribute('href', src);

        document.head.appendChild(link);
        urlList.add(src);
    });

    return loadCSSPromise;
}
