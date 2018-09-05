import dom from "../library/tagged-dom.js";

export default class Wave extends HTMLElement {
    shadow =  this.attachShadow({ mode: "open" });
    color = this.dataset.color;
    height = this.dataset.height;

    connectedCallback() {
        const html = dom`
            <style>
                :host {
                    display: block;
                    width: 100%;
                    height: ${this.height || "var(--section-margin-height)"};
                    border-radius: 0 0 65% 55%/0 0 100% 60%;
                    background: ${this.color};
                    transform: scale(1.3, 2.7) rotate(-0.3deg);
                    transform-origin: center bottom;
                    position: relative;
                }
            </style>
        `;

        this.setAttribute("aria-hidden", String(true));
        html.render(this.shadow);
    }
}
