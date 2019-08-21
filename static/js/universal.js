
/* Get college and high school data */
var college_list = [];
var college_data = {};
$.get("/getcolleges", function(data) {
  college_data = $.parseJSON(data);
  college_list = Object.keys(college_data);
});

jQuery.ui.autocomplete.prototype._resizeMenu = function () {
  var ul = this.menu.element;
  ul.outerWidth(this.element.outerWidth());
};

/* Function retrieves top 5 schools that match a query - used for autocomplete */
var cached_results = {};
function get_res(request, response) {
  console.log(cached_results);
  var results = new Set();
  var stopwords = ['of','at','and','the','for'];
  var query = request.term.toLowerCase().trim();
  if (query in cached_results) {
    response(cached_results[query]);
    return;
  }

  var terms = query.split(' ').filter(Boolean);
  var second = [];
  var third = [];
  var fourth = [];
  var fifth = [];

  for (let college of college_list) {
    // Format College
    var acronym = college.toLowerCase().match(/\b(?!(?:of|at|and|the|for)[^a-zA-Z0-9])(\w)/g).join('');
    var shortened = college.toLowerCase().match(/\b(?!(?:of|at|and|the|for)[^a-zA-Z0-9])(\w+)/g).join(' ');

    // Get results in order of relevance
    if ( acronym === query || acronym === query.replace(/\s/g, '') )
      results.add(college);
    else if ( college.toLowerCase().startsWith(query) || shortened.startsWith(query) )
      second.push(college);
    else if ( acronym.startsWith(query) )
      third.push(college);
    // Check acronym versions of query
    else if ( terms.length > 1 && acronym.startsWith(terms[0]) ) {
      var parsed_college = college.toLowerCase().match(/\b(\w+)/g);
      var shift_parsed = parsed_college.slice();
      for (i=0; i<terms[0].length;) {
        if (shift_parsed.length === 0)
          break;
        if ( !stopwords.includes(shift_parsed[0]) )
          i++;
        shift_parsed.splice(0, 1);
      }
      var remaining_college = shift_parsed.join(' ').trim();
      var remaining_query = query.substring(terms[0].length+1);

      if ( shift_parsed.length === terms.length-1 && remaining_college.includes(remaining_query) ) {
        third.push(college);
      } else if ( remaining_college.includes(remaining_query) ) {
        fourth.push(college);
      }
    }
    else {
      var allin = true;
      for (let term of terms) {
        var regex = new RegExp("\\b" + term, 'g');
        if ( !college.toLowerCase().match(regex) )
          allin = false;
      }
      if (allin)
        fourth.push(college);

    }
  }
  maxres:
  for (let tier of [second, third, fourth]) {
    for (let item of tier) {
      results.add(item);
      if (results.size >= 5)
        break maxres;
    }
  }
  if (results.size > 0 && Object.keys(cached_results).length < 50)
    cached_results[query] = Array.from(results).splice(0,5);
  response(cached_results[query]);
}

/* Helper function to focus an input field */
function focusField(elem) {
  window.setTimeout(function()
  {
    elem.focus();
  }, 0);
}

function linkToSchool(event, ui)
{
  school = ui.item.value;
  console.log(school);
  if (!(school in college_data))
    return false;
  var sid = college_data[school]['sid'];
  window.location.href = ("/school/" + sid);
}

