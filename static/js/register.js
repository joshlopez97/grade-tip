$(document).ready(function() {
  $(window).on('load',function(){
    var un_index = 0;
    var usernames = [];
    var ondeck = [];
    $.get("/getusernames", function(data) {
      usernames = $.parseJSON(data);
      getUsername();
    });
    focusField($("#element_1"));

    /* Specific validators for each field */
    function validate_school() {
      var school = $("#element_1").val();
      return college_list.includes(school);
    }
    function validate_email() {
      console.log('validate_email')
      var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
      var email = $("#element_2").val()
      if (re.test(email)) {
          $.post("/validate_email", {"email":email}, function(data) {
            if (!$.parseJSON(data)) {
              invalid($("#element_2"),"Account already exists with this email")
            }
          });
      }
      return re.test($("#element_2").val());
    }
    function validate_password_len() {
      console.log('validate_password_len')
      if ($("#element_3").val().length < 8) {
        return false;
      }
      if ($("#element_4").val().length > 0) {
        if (validate_passwords_match()) {
          valid($("#element_3"));
          valid($("#element_4"));
        }
        else {
          invalid($("#element_3"));
          invalid($("#element_4"),"Passwords do not match");
        }
      }
      return true;
    }
    function validate_passwords_match() {
      console.log('validate_passwords_match')
      console.log($("#element_3").val() == $("#element_4").val())
      if ($("#element_4").val().length < 8 || $("#element_3").val() != $("#element_4").val()) {
        return false;
      }
      return true;
    }
    var validators = {"element_1": validate_school,
                      "element_2": validate_email,
                      "element_3": validate_password_len,
                      "element_4": validate_passwords_match
                     };
    var error_msgs = {"element_1": "Please choose a valid university.",
                      "element_2": "Please enter a valid email address",
                      "element_3": "Password must be at least 8 characters",
                      "element_4": "Passwords do not match"
    }
    var is_valid   = {"element_1": false,
                      "element_2": false,
                      "element_3": false,
                      "element_4": false
                     };

    /* Change UI for when field has been validated or user is typing */
    function invalid(field, error="") {

      // Add error elements
      var elem = field.parent().parent();
      var icon = elem.find(".ok");
      if (icon.length == 0)
        $("<img src=\"/img/cancel.png\" class=\"ok\">").appendTo(elem);
      else
        icon.attr("src","/img/cancel.png");
      if (elem.find(".error").length == 0 && error != "")
        $('<p class="error">' + error + '</p>').appendTo(elem);

      // Set element to invalid
      is_valid[field.attr('id')] = false;
      $("#saveForm").prop('disabled', true);
    }
    function valid(field) {

      // Remove error elements and add success elements
      var elem = field.parent().parent();
      var icon = elem.find(".ok");
      var error = elem.find(".error");
      if (icon.length == 0)
        $("<img src=\"/img/confirm.png\" class=\"ok\">").appendTo(elem);
      else
        icon.attr("src","/img/confirm.png");
      if (error.length != 0)
        error.remove();

      // Enable next field
      var next = elem.next(".ritem");
      if (next.length != 0) {
        var nxtin = next.find("input.element");
        nxtin.prop('disabled', false);
      }

      // Set element to valid
      is_valid[field.attr('id')] = true;
    }
    function typing(field) {
      console.log("typing")
      var elem = field.parent().parent();
      var icon = elem.find(".ok");
      var error = elem.find(".error");
      console.log(error);
      if (field.val().length != 0 && validators[field.attr('id')]())
        valid(field);
      else {
        if (field.attr('id') == "element_1" && field.val().length == 0)
          is_valid["element_1"] = true;
        if (icon.length != 0)
          icon.remove();
        if (error.length != 0)
          error.remove();
      }
    }
    function highlight_required() {
      for (var field in validators)
        if (field != "element_1" && !validators[field]())
          invalid(field,"Required Field")
    }

    /* Attach validators and UI changers to event handlers for each field */
    $("input.element").change( function() {
      if (validators[$(this).attr('id')]())
        valid($(this));
    });
    $("input.element").on("input focus", function() {
      typing($(this));
      finished = true;
      for (var check in is_valid)
        if (!is_valid[check])
          finished = false;
      if (finished)
        $("#saveForm").prop("disabled",false);
      else if ($("#saveForm").is(":disabled"))
        $("#saveForm").prop("disabled",true);
    });
    $("input.element").on("blur", function() {
      if (validators[$(this).attr('id')]())
        valid($(this));
      else if ($(this).val().length > 0)
        invalid($(this),error_msgs[$(this).attr('id')]);
    });
    $("#element_1").on("focus", function() {
      $(this).autocomplete("search");
    })
    $("#element_1").autocomplete({
      select: function(event, ui){
        $(this).val(ui.item.value);
        valid($(this));
        $(this).blur();
        focusField($("#element_2"));
      },
      source: get_res,
      appendTo: "#school-holder"
    });
    $("#get-username").click(getUsername);
    $("#saveForm").click(function() {
      var all_valid = true;
      for (var check in is_valid)
        if (check != "element_1" && !is_valid[check])
          all_valid = false;
      if (all_valid)
        $("form.appnitro").submit();
    });

    function getUsername(){
      console.log(un_index + ", " + usernames[un_index])
      var username = usernames[un_index];
      un_index++;
      if (un_index == 50) {
        usernames = ondeck
        un_index = 0;
      }

      if (un_index == 25) {
        $.get("/getusernames", function(data) {
          ondeck = $.parseJSON(data);
        });
        console.log(ondeck);
      }
      $("#userholder").empty();
      $("#userholder").append("<span id=\"username\">" + username + "</span>");
      document.getElementById("element_5").value = username
      return false;
    }
  });
});