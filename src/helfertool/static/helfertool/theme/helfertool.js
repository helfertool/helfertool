$(document).ready(function () {
    // Register event handler to toggle sidemenu
    $('#toggle_sidemenu').on('click', function () {
        if($('#sidemenu').hasClass('visibility-always')) {
            // the visibility-always class is set -> handle it

            // first, remove the class
            $('#sidemenu').removeClass('visibility-always');

            // make sure that the first click really changes something
            // on smaller screens, if we remove the class and change the flag, the two changes result in no change
            if($(document).width() > 768) {
                $('#sidemenu').toggleClass('visibility');
            }
        } else {
            // default case -> just toggle
            $('#sidemenu').toggleClass('visibility');
        }
    });
});
