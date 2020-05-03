max_overlapping = parseInt($('#register_form').data('max-overlapping'));

function overlap_toggle_shift(input_field) {
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
            $(e.parentNode).addClass('colliding');
            $(e.parentNode).removeClass('notcolliding');
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
                $(e.parentNode).removeClass('colliding');
                $(e.parentNode).addClass('notcolliding');
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
        is_overlapping = (other_end-begin > max_overlapping_seconds &&
                          end-other_begin > max_overlapping_seconds) ||
                         (begin >= other_begin && end <= other_end) ||
                         (other_begin >= begin && other_end <= end);

        if (is_overlapping) {
            modifier(other_field);
        }
    });
}

function prerequisite_toggle_shift(input_field) {
    /// Enable prerequisite, if it is required by a shift
    /// if javascript were disabled, all prerequisites are rendered, so that our user can still select evth.

    /// Convert input data a;b;c to [a, b, c] - django is a bitch and cannot export properly
    if (!Array.isArray($(input_field).data('prerequisites'))) {
        $(input_field).data('prerequisites',
            $(input_field).data('prerequisites').split(';')
        );
    }

    $(input_field).data('prerequisites').forEach(function(prerequisite){
        /// a prerequisite element XXX has to be described in <div id='prerequisite_XXX_description'>
        element = $("#prerequisite_" + prerequisite + "_description");
        if (element.length > 0) {
            if (!$(element).data('pending-shifts')) {
                $(element).data('pending-shifts', {})
            }

            /// use addClass, because it will only enable the class if not already enabled
            if (input_field.checked) {
                /// Add the shifts that require this prerequisite to the prerequisite description
                /// in the DOM tree
                element.data('pending-shifts')[input_field.id] = input_field;
                $(element).removeClass('prerequisite-hidden');
                $(element).addClass('prerequisite-required');
            } else {
                /// Remove the prerequisite from the description in the DOM tree
                if ($(element).data('pending-shifts')[input_field.id]) {
                    delete $(element).data('pending-shifts')[input_field.id];
                }

                /// If this prerequisite is not required by a shift, we can disable it again
                if ($.isEmptyObject($(element).data('pending-shifts'))) {
                    $(element).removeClass('prerequisite-required');
                    $(element).addClass('prerequisite-hidden');
                }
            }
        }
    });
}


function update_shift_registration(input_field) {
    /// Check overlap and prerequisites.
    overlap_toggle_shift(input_field);
    prerequisite_toggle_shift(input_field);
}

// update and register event handler for every field at startup
$('input.registration_possible').each(function (i, element) {
    update_shift_registration(element);
    $(this).change(function () {
        update_shift_registration(this);
    });
});