/* Search bar display animation for mobile devices */
function mobileSearchActive(e) {
  e.stopPropagation();
  if ($(".navbar-list").find("li.usearch-mobile-holder").length > 0)
    return false;
  if ($(".sidebar").length > 0)
    hideSidebar();
  $(".navbar-brand").css('display','none');
  $(".navbar-list").append('<li class="usearch-mobile-holder" id="usearch-mobile-holder"><input class="usearch-mobile usearch-bar" id="usearch-mobile" type="text" placeholder="Search for a school"></li>');
  $("#usearch-mobile-holder").width(document.documentElement.clientWidth-100);
  $("#usearch-mobile").width(0);
  $("#usearch-mobile").css('padding', '0px');
  $("#usearch-mobile").focus();
  $("#usearch-mobile").animate({
    width: (document.documentElement.clientWidth-100) + "px",
    padding: "6px 10px"},
    300, function() {
    focusField($(this));
  });
  $("#usearch-mobile").autocomplete({
    source: get_res, 
    open: function( event, ui ) {
      $('.ui-autocomplete.ui-menu').addClass('usearch');
      $('.ui-menu-item').addClass('usearch')
    },
    select: linkToSchool
  });
  const searchbtn = $(".usearch-mobile-icon-holder");
  searchbtn.unbind('click');
  searchbtn.click(mobileSearchInactive);
}
function mobileSearchInactive() {
  if ($(".navbar-list").find("li.usearch-mobile-holder").length === 0)
    return false;
  $("#usearch-mobile").animate(
      {
          width: "0px",
          padding: "0px"
      },
      300,
      function() {
          $(".navbar-brand").css('display', 'inline-block');
          $("li.usearch-mobile-holder").remove();
          const searchbtn = $(".usearch-mobile-icon-holder");
          searchbtn.unbind('click');
          searchbtn.click(mobileSearchActive);
      }
  );
}

/* Sidebar display for mobile devices */
function displaySidebar() {
    const sidebar = $(".sidebar");
    const ANIMATE_TIME = 300;
    if (sidebar.length > 0)
        return false;
    else {
        if ($(".navbar-list").find("li.usearch-mobile-holder").length > 0)
            mobileSearchInactive();
        $(".icon").addClass("close");
        const buttons = $(".gtbtn");
        console.log(buttons);
        var contents = "<ul class='side sidenav-list'>";
        for (let button of buttons) {
            button = $(button);
            if (button.attr("id") !== "usearch-btn")
                contents += "<li class='side sidenav-holder'>" + $(button).prop('outerHTML') + "</li>";
        }
        contents += "</ul>";
        $("body").append("<div class='side sidebar'>" + contents + "</div>");
        $("body").append("<div class='side navcolor'></div>");
        $(".navcolor").css({left: (-document.documentElement.clientWidth) + "px",
            background: $(".sidebar").css("background"),
            display: "block",
            width: document.documentElement.clientWidth + "px"});
        sidebar.find("button").attr("class", "navbtn side");
        $(".navcolor").animate({ left: "0px" }, ANIMATE_TIME);
        $(".sidebar").animate({ left: "0px" },
            ANIMATE_TIME,
            function () {
                const sidebtn = $(".sidebar-mobile-icon-holder");
                sidebtn.unbind('click');
                sidebtn.click(hideSidebar);
              });
    }
}

function hideSidebar() {
    const sidebar = $(".sidebar");
    if (sidebar.length === 0)
        return false;
    else {
        $(".icon").removeClass("close");
        $(".sidebar").animate({ left: "-325px" },
            300,
          function () {
            sidebar.remove();
            const sidebtn = $(".sidebar-mobile-icon-holder");
            sidebtn.unbind('click');
            sidebtn.click(displaySidebar);
          });
        $(".navcolor").animate({left: (-document.documentElement.clientWidth) + "px"}, 300, function() {
            $(".navcolor").remove();
        });
    }
}

/* Find School Search Bar - hover and focus (for default web page) */
function searchActive() {
  console.log('searchActive')
  $('#usearch-btn').css({'border-bottom': '4px solid #cc0066', 'color': '#f3f3f3'});
  $('#usearch-holder').css({'display': 'block'});
  $("input").blur();
  focusField($('#usearch'));
  if ( $('#usearch').val() ) {
    $("#usearch").autocomplete("search");
  }
};
function searchInactive() {
  console.log('searchInactive')
  console.log($('.ui-autocomplete:hover').length)

  if ( $('#usearch-holder').css('display') == 'block' && $('.ui-autocomplete:hover').length == 0 && $('.usearch:hover').length == 0 ) {
    $('#usearch').blur();
    $('#usearch-btn').css({'border-bottom': '', 'color': ''});
    $('#usearch-holder').css({'display': 'none'});
  }
};

