const MEDIA = 'media';
const MEDIA_MIN = 'media-min';
const MEDIA_MAX = 'media-max';

function mediaOnClick(id) {
    var element = document.getElementById(id);
    var media = element.querySelector(`.${MEDIA}`)

    if (media.classList.contains(MEDIA_MIN)) {
        // Maximize
        media.classList.remove(MEDIA_MIN);
        media.classList.add(MEDIA_MAX);
        return
    }
    else if (media.classList.contains(MEDIA_MAX)) {
        // Minimize
        media.classList.remove(MEDIA_MAX);
        media.classList.add(MEDIA_MIN);
        return
    }
}