$(function() {
    $("#player-list").sortable();
    
    $("#submit").click(function() {
        var new_order = $("#player-list").sortable("toArray", { attribute: "textContent" });
        $.ajax({
            url: '/reorder',
            type: 'post',
            contentType: 'application/json',
            data: JSON.stringify(new_order),
            success: function() {
                alert("New order submitted!");
            }
        });
    });
});