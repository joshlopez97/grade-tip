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
    postsHolder.append(createPostHolder("Title", "Description preview goes here", "User", new Date()));
    for (let [pid, post_data] of Object.entries(posts))
    {
      let post = createPostHolder(post_data["title"], post_data["description"], post_data["uid"], new Date(post_data["time"]), pid);
      post.click(() => showPost(post_data, pid));
      postsHolder.append(post);
    }
  });
}

function createPostHolder(title, description, user, time, pid) {
  return $(`
    <li class='post-holder' id="${pid}">
      <div class="post-info">
        <span class="post-user">Posted by ${user}</span>
        <span class="post-time">${moment(time).fromNow()}</span>
      </div>
      <div class="post-content">
        <div class="post-title">${title}</div>
        <div class="post-description">${description}</div>
      </div>
      <div class="post-controls">
        <a class="post-btn">Like</a>
        <a class="post-btn">Reply</a>
      </div>
    </li>
  `);
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