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
      let post = createRequestHolder(post_data["title"], post_data["description"], post_data["uid"], new Date(post_data["time"]), pid);
      post.click(() => showPost(post_data, pid));
      postsHolder.append(post);
    }
  });
}

function createRequestHolder(title, description, user, time, pid) {
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