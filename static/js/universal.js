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

function bold(str) {
  return `<span class="ui-autocomplete-term">${str}</span>`;
}

function format_acronym_match(result, query) {
  let words = [];
  let result_words = result.split(' ');
  for (let word of result_words) {
    let firstLetter = word.charAt(0);
    if (word.length > 0 && query.includes(firstLetter.toLowerCase()))
      words.push(`${bold(firstLetter)}${word.substring(1)}`);
    else
      words.push(word);
  }
  return words.join(' ');
}

function format_partial_match(result, terms) {
  for (let term of terms) {
    result = result.replace(new RegExp(`(^${term}|\\s${term})`, "gi"), bold("$1"));
  }
  return result;
}


function search(request, response) {
  let results = new Set();
  let stopwords = ['of', 'at', 'and', 'the', 'for'];
  let query = request.term.toLowerCase().trim();
  if (query in cached_results) {
    response(cached_results[query]);
    return;
  }

  let terms = query.split(' ').filter(Boolean);
  let first = [];
  let second = [];
  let third = [];
  let fourth = [];
  for (let i = 0; i < college_list.length; i++) {
    let college = college_list[i];
    let sid = college_data[college]["sid"];
    // Format College
    let lowerCollege = college.toLowerCase();
    let acronym = lowerCollege.match(/\b(?!(?:of|at|and|the|for)[^a-zA-Z0-9])(\w)/g).join('');
    let shortened = lowerCollege.match(/\b(?!(?:of|at|and|the|for)[^a-zA-Z0-9])(\w+)/g).join(' ');

    // Get results in order of relevance
    if (acronym === query || acronym === query.replace(/\s/g, '')) {
      const formatted_college = format_acronym_match(college, query);
      first.push([sid, formatted_college]);
    }
    else if (lowerCollege.startsWith(query) || shortened.startsWith(query)) {
      const formatted_college = format_partial_match(college, terms);
      second.push([sid, formatted_college]);
    }
    else if (acronym.startsWith(query)) {
      const formatted_college = format_acronym_match(college, query);
      third.push([sid, formatted_college]);
    }
    // Check acronym versions of query
    else if (terms.length > 1 && acronym.startsWith(terms[0])) {
      // continuously remove letters from college name to handle partial acronym match
      // ex: for the school "Univerity of California Irvine",
      // "uc" matches "University of California" leaving "Irvine" remaining in shift_parsed
      let parsed_college = college.match(/\b(\w+)/g);
      let shift_parsed = parsed_college.slice();
      let removed = [];
      for (let i = 0; i < terms[0].length;) {
        if (shift_parsed.length === 0)
          break;
        if (!stopwords.includes(shift_parsed[0].toLowerCase()))
          i++;
        removed.push(shift_parsed[0].slice());
        shift_parsed.splice(0, 1);
      }

      let remaining_college = shift_parsed.join(' ').trim();
      let remaining_query = query.substring(terms[0].length + 1);

      if (new RegExp(remaining_query, "gi").test(remaining_college)) {
        const formatted_college = format_acronym_match(removed.join(" "), terms[0]) + " " +
          format_partial_match(shift_parsed.join(" "), terms.slice(1, terms.length));
        if (shift_parsed.length === terms.length - 1) {
          third.push([sid, formatted_college]);
        }
        else {
          fourth.push([sid, formatted_college]);
        }
      }
    }
  }
  for (let tier of [first, second, third, fourth]) {
    for (let school_info of tier) {
      results.add(`<span id=${school_info[0]}>${school_info[1]}</span>`);
    }
  }
  if (results.size > 0 && Object.keys(cached_results).length < 50)
    cached_results[query] = Array.from(results);
  response(cached_results[query]);
}

/* Helper function to focus an input field */
function focusField(elem) {
  window.setTimeout(function () {
    elem.focus();
  }, 0);
}

function linkToSchool(event, ui) {
  event.preventDefault();
  let school = $(ui.item.value);
  let sid = school.attr("id");
  window.location.href = ("/school/" + sid);
  return false;
}

function selectSchool(event, ui) {
  event.preventDefault();
  let sid = $(ui.item.value).attr("id");
  let school_name = "";
  for (let college_name of college_list) {
    if (`${college_data[college_name]["sid"]}` === sid) {
      school_name = college_name;
      break;
    }
  }
  return school_name;
}

/* Sidebar display for mobile devices */
function displaySidebar() {
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