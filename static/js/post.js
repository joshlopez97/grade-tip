function show_post(post_data, pid, pushState=true)
{
  console.log(post_data);
  $(".school-page-controls").css("display", "none");
  $("ul.posts").css("display", "none");
  if (pushState)
    changeURLtoPost(post_data, pid);
  displayBackBtnInBanner(post_data, pid);
  populatePostData(post_data);
}

function changeURLtoPost(post_data, pid){
  let sid = get_school_id();
  window.history.pushState({"page": "details", "pid": pid, "post_data": post_data}, "", `/school/${sid}/${pid}`);
}

function displayBackBtnInBanner()
{
  $(".panel-icon-holder").css("display", "none");
  $(".banner-title").css("display", "none");
  let backBtn = $(".back-btn");
  backBtn.css("display", "table-cell");
  backBtn.click(() => {
    let sid = get_school_id();
    window.history.pushState({"page": "school"}, "", `/school/${sid}`);
    show_school_page(false);
  });
}

function populatePostData(post_data)
{
  let post_holder = $("div.large-post-holder");
  post_holder.css("display", "block");
  post_holder.empty().append(`
    <div class="post-info">
      <span class="post-user">Posted by ${post_data["uid"]}</span>
      <span class="post-time">${moment(post_data["time"]).fromNow()}</span>
    </div>
    <div class="post-content">
      <div class="post-title">${post_data["title"]}</div>
      <div class="post-description">${post_data["description"]}</div>
    </div>
    <div class="post-controls">
      <a class="post-btn">Like</a>
      <a class="post-btn">Reply</a>
    </div>
  `);
}

function getComments(pid, callback)
{
  $.post("/comments");
}