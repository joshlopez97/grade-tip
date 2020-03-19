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

function getNumPagesLabel(numPages) {
  if (typeof numPages === 'undefined' || numPages === null || numPages === 0)
    return "";
  if (numPages === "1")
    return "1 page";
  return numPages + " pages";
}

function getReplyHolder(pid) {
  return $(`
    <form id="make-reply" action="/reply" method="post">
      <input type="hidden" name="content_id" value="${pid}">
      <input type="hidden" name="school_id" value="${getSchoolId()}">
      <textarea id="reply-text" name="text" maxlength="2000"></textarea>
      <input id="reply-submit" type="submit" value="Submit">
    </form>
  `);
}

function getListingHolder(post_data, pid) {
  return $(`
    <li class='post-holder' id="${pid}">
      <div class="post-info">
        <span class="post-user">Posted by ${post_data["uid"]}</span>
        <span class="post-time">${moment(new Date(post_data["time"])).fromNow()}</span>
      </div
      <div class="post-thumbnail-holder">
        <img class="post-thumbnail" src="${post_data["preview"]}"
      </div>
      <div class="post-content">
        <div class="post-title">${post_data["title"]}</div>
        <div class="post-description">Course: <i>${post_data["course"]}</i></div>
        <div class="post-description">${getNumPagesLabel(post_data["numPages"])}</div>
      </div>
    </li>
  `);
}

function addCharCounter(inputBox) {
  let charCounter = $(`<span class='char-counter'>0 / 2000 characters</span>`);
  inputBox.on("input", () => {
    charCounter.text(`${inputBox.val().length} / 2000 characters`);
  });
  charCounter.insertAfter(inputBox);
}

function replyToPost(pid) {
  console.log("reply");
  let replyInputBox = getReplyHolder(pid).insertAfter(`#${pid}`).find("#reply-text");
  replyInputBox.focus();
  addCharCounter(replyInputBox);
}

function getLikeReplyControls(pid) {
  let controls = $(`
    <div class="post-controls">
      <a id="like-${pid}" class="post-btn">Like</a>
      <a id="reply-${pid}" class="post-btn">Reply</a>
    </div>
  `);
  controls.on("click", `#like-${pid}`, (e) => {
    e.stopPropagation();
    likePost(pid);
  });
  controls.on("click", `#reply-${pid}`, (e) => {
    e.stopPropagation();
    replyToPost(pid);
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
  controls.on("click", `#approve-${pid}`, () => {
    console.log("Approved " + pid);
    adminRequest(`/admin/approve/${pid}`, "GET", (res) => console.log(res));
  });
  controls.on("click", `#deny-${pid}`, () => {
    console.log("Deny " + pid);
    adminRequest(`/admin/deny/${pid}`, "GET", (res) => console.log(res));
  });
  return controls;
}

function showRequestProcessedNotice() {
  notice("Your request has been received and will be processed by our moderators shortly.", 4000);
}
