document.addEventListener("DOMContentLoaded", function () {
    const captureButton = document.getElementById("capture-button");
    const personNameInput = document.getElementById("name");

    let currentStream = null;
    let boundary = null;

    $("#capture-button").prop('disabled', true);

    $("#btnstarttimelog").click(function(){
        $('#alert_message').text("");
        $('#stud_name').text("");
        $('#timelogdata').text("");
    });

    $("#name").keyup(function() {
        var value = $(this).val();
        if ( value.length > 0 ) {
            $('#capture-button').prop('disabled', false);
            
            $('#alert_message').empty();
        } else {
            $('#capture-button').prop('disabled', true);
        }
    });
});
