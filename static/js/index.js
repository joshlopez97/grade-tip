$(document).ready(function () {
  $(window).resize(function () {
    sizer();
  });
  let lastSchools = [];
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
    if (geolocationProvidedPreviously()) {
      requestLocation(function onFailure(error) {
        console.log(error, 'poop');
        storeLocationCookie(false);
        $(".lds-ring").remove();
        fetchSchools(showSchools);
      });
    }
    else {
      fetchSchools(showSchools);
    }
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
    if (navigator.geolocation && getCookie("location") !== 'false') {
      let changeBtn = $("<a id='change-location'>Change</a>").click(function () {
        changeBtn.append(`<div class="lds-ring"><div></div><div></div><div></div><div></div></div>`);
        requestLocation(function onFailure(error) {
          storeLocationCookie(false);
          $(".lds-ring").remove();
          $("#change-location").css("display", "none");
        });
      });
      approxLocationHolder.append(changeBtn);
    }
  }

  function requestLocation(onFailure) {
    navigator.geolocation.getCurrentPosition(
      function onSuccess(pos) {
        storeLocationCookie(true);
        lastSchools = [];
        clearSchools();
        fetchSchools(showSchools, pos);
      },
      onFailure
    );
  }

  function hideApproximateLocation() {
    $("#approximate-location").css("display", "none");
  }

  function getCookie(name) {
    let match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) return match[2];
  }

  function geolocationProvidedPreviously() {
    let locationCookie = getCookie("location");
    return !!locationCookie && (locationCookie === true || locationCookie === 'true');

  }

  function storeLocationCookie(result) {
    document.cookie = `location=${result}`;
  }

  function fetchSchools(callback = () => {
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

        // show approx location if geolocation not provided
        const approx_location = nearest["approximate_location"];
        if (!!approx_location && pos == null) {
          showApproximateLocation(approx_location);
        }
      }
      callback(lastSchools);
    });
  }

  function showSchools(schools = lastSchools, heightAdjust = 0, callback = () => {
  }) {
    let nextSchools = getNextSchools(schools);
    if (nextSchools.length > 0) {
      $(".schools-header").css('display', 'block');
    }
    for (let i = 0; i < nextSchools.length; i++) {
      let school = nextSchools[i];
      appendSchool(school.name, school.id);
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
      return showSchools(lastSchools, height, animateSchools);
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