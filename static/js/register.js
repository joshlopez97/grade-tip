$(document).ready(function() {
  $(window).on('load',function(){
    focusField($("#school"));
    let un_index = 0;
    let usernames = [];
    let ondeck = [];
    $.get("/usernames", function(data) {
      usernames = $.parseJSON(data);
      getUsername();
    });

    /* Specific validators for each field */
    function validate_school() {
      console.log("validate_school");
      let school = $("#school").val();
      return school === "" || college_list.includes(school);
    }
    function validate_checkbox() {
      return $("#read").prop("checked");
    }
    function validate_email() {
      let re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      let emailElem = $("#email");
      let email = emailElem.val();
      if (re.test(email)) {
          $.post("/validate_email", {"email":email}, function(data) {
            if (!$.parseJSON(data)) {
              invalid($("#email"),"Account already exists with this email")
            }
          });
      }
      return re.test(emailElem.val());
    }
    function validate_password_len() {
      if ($("#password").val().length < 8) {
        return false;
      }
      if ($("#confirmpassword").val().length > 0) {
        if (validate_passwords_match()) {
          valid($("#password"));
          valid($("#confirmpassword"));
        }
        else {
          invalid($("#password"));
          invalid($("#confirmpassword"),"Passwords do not match");
        }
      }
      return true;
    }
    function validate_passwords_match() {
      console.log('validate_passwords_match');
      let pword = $("#password").val();
      let confirm_pword = $("#confirmpassword").val();
      console.log(pword === confirm_pword);
      return !(confirm_pword < 8 || pword !== confirm_pword);

    }
    let validators = {"school": validate_school,
                      "email": validate_email,
                      "password": validate_password_len,
                      "confirmpassword": validate_passwords_match,
                      "read": validate_checkbox,
                     };
    let error_msgs = {"school": "Please choose a valid university.",
                      "email": "Please enter a valid email address",
                      "password": "Password must be at least 8 characters",
                      "confirmpassword": "Passwords do not match",
                      "read": "You must accept the terms and conditions"
    };
    let is_valid   = {"school": true,
                      "email": false,
                      "password": false,
                      "confirmpassword": false,
                      "read": false
                     };

    /* Change UI for when field has been validated or user is typing */
    function invalid(field, error="") {

      // Add error elements
      let elem = field.parent().parent();
      let icon = elem.find(".ok");
      if (icon.length === 0)
        $("<img src=\"/img/cancel.png\" class=\"ok\">").appendTo(elem);
      else
        icon.attr("src","/img/cancel.png");
      if (elem.find(".error").length === 0 && error !== "")
        $('<p class="error">' + error + '</p>').appendTo(elem);

      // Set element to invalid
      is_valid[field.attr('id')] = false;
      $("#saveForm").prop('disabled', true);
    }
    function valid(field) {
      // Remove error elements and add success elements
      let elem = field.parent().parent();
      let icon = elem.find(".ok");
      let error = elem.find(".error");
      if (icon.length === 0 && field[0].id !== "read" && field[0].id !== "school")
        $("<img src=\"/img/confirm.png\" class=\"ok\">").appendTo(elem);
      else
        icon.attr("src","/img/confirm.png");
      if (error.length !== 0)
        error.remove();

      // Enable next field
      let next = elem.next(".ritem");
      if (next.length !== 0) {
        let nxtin = next.find("input.element");
        nxtin.prop('disabled', false);
      }

      // Set element to valid
      is_valid[field.attr('id')] = true;
    }

    function checkIfAllValid() {
      let finished = true;
      for (let check in is_valid) {
        console.log(check, is_valid[check]);
        if (!is_valid[check])
          finished = false;
      }
      console.log("finished: ", finished);
      return finished
    }
    function typing(field) {
      let elem = field.parent().parent();
      let icon = elem.find(".ok");
      let error = elem.find(".error");
      if (field.val().length !== 0 && validators[field.attr('id')]())
        valid(field);
      else {
        if (field.attr('id') === "school" && field.val().length === 0)
          is_valid["school"] = true;
        if (icon.length !== 0)
          icon.remove();
        if (error.length !== 0)
          error.remove();
      }
    }
    /* Attach validators and UI changers to event handlers for each field */
    $("input.element, input[type='checkbox']").change( function() {
      if (validators[$(this).attr('id')]())
        valid($(this));
    }).on("input focus", function() {
      typing($(this));
      if (checkIfAllValid())
        $("#saveForm").prop("disabled",false);
      else if ($("#saveForm").is(":disabled"))
        $("#saveForm").prop("disabled",true);
    }).on("blur", function() {
      if (validators[$(this).attr('id')]())
        valid($(this));
      else if ($(this).val().length > 0)
        invalid($(this),error_msgs[$(this).attr('id')]);
    });
    $("input[type='checkbox']").change( function() {
      if (validators[$(this).attr('id')]())
        valid($(this));
      if (checkIfAllValid())
        $("#saveForm").prop("disabled",false);
      else if ($("#saveForm").is(":disabled"))
        $("#saveForm").prop("disabled",true);
    });
    $("#school").on("focus", function() {
      $(this).autocomplete("search");
    }).autocomplete({
      select: function(event, ui){
        $(this).val(ui.item.value);
        valid($(this));
        $(this).blur();
        focusField($("#email"));
      },
      source: get_res,
      appendTo: "#school-holder"
    });
    $("#get-username").click(getUsername);
    $("#saveForm").click(function() {
      if (checkIfAllValid())
        $("form.gt-form").submit();
    });

    function getUsername(){
      console.log(un_index + ", " + usernames[un_index])
      let username = usernames[un_index];
      un_index++;
      if (un_index === 50) {
        usernames = ondeck
        un_index = 0;
      }

      if (un_index === 25) {
        $.get("/usernames", function(data) {
          ondeck = $.parseJSON(data);
        });
      }
      $("#userholder").empty().append("<span id=\"username\">" + username + "</span>");
      $("#displayname")[0].value = username;
      return false;
    }
  });
});