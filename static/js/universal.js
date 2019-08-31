/* Get college and high school data */
let college_list = [];
let college_data = {};
$.get("/colleges", function (data) {
  college_data = $.parseJSON(data);
  college_list = Object.keys(college_data);
});

jQuery.ui.autocomplete.prototype._resizeMenu = function () {
  let ul = this.menu.element;
  ul.outerWidth(this.element.outerWidth());
};

/* Function retrieves top 5 schools that match a query - used for autocomplete */
let cached_results = {};

function get_res(request, response) {
  console.log(cached_results);
  let results = new Set();
  let stopwords = ['of', 'at', 'and', 'the', 'for'];
  let query = request.term.toLowerCase().trim();
  if (query in cached_results) {
    response(cached_results[query]);
    return;
  }

  let terms = query.split(' ').filter(Boolean);
  let second = [];
  let third = [];
  let fourth = [];
  for (let college of college_list) {
    // Format College
    let acronym = college.toLowerCase().match(/\b(?!(?:of|at|and|the|for)[^a-zA-Z0-9])(\w)/g).join('');
    let shortened = college.toLowerCase().match(/\b(?!(?:of|at|and|the|for)[^a-zA-Z0-9])(\w+)/g).join(' ');

    // Get results in order of relevance
    if (acronym === query || acronym === query.replace(/\s/g, ''))
      results.add(college);
    else if (college.toLowerCase().startsWith(query) || shortened.startsWith(query))
      second.push(college);
    else if (acronym.startsWith(query))
      third.push(college);
    // Check acronym versions of query
    else if (terms.length > 1 && acronym.startsWith(terms[0])) {
      let parsed_college = college.toLowerCase().match(/\b(\w+)/g);
      let shift_parsed = parsed_college.slice();
      for (let i = 0; i < terms[0].length;) {
        if (shift_parsed.length === 0)
          break;
        if (!stopwords.includes(shift_parsed[0]))
          i++;
        shift_parsed.splice(0, 1);
      }
      let remaining_college = shift_parsed.join(' ').trim();
      let remaining_query = query.substring(terms[0].length + 1);

      if (shift_parsed.length === terms.length - 1 && remaining_college.includes(remaining_query)) {
        third.push(college);
      } else if (remaining_college.includes(remaining_query)) {
        fourth.push(college);
      }
    }
    else {
      let allin = true;
      for (let term of terms) {
        let regex = new RegExp("\\b" + term, 'g');
        if (!college.toLowerCase().match(regex))
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
    cached_results[query] = Array.from(results).splice(0, 5);
  response(cached_results[query]);
}

/* Helper function to focus an input field */
function focusField(elem) {
  window.setTimeout(function () {
    elem.focus();
  }, 0);
}

function linkToSchool(event, ui) {
  let school = ui.item.value;
  console.log(school);
  if (!(school in college_data))
    return false;
  let sid = college_data[school]['sid'];
  window.location.href = ("/school/" + sid);
}

/* Sidebar display for mobile devices */
function displaySidebar() {
  console.log("display");
  let sidebar = $(".sidebar");
  const ANIMATE_TIME = 300;
  if (sidebar.length > 0)
    return false;
  else {
    sidebar = $(`
        <div class='side sidebar'>
          <ul class="side sidebar-list"></ul>
        </div>`);
    $(".icon").addClass("close");
    const buttons = $(".gtbtn");
    let sidebarList = sidebar.find("ul");
    for (let button of buttons) {
      sidebarList.append(`<li class='side sidebtn-holder'>${$(button).prop('outerHTML')}</li>`);
    }
    $("body").append(sidebar)
    .append(`<div class="side sidebar empty"></div>`);
    darkenPage();
    sidebar.animate({left: "0px"},
      ANIMATE_TIME,
      function () {
        const sidebtn = $(".sidebar-icon-holder");
        sidebtn.unbind('click');
        sidebtn.click(hideSidebar);
      });
  }
}

function hideSidebar() {
  console.log("hide");
  let sidebar = $(".sidebar");
  if (sidebar.length === 0)
    return false;
  else {
    $(".icon").removeClass("close");
    sidebar.animate({left: "-325px"},
      300,
      function () {
        sidebar.remove();
        const sidebtn = $(".sidebar-icon-holder");
        sidebtn.unbind('click');
        sidebtn.click(displaySidebar);
      });
    lightenPage();
    $(".navcolor").animate({left: (-document.documentElement.clientWidth) + "px"}, 300, function () {
      $(this).remove();
    });
  }
}

function darkenPage() {
  $("#darken").fadeIn();
}

function lightenPage() {
  $("#darken").fadeOut();
}