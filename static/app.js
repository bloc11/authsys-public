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

});

function save_signature()
{
    $("#error").html("");
    var inputs = $("form").find("input");
    if (!inputs[0].value) {
        $("#error").html("please provide your full name");
        return false;
    }
    if (!inputs[1].value) {
        $("#error").html("please provide ID number");
        return false;
    }
    if (!inputs[2].value) {
        $("#error").html("please provide email address");
        return false;
    }
    if (inputs[2].value.indexOf("@") == -1) {
        $("#error").html("email address must be valid");
        return false;
    }
    if (signaturePad.isEmpty()) {
        $("#error").html("signature cannot be empty");
        return false;
    }
    $("#progress").html("Uploading signature...");
    $.post("/upload_signature", signaturePad.toDataURL(), function(res) {
        inputs[4].value = res;
        inputs[5].onclick = undefined;
        $(inputs[5]).click();
    })
    return false;
}