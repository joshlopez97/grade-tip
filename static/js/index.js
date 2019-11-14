$(document).ready(function () {
  $(window).resize(function () {
    sizer();
  });
  let lastSchools = [];
  let lastSIDS = [];
  let current = 0;
  let searchbar = $("#cv-searchbar");
  let searchbtn = $("#cv-searchbtn");
  searchbar.autocomplete({
    source: search,
    focus: () => {
      return false;
    },
    select: schoolAutocompleteClickHandler,
    scroll: true,
    open: function () {
      $("ul.ui-menu").width(searchbtn.outerWidth() + searchbar.outerWidth() - 2);
    }
  });

  searchbtn.click(function (e) {
    e.preventDefault();
    return false;
  });
  setUpHomepage();

  function sizer() {
    $("#cv-search").css("margin-top", (document.body.clientHeight * 0.17) + "px");
  }

  function generateMore() {
    if (!$(".schools").hasClass('loading')) {
      $(this).off('click');
      return showNewSchools();
    }
    return false;
  }

  function setUpHomepage() {
    sizer();
    let searchBar = $("#cv-search");
    searchBar.append(`
      <div class='schools-header'>
        <h5 class='schools-title'>Suggested Schools</h5>
        <span id="approximate-location"></span>
      </div>
      <div class='schools-holder'><ul class='schools'></ul></div>`
    );
    fetchSchools2(showSchools);
    let createLoadMoreBtn = function () {
      if ($("#more").length === 0) {
        let loadMoreBtn = $("<div id='more'><svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.0\" x=\"0px\" y=\"0px\" viewBox=\"0 0 100 125\" enable-background=\"new 0 0 100 100\" xml:space=\"preserve\"><path d=\"M21.364,42.218l24.329,24.329c0.026,0.027,0.034,0.065,0.061,0.091c1.146,1.146,2.659,1.715,4.17,1.711   c1.511,0.004,3.023-0.564,4.17-1.711c0.027-0.027,0.034-0.064,0.061-0.091l24.329-24.329c2.285-2.285,2.285-6.024,0-8.308   s-6.024-2.285-8.308,0L49.923,54.161L29.672,33.91c-2.285-2.285-6.024-2.285-8.308,0S19.079,39.934,21.364,42.218z\"/></svg></div>").click(generateMore);
        searchBar.append(loadMoreBtn);
        $(".schools-holder").height($(".schools").height());
      }
    };
    // fetchSchools(createLoadMoreBtn, 0, true);
  }

  function createLoadMoreBtn() {
    if ($("#more").length === 0) {
      let loadMoreBtn = $("<div id='more'><svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.0\" x=\"0px\" y=\"0px\" viewBox=\"0 0 100 125\" enable-background=\"new 0 0 100 100\" xml:space=\"preserve\"><path d=\"M21.364,42.218l24.329,24.329c0.026,0.027,0.034,0.065,0.061,0.091c1.146,1.146,2.659,1.715,4.17,1.711   c1.511,0.004,3.023-0.564,4.17-1.711c0.027-0.027,0.034-0.064,0.061-0.091l24.329-24.329c2.285-2.285,2.285-6.024,0-8.308   s-6.024-2.285-8.308,0L49.923,54.161L29.672,33.91c-2.285-2.285-6.024-2.285-8.308,0S19.079,39.934,21.364,42.218z\"/></svg></div>");
      loadMoreBtn.click(generateMore);
      $("#cv-search").append(loadMoreBtn);
      $(".schools-holder").height($(".schools").height());
    }
  }

  function showApproximateLocation(approx_location) {
    let approxLocationHolder = $("#approximate-location");
    approxLocationHolder.text(`Near ${approx_location} `);
    let changeBtn = $("<a id='change-location'>Change</a>").click(function () {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (pos) {
          console.log(pos);
          lastSIDS = [];
          lastSchools = [];
          clearSchools();
          fetchSchools2(showSchools, pos);
        });
      }
    });
    approxLocationHolder.append(changeBtn);
  }

  function hideApproximateLocation() {
    $("#approximate-location").css("display", "none");
  }

  function fetchSchools2(callback = () => {
  }, pos = null) {
    let payload = {"last": JSON.stringify(lastSchools), "quantity": 50};
    if (pos !== null) {
      payload["lat"] = pos.coords.latitude;
      payload["lon"] = pos.coords.longitude;
      hideApproximateLocation();
    }
    $.post("/nearest", payload, function cacheSchools(data) {
      const nearest = $.parseJSON(data);
      if (!!nearest && !!nearest['schools'] && nearest['schools'].length > 0) {
        // cache nearest school data
        lastSchools = lastSchools.concat(nearest['schools']);
        lastSIDS = lastSIDS.concat(nearest['sids']);

        // show approx location if geolocation not provided
        const approx_location = nearest["approximate_location"];
        if (!!approx_location && pos == null) {
          showApproximateLocation(approx_location);
        }
      }
      callback(lastSchools, lastSIDS);
    });
  }

  function showSchools(schools = lastSchools, sids = lastSIDS, heightAdjust = 0, callback = () => {
  }) {
    let nextSchools = getNextSchools(schools);
    console.log("next schools are ", nextSchools);
    for (let i = 0; i < nextSchools.length; i++) {
      appendSchool(nextSchools[i], sids[i]);
      if (i + 1 === nextSchools.length) {
        $(".schools-holder").height($(".schools").height() - heightAdjust);
      }
    }
    if (nextSchools[nextSchools.length - 1] !== schools[schools.length - 1]) {
      console.log(nextSchools[nextSchools.length - 1], schools[schools.length - 1]);
      createLoadMoreBtn();
    }
    else {
      $("#more").css("visibility", "hidden");
    }
    callback();
  }

  function clearSchools() {
    $(".schools").empty();
  }


  function fetchSchools(end = function () {
  }, heightAdjust = 0, firstCall = false) {
    let ipGeoLocationUsed = false;
    let onComplete = function (data) {
      const nearest = $.parseJSON(data);
      if (nearest.length === 0 || nearest['schools'].length === 0) {
        return noSchools();
      }
      else {
        if (firstCall) {
          $(".schools").empty();
          ipGeoLocationUsed = false;
        }
        $(".lds-ring").remove();
        lastSchools = lastSchools.concat(nearest['schools']);
        for (let i = 0; i < nearest['schools'].length; i++) {
          appendSchool(nearest['schools'][i], nearest['sids'][i]);
          if (i + 1 === nearest['schools'].length)
            $(".schools-holder").height($(".schools").height() - heightAdjust);
        }
        const approx_location = nearest["approximate_location"];
        if (!!approx_location) {
          showApproximateLocation(approx_location);
        }
        return end();
      }
    };

    let geoLocSuccess = function (pos) {
      console.log('success');
      let payload = {
        "last": JSON.stringify(lastSchools),
        "quantity": 5,
        "lat": pos.coords.latitude,
        "lon": pos.coords.longitude
      };
      $.post("/nearest", payload, onComplete);
    };

    let geoLocFailure = function () {
      console.log('failed');
      ipGeoLocationUsed = true;
      let payload = {"last": JSON.stringify(lastSchools), "quantity": 5};
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
      let animateSchools = function () {
        schools.addClass("loading").animate({"top": "-" + height + "px"}, 400, function () {
          $(this).css("top", "0px");
          $(this).removeClass("loading");
          $(".pending").remove();
          $("#more").click(generateMore)
        });
      };
      return fetchSchools(animateSchools, height);
    }
  }

  function showNewSchools() {
    let schools = $(".schools");
    if (!schools.hasClass('loading')) {
      // Schools to remove are given class 'pending'
      $(".ns").addClass('pending');

      const height = schools.height();
      let animateSchools = function () {
        schools.addClass("loading").animate({"top": "-" + height + "px"}, 400, function () {
          $(this).css("top", "0px");
          $(this).removeClass("loading");
          $(".pending").remove();
          $("#more").click(generateMore)
        });
      };
      return showSchools(lastSchools, lastSIDS, height, animateSchools);
    }
  }

  function getNextSchools(schools) {
    if (schools.length <= current) {
      return [];
    }
    console.log(schools);
    let nextSchools = schools.slice(current, current + 5);
    current += 5;
    return nextSchools;
  }

  function appendSchool(school, sid) {
    if ($(`#${sid}`).length === 0) {
      $(".schools").append(
        $(`
        <li class="ns">
          <a class="nschool" id="sid">${school}</a>
        </li>
        `).click(() => window.location = `/school/${sid}`)
      );
    }
  }
});