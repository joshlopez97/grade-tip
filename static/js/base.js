$(document).ready(function() {
  /* Resize elements if user changes screen width */
  $(window).resize(function() {
    if ($(".navcolor").length > 0)
      $(".navcolor").width(document.documentElement.clientWidth)
    if (document.documentElement.clientWidth <= 975) {
      if ($(".navbar-list").find("li.usearch-mobile-holder").length > 0) {
        $("#usearch-mobile").css('width',(document.documentElement.clientWidth - 100) + "px");
        $("#usearch-mobile-holder").css('width',(document.documentElement.clientWidth - 55) + "px");
      }
    } else {
      if ($(".navbar-list").find("li.usearch-mobile-holder").length > 0) {
        $(".navbar-brand").css('display','inline-block');
        $("li.usearch-mobile-holder").remove();
      }
    }
  });
  /* (Mobile only) Event handlers for showing hidebar and showing search bar */
  $(".sidebar-icon-holder").click(displaySidebar);

  /* (Mobile only) Hide sidebar and search bar when user clicks away */
  $("#darken").click(function(e){
    hideSidebar();
  });
  $(".usearch-mobile-holder, .usearch-mobile, .usearch-bar, .navbar, .navbar-list, .side, .gtbtn, div.side.sidebar").click(function(e){e.stopPropagation();});

  /* Autocomplete school search bar */
  $("#usearch").autocomplete({
    source: get_res, 
    open: function( event, ui ) {
      $('.ui-autocomplete.ui-menu').addClass('usearch');
      $('.ui-menu-item').addClass('usearch')
    },
    appendTo:"#usearch-holder",
    select: linkToSchool
  });
  $(window).on('load', function() {
    console.log('base.js window loaded')
  });
});