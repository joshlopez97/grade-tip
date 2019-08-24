$(document).ready(function() {
  showMonitoringPage();
});

function showMonitoringPage() {
  showRequests();
}


function showRequests() {
  let postsHolder = $("ul.posts");
  $.get("/admin/requests", function(posts) {
    console.log(posts);
    postsHolder.empty();
    postsHolder.append(createRequestHolder("Title", "Description preview goes here", "User", new Date()));
    for (let [pid, post_data] of Object.entries(posts))
    {
      console.log(post_data)
      let post = createRequestHolder(post_data, pid);
      post.click(() => showPost(post_data, pid));
      postsHolder.append(post);
    }
  });
}

function createRequestHolder(post_data, pid) {
  return $(`
    <li class='post-holder' id="${pid}">
      <div class="post-info">
        <span class="post-user">Posted by ${post_data["uid"]}</span>
        <span class="post-time">${moment(new Date(post_data["time"])).fromNow()}</span>
        <span>to SID ${post_data["sid"]}</span>
      </div>
      <div class="post-content">
        <div class="post-title">${post_data["title"]}</div>
        <div class="post-description">${post_data["description"]}</div>
      </div>
      <div class="post-controls">
        <a class="post-btn">Approve</a>
        <a class="post-btn">Delete</a>
      </div>
    </li>
  `);
}