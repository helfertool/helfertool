function all_gifts_delivered() {
    // It it is not set, set all checkboxes to their originial value.
    delivery_state=$("#set_all_pending_gifts").prop("checked");

    // If the "All delivered" checkbox is checked, set all other checkboxes.
    if(delivery_state) {
        $(".delivery input[type=checkbox]").prop("checked", true);
    } else {
        $(".delivery").each(function(index) {
            value=$(this).data("original");
            $(this).children("input[type=checkbox]").prop("checked", value=="True");
        });
    }
}

function set_all(presence) {
    $('.presence input[value="'+presence+'"]').prop('checked', true);
}

function set_default_deposit(deposit) {
    $("input#id_gifts-deposit").val(deposit);
}