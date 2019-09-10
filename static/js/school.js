let url = [location.protocol, '//', location.host, location.pathname].join('');
$(document).ready(function() {
  checkIfUserCreatedPost();
  show_school_page(true);
});

window.onpopstate = function(e){
  console.log(e);
  console.log(e.state);
  if (!!e.state && e.state.page === 'school') {
    show_school_page();
  }
  else if (!!e.state && e.state.page === 'details') {
    show_post(e.state.post_data, e.state.pid, false);
  }

};

function checkIfUserCreatedPost()
{
  let created = $("#created")
  if (created[0].value === "1")
  {
    showRequestProcessedNotice();
    created[0].value = "0";
  }
}

function get_school_id() {
  return $("#sid")[0].value;
}

function changeUrlToSchool(sid) {
  window.history.pushState({"page": "school"}, "", `/school/${sid}`);
}

function show_school_page(pushState=false) {
  let sid = get_school_id();
  if (pushState)
    changeUrlToSchool(sid);
  ensurePostsAndBannerAreVisible();
  attachEventListeners(sid);
  showPosts(sid);
}

function ensurePostsAndBannerAreVisible() {
  $(".back-btn").css("display", "none");
  $("div.large-post-holder").css("display", "none");

  $(".panel-icon-holder").css("display", "table-cell");
  $(".banner-title").css("display", "table-cell");
  $(".school-page-controls").css("display", "block");
  $("ul.posts").css("display", "block");
}

function attachEventListeners(sid) {
  $("#create-post").click(showPostTypesDropDown);
  $("#create-text-post").click(showNewPostPopup);
  $("#sell-document").click(()=>window.location = `/upload?sid=${sid}`)
}

function showPostTypesDropDown() {
  $(".post-types-list").toggleClass("show");
}

function validate_form_data(form_data) {
  if (non_empty(form_data["title"]) && non_empty(form_data["description"]))
    return form_data["title"].length < 256 && form_data["description"].length < 2000;
  return false;
}

function non_empty(data) {
  return typeof data !== 'undefined' && data !== null && (!!!data.length || data.length > 0);
}

function showPosts(sid) {
  let postsHolder = $("ul.posts");
  $.post("/school/posts", {"sid":sid}, function(data) {
    let posts = $.parseJSON(data);
    postsHolder.empty();
    let sortedPosts = Object.entries(posts);
    sortedPosts.sort(function(a, b){
      return new Date(b[1].time) - new Date(a[1].time);
    });
    for (let [pid, post_data] of sortedPosts)
    {
      console.log(post_data);
      if (validate_post_data(post_data)) {
        postsHolder.append(createPostHolder(post_data, pid));
      }
    }
    if (location.pathname.match("/[0-9]*/[0-9]*")) {
      let path = location.pathname;
      let pid = path.substring(path.lastIndexOf('/') + 1);
      show_post(posts[pid], pid);
    }
  });
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
  else
    post = getListingHolder(post_data, pid);
  post.append(getLikeReplyControls(pid));
  post.click(() => show_post(post_data, pid));
  return post;
}

function likePost(pid)
{
  $(`#like-${pid}`).toggleClass("clicked");
}

function showNewPostPopup()
{
  let popup = createPopup("Create Text Post", "Submit");
  addField(popup, "Title", "text");
  addTextBox(popup, "Description");
  addSubmitAction(popup, (e)=>{
    e.preventDefault();
    let formData = getFormData(popup);
    let parsedFormData = {"title": formData["title"], "description": formData["description"]};
    console.log(formData);
    if (validate_form_data(parsedFormData))
    {
      console.log(window.location);
      $.post(window.location, parsedFormData, (res, status, xhr) => {
        if (!!res && res['requested'] === true)
        {
          destroyPopup();
          if (res['created'] === true)
          {
            location.reload();
          }
          else
          {
            showRequestProcessedNotice();
          }
        }
        else
        {
          console.log(res);
        }

      });
    }
    else
    {
      console.log("validation failed");
    }
    return false;
  });
  focusField($("input[name='Title']"));
}