$(document).ready(function(){
  animateMainText();
  $(".learn-more-btn").click(() => {
    $("html, body").animate({'scrollTop': $(".main-holder").outerHeight() - $(".navbar").outerHeight() }, 1000);
  });
});
function animateMainText() {
  let words = ['classes', 'homework', 'projects', 'quizzes', 'essays'];
  let colors = ['#be46a2', '#ad79df', '#df79ac', '#be46a2', '#ad79df'];
  swapInWords(words, colors);
}

function swapInWords(words, colors)
{
  if (words.length > 1)
  {
    setTimeout(() => {
      swapInWords(words, colors);
      let word = words.pop();
      let swap = $("#big-text-swap");
      swap.removeClass("appear");
      swap.addClass("disappear");
      let newText = $(`<div id="big-text-swap" class="appear">${word}</div>`).css("color", colors.pop());
      setTimeout(() => {
        $("#big-text-swap.disappear").remove();
        $(".big-text").append(newText);
      }, 300);
    }, 1500, ()=>swapInWords(words, colors));
  }
}
