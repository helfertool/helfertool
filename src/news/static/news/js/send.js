function handle_lang()
{
    var $lang = $("#id_language").val();

    // preface and end of first text
    $(".mail_preface").hide();
    $(".mail_end").hide();

    $("#preface_" + $lang).show();
    $("#end_" + $lang).show();

    // maybe disable second text
    if($("#id_language").val() == "en") {
        $("#englishbelow").hide()
        $("#id_english").parent().hide()
        $("#block_en").hide()
        $("#id_text_en").removeAttr('required');
    }
    else {
        $("#id_english").parent().show()

        if($("#id_english").prop('checked')) {
            $("#englishbelow").show()
            $("#block_en").show()
            $("#id_text_en").setAttr('required', '');
        }
        else {
            $("#englishbelow").hide()
            $("#block_en").hide()
            $("#id_text_en").removeAttr('required');
        }
    }
}

handle_lang();
