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
                "lw": $(lw_min)[0].value,
                "rw": $(rw_min)[0].value,
                "centre": $(centre_min)[0].value,
            },
            "max_picks": {
                "goalie": $(goalie_max)[0].value,
                "ld": $(ld_max)[0].value,
                "rd": $(rd_max)[0].value,
                "lw": $(lw_max)[0].value,
                "rw": $(rw_max)[0].value,
                "rw": $(rw_max)[0].value,
                "centre": $(centre_max)[0].value,
            }
        }
        min_number_of_picks = parseInt($(goalie_min)[0].value) + parseInt($(ld_min)[0].value) + parseInt($(rd_min)[0].value) + parseInt($(lw_min)[0].value) + $(rw_min)[0].value + parseInt($(centre_min)[0].value)
        if (min_number_of_picks > parseInt($(num_picks)[0].getAttribute("value"))) {
            alert("Not enough draft picks available for min number of picks selected")
        }
        else {
            $.ajax({
                url: window.location.pathname + '/submit_preferences',
                type: 'post',
                contentType: 'application/json',
                data: JSON.stringify(
                    {
                        "new_order": new_order,
                        "positional_weight": positional_weight,
                        "min_max_constraints": min_max_constraints
                    }
                ),
                success: function(data) {
                    window.location.href = data.url;
                }
            });
        }
    });
});

function validateValues(id1, id2) {
    var input1 = document.getElementById(id1);
    var input2 = document.getElementById(id2);

    if (parseInt(input1.value) > parseInt(input2.value)) {
        input1.value = input2.value;
    }
}
