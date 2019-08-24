$(document).ready(function() {
  showMonitoringPage();
});

function showMonitoringPage() {
  showRequests();
}


function adminRequest(path, methodType, callback) {
  let email = $("#email")[0].value;
  let sessionID = $("#sessionID")[0].value;
  $.ajax({
    method: methodType,
    url: path,
    headers: {"email": email, "sessionID": sessionID},
    success: callback,
    error: (res, status, xhr) => {console.log(res, status, xhr)}
  });
}


function showRequests() {
  let postsHolder = $("ul.posts");
  adminRequest("/admin/requests", "GET", function(posts) {
    console.log(posts);
    postsHolder.empty();
    for (let [pid, post_data] of Object.entries(posts))
    {
      console.log(post_data);
      let post = createRequestHolder(post_data, pid);
      postsHolder.append(post);
    }
  });
}

function createRequestHolder(request_data, rid) {
  let request = $(`
    <li class='post-holder' id="${rid}">
      <div class="post-info">
        <span class="post-user">Posted by ${request_data["uid"]}</span>
        <span class="post-time">${moment(new Date(request_data["time"])).fromNow()}</span>
        <span>to SID ${request_data["sid"]}</span>
      </div>
      <div class="post-content">
        <div class="post-title">${request_data["title"]}</div>
        <div class="post-description">${request_data["description"]}</div>
      </div>
      <div class="post-controls">
        <a class="post-btn" id="approve-${rid}">Approve</a>
        <a class="post-btn" id="deny-${rid}">Deny</a>
      </div>
    </li>
  `);
  request.on("click", `#approve-${rid}`, ()=>{
    console.log("Approved " + rid);
    adminRequest(`/admin/approve/${rid}`, "GET", (res) => console.log(res));
  });
  request.on("click", `#deny-${rid}`, ()=>{
    console.log("Deny " + rid);
    adminRequest(`/admin/deny/${rid}`, "GET", (res) => console.log(res));
  });
  return request;
}