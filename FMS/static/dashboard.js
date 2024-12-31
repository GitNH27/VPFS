var activeFareDiv, pastFareDiv, pastFareDivider;

function setVisibility(element, visible){
    if(!visible)
        element.style.display = "none"
    else
        element.style.display = "unset";
}

function getTimeDelta(utcTimeSeconds){
    let currentTime = (new Date()).getTime() / 1000
    return (utcTimeSeconds - currentTime).toFixed(1);
}

function generateFareElement(fare, id){
    let element = document.createElement("div");
    element.classList.add("fare");
    element.id = id;
    element.innerHTML = `
    <h3>${fare.id}:</h3>
    <span class="tofrom">${fare.src.x},${fare.src.y} -> ${fare.dest.x},${fare.dest.y}</span>
    <span id="fare-${fare.id}-claim" style="display: none" class="bg-neutral">Team</span>
    <span id="fare-${fare.id}-pickedUp" style="display:none" class="bg-ok">Picked Up</span>
    <span id="fare-${fare.id}-completed" style="display:none" class="bg-ok">Completed</span>
    <span id="fare-${fare.id}-paid" style="display:none" class="bg-ok">Paid</span>
    <span id="fare-${fare.id}-inPosition" style="display:none" class="bg-warn">In Position</span>
    <span id="fare-${fare.id}-expiry" style="display:none">Expires in </span>
    `

    // if(fare.active)
        activeFareDiv.appendChild(element);
    // else
    //     pastFareDiv.appendChild(element);

    return element;
}

async function updateFares(){
    let req = await fetch("http://localhost:5000/fares?all=true");
    let data = await req.json();

    for(var fare of data){
        let id = fare.id;
        let element = document.getElementById(`fare-${id}`);
        if(element == null){
            element = generateFareElement(fare, `fare-${id}`)
        }

        // If fare is no longer active, move it
        if(element.parentElement == activeFareDiv && !fare.active){
            if(fare.claimed)
                pastFareDiv.insertBefore(element, pastFareDivider)
            else
                pastFareDiv.insertBefore(element, pastFareDivider.nextSibling);
        }

        team = document.getElementById(`fare-${id}-claim`);
        expiry = document.getElementById(`fare-${id}-expiry`);
        if(fare.claimed){
            team.innerText = `Team ${fare.team}`
            setVisibility(team, true)
            setVisibility(expiry, false)
        }
        else {
            let delta = getTimeDelta(fare.expiry);
            if(delta < 0)
                expiry.innerText = "Expired"
            else
                expiry.innerText = `Expires in ${delta}`
            setVisibility(team, false)
            setVisibility(expiry, true)
        }

        setVisibility(document.getElementById(`fare-${id}-inPosition`), fare.inPosition);
        setVisibility(document.getElementById(`fare-${id}-pickedUp`), fare.pickedUp);
        setVisibility(document.getElementById(`fare-${id}-completed`), fare.completed);
        setVisibility(document.getElementById(`fare-${id}-paid`), fare.paid);
    }
}

window.onload = () => {
    activeFareDiv = document.getElementById("active-fares");
    pastFareDiv = document.getElementById("past-fares");
    pastFareDivider = document.getElementById("fare-divider");

    setInterval(() => {
        updateFares();
    }, 500);
}