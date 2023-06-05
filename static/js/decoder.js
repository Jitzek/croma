const CLASSNAME = 'decode';
const LIMITATTR = 'limit';
const SPEEDATTR = 'speed';
const DELAYATTR = 'delay';
const UNICODE_LIMIT = 1200;

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function decode_init() {
    var classes = document.getElementsByClassName(CLASSNAME);
    for (let i = 0; i < classes.length; i++) {
        var classn = classes.item(i);
        decode(classn, classn.getAttribute(LIMITATTR), classn.getAttribute(SPEEDATTR), classn.getAttribute(DELAYATTR));
    }
}

/**
 * 
 * @param {class object} classn 
 * @param {amount of allowed randomized tries, 'inf' means no limit} limit 
 * @param {speed in milliseconds before new character attempt (lower is faster)} speed 
 * @param {delay in milliseconds before starting decode} delay 
 */
async function decode(classn, limit=null, speed=50, delay=0) {
    var result = classn.innerHTML;
    var length = classn.innerHTML.length;
    classn.innerHTML = '';
    
    var count = 0;
    var limit_count = 0;

    await sleep(delay);
    while (count < length) {
        var char = String.fromCharCode(Math.floor(Math.random() * UNICODE_LIMIT + 1));

        // Limit has been reached
        if (limit && limit != 'inf') {
            if (limit_count > limit) {
                classn.innerHTML += result[count];
                count++;
                limit_count = 0;
                continue;
            }
        }

        classn.innerHTML += char;

        await sleep(speed);

        // Wrong char
        if (result[count] != char || limit == 'inf') { 
            // Remove wrong char
            classn.innerHTML = classn.innerHTML.substring(0, count);
            limit_count++;
            continue;
        }
        count++; 
    }
}