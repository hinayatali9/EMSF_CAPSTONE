$(function () {
    $("#player-list").sortable();

    $("#submit").click(function () {
        $.blockUI({ message: '<h1>Processing...</h1>' });
        var new_order = $("#player-list")[0].innerText.split('\n')
        var positional_weight = $("#positional-weight")[0].value
        var min_max_constraints = {
            "min_picks": {
                "G": $(goalie_min)[0].value,
                "LD": $(ld_min)[0].value,
                "RD": $(rd_min)[0].value,
                "LW": $(lw_min)[0].value,
                "RW": $(rw_min)[0].value,
                "C": $(centre_min)[0].value,
            },
            "max_picks": {
                "G": $(goalie_max)[0].value,
                "LD": $(ld_max)[0].value,
                "RD": $(rd_max)[0].value,
                "LW": $(lw_max)[0].value,
                "RW": $(rw_max)[0].value,
                "C": $(centre_max)[0].value,
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
