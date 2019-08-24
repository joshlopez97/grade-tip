let url = [location.protocol, '//', location.host, location.pathname].join('');
$(document).ready(function() {
  showSchoolPage();
  window.onpopstate = function(e){
    if(e.state){
      console.log(e.state);
    }
  };
});

function showSchoolPage() {
  let sid = $("#sid")[0].value;
  ensurePostsAndBannerAreVisible();
  attachEventListeners();
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

function attachEventListeners() {
  $("#create-post").click(showNewPostPopup);
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
  $.post("/posts_by_sid", {"sid":sid}, function(data) {
    console.log(data);
    let posts = $.parseJSON(data);
    postsHolder.empty();
    for (let [pid, post_data] of Object.entries(posts))
    {
      if (validate_post_data(post_data)) {
        postsHolder.append(createPostHolder(post_data, pid));
      }
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
  let post = $(`
    <li class='post-holder' id="${pid}">
      <div class="post-info">
        <span class="post-user">Posted by ${post_data["uid"]}</span>
        <span class="post-time">${moment(new Date(post_data["time"])).fromNow()}</span>
      </div>
      <div class="post-content">
        <div class="post-title">${post_data["title"]}</div>
        <div class="post-description">${post_data["description"]}</div>
      </div>
      <div class="post-controls">
        <a id="like-${pid}" class="post-btn">Like</a>
        <a id="reply-${pid}" class="post-btn">Reply</a>
      </div>
    </li>
  `);
  post.click(() => showPost(post_data, pid)).on("click", `#like-${pid}`, (e)=>{
    e.stopPropagation();
    likePost(pid);
  });
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
        console.log(res);
        console.log(status);
        console.log(xhr);
      });
    }
    else
    {
      console.log("validation failed");
    }
    return false;
  });
}