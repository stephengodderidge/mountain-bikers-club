const buttons = document.querySelectorAll('.button');
let isTouch = false;

for (const button of buttons) {
    button.addEventListener('mousemove', move);
    button.addEventListener('touchstart', preventTouch);
}

function preventTouch() {
    isTouch = true;
}

function move(event) {
    if (isTouch) {
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
