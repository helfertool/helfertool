var counter = 0;
var timer;

function reload_tasklist()
{
    if(counter < 600)  // stop reloading after 20 minutes
    {
        var url = $("#tasks").data("url");
        $("#tasks").load(url);

        counter++;
    }
    else
    {
        $("#tasks").addClass("d-none")
        $("#tasks-reload").removeClass("d-none")

        clearInterval(timer);
    }
}

reload_tasklist();
timer = setInterval(reload_tasklist, 2000);
