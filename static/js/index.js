$(document).ready(function() {
  $(window).resize(function() {
    sizer();
  });
  let schools = [];
  let last = [];
  let searchbar = $("#cv-searchbar");
  searchbar.autocomplete({
    source: get_res, 
    select: linkToSchool
  });
  focusField(searchbar);
  
  $("#cv-searchbtn").click(function(e){
    e.preventDefault();
    return false;
  });
  setUpHomepage();
  function sizer() {
    $("#cv-search").css("margin-top",(document.body.clientHeight * 0.17) + "px");
  }
  function generateMore() {
    if (!$(".schools").hasClass('loading')) {
      $(this).off('click'); 
      return fetchNewSchools();
    }
    return false;
  }
  function setUpHomepage() {
    sizer();
    $("#cv-search").append(
      `<h5 class='schools-header' style='margin:10px 0'>Schools Near You</h5>
            <div class="lds-ring"><div></div><div></div><div></div><div></div></div>
            <div class='schools-holder'><ul class='schools'></ul></div>`
    );
    let createLoadMoreBtn = function() {
      if ($("#more").length === 0) {
        $("#cv-search").append("<div id='more'></div>");
        $("#more").click(generateMore);
        $(".schools-holder").height($(".schools").height());
      }
    };
    fetchSchools(createLoadMoreBtn, 0, true);
  }


  function fetchSchools(end=function(){}, heightAdjust=0, firstCall=false) {
    let ipGeoLocationUsed = false;
    let onComplete = function(data) {
      const nearest = $.parseJSON(data);
      if (nearest.length === 0 || nearest['schools'].length === 0)
        return noSchools();
      else {
        if (firstCall) {
          $(".schools").empty();
          ipGeoLocationUsed = false;
        }
        $(".lds-ring").remove();
        last = last.concat(nearest['schools']);
        for (let i = 0; i<nearest['schools'].length; i++) {
          appendSchool(nearest['schools'][i],nearest['sids'][i]);
          if (i+1 === nearest['schools'].length)
            $(".schools-holder").height($(".schools").height()-heightAdjust);
        }
        return end();
      }
    };

    let geoLocSuccess = function(pos) {
      console.log('success');
      let payload = {"last": JSON.stringify(last), "quantity": 5, "lat": pos.coords.latitude, "lon": pos.coords.longitude};
      $.post("/nearest", payload, onComplete);
    };

    let geoLocFailure = function() {
      console.log('failed');
      ipGeoLocationUsed = true;
      let payload = {"last": JSON.stringify(last), "quantity": 5};
      $.post("/nearest", payload, onComplete);
    };

    if (firstCall) {
      geoLocFailure();
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(geoLocSuccess);
      }
    }
    else {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(geoLocSuccess, geoLocFailure);
      }
      else {
        geoLocFailure();
      }
    }
  }

  /**
   * Action when no schools were able to be retrieved
   */
  function noSchools() {
    $(".nschool, #more, .schools-header, .schools-holder").remove();
  }

  /**
   * Fetches new list of schools to replace current list
   */
  function fetchNewSchools() {
    let schools = $(".schools");
    if (!schools.hasClass('loading')) {
      // Schools to remove are given class 'pending'
      $(".ns").addClass('pending');

      const height = schools.height();
      let animateSchools = function() {
        schools.addClass("loading").animate({"top":"-"+height+"px"}, 400, function() {
          $(this).css("top","0px");
          $(this).removeClass("loading");
          $(".pending").remove();
          $("#more").click(generateMore)
        });
      };
      return fetchSchools(animateSchools, height);
    }
  }
  function appendSchool(school, sid) {
    if ($("#" + sid).length === 0) {
      let newSchool = $("<li class='ns'><a class='nschool' id=" + sid + ">" + school + "</a></li>")
      $(".schools").append(newSchool);
      newSchool.on("click", "a.nschool", () => window.location = ("/school/" + sid));
    }
  }
  $(window).on('load', function() {
    console.log('index.js window loaded');
  });
});