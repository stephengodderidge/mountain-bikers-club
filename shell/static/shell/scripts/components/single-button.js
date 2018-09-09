export default class Button extends HTMLElement {
    constructor() {
        super();
        this.shadow = this.attachShadow({ mode: 'open' });
        this.isTouch = false;
    }

    connectedCallback() {
        this.shadow.innerHTML = '<slot></slot>';
        this.addEventListener('mousemove', this.move);
        this.addEventListener('touchstart', this.preventTouch);
    }

    move(event) {
        if (this.isTouch) {
            event.preventDefault();
            return false;
        }

        const rect = event.currentTarget.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        event.currentTarget.style.setProperty('--x', `${x}px`);
        event.currentTarget.style.setProperty('--y', `${y}px`);

        return true;
    }

    preventTouch() {
        this.isTouch = true;
    }
}
