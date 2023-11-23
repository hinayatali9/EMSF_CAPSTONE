$(document).ready(function() {
    $(document).on('click', '.draft-button', function() {
        $.blockUI({ message: '<h1>Processing...</h1>' });
        var playerId = $(this).attr('id').split('_')[1];
        var teamAbvr = window.location.pathname.split('/')[1];
        var apiUrl = '/' + teamAbvr + '/api/draft';
        $.ajax({
            url: apiUrl,
            type: 'POST',
            data: JSON.stringify({ 'player_id': playerId }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function(msg) {
                // Update the players_team_ranking
                headerHtml = `
                <li class="list-group-item">
                    <div class="form-check">
                        <div class="row">
                            <div class="col">
                                <!-- Player Name -->
                                <p class="mb-0"><b>Name</b></p>
                            </div>
                            <div class="col">
                                <!-- Player Position -->
                                <p class="mb-0"><b>Position</b></p>
                            </div>
                            <div class="col">
                                <!-- Player Val. -->
                                <p class="mb-0"><b>Player Val.</b></p>
                            </div>
                            <div class="col">
                                <!-- Pick Prob. -->
                                <p class="mb-0"><b>Pick Prob.</b></p>
                            </div>
                `
                if (msg.is_next_pick_team_draft_pick === true){
                    headerHtml = headerHtml +
                    `<!-- Draft Button -->
                    <div class="col-auto">
                        <button class="btn btn-primary mb-0 draft-button-header float-right">Draft</button>
                    </div>`
                }
                headerHtml = headerHtml +
                `    
                        </div>
                    </div>
                </li>`

                $('#nextPick, #yourNextPick').prop('disabled', msg.is_next_pick_team_draft_pick);

                $('#players-team-ranking').empty();
                $('#players-team-ranking').append(headerHtml);
                $.each(msg.players_team_ranking, function(i, player) {
                    var listItem = '<li class="list-group-item">' +
                        '<div class="form-check">' +
                        '<div class="row">' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.name + '</p>' +
                        '</div>' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.position + '</p>' +
                        '</div>' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.player_value + '</p>' +
                        '</div>'+
                        '<div class="col">' +
                        '<p class="mb-0">' + player.pick_prob + '</p>' +
                        '</div>'
                        
                    if (msg.is_next_pick_team_draft_pick === true){
                        listItem = listItem +
                        '<div class="col-auto">' +
                        '<button id="draftButton_' + player.id + '" class="btn btn-primary draft-button mb-0 float-right">Draft</button>' +
                        '</div>'
                    }

                    listItem = listItem +
                        '</div>' +
                        '</div>' +
                        '</div>' +
                        '</li>';
                    $('#players-team-ranking').append(listItem);
                });

                // Update the draft_picks
                $('#team-list').empty();
                $.each(msg.draft_picks, function(i, pick) {
                    if (teamAbvr == pick.team_abrv) {
                        playerName = '<b>' + pick.player_name + '</b>'
                    } else {
                        playerName = pick.player_name                       
                    }
                    var listItem = '<li class="list-group-item">' +
                        '<img src="/static/img/' + pick.team_abrv + '.svg" alt="'+ pick.team_name +'" width="55">' +
                        '<span>' + playerName + '</span>' +
                        '</li>';
                    $('#team-list').append(listItem);
                });

                // Update the suggested_player
                $('#suggested_player').empty();
                $('#suggested_player').append(headerHtml);
                if (msg.is_next_pick_team_draft_pick === true){
                    $.each(msg.suggested_player, function(i, player) {
                        var listItem = '<li class="list-group-item">' +
                            '<div class="form-check">' +
                            '<div class="row">' +
                            '<div class="col">' +
                            '<p class="mb-0">' + player.name + '</p>' +
                            '</div>' +
                            '<div class="col">' +
                            '<p class="mb-0">' + player.position + '</p>' +
                            '</div>' +
                            '<div class="col">' +
                            '<p class="mb-0">' + player.player_value + '</p>' +
                            '</div>'+
                            '<div class="col">' +
                            '<p class="mb-0">' + player.pick_prob + '</p>' +
                            '</div>' +
                            '<div class="col-auto">' +
                            '<button id="draftButton_' + player.id + '" class="btn btn-primary draft-button mb-0 float-right">Draft</button>' +
                            '</div>' +
                            '</div>' +
                            '</div>' +
                            '</li>';
                        $('#suggested_player').append(listItem);
                    });
                }

                // Update the next_pick_number
                $('#next_pick_number').text("Your next pick: " + msg.next_pick_number);

                // Update the players_pick_prob_ranking
                $('#players-pick-prob-ranking').empty();
                $('#players-pick-prob-ranking').append(headerHtml);
                $.each(msg.players_pick_prob_ranking, function(i, player) {
                    var listItem = '<li class="list-group-item">' +
                        '<div class="form-check">' +
                        '<div class="row">' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.name + '</p>' +
                        '</div>' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.position + '</p>' +
                        '</div>' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.player_value + '</p>' +
                        '</div>'+
                        '<div class="col">' +
                        '<p class="mb-0">' + player.pick_prob + '</p>' +
                        '</div>'
                        
                    if (msg.is_next_pick_team_draft_pick === true){
                        listItem = listItem +
                        '<div class="col-auto">' +
                        '<button id="draftButton_' + player.id + '" class="btn btn-primary draft-button mb-0 float-right">Draft</button>' +
                        '</div>'
                    }

                    listItem = listItem +
                        '</div>' +
                        '</div>' +
                        '</div>' +
                        '</li>';
                    $('#players-pick-prob-ranking').append(listItem);
                });
                $.unblockUI();
            }
        });
    });
});


$(document).ready(function() {
    $('#nextPick, #yourNextPick').click(function() {
        // Show the loading overlay
        $.blockUI({ message: '<h1>Processing...</h1>' });

        var buttonId = $(this).attr('id');
        var teamAbvr = window.location.pathname.split('/')[1];
        var apiUrl = '/' + teamAbvr + '/api/simulate_pick';
        $.ajax({
            url: apiUrl,
            type: 'POST',
            data: JSON.stringify({ 'button_id': buttonId }),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            success: function(msg) {
                // Update the players_team_ranking
                headerHtml = `
                <li class="list-group-item">
                    <div class="form-check">
                        <div class="row">
                            <div class="col">
                                <!-- Player Name -->
                                <p class="mb-0"><b>Name</b></p>
                            </div>
                            <div class="col">
                                <!-- Player Position -->
                                <p class="mb-0"><b>Position</b></p>
                            </div>
                            <div class="col">
                                <!-- Player Val. -->
                                <p class="mb-0"><b>Player Val.</b></p>
                            </div>
                            <div class="col">
                                <!-- Pick Prob. -->
                                <p class="mb-0"><b>Pick Prob.</b></p>
                            </div>
                `
                if (msg.is_next_pick_team_draft_pick === true){
                    headerHtml = headerHtml +
                    `<!-- Draft Button -->
                    <div class="col-auto">
                        <button class="btn btn-primary mb-0 draft-button-header float-right">Draft</button>
                    </div>`
                }
                headerHtml = headerHtml +
                `    
                        </div>
                    </div>
                </li>`

                $('#nextPick, #yourNextPick').prop('disabled', msg.is_next_pick_team_draft_pick);

                $('#players-team-ranking').empty();
                $('#players-team-ranking').append(headerHtml);
                $.each(msg.players_team_ranking, function(i, player) {
                    var listItem = '<li class="list-group-item">' +
                        '<div class="form-check">' +
                        '<div class="row">' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.name + '</p>' +
                        '</div>' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.position + '</p>' +
                        '</div>' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.player_value + '</p>' +
                        '</div>'+
                        '<div class="col">' +
                        '<p class="mb-0">' + player.pick_prob + '</p>' +
                        '</div>'
                        
                    if (msg.is_next_pick_team_draft_pick === true){
                        listItem = listItem +
                        '<div class="col-auto">' +
                        '<button id="draftButton_' + player.id + '" class="btn btn-primary draft-button mb-0 float-right">Draft</button>' +
                        '</div>'
                    }

                    listItem = listItem +
                        '</div>' +
                        '</div>' +
                        '</li>';
                    $('#players-team-ranking').append(listItem);
                });

                // Update the draft_picks
                $('#team-list').empty();
                $.each(msg.draft_picks, function(i, pick) {
                    if (teamAbvr == pick.team_abrv) {
                        playerName = '<b>' + pick.player_name + '</b>'
                    } else {
                        playerName = pick.player_name                       
                    }
                    var listItem = '<li class="list-group-item">' +
                        '<img src="/static/img/' + pick.team_abrv + '.svg" alt="'+ pick.team_name +'" width="55">' +
                        '<span>' + playerName + '</span>' +
                        '</li>';
                    $('#team-list').append(listItem);
                });

                // Update the suggested_player
                $('#suggested_player').empty();
                $('#suggested_player').append(headerHtml);
                if (msg.is_next_pick_team_draft_pick === true){
                    $.each(msg.suggested_player, function(i, player) {
                        var listItem = '<li class="list-group-item">' +
                            '<div class="form-check">' +
                            '<div class="row">' +
                            '<div class="col">' +
                            '<p class="mb-0">' + player.name + '</p>' +
                            '</div>' +
                            '<div class="col">' +
                            '<p class="mb-0">' + player.position + '</p>' +
                            '</div>' +
                            '<div class="col">' +
                            '<p class="mb-0">' + player.player_value + '</p>' +
                            '</div>'+
                            '<div class="col">' +
                            '<p class="mb-0">' + player.pick_prob + '</p>' +
                            '</div>' +
                            '<div class="col-auto">' +
                            '<button id="draftButton_' + player.id + '" class="btn btn-primary draft-button mb-0 float-right">Draft</button>' +
                            '</div>' +
                            '</div>' +
                            '</div>' +
                            '</li>';
                        $('#suggested_player').append(listItem);
                    });
                }

                // Update the next_pick_number
                $('#next_pick_number').text("Your next pick: " + msg.next_pick_number);

                // Update the players_pick_prob_ranking
                $('#players-pick-prob-ranking').empty();
                $('#players-pick-prob-ranking').append(headerHtml);
                $.each(msg.players_pick_prob_ranking, function(i, player) {
                    var listItem = '<li class="list-group-item">' +
                        '<div class="form-check">' +
                        '<div class="row">' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.name + '</p>' +
                        '</div>' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.position + '</p>' +
                        '</div>' +
                        '<div class="col">' +
                        '<p class="mb-0">' + player.player_value + '</p>' +
                        '</div>'+
                        '<div class="col">' +
                        '<p class="mb-0">' + player.pick_prob + '</p>' +
                        '</div>'

                    if (msg.is_next_pick_team_draft_pick === true){
                        listItem = listItem +
                        '<div class="col-auto">' +
                        '<button id="draftButton_' + player.id + '" class="btn btn-primary draft-button mb-0 float-right">Draft</button>' +
                        '</div>'
                    }

                    listItem = listItem +
                        '</div>' +
                        '</div>' +
                        '</div>' +
                        '</li>';
                    $('#players-pick-prob-ranking').append(listItem);
                });
                $.unblockUI();
            }
        });
    });
});
