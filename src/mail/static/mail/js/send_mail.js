function handle_reply_to()
{
    if($("#id_reply_to").val() == "-") {
        $("#id_custom_reply_to").prop("disabled", false);
    } else {
        $("#id_custom_reply_to").prop("disabled", true);
        $("#id_custom_reply_to").val("");
    }
}

handle_reply_to();
