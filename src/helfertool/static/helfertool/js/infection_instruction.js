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
