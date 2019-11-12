$(document).ready(function () {
  setupPage();
});

function populateSchoolResults(query, type) {
  const MAX_RESULTS = 3;
  let schoolResults = search_college_names(query);
  let schoolsHolder = $("#school-results");
  if (type === "all" && schoolResults.length > MAX_RESULTS) {
    schoolResults = schoolResults.slice(0, MAX_RESULTS);
    $(`<a class="see-more-btn" href="/search?query=${query}&type=schools">See more</a>`).insertAfter(schoolsHolder);
  }

  for (let result of schoolResults) {
    let schoolInfo = $(result);
    let schoolID = schoolInfo.attr("id"),
      schoolData = {name: schoolInfo.text(), formattedName: result};
    schoolsHolder.append(schoolResultHolder(schoolData, schoolID));
  }
  $("#schools-container").addClass("show");
}

function setupPage() {
  const query = $("#query-value").val(),
    type = $("#type-value").val();
  if (type !== 'schools') {
    populatePostResults(query);
  }
  if (type !== 'posts') {
    if (college_list.length === 0) {
      get_college_data(() => populateSchoolResults(query, type));
    }
    else {
      populateSchoolResults(query, type);
    }
  }
}

function populatePostResults(query) {
  const uri = `${$("#api-content-search").data().endpoint}?query=${query}`,
    resultsHolder = $("#post-results");
  $.get(uri, function (resp) {
    if (!!resp && resp.length > 0) {
      let results = resp;
      console.log(resp);
      resultsHolder.empty();
      results.sort(function (a, b) {
        return new Date(b[1].time) - new Date(a[1].time);
      });
      for (let post_data of results) {
        resultsHolder.append(createPostHolder(post_data));
      }
      $("#posts-container").addClass("show");
    }
    else {
      resultsHolder.append(`
      <div class="no-results-msg">
        No results found
      </div>
      `);
    }
  });
}

function attachSchoolsToContainer(schools, resultsHolder) {
  console.log(schools);
}

function schoolResultHolder(schoolData, sid) {
  let schoolHolder = $(`
  <div class="school-result-holder">
    ${schoolData.formattedName}
    <input type="hidden" value="${schoolData.name}">
  </div>
  `);
  schoolHolder.click(() => linkToSchool(sid));
  return schoolHolder;
}

function createPostHolder(post_data) {
  let pid = post_data["id"];
  let post;
  if (post_data["postType"] === "textpost") {
    post = getTextPostHolder(post_data, pid);
  }
  else {
    post = getListingHolder(post_data, pid);
  }
  post.click(() => showPost(post_data, pid));
  return post;
}

function showPost(post_data, pid) {
  window.location = `/school/${post_data.sid}/${pid}`;
}