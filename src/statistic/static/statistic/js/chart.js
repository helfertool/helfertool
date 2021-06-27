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
            var emptynode = $("#" + empty);

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
