function getTextPostHolder(post_data, pid) {
  return $(`
    <li class='post-holder' id="${pid}">
      <div class="post-info">
        <span class="post-user">Posted by ${post_data["uid"]}</span>
        <span class="post-time">${moment(new Date(post_data["time"])).fromNow()}</span>
      </div>
      <div class="post-content">
        <div class="post-title">${post_data["title"]}</div>
        <div class="post-description">${post_data["description"]}</div>
      </div>
    </li>
  `);
}

function getListingHolder(post_data, pid) {
  return $(`
    <li class='post-holder' id="${pid}">
      <div class="post-info">
        <span class="post-user">Posted by ${post_data["uid"]}</span>
        <span class="post-time">${moment(new Date(post_data["time"])).fromNow()}</span>
      </div>
      <div class="post-thumbnail-holder">
        <img class="post-thumbnail" src="${post_data["preview"]}"
      </div>
      <div class="post-content">
        <div class="post-title">${post_data["title"]}</div>
        <div class="post-description">Course: <i>${post_data["course"]}</i></div>
      </div>
    </li>
  `);
}

function getLikeReplyControls(pid) {
  let controls = $(`
    <div class="post-controls">
      <a id="like-${pid}" class="post-btn">Like</a>
      <a id="reply-${pid}" class="post-btn">Reply</a>
    </div>
  `);
  controls.on("click", `#like-${pid}`, (e)=>{
    e.stopPropagation();
    likePost(pid);
  });
  return controls;
}

function getApproveDenyControls(pid) {
  let controls = $(`
    <div class="post-controls">
      <a class="post-btn" id="approve-${pid}">Approve</a>
      <a class="post-btn" id="deny-${pid}">Deny</a>
    </div>
  `);
  controls.on("click", `#approve-${pid}`, ()=>{
    console.log("Approved " + pid);
    adminRequest(`/admin/approve/${pid}`, "GET", (res) => console.log(res));
  });
  controls.on("click", `#deny-${pid}`, ()=>{
    console.log("Deny " + pid);
    adminRequest(`/admin/deny/${pid}`, "GET", (res) => console.log(res));
  });
  return controls;
}