function doneLoading() {
  var now = (new Date()).getSeconds();
  console.log(now - preload_st)
  $("#loader").remove();
}

/* SVG icons as inline HTML */
var lecture_icon = '<div class="btn-icon-holder"> <?xml version="1.0" encoding="utf-8"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"> <svg class="btn-icon" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="50px" height="50px" viewBox="0 0 50 50" enable-background="new 0 0 50 50" xml:space="preserve"> <path fill="#FFFFFF" d="M11.953,9.497c2.944,1.172,2.625,4.11,2.625,7.55H3.266c0-3.386-0.289-6.286,2.583-7.494 c0,0,1.042,1.119,2.979,1.119S11.953,9.497,11.953,9.497z"/> <path fill="#FFFFFF" d="M12.479,39.121c2.944,1.172,4.225,4.486,4.225,7.926H0.953c0-3.387,1.378-6.717,4.25-7.926 c0,0,1.688,1.551,3.625,1.551S12.479,39.121,12.479,39.121z"/> <circle fill="#FFFFFF" cx="8.828" cy="35.119" r="4.001"/> <path fill="#FFFFFF" d="M27.479,39.121c2.944,1.172,4.225,4.486,4.225,7.926h-15.75c0-3.387,1.378-6.717,4.25-7.926 c0,0,1.688,1.551,3.625,1.551S27.479,39.121,27.479,39.121z"/> <circle fill="#FFFFFF" cx="23.828" cy="35.119" r="4.002"/> <path fill="#FFFFFF" d="M42.479,39.121c2.944,1.172,4.225,4.486,4.225,7.926h-15.75c0-3.387,1.378-6.717,4.25-7.926 c0,0,1.688,1.551,3.625,1.551S42.479,39.121,42.479,39.121z"/> <circle fill="#FFFFFF" cx="38.828" cy="35.119" r="4.002"/> <path fill="#FFFFFF" d="M19.953,20.015"/> <path fill="#FFFFFF" d="M47.203,20.015"/> <path fill="#FFFFFF" d="M47.203,20.015V8.39c0-2.209,0.418-4-1.791-4H21.744c-2.209,0-1.791,1.791-1.791,4v11.625H47.203z"/> <rect x="18.109" y="20.953" fill="#FFFFFF" width="30.938" height="1.688"/> <rect x="0.953" y="18.182" fill="#FFFFFF" width="15.75" height="1.833"/> <rect x="2.453" y="20.015" fill="#FFFFFF" width="13" height="9.334"/> <circle fill="#FFFFFF" cx="8.828" cy="6.225" r="3.271"/> </svg> </div>';
var toclass_icon = '<div class="btn-icon-holder"><?xml version="1.0" encoding="utf-8"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"> <svg class="btn-icon" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="50px" height="50px" viewBox="0 0 50 50" enable-background="new 0 0 50 50" xml:space="preserve"> <path fill="#FFFFFF" d="M43.582,26.834v8.291c0,0,0.167,0.875,1.167,0.875c0,0,3.042,0.291,2.917-1.542l-2.041-7.624 c0,0-0.173-0.803-1.126-0.553C44.499,26.281,43.696,26.417,43.582,26.834z"/> <path fill="#FFFFFF" d="M40.332,25.031h1.104c0,0,1.594,0.5,1.594,1.344s0,8.656,0,8.656l0.552,5.553l2.959,5.833 c0,0,0.207,1.375-0.584,1.875s-1.875-0.5-1.875-0.5l-2.875-6.5l-0.875-3.75l-3,3l-0.75,6.792c0,0-0.416,0.875-1.583,0.583 s-1-1.125-1-1.125L34.832,40l3.625-4.625l0.125-6.041c0,0-0.209,0.542-0.625,0.833l-2.458,2.375c0,0-0.751,0.958-1.917,0.25 s0-1.417,0-1.417l2.667-2.584l1.417-2.833c0,0,0.291-0.646,2.5-0.927"/> <circle fill="#FFFFFF" cx="40.332" cy="20" r="3.75"/> <path fill="#FFFFFF" d="M28.583,13.25h-5.375v-1.54l-7.333-4l-7.333,4v1.54H3.167c-0.552,0-1,0.448-1,1v15.334h27.417V14.25 C29.583,13.698,29.136,13.25,28.583,13.25z M8.625,26h-3.5v-3.5h3.5V26z M8.625,20h-3.5v-3.5h3.5V20z M14.625,26h-3.5v-3.5h3.5V26z M14.625,20h-3.5v-3.5h3.5V20z M13.688,12.414c0-1.208,0.979-2.188,2.188-2.188s2.188,0.979,2.188,2.188s-0.979,2.188-2.188,2.188 S13.688,13.622,13.688,12.414z M20.625,26h-3.5v-3.5h3.5V26z M20.625,20h-3.5v-3.5h3.5V20z M26.625,26h-3.5v-3.5h3.5V26z M26.625,20 h-3.5v-3.5h3.5V20z"/> <polygon fill="#FFFFFF" points="16.213,5.717 16.213,1.156 15.538,1.156 15.538,5.717 7.112,10.329 7.112,11.726 15.875,6.833 24.638,11.726 24.638,10.329 "/> <path fill="#FFFFFF" d="M16.484,1.156v2.734c0,0,0.781-0.516,1.547,0s1.641,0,1.641,0s0.703-0.516,1.5,0V1.156 c0,0-0.766-0.594-1.594,0s-1.469,0-1.469,0S17.281,0.625,16.484,1.156z"/> </svg> </div>';
var offer_icon = '<div class="btn-icon-holder"><?xml version="1.0" encoding="utf-8"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"> <svg class="btn-icon" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="50px" height="50px" viewBox="0 0 50 50" enable-background="new 0 0 50 50" xml:space="preserve"> <path fill="#FFFFFF" d="M38.089,28.557V8.15c0-2.453-1.988-4.441-4.441-4.441H18.509c-2.146,0-2.813,0.592-2.813,0.592l-8.883,8.735 c-1.037,1.185-0.667,3.257-0.667,3.257V41.85c0,2.453,1.989,4.441,4.442,4.441h23.059c0.124,0,0.24-0.027,0.361-0.035 c0.238,0.018,0.478,0.035,0.721,0.035c5.075,0,9.188-4.113,9.188-9.188C43.918,33.215,41.5,29.9,38.089,28.557z M17.699,7.314v7.165 h-7.287L17.699,7.314z M10.588,42.738c-0.49,0-0.889-0.398-0.889-0.889V17.089h8.125c0,0,1,0.056,1.832-0.722 c0.833-0.777,0.667-1.554,0.667-1.554l0.012-7.551h13.312c0.49,0,0.888,0.398,0.888,0.888v19.773 c-4.984,0.105-8.994,4.17-8.994,9.18c0,2.125,0.728,4.078,1.941,5.635H10.588z M34.729,44.07c-3.842,0-6.968-3.125-6.968-6.967 s3.126-6.969,6.968-6.969c3.843,0,6.968,3.127,6.968,6.969S38.572,44.07,34.729,44.07z"/> <path fill="#FFFFFF" d="M31.76,21.586c0,1.165-0.945,2.11-2.11,2.11H14.216c-1.165,0-2.11-0.945-2.11-2.11l0,0c0-1.165,0.945-2.109,2.11-2.109 h15.434C30.814,19.477,31.76,20.421,31.76,21.586L31.76,21.586z"/> <path fill="#FFFFFF" d="M24.653,35.799c0,1.164-0.945,2.109-2.11,2.109h-8.328c-1.165,0-2.11-0.945-2.11-2.109l0,0c0-1.166,0.945-2.109,2.11-2.109 h8.328C23.708,33.689,24.653,34.633,24.653,35.799L24.653,35.799z"/> <path fill="#FFFFFF" d="M27.873,28.691c0,1.166-0.944,2.109-2.109,2.109H14.216c-1.165,0-2.11-0.943-2.11-2.109l0,0c0-1.164,0.945-2.109,2.11-2.109 h11.548C26.929,26.582,27.873,27.527,27.873,28.691L27.873,28.691z"/> <polygon fill="#FFFFFF" points="34.63,30.801 29.75,37.447 32.894,37.447 32.894,42.479 34.63,42.479 36.367,42.479 36.367,37.447 39.5,37.447 "/> </svg> </div>';
var request_icon = '<div class="btn-icon-holder"><?xml version="1.0" encoding="utf-8"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"> <svg class="btn-icon" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="50px" height="50px" viewBox="0 0 50 50" enable-background="new 0 0 50 50" xml:space="preserve"> <path fill="#FFFFFF" d="M38.089,28.557V8.15c0-2.453-1.988-4.441-4.441-4.441H18.509c-2.146,0-2.813,0.592-2.813,0.592l-8.883,8.735 c-1.037,1.185-0.667,3.257-0.667,3.257V41.85c0,2.453,1.989,4.441,4.442,4.441h23.059c0.124,0,0.24-0.027,0.361-0.035 c0.238,0.018,0.478,0.035,0.721,0.035c5.075,0,9.188-4.113,9.188-9.188C43.918,33.215,41.5,29.9,38.089,28.557z M17.699,7.314v7.165 h-7.287L17.699,7.314z M10.588,42.738c-0.49,0-0.889-0.398-0.889-0.889V17.089h8.125c0,0,1,0.056,1.832-0.722 c0.833-0.777,0.667-1.554,0.667-1.554l0.012-7.551h13.312c0.49,0,0.888,0.398,0.888,0.888v19.773 c-4.984,0.105-8.994,4.17-8.994,9.18c0,2.125,0.728,4.078,1.941,5.635H10.588z M34.729,44.07c-3.842,0-6.968-3.125-6.968-6.967 s3.126-6.969,6.968-6.969c3.843,0,6.968,3.127,6.968,6.969S38.572,44.07,34.729,44.07z"/> <path fill="#FFFFFF" d="M31.76,21.586c0,1.165-0.945,2.11-2.11,2.11H14.216c-1.165,0-2.11-0.945-2.11-2.11l0,0 c0-1.165,0.945-2.109,2.11-2.109h15.434C30.814,19.477,31.76,20.421,31.76,21.586L31.76,21.586z"/> <path fill="#FFFFFF" d="M24.653,35.799c0,1.164-0.945,2.109-2.11,2.109h-8.328c-1.165,0-2.11-0.945-2.11-2.109l0,0 c0-1.166,0.945-2.109,2.11-2.109h8.328C23.708,33.689,24.653,34.633,24.653,35.799L24.653,35.799z"/> <path fill="#FFFFFF" d="M27.873,28.691c0,1.166-0.944,2.109-2.109,2.109H14.216c-1.165,0-2.11-0.943-2.11-2.109l0,0 c0-1.164,0.945-2.109,2.11-2.109h11.548C26.929,26.582,27.873,27.527,27.873,28.691L27.873,28.691z"/><path fill="#FFFFFF" d="M37.674,32.061c-0.721-0.639-1.691-0.957-2.912-0.957c-1.161,0-2.097,0.315-2.811,0.945 c-0.715,0.631-1.099,1.397-1.154,2.301l1.952,0.242c0.136-0.631,0.386-1.1,0.749-1.408c0.363-0.307,0.814-0.461,1.354-0.461 c0.559,0,1.004,0.147,1.335,0.442c0.33,0.295,0.496,0.649,0.496,1.063c0,0.298-0.094,0.569-0.28,0.817 c-0.121,0.156-0.492,0.486-1.112,0.991c-0.62,0.504-1.034,0.957-1.24,1.361c-0.208,0.403-0.311,0.918-0.311,1.544 c0,0.061,0.002,0.229,0.008,0.507h1.929c-0.01-0.586,0.039-0.992,0.148-1.219c0.108-0.227,0.387-0.527,0.835-0.9 c0.868-0.722,1.435-1.291,1.699-1.71c0.265-0.418,0.397-0.862,0.397-1.331C38.757,33.441,38.396,32.698,37.674,32.061z"/> <circle fill="#FFFFFF" cx="34.776" cy="41.845" r="1.393"/></svg> </div>';
