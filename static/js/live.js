var msgDiv = document.getElementById('msgDiv');

function displayMSG( msg, color='#ffffff', code=null) {
    msgDiv.innerHTML = '';
    if (code) {msgDiv.innerHTML =+ `<h2>${code ? code : ''}</h2><br>`; }
    msgDiv.innerHTML +=
        `<p style="color: ${color}">${msg}</p>`;
}