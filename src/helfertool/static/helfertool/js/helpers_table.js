$(function () {
    $(".table").DataTable({
        "paging": false,
        "searching": false,
        "info": false,
        "responsive": true,
        "columnDefs": [
            { "orderable": false, "targets": "nosort" },
        ],
        "sorting": [[2, 'asc'], [1, 'asc']],
    });
});
