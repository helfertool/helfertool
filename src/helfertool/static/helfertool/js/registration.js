allowed_overlap = parseInt($('#max_overlapping').val()) * 60;

function update_shit_registration(element) {
    var modifier = null;
    if (element.checked) {
        // the user has activated a shift, disable all colliding shifts
        modifier = function(e){
            if (!$(e).data('colliders')) {
                $(e).data('colliders', {})
            }
            $(e).data('colliders')[element.id] = element;
            e.disabled = true;
            $(e.parentNode).addClass('colliding');
            $(e.parentNode).removeClass('notcolliding');
        }
    } else {
        modifier = function(e){
            if (!$(e).data('colliders')) {
                $(e).data('colliders', {})
            }

            if ($(e).data('colliders')[element.id]) {
                delete $(e).data('colliders')[element.id];
            }

            if ($.isEmptyObject($(e).data('colliders'))) {
                e.disabled = false;
                $(e.parentNode).removeClass('colliding');
                $(e.parentNode).addClass('notcolliding');
            }
        }
    }

    var newshift = element
    var start = $(element).data('start');
    var end = $(element).data('end');
    $('.shift_registration').each(function(i, element) {
        if (newshift == element) return;
        var mystart = $(element).data('start') + allowed_overlap;
        var myend = $(element).data('end') - allowed_overlap;

        if ((mystart > start && mystart < end) ||
            (myend > start   && myend < end) ||
            (start > mystart && start < myend) ||
            (end > mystart   && end < myend)) {
            modifier(element);
        }
    });

}

$('.shift_registration').each(function (i, element) {
    update_shit_registration(element);
    $(this).change(function () {
        update_shit_registration(this);
    });
});

function handle_infection_instruction()
{
    var show_field = 0;

    // iterate over all relevant checkboxes
    $(".infection_instruction").each(function() {
        if($(this).prop('checked'))
        {
            show_field = 1;
            return false;
        }
    })

    // show or hide input field
    if(show_field)
        $("#id_infection_instruction").parent().show()
    else
        $("#id_infection_instruction").parent().hide()
}

handle_infection_instruction();
