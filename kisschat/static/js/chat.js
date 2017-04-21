$( function() {
    var websocket, is_loggedin, reject_reason, dialog, form,
      name = $( "#name" ),
      passwd = $( "#passwd" ),
      allFields = $( [] ).add( name ).add( passwd ),
      tips = $( ".validateTips" ),
      textarea = $( "#chatbox" ),
      userlist = $( "#userlist" ),
      msgin = $( "#msgin" ),
      msgbut = $( "#msgbut" ),
      allusers = [];

    function login() {

      allFields.removeClass( "ui-state-error" );

      valid = checkLength( name, "username", 3, 16 );
      valid &= checkLength( passwd, "password", 3, 32 );

      if (valid) {
          reject_reason = "";
          is_loggedin = false;
          websocket = new WebSocket("ws://" + location.host + "/ws");
          websocket.onmessage = onWsData;
          websocket.onopen = onWsOpen;
          websocket.onclose = onWsClose;
      }

    }

    function checkLength( o, n, min, max ) {
      if ( o.val().length > max || o.val().length < min ) {
        o.addClass( "ui-state-error" );
        updateTips( "Length of " + n + " must be between " +
          min + " and " + max + "." );
        return false;
      } else {
        return true;
      }
    }

    function updateTips( t ) {
      tips
        .text( t )
        .addClass( "ui-state-highlight" );
      setTimeout(function() {
        tips.removeClass( "ui-state-highlight", 1500 );
      }, 500 );
    }

    dialog = $( "#dialog-form" ).dialog({
      autoOpen: true,
      height: 350,
      width: 250,
      modal: true,
      buttons: {
        "Login": login,
      },
      closeOnEscape: false,
      open: function(event, ui) {
          $(".ui-dialog-titlebar-close", ui.dialog | ui).hide();
      }
    });

    form = dialog.find( "form" ).on( "submit", function( event ) {
      event.preventDefault();
      login();
    });


    onWsOpen = function(event) {
        var msg = '{"name": "' + name.val() + '", ';
        msg += '"passwd": "' + passwd.val() + '"}'
        websocket.send(msg)
    };

    onWsData = function(event) {
        var resp = $.parseJSON(event.data);
        if (is_loggedin) {
            if (resp["type"] == "new_message") {
                var msg = escapeHtml(resp["message"]);
                if (textarea.val()) {
                    msg = "\n" + msg
                }
                textarea.append(msg);
                textarea.scrollTop(textarea[0].scrollHeight - textarea.height());
            } else if (resp["type"] == "new_users") {
                addUsers(resp["names"]);
            } else if (resp["type"] == "del_users") {
                delUsers(resp["names"]);
            }
        } else {
            is_loggedin = Boolean(resp["ok"]);
            reject_reason = resp["reason"];
            if (is_loggedin) {
                textarea.empty();
                clearUsers();
                allusers = [name.val()];
                updateUsers();
                dialog.dialog("close");
            }
        }
    };

    onWsClose = function(event) {
        var msg;
        dialog.dialog("open");
        if (reject_reason == "user_logged_in") {
            msg = "This user is already logged in!";
        } else if (reject_reason == "user_banned") {
            msg = "User is banned.";
        } else if (reject_reason == "authentication_failed") {
            msg = "Incorrect password.";
        } else {
            msg = "You have been disconnected.";
        }
        updateTips(msg);
    };

    addUsers = function(names) {
        for (var i = 0; i < names.length; i++) {
            allusers.push(names[i])
        }
        allusers.sort();
        updateUsers();
    };

    delUsers = function(names) {
        var newusers = [];
        for (var i = 0; i < allusers.length; i++) {
            curname = allusers[i];
            to_delete = false;
            for (var j = 0; j < names.length; j++){
                delname = names[j];
                if (curname == delname) {
                    to_delete = true;
                }
            }
            if (!to_delete) {
                newusers.push(curname)
            }
        }
        newusers.sort();
        allusers = newusers;
        updateUsers();
    };

    updateUsers = function() {
        userlist.empty();
        for (var i = 0; i < allusers.length; i++) {
            username = escapeHtml(allusers[i]);
            if (username == name.val()) {
                username = "<h4>" + username + "</h4>"
            }
            entry = '<li class="list-group-item">' + username  + '</li>'
            userlist.append(entry);
        }
    }

    clearUsers = function() {
        userlist.empty();
        allusers = [];
    };

    sendMessage = function() {
        var msg = msgin.val().trim();
        if (msg) {
            websocket.send(msg);
        }
        msgin.val("");
    };

    msgin.keypress(function(e) {
        if (e.which == 13) {
            sendMessage();
        }
    });

    msgbut.click(sendMessage)


    var entityMap = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': '&quot;',
      "'": '&#39;',
      "/": '&#x2F;'
    };

    function escapeHtml(string) {
      return String(string).replace(/[&<>"'\/]/g, function (s) {
        return entityMap[s];
      });
    }

  } );
