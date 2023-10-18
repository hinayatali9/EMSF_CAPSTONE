// Get all player radio buttons
var playerButtons = document.querySelectorAll('input[type=radio][name="player"]');

// Function to handle player selection
function handlePlayerSelection(event) {
    // Get selected player
    var selectedPlayer = event.target.value;

    // Select this player in all quadrants
    var allPlayerButtons = document.querySelectorAll('input[type=radio][value="' + selectedPlayer + '"]');
    allPlayerButtons.forEach(function(button) {
        button.checked = true;
    });

    // Fetch updated list of draft picks
    fetch('/api/draft_picks')
        .then(response => response.json())
        .then(data => {
            // Update draft picks in quadrant 2
            var quadrant2 = document.getElementById('quadrant2');
            quadrant2.innerHTML = '';
            data.forEach(function(pick) {
                var p = document.createElement('p');
                p.textContent = pick.number + ': ' + pick.player;
                quadrant2.appendChild(p);
            });
        });
}

// Add event listener to all player radio buttons
// playerButtons.forEach(function(button) {
    // button.addEventListener('change', handlePlayerSelection);
// });

// Function to handle Draft button click
function handleDraftButtonClick() {
    // Get selected player
    var selectedPlayer = document.querySelector('input[type=radio][name="player"]:checked').value;

    // Send selected player to backend
    fetch('/api/draft', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player: selectedPlayer }),
    })
        .then(response => response.json())
        .then(data => {
            // update all lists and suggestions
        });
    }
    
// Get Draft button
var draftButton = document.getElementById('draftButton');

// Add event listener to Draft button
draftButton.addEventListener('click', handleDraftButtonClick);

// Get Next Pick and Your Next Pick buttons
var nextPickButton = document.getElementById('nextPick');
var yourNextPickButton = document.getElementById('yourNextPick');

// Function to handle button click
function handleButtonClick() {
    // Fetch suggested player
    fetch('/api/suggested_player')
        .then(response => response.json())
        .then(data => {
            // Update suggested player in quadrant 3
            var quadrant3 = document.getElementById('quadrant3');
            quadrant3.innerHTML = '<h2>Player Suggestion</h2>';
            var input = document.createElement('input');
            input.type = 'radio';
            input.id = data.id;
            input.name = 'player';
            input.value = data.id;
            var label = document.createElement('label');
            label.for = data.id;
            label.textContent = data.name;
            quadrant3.appendChild(input);
            quadrant3.appendChild(label);
        });

    // Fetch updated list of draft picks
    fetch('/api/draft_picks')
        .then(response => response.json())
        .then(data => {
            // Update draft picks in quadrant 2
            var quadrant2 = document.getElementById('quadrant2');
            quadrant2.innerHTML = '';
            data.forEach(function(pick) {
                var p = document.createElement('p');
                p.textContent = pick.number + ': ' + pick.player;
                quadrant2.appendChild(p);
            });
        });
}

// Add event listener to Next Pick and Your Next Pick buttons
nextPickButton.addEventListener('click', handleButtonClick);
yourNextPickButton.addEventListener('click', handleButtonClick);
