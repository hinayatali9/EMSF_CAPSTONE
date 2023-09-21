$(function () {
    $("#player-list").sortable();

    $("#submit").click(function () {
        var new_order = $("#player-list")[0].innerText.split('\n')
        var positional_weight = $("#positional-weight")[0].value
        var min_max_constraints = {
            "min_picks": {
                "goalie": $(goalie_min)[0].value,
                "ld": $(ld_min)[0].value,
                "rd": $(rd_min)[0].value,
                "lf": $(lf_min)[0].value,
                "rf": $(rf_min)[0].value,
            },
            "max_picks": {
                "goalie": $(goalie_max)[0].value,
                "ld": $(ld_max)[0].value,
                "rd": $(rd_max)[0].value,
                "lf": $(lf_max)[0].value,
                "rf": $(rf_max)[0].value,
            }
        }
        min_number_of_picks = parseInt($(goalie_min)[0].value) + parseInt($(ld_min)[0].value) + parseInt($(rd_min)[0].value) + parseInt($(lf_min)[0].value) + $(rf_min)[0].value
        if(min_number_of_picks > parseInt($(num_picks)[0].getAttribute("value") )){ // CHANGE GIVEN TEAM
            alert("Not enough draft picks available for min number of picks selected")
        }
        else{
            $.ajax({
                url: '/submit_preferences',
                type: 'post',
                contentType: 'application/json',
                data: JSON.stringify(
                    {
                        "new_order": new_order,
                        "positional_weight": positional_weight,
                        "min_max_constraints": min_max_constraints
                    }
                ),
                success: function () {
                    alert("Inputs taken successfully!");
                }
            });
        }
    });
});

function validateValues(id1, id2, max_picks) {
    var input1 = document.getElementById(id1);
    var input2 = document.getElementById(id2);

    if (parseInt(input1.value) > parseInt(input2.value)) {
        input1.value = input2.value;
    }
}
