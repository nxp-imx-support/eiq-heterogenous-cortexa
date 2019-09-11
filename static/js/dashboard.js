/*
 Copyright (C) 2019 NXP Semiconductor
 Distributed under the MIT License
 */
jQuery(document).ready(function($) {
  $(document).ready(function() {

    console.log("   >>> Using board IP: " +  BOARD_IP);

    var CLEAR_MSG = ""
    var MAX_NUM_SNAPSHOTS = 8 // Keep in sync with NUM_TRAIN_SAMPLES in Recognition/recongnition_common.py
    var TMP_SNAPSHOT_PATH = "../media/tmp_snapshot.jpg" // Keep in sync with TMP_SNAPSHOT_PATH in Recognition/recongnition_common.py
    var TMP_SNAPSHOT_ROI_PATH = "../media/tmp_snapshot_roi.jpg" // Keep in sync with TMP_SNAPSHOT_ROI_PATH in Recognition/recongnition_common.py
    var crtUserName = ""
    var crtUserDbId = -1
    var crtNumSnapshots = 0


    $.getJSON(BOARD_IP + "/profile/users/", function(data) {
        if (data.response != "No active users") {
              $.each(data, function(index, value) {
                  console.log("   >>> [/profile/users/]: index = " + index);
                  console.log("   >>> [/profile/users/]: name = " + value.name);
                  console.log("   >>> [/profile/users/]: picture = " + value.picture);
                
              	  if (value.picture == "") {
                    console.log("   >>> [/profile/user/]: Deleting incomplete user");
                    $.getJSON(BOARD_IP + "/recognition/cancel_adding_user/" + index);
                    return;
                  }
                
                  var table_entry = "<tr>\n" +
                  "<td class=\"align-middle\"><img class=\"user-img img-fluid z-depth-1 rounded-circle\" src=\"" + value.picture + "\"></td>" +
                  "<td class=\"align-middle\">" + value.name + "</td>\n" +
                  "</tr>\n";
                  if (value.name != "Unknown") {
                      $("table #users").append(table_entry);
                  }
              });
        }
    });

    $.getJSON(BOARD_IP + "/profile/logs/", function(data) {
      if (data.response != "Logs non existent") {
              $.each(data, function(index, value) {
                  console.log("   >>> [/profile/logs/]");
                  var table_entry = "<tr>\n" +
                  "<td class=\"align-middle\">" + value.name + "</td>\n" +
                  "<td class=\"align-middle\"><img class=\"w-25 img-fluid z-depth-1\" src=\"" + value.face + "\"></td>" +
                  "<td class=\"align-middle\">" + value.timestamp + "</td>\n" +
                  "<td class=\"align-middle\">" + value.known + "</td>\n" +
                  "</tr>\n";
                  $("table #logs").append(table_entry);
              });
      }
    });

    $("#refresh-btn").click(function (){
        $.getJSON(BOARD_IP + "/profile/logs/", function(data) {
                $("table #logs").empty();
          		if (data.response != "Logs non existent") {
                    $.each(data, function(index, value) {
                        console.log("   >>> [/profile/logs/] - refresh");
                        var table_entry = "<tr>\n" +
                        "<td class=\"align-middle\">" + value.name + "</td>\n" +
                        "<td class=\"align-middle\"><img class=\"w-25 img-fluid z-depth-1\" src=\"" + value.face + "\"></td>" +
                        "<td class=\"align-middle\">" + value.timestamp + "</td>\n" +
                        "<td class=\"align-middle\">" + value.known + "</td>\n" +
                        "</tr>\n";
                        $("table #logs").append(table_entry);
                    });
                }
         });
    });

    // Based on https://stackoverflow.com/questions/31775177/nodejs-and-mysql-wait-for-query-result
    function isUserInDb(name, callback) {
        var isInDb = false;

        $.getJSON(BOARD_IP + "/profile/users/", function(data) { /* database name search */
            $.each(data, function(index, value) {
                if (value.name === name) {
                    console.log("   >>> [isUserInDb]: TRUE");
                    isInDb = true;

                }
            });
            if (isInDb) {
                return callback(true);
            }
            console.log("   >>> [isUserInDb]: FALSE");
            return callback(false);
        });
    }

    $("#add-user-btn").click(function() {
        var name = document.getElementById("user-name").value;
        console.log("   >>> [#add-user-btn]: ADD NEW USER - " + name);
        userAddElement = document.getElementById("add-user-msg");
        userAddElement.style.display = "block";
        userAddElement.style.fontWeight = "bold";

        if (name === "") {
            userAddElement.textContent = "Please fill in the user's name!";
            return;
        }

        isUserInDb(name, function(returndata) {
            console.log("   >>> [#add-user-btn]: is in DB - " + returndata);
            if (returndata) {

                userAddElement.textContent = "User " + name + " is already in the database";
            }
            else {
                userAddElement.textContent = "Please position yourself so that the camera detects your face. Need to take " + MAX_NUM_SNAPSHOTS + " snapshots.";
                document.getElementById("take-snapshot-btn").style.display = "block";
                document.getElementById("user-snapshot-img").style.display = "block";
                document.getElementById("user-snapshot-img").src = "../media/snapshot_placeholder.jpg";
                document.getElementById("save-snapshot-btn").style.display = "block";
                document.getElementById("cancel-adding-user-btn").style.display = "block";
                crtUserName = name;
                $.getJSON(BOARD_IP + "/recognition/add_user/" + name, function(data) {
                    if (data.response == true) {
                        console.log("   >>> [#add-user-btn]: DB ID =  " + data.user_db_id);
                        crtUserDbId = data.user_db_id
                    }
                    else {
                        console.log("   >>> [#add-user-btn]: DATA response  =FALSE");
                    }
                });
            }
        });

    });

    $("#take-snapshot-btn").click(function() {
        console.log("   >>> [#take-snapshot-btn]: TAKE SNAPSHOT");
        $.getJSON(BOARD_IP + "/recognition/take_snapshot", function(data) {
            if (data.response == true) {
                var loc = window.location.pathname;
                console.log("   >>> [#take-snapshot-btn]: crt loc " + loc);
                document.getElementById("user-snapshot-img").src = TMP_SNAPSHOT_PATH + "?t=" + new Date().getTime();
                document.getElementById("user-snapshot-img-title").style.display = "block";
                document.getElementById("user-snapshot-img-title").innerText = "Snapshot " + (crtNumSnapshots + 1);
                document.getElementById("save-snapshot-btn").disabled = false;
                document.getElementById("cancel-adding-user-btn").disabled = false;
            }

        });
    });

    $("#save-snapshot-btn").click(function() {
        console.log("   >>> [#save-snapshot-btn]: SAVE SNAPSHOT");

        $.getJSON(BOARD_IP + "/recognition/save_snapshot/" + crtUserDbId + "/" + crtNumSnapshots + "/", function(data) {
            if (data.response == true) {
                crtNumSnapshots = crtNumSnapshots + 1
                if (crtNumSnapshots == MAX_NUM_SNAPSHOTS) {
                    console.log("   >>> [#save-snapshot-btn]: Got all snapshots. TRAINING .... ");
                    document.getElementById("take-snapshot-btn").style.display = "none";
                    document.getElementById("user-snapshot-img").style.display = "none";
                    document.getElementById("save-snapshot-btn").style.display = "none";
                    document.getElementById("cancel-adding-user-btn").style.display = "none";
                    document.getElementById("user-snapshot-img-title").style.display = "none";
                    document.getElementById("user-name").value = "New User Name ...";

                    crtNumSnapshots = 0;
                    document.getElementById("load-dots").style.display = "block";
                    $.getJSON(BOARD_IP + "/recognition/retrain_new_user/" + crtUserName + "/"  + crtUserDbId + "/" + crtNumSnapshots + "/", function(data) {
                        if (data.response == true) {
                            document.getElementById("add-user-msg").textContent = ("User " + crtUserName + " added successfully to database!"
                                                                                    + " Training time: " + data.trainingtime + " for " + data.usersnumber + " users");
                        }
                        setTimeout(function() {
                           $.getJSON(BOARD_IP + "/profile/users/", function(data) {
                                var lastEntry = data[crtUserDbId];
                                var table_entry = "<tr>\n" +
                                    "<td class=\"align-middle\"><img class=\"user-img img-fluid z-depth-1 rounded-circle\" src=\"" + lastEntry.picture + "\"></td>" +
                                    "<td class=\"align-middle\">" + lastEntry.name + "</td>\n" +
                                    "</tr>\n";
                                if (lastEntry.name != "Unknown") {
                                    $("table #users").append(table_entry);
                                    console.log("   >>> Added new entry to user table")
                                }
                            });

                            document.getElementById("load-dots").style.display = "none";
                            document.getElementById("add-user-msg").textContent = CLEAR_MSG;
                        }, 3000);
                    });

                }
                document.getElementById("save-snapshot-btn").disabled = true;
            }
        });
    });

    $("#cancel-adding-user-btn").click(function() {
        console.log("   >>> [#cancel-adding-user-btn]: CANCEL ADDING USER");
        $.getJSON(BOARD_IP + "/recognition/cancel_adding_user/" + crtUserDbId, function(data) {
            if (data.response == true) {
                crtNumSnapshots = 0;
                document.getElementById("take-snapshot-btn").style.display = "none";
                document.getElementById("user-snapshot-img").style.display = "none";
                document.getElementById("user-snapshot-img").style.display = "none";
                document.getElementById("user-snapshot-img-title").style.display = "none";
                document.getElementById("save-snapshot-btn").style.display = "none";
                document.getElementById("cancel-adding-user-btn").style.display = "none";
                document.getElementById("user-name").value = "New User Name ...";
                document.getElementById("add-user-msg").textContent = CLEAR_MSG;
            }
        });
    });

    $("#user-name").keyup(function(event) {
        if (event.keyCode === 13) {  // 13 = Enter Key
            $("#add-user-btn").click();
        }
    });

  });
})
