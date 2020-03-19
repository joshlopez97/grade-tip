function showPost(post_data, pid, pushState = true) {
  $(".school-page-controls").css("display", "none");
  $("ul.posts").css("display", "none");
  if (pushState) {
    changeURLtoPost(post_data, pid);
  }
  window.document.title = `${post_data["title"]} | GradeTip`;
  displayBackBtnInBanner(post_data, pid);
  populatePostData(post_data);
}

function getReplies(pid, callback) {
  const repliesEndpoint = $("#api-content-replies").data().endpoint;
  console.log(repliesEndpoint);
  $.ajax({
    type: "get",
    url: repliesEndpoint,
    success: callback,
    error: function(xhr) {
      console.log("Something went wrong", xhr);
    }
});
}

function changeURLtoPost(post_data, pid) {
  let sid = getSchoolId();
  window.history.pushState({"page": "details", "pid": pid, "post_data": post_data}, "", `/school/${sid}/${pid}`);
}

function displayBackBtnInBanner() {
  $(".panel-icon-holder").css("display", "none");
  $(".banner-title").css("display", "none");
  $(".large-post-holder").css("display", "block");
  let backBtn = $(".back-btn");
  backBtn.css("display", "table-cell");
  backBtn.click(() => {
    showSchoolPage(true);
  });
}

function createRepliesSection(replies) {
  console.log("replies");
  console.log(typeof replies);
  let sortedReplies = Object.entries(replies);
  sortedReplies.sort(function (a, b) {
    return new Date(b[1].time) - new Date(a[1].time);
  });
  let repliesHolder = $("#post-replies-container");
  for (let [pid, post_data] of sortedReplies) {
    console.log(post_data);
    repliesHolder.append(createPostHolder(post_data, pid));
  }
}

function populatePostData(post_data) {
  let postHolder = $("div#large-post-content");
  postHolder.css("display", "block");
  postHolder.empty();
  if (post_data["postType"] === 'listing') {
    postHolder.append(listingDetails(post_data));
  }
  else {
    postHolder.append(textPostDetails(post_data));
  }
  getReplies(pid, function (res) {
    const jsonData = JSON.parse(res);
    postHolder.append(createRepliesSection(jsonData));
  });
}

function textPostDetails(post_data) {
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

function listingDetails(post_data) {
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