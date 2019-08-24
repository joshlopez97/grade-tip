function showPost(post_data, pid)
{
  console.log(post_data);
  $(".school-page-controls").css("display", "none");
  $("ul.posts").css("display", "none");
  changeURLtoPost(pid);
  displayBackBtnInBanner();
  populatePostData(post_data);
}

function changeURLtoPost(pid){
   window.history.pushState({"state": "post"}, "", location.pathname + "/" + pid);
}

function displayBackBtnInBanner()
{
  $(".panel-icon-holder").css("display", "none");
  $(".banner-title").css("display", "none");
  let backBtn = $(".back-btn");
  backBtn.css("display", "table-cell");
  backBtn.click(() => {
    let path = location.pathname;
    window.history.pushState({"school": "school"}, "", "/school/" + $("#sid")[0].value);
    showSchoolPage();
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