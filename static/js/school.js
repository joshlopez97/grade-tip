let url = [location.protocol, '//', location.host, location.pathname].join('');
$(document).ready(function () {
  checkIfUserRequestedPost();
  const post_id = $("#pid").val();
  let pushState = !!!post_id || post_id.length === 0;
  showSchoolPage(pushState);
});

window.onpopstate = function (e) {
  if (!!e.state && e.state.page === 'school') {
    showSchoolPage();
  }
  else if (!!e.state && e.state.page === 'details') {
    showPost(e.state.post_data, e.state.pid, false);
  }

};

function checkIfUserRequestedPost() {
  let requested = $("#requested");
  if (requested[0].value === "1") {
    showRequestProcessedNotice();
    requested[0].value = "0";
  }
}

function get_school_id() {
  return $("#sid")[0].value;
}

function changeUrlToSchool(sid) {
  window.history.pushState({"page": "school"}, "", `/school/${sid}`);
}

function showSchoolPage(pushState = false) {
  let sid = get_school_id();
  if (pushState) {
    changeUrlToSchool(sid);
    ensurePostsAndBannerAreVisible(sid);
  }
  attachEventListeners(sid);
  getPostsForSchool(sid);
}

function ensurePostsAndBannerAreVisible(sid) {
  $(".back-btn").css("display", "none");
  $("div.large-post-holder").css("display", "none");

  $(".panel-icon-holder").css("display", "table-cell");
  $(".banner-title").css("display", "table-cell");
  $(".school-page-controls").css("display", "block");
  $("ul.posts").css("display", "block");
}

function attachEventListeners(sid) {
  $("#create-post").unbind("click").click(togglePostTypesDropDown);
  $("#create-text-post").unbind("click").click(showNewPostPopup);
  $("#sell-document").unbind("click").click(() => window.location = `/upload?sid=${sid}`)
}

function togglePostTypesDropDown() {
  $(".post-types-list").toggleClass("show");
  $(".clickaway").toggleClass("show").click(togglePostTypesDropDown);
}

function validateFormData(form_data) {
  if (non_empty(form_data["title"]) && non_empty(form_data["description"])) {
    return form_data["title"].length < 256 && form_data["description"].length < 2000;
  }
  return false;
}

function non_empty(data) {
  return typeof data !== 'undefined' && data !== null && (!!!data.length || data.length > 0);
}

function getPostsForSchool(sid) {
  const postsFromSchoolEndpoint = $("#api-school-posts").data().endpoint;
  $.post(postsFromSchoolEndpoint, {"sid": sid}, function (data) {
    let posts = $.parseJSON(data);
    showPosts(posts);
    if (location.pathname.match("/[0-9]*/(l|p)-[0-9a-zA-Z]*")) {
      console.log("pathname");
      let path = location.pathname;
      let pid = path.substring(path.lastIndexOf('/') + 1);
      showPost(posts[pid], pid);
    }
    else {
      console.log("no pathname");
    }
  });
}

function showPosts(posts) {
  const postsHolder = $("ul.posts");
  postsHolder.empty();
  let sortedPosts = Object.entries(posts);
  sortedPosts.sort(function (a, b) {
    return new Date(b[1].time) - new Date(a[1].time);
  });
  for (let [pid, post_data] of sortedPosts) {
    console.log(post_data);
    if (validate_post_data(post_data)) {
      postsHolder.append(createPostHolder(post_data, pid));
    }
  }
}

function validate_post_data(post_data) {
  return non_empty(post_data["title"]) && non_empty(post_data["time"]) && valid_date(new Date(post_data["time"])) && non_empty(post_data["uid"])
}

function valid_date(d) {
  return d instanceof Date && !isNaN(d);
}

function createPostHolder(post_data, pid) {
  let post;
  if (post_data["postType"] === "textpost") {
    post = getTextPostHolder(post_data, pid);
  }
  else {
    post = getListingHolder(post_data, pid);
  }
  post.append(getLikeReplyControls(pid));
  post.click(() => showPost(post_data, pid));
  return post;
}

function likePost(pid) {
  $(`#like-${pid}`).toggleClass("clicked");
}

function showNewPostPopup() {
  let popup = createPopup("Create Text Post", "Submit");
  addField(popup, "Title", "text");
  addTextBox(popup, "Description");
  addSubmitAction(popup, (e) => {
    e.preventDefault();
    let formData = getFormData(popup);
    let parsedFormData = {"title": formData["title"], "description": formData["description"]};
    console.log(formData);
    if (validateFormData(parsedFormData)) {
      console.log(window.location);
      $.post(window.location, parsedFormData, (res, status, xhr) => {
        if (!!res && res['requested'] === true) {
          destroyPopup();
          if (res['created'] === true) {
            location.reload();
          }
          else {
            showRequestProcessedNotice();
          }
        }
        else {
          console.log(res);
        }

      });
    }
    else {
      console.log("validation failed");
    }
    return false;
  });
  focusField($("input[name='Title']"));
}