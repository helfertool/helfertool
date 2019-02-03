function reload_tasklist()
{
    var url = $("#tasks").data("url");
    $("#tasks").load(url);
}

reload_tasklist();
setInterval(reload_tasklist, 2000);
