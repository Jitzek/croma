const ELEMENTID = 'introduction';
const OVERLAY = 'about-overlay';
const EXPANDER = 'about-expander';
const INTRODUCTION = 'intro-container';
const EXPANDEDKEY = 'expanded';
const STDHEIGHT = '4.76em'; // Yes this magic number is horribly hardcoded
                          // It is the only way to make the height changing animation work for the current config
                          // TODO: Find a better way
const ANIMATIONTIME = 500;

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function expanderOnClick(id) {
    var element = document.getElementById(`${ELEMENTID}-${id}`);
    var overlay = element.querySelector(`.${OVERLAY}`)
    var expander = element.querySelector(`.${EXPANDER}`);
    var introduction = element.querySelector(`.${INTRODUCTION}`);
    // Element has already been expanded
    if (element.classList.contains(EXPANDEDKEY)) {
        // Hide Content

        // Remove Key
        element.classList.remove(EXPANDEDKEY);

        // rotate expander
        expander.style.transform = 'rotate(90deg)';

        introduction.style.maxHeight = STDHEIGHT;
        overlay.style.maxHeight = STDHEIGHT;

        introduction.style.transition = `all 0.${ANIMATIONTIME}s ease-out`;
        overlay.style.transition = `all 0.${ANIMATIONTIME}s ease-out`;

        return;
    }
    // Expand Content

    // rotate expander
    expander.style.transform = 'rotate(0deg)';

    // reintroduce introduction
    // Using % cancels animation
    introduction.style.maxHeight = '80em';
    overlay.style.maxHeight = '80em';

    introduction.style.transition = `all 0.${ANIMATIONTIME}s ease-in`;
    overlay.style.transition = `all 0.${ANIMATIONTIME}a ease-in`;

    // Add Key
    element.classList.add(EXPANDEDKEY);
}