/*
 * Overlapping shifts
 */
var max_overlapping = parseInt($('#register_form').data('max-overlapping'));

function update_shift_registration(input_field) {
    // do not check, if the overlapping setting is None (in python)
    if(isNaN(max_overlapping)) {
        return
    }

    var modifier = null;
    if (input_field.checked) {
        // the user has selected a shift, disable all colliding shifts
        modifier = function(e){
            // when enabling a shift lateron again, we need to know why the shift was disabled
            // if there were other additional colliding shift, we cannot enable the shift.
            // so we store the colliding shifts for every single shift here
            if (!$(e).data('colliders')) {
                $(e).data('colliders', {})
            }
            $(e).data('colliders')[input_field.id] = input_field;

            // now disable the input field
            e.disabled = true;
        }
    } else {
        // the user has removed a shift selection, enable the colliding shifts again
        modifier = function(e){
            // we can only enable the shift, if we have no other colliding shifts
            if (!$(e).data('colliders')) {
                $(e).data('colliders', {})
            }

            // so first remove this one
            if ($(e).data('colliders')[input_field.id]) {
                delete $(e).data('colliders')[input_field.id];
            }

            // and the check if we have other ones
            if ($.isEmptyObject($(e).data('colliders'))) {
                e.disabled = false;
            }
        }
    }

    // check for overlapping shifts
    var begin = $(input_field).data('begin');
    var end = $(input_field).data('end');
    var max_overlapping_seconds = max_overlapping * 60;

    $('input.registration_possible').each(function(i, other_field) {
        // skip the handled shift itself
        if (input_field == other_field) {
            return
        }

        var other_begin = $(other_field).data('begin');
        var other_end = $(other_field).data('end');

        // this is the same logic as in RegisterForm, so the frontend and backend reject the same shifts
        var is_overlapping = (other_end-begin > max_overlapping_seconds
                              && end-other_begin > max_overlapping_seconds)
                             || (begin >= other_begin && end <= other_end)
                             || (other_begin >= begin && other_end <= end);

        if (is_overlapping) {
            modifier(other_field);
        }
    });
}

// update and register event handler for every field
$('input.registration_possible').each(function (i, element) {
    update_shift_registration(element);
    $(this).change(function () {
        update_shift_registration(this);
    });
});

/*
 * infection instruction
 */

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

// register event handler
$('input.infection_instruction').each(function (i, element) {
    $(this).change(function () {
        handle_infection_instruction();
    });
});

// and run it directly
handle_infection_instruction();
