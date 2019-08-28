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
  let request;
  if (request_data["requestType"] === "listing")
    request = getListingHolder(request_data, rid);
  else
    request = getTextPostHolder(request_data, rid);
  request.find(".post-info").append(`<span>to SID ${request_data["sid"]}</span>`);
  request.append(getApproveDenyControls(rid));
  return request;
}