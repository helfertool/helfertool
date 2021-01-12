function all_gifts_delivered(element, include_deposit) {
    // If it is not set, set all checkboxes to their originial value.
    var delivery_state=$(element).prop("checked");

    // decide wether to include boxes with deposit
    var boxes = null;
    if (include_deposit) {
        boxes = $('.delivery');
    } else {
        boxes = $('.delivery.nodeposit');
    }

    // If the "All delivered" checkbox is checked, set all other checkboxes.
    if(delivery_state) {
        boxes.each(function(index) {
            $(this).find("input[type=checkbox]:not([disabled])").prop("checked", true);
        });
    } else {
        boxes.each(function(index) {
            let value=$(this).data("original");
            $(this).find("input[type=checkbox]:not([disabled])").prop("checked", value=="True");
        });
    }
}

function set_all(presence) {
    $('.presence input[value="'+presence+'"]').prop('checked', true);
}

function set_default_deposit(deposit) {
    $("input#id_gifts-deposit").val(deposit);
}
