// CSP: disable automatic style injection (remove for chart.js 3)
Chart.platform.disableCSSInjection = true;

$("canvas.chart").each(function() {
    var chart = $(this);

    var url = chart.data("url");

    $.ajax({
        url: url,
        dataType: 'json',
    }).done(function (results) {
        if($.isEmptyObject(results))
        {
            // hide chart canvas and show text
            var empty = chart.data("empty");
            emptynode = $("#" + empty);

            chart.addClass('d-none');
            emptynode.removeClass('d-none');
        }
        else
        {
            // render chart
            new Chart(chart, results);
        }
    });
});
