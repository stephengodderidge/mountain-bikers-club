export default function dom(strings, ...expressions) {
    const template = document.createElement("template");
    const tagPromise = promiseTagger();
    const proxyProperties = new Map();
    let html = [strings[0]];
    const proxy = new Proxy({}, {
        get(_obj, prop) {
            return proxyProperties.get(prop);
        },
        set(_obj, prop, value) {
            const parent = proxyProperties.get(prop);
            if (parent) {
                value = isDomObject(value) ? value : dom `${value}`;
                value.render(parent);
                return true;
            }
            return false;
        },
    });
    if (expressions.length > 0) {
        const resolvedExpressions = resolveExpressions(expressions, tagPromise);
        resolvedExpressions.forEach((expr, i) => html.push(expr, strings[i + 1]));
    }
    template.innerHTML = flatten(html).join("");
    const fragment = template.content;
    const promisesMap = tagPromise();
    for (const [tag, promise] of promisesMap) {
        const element = fragment.querySelector(tag);
        if (!element)
            continue;
        promise.then(value => {
            if (value == undefined ||
                (Array.isArray(value) && value.length === 0)) {
                return;
            }
            if (typeof value !== "object" && typeof value !== "function") {
                value = dom `${value}`.fragment;
            }
            else if (!(value instanceof DocumentFragment)) {
                const { fragment } = isDomObject(value)
                    ? value
                    : dom `${typeof value === "function" ? value() : value}`;
                value = fragment;
            }
            const parent = (element.parentNode);
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
    async function render(element) {
        if (element != undefined) {
            element.innerHTML = "";
            (element).append(fragment);
        }
        return Promise.all(promisesMap.values()).then(() => proxy);
    }
}
function promiseTagger(tagName = "dompr") {
    const map = new Map();
    let index = 0;
    return function (promise) {
        const tag = `${tagName}-${index}`;
        if (promise == undefined) {
            return map;
        }
        map.set(tag, promise);
        index += 1;
        return `<${tag}></${tag}>`;
    };
}
function resolveExpressions(expressions, tagPromise) {
    const result = [];
    expressions.forEach(entry => {
        if (entry == undefined ||
            (Array.isArray(entry) && entry.length === 0)) {
            return;
        }
        if (Array.isArray(entry)) {
            entry = entry.map(value => resolveExpressions([value], tagPromise));
        }
        else if (entry instanceof Promise) {
            entry = tagPromise(entry);
        }
        else if (typeof entry === "function") {
            entry = resolveExpressions([entry()], tagPromise);
        }
        else {
            entry =
                typeof entry !== "object"
                    ? entry
                    : tagPromise(Promise.resolve(entry));
        }
        result.push(entry);
    });
    return result;
}
function isDomObject(obj) {
    return typeof obj === "object" && "fragment" in obj && "render" in obj;
}
function flatten(arr = []) {
    let list = [];
    for (let v of arr) {
        list = list.concat(Array.isArray(v) ? flatten(v) : v);
    }
    return list;
}
//# sourceMappingURL=tagged-dom.js.map