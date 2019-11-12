function showPost(post_data, pid, pushState=true)
{
  $(".school-page-controls").css("display", "none");
  $("ul.posts").css("display", "none");
  if (pushState) {
    changeURLtoPost(post_data, pid);
  }
  window.document.title = `${post_data["title"]} | GradeTip`;
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
    showSchoolPage(true);
  });
}

function populatePostData(post_data)
{
  let post_holder = $("div.large-post-holder");
  post_holder.css("display", "block");
  post_holder.empty();
  if (post_data["postType"] === 'listing')
    post_holder.append(listingDetails(post_data));
  else
    post_holder.append(textPostDetails(post_data));
}

function textPostDetails(post_data)
{
  return $(`
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

function listingDetails(post_data)
{
  return $(`
    <div class="post-info">
      <span class="post-user">Posted by ${post_data["uid"]}</span>
      <span class="post-time">${moment(post_data["time"]).fromNow()}</span>
    </div>
    <div class="post-content">
      <div class="post-title">${post_data["title"]}</div>
      <div class="post-description">${post_data["course"]}</div>
    </div>
    <div class="post-preview-holder">
      <img class="post-preview" src="${post_data["preview"]}"
    </div>
    <div class="post-controls">
      <a class="post-btn">Like</a>
      <a class="post-btn">Reply</a>
    </div>
  `);
}