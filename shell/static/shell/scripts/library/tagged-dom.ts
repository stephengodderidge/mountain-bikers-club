/**
 * DocumentFragment Tagged templates
 * @param {TemplateStringsArray} strings
 * @param {*[]} expressions
 * @returns {{fragment: DocumentFragment, render: function(Node?): Promise<*>}}
 */
export default function dom(strings: TemplateStringsArray, ...expressions: any[]) {
    // Use template instead of document.createDocumentFragment() because it needs a parentNode
    const template: HTMLTemplateElement = document.createElement("template");
    const tagPromise = promiseTagger();
    const proxyProperties: Map<PropertyKey, HTMLElement> = new Map();

    let html = [strings[0]];

    const proxy = new Proxy(
        {},
        {
            get(_obj, prop) {
                return proxyProperties.get(prop);
            },
            set(_obj, prop, value) {
                const parent = proxyProperties.get(prop);

                if (parent) {
                    value = isDomObject(value) ? value : dom`${value}`;
                    value.render(parent);

                    return true;
                }

                return false;
            },
        },
    );

    /* --- Create DOM --- */
    if (expressions.length > 0) {
        const resolvedExpressions = resolveExpressions(expressions, tagPromise);

        resolvedExpressions.forEach((expr, i) =>
            html.push(expr, strings[i + 1]),
        );
    }

    template.innerHTML = flatten(html).join("");

    /* --- Resolve promises --- */
    const fragment = template.content;
    const promisesMap: Map<string, Promise<any>> = tagPromise();

    for (const [tag, promise] of promisesMap) {
        const element = fragment.querySelector(tag);

        // element doesn't exist or has been replaced by the proxy
        if (!element) continue;

        // resolve the Promises - async
        promise.then(value => {
            if (
                value == undefined || // null or undefined
                (Array.isArray(value) && value.length === 0) // empty Array
            ) {
                return;
            }

            if (typeof value !== "object" && typeof value !== "function") {
                // this is a simple text node but we parse it. !createTextNode
                value = dom`${value}`.fragment;
            } else if (!(value instanceof DocumentFragment)) {
                const { fragment } = isDomObject(value)
                    ? value
                    : dom`${typeof value === "function" ? value() : value}`;

                value = fragment;
            }

            // replace the promise node
            const parent = /** @type {HTMLElement} */ (element.parentNode);

            if (parent) {
                if (parent.nodeType === 1) {
                    const proxyPropName = parent.getAttribute(":proxy");

                    if (proxyPropName) {
                        parent.removeAttribute(":proxy");
                        proxyProperties.set(proxyPropName, parent);
                    }
                }

                parent.replaceChild(value, element);
            }
        });
    }

    return {
        fragment,
        render,
    };

    /**
     * @param {HTMLElement} element
     * @returns {Promise<*>}
     */
    async function render(element) {
        if (element != undefined) {
            element.innerHTML = "";
            // append is not yet supported by typescript
            /** @type {*} */ (element).append(fragment);
        }

        return Promise.all(promisesMap.values()).then(() => proxy);
    }
}

/**
 * Specific tag replaced by the promise result
 * @param {string} tagName
 * @returns {Function}
 */
function promiseTagger(tagName = "dompr") {
    /** @type {Map<string, Promise<*>>} */
    const map = new Map();
    let index = 0;

    /**
     * @param {Promise} [promise]
     * @returns {string|Map<string, Promise<*>>}
     */
    return function(promise) {
        const tag = `${tagName}-${index}`;

        if (promise == undefined) {
            return map;
        }

        map.set(tag, promise);
        index += 1;

        return `<${tag}></${tag}>`;
    };
}

/**
 * @param {*[]} expressions string literals expressions
 * @param {Function} tagPromise promiseTagger return
 * @returns {string[]}
 */
function resolveExpressions(expressions, tagPromise) {
    /** @type {string[]} */
    const result = [];

    expressions.forEach(entry => {
        // null or undefined
        if (
            entry == undefined ||
            (Array.isArray(entry) && entry.length === 0)
        ) {
            return;
        }

        if (Array.isArray(entry)) {
            // resolve each expression on the array
            entry = entry.map(value => resolveExpressions([value], tagPromise));
        } else if (entry instanceof Promise) {
            // create a tag
            entry = tagPromise(entry);
        } else if (typeof entry === "function") {
            // resolve the result of the function
            entry = resolveExpressions([entry()], tagPromise);
        } else {
            entry =
                typeof entry !== "object"
                    ? entry // String
                    : tagPromise(Promise.resolve(entry)); // DOM -> create a tag
        }

        result.push(entry);
    });

    return result;
}

/**
 * @param {*} obj
 * @returns {boolean}
 */
function isDomObject(obj) {
    return typeof obj === "object" && "fragment" in obj && "render" in obj;
}

/**
 * Flatten an Array or a Set
 * @param {*[]|Set<*>} [arr=[]] An array may hide other arrays
 * @returns {*[]}
 */
function flatten(arr = []) {
    let list = [];

    for (let v of arr) {
        list = list.concat(Array.isArray(v) ? flatten(v) : v);
    }

    return list;
}
