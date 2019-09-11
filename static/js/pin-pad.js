/*
 Copyright (C) 2019 NXP Semiconductor
 Distributed under the MIT License
 */
jQuery(document).ready(function($) {
  $(document).ready(function() {
    ////////////////////////////////////////////////////////////////////////////////////////
    //
    // The classes/fields used here are correlated with the ones in static/css/style-pin.css
    // and templates/pin_pad.html.
    //
    // [pin_pad.html] fields: the 4 small buttons horizontal bar that react to entering pin.
    // [pin_pad.html] numbers: the 9 digits to use for entering pin.
    //
    ////////////////////////////////////////////////////////////////////////////////////////

    // http://www.jsfuck.com/
    var pin = (+!![] + []) + (!+[] + !![] + []) + (!+[] + !![] + !![] + []) + (!+[] + !![] + !![] + !![] + []);

    var enterCode = "";
    enterCode.toString();

    var initialMsg = "<p><strong>Try Face Recognition</strong></p>"
    var kwsInitialMsg = "<p><strong>Say \"GO\" to try key word spotting</strong></p>"
    var correctPinMsg = "Pin Correct!<br>Door Unlocked";
    var wrongPinMsg = "Wrong PIN! Try again.";
    var correctVoicePassMsg = "Password Correct!<br>Door Unlocked!"
    var wrongVoicePassMsg = "Not able to recognize password, try again.";
    var faceRecognizedMsg_part1 = "Welcome ";
    var faceRecognizedMsg_part2 = "!<br>Door Unlocked!";
    var faceRecognizedMsg_part3 = "<br>Inference time: "
    var unauthorizedAccessMsg = "Unauthorized Access Attempt!";;
    var faceNotRecognizedMsg = "Couldn\'t detect face. Please correct your position in front of the camera and try again.";
    var placeInFrontOfCameraMsg = "Please position yourself so that the camera detects your face.";
    var PIN_LENGTH = 4; // 4 digit pin

    IP = LOCALHOST;

    $("#numbers #face_recognition").click(function() {
        $("#anleitung p").html(placeInFrontOfCameraMsg);
        $.getJSON(IP + "/recognition", function(data) {
            console.log("   >>> [face_recognition]: data.response = " + data.response);$("#anleitung p").html(placeInFrontOfCameraMsg);
            if (data.response == true) {
                // FACE recognized.
                var name = data.identity;
                var inferenceTime = data.inftime
                $("#anleitung p").html(faceRecognizedMsg_part1.concat(name, faceRecognizedMsg_part2, faceRecognizedMsg_part3, inferenceTime));
                setTimeout(function() {
                    $("#anleitung p").html(initialMsg);
                }, 3000);
            }
            else {
                if (data.identity != 'ERROR') {
                	$("#anleitung p").html(unauthorizedAccessMsg);
                } else {
                    $("#anleitung p").html(faceNotRecognizedMsg);
                }
                setTimeout(function() {
                    $("#anleitung p").html(initialMsg);
                }, 3000);
            }
        });
    });

    $("#numbers #sleep_btn").click(function() {
        console.log("   >>> [sleep_btn]")
        $.getJSON(IP + "/recognition/sleep", function(data) {
            console.log("   >>> [sleep_btn]: data.response = " + data.response);
        });
    });
    
    (function poll() {
       setTimeout(function() {
           $.ajax({ url: IP + "/speech/key_word_spotting", success: function(data) {
                console.log(data.response)
                if(data.response == 'Y') {
                    console.log(data.response)
                    $( '#kws p' ).html('Key word detected')
                }
                else {
                    //console.log(data.response)
                    $( '#kws p' ).html(kwsInitialMsg)
                }
           }, dataType: "json", complete: poll });
        }, 3000);
    })();

  });
});
