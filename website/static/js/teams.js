$(document).ready(function(){
    $(".team-box").on('click', function(){
        $(this).find('input[type=radio]').prop('checked', true);
        $(".team-box").removeClass("selected");
        $(this).addClass("selected");
    });

    $("#team-form").on('submit', function(e){
        e.preventDefault();
        var selectedTeam = $('input[name=team]:checked', '#team-form').val();
        // Send the selected team to the backend
        $.post("/submit_team", { team: selectedTeam }, function(data){
            alert("Team submitted");
        });
    });
});