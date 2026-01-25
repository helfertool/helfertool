function handle_password()
{
    var $no_password = $("#id_no_password").is(':checked');

    if($no_password) {
        $("#id_password1").removeAttr('required');
        $("#id_password2").removeAttr('required');

        $("#id_password1").parent().hide()
        $("#id_password2").parent().hide()
    } else {
        $("#id_password1").attr('required', '');
        $("#id_password2").attr('required', '');

        $("#id_password1").parent().show()
        $("#id_password2").parent().show()
    }
}

handle_password();
