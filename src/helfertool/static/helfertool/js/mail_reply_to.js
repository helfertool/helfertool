function handle_reply_to()
{
    if($("#id_reply_to").val() == "-")
        $("#id_custom_reply_to").parent().show()
    else
        $("#id_custom_reply_to").parent().hide()
}

handle_reply_to();
