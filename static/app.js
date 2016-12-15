var signaturePad;

$(document).ready(function () {
    var wrapper = document.getElementById("signature-pad"),
        clearButton = wrapper.querySelector("[data-action=clear]"),
        saveButton = wrapper.querySelector("[data-action=save]"),
        canvas = wrapper.querySelector("canvas");

    // Adjust canvas coordinate space taking into account pixel ratio,
    // to make it look crisp on mobile devices.
    // This also causes canvas to be cleared.
    function resizeCanvas() {
        // When zoomed out to less than 100%, for some very strange reason,
        // some browsers report devicePixelRatio as less than 1
        // and only part of the canvas is cleared then.
        var ratio =  Math.max(window.devicePixelRatio || 1, 1);
        canvas.width = canvas.offsetWidth * ratio;
        canvas.height = canvas.offsetHeight * ratio;
        canvas.getContext("2d").scale(ratio, ratio);
    }

    window.onresize = resizeCanvas;
    resizeCanvas();

    signaturePad = new SignaturePad(canvas);

    clearButton.addEventListener("click", function (event) {
        signaturePad.clear();
    });

    $('.iagree').on('click', function(e){
      var ia = $(e.target).closest('.iagree')
      if (ia.hasClass('accepted')) {
        ia.removeClass('accepted').find('input').prop('checked',false)
      } else {
        ia.addClass('accepted').removeClass('error').find('input').prop('checked',true)
      }
    })

    $('.spam').on('click', function(e){
        var ia = $(e.target).closest('.spam').find('input')
        ia.prop('checked', !ia.prop('checked'))
    });

    $('#fullname').on('keydown', function(){
      $('#fullname-input').removeClass('error');
      $("#error").removeClass('show');
    });
    $('#id_no').on('keydown', function(){
      $('#id-input').removeClass('error');
      $("#error").removeClass('show');
    })
    $('#email').on('keydown', function(){
      $('#email-input').removeClass('error');
      $("#error").removeClass('show');
    })

});

function save_signature()
{
    var preMessage = 'You have errors:<br><br>'
    var inputs = $("form").find("input");
    var errors = [];

    $("#error").html("");

    if ($(".iagree input:checkbox:not(:checked)") .length > 0) {
      $(".iagree input:checkbox:not(:checked)") .parent().addClass('error');
      errors.push("Please agree to all sections");
    }
    if (!inputs[0].value) {
        errors.push("<a href='#fullname-input'><i class='icon-up'></i> Please provide your full name.</a>");
        $("#fullname-input").addClass('error');
    }
    if (!inputs[1].value) {
        errors.push("<a href='#id-input'><i class='icon-up'></i> Please provide your South African ID number or passport number.</a>");
        $("#id-input").addClass('error');
    }
    if (!$('#email').val()) {
        errors.push("<a href='#email-input'><i class='icon-up'></i> Please provide your email address.</a>");
        $("#email-input").addClass('error');
    }
    if ($('#email').val().indexOf("@") == -1) {
        errors.push("<a href='#email-input'><i class='icon-up'></i> Email address must be valid.</a>");
        $("#email-input").addClass('error');
    }
    if (signaturePad.isEmpty()) {
        errors.push("<a href='#signature-input'><i class='icon-up'></i> Signature cannot be empty.</a>");
        $("#error").addClass('show');
    }
    if (errors.length > 0) {
      $("#error").addClass('show');
      $("#error").html(preMessage + errors.join('<br>'))
      return false;
    }
    $("#error").removeClass('show');
    $("#progress").html("Uploading signature...");
    $.post("/upload_signature", signaturePad.toDataURL(), function(res) {
        inputs[4].value = res;
        inputs[5].onclick = undefined;
        $(inputs[5]).click();
    })
    return false;
}
