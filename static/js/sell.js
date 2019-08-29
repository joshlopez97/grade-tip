let course_data = {};
$.get("/getcolleges", function(data) {
  course_data = $.parseJSON(data);
});
$(document).ready(function() {
  $(window).on('load',function(){
    setSchoolValue();
    $("#school").on("focus", function() {
      $(this).autocomplete("search");
    }).autocomplete({
      select: function(event, ui){
        $(this).val(ui.item.value);
        $(this).blur();
        focusField($("#cid"));
      },
      source: get_res,
      appendTo: '#school-holder'
    });
    $("#cid").on("focus", function() {
      $(this).autocomplete("search");
    }).autocomplete({
        select: function(event, ui){
          $(this).val(ui.item.value);
          $(this).blur();
        },
        source: function(request, response) {
          let entered_college = $("#school").val();
          let query = request.term.toUpperCase().trim();
          if (query.length > 0 && college_list.includes(entered_college) && Array.isArray(course_data[entered_college]['courses'])) {
            let course_list = course_data[entered_college]['courses'];
            let results = new Set();
            let priority = {};
            for (let course of course_list) {
              if (course.toUpperCase().startsWith(query)) {
                results.add(course);
                if (results.length >= 5)
                  return;
              }
              else if (query.length > 1 && query.length <= course.length) {
                let orderedFound = 0;
                let matches = [];
                for (let i = 0; i < course.length && orderedFound < query.length; ++i) {
                  if (course.charAt(i).toUpperCase() === query.charAt(orderedFound))
                    ++orderedFound;
                  let findchar = course.indexOf(query.charAt(matches.length))
                  while (findchar !== -1) {
                    if (!matches.includes(findchar)) {
                      matches.push(findchar);
                      break;
                    }
                    findchar = course.indexOf(query.charAt(matches.length), findchar + 1);
                  }
                }
                let weight = (course.length - matches.length) + 1;

                if (orderedFound === query.length && course.toUpperCase().startsWith(query.charAt(0))) {
                  if (0 in priority)
                    priority[0].push(course);
                  else
                    priority[0] = [course];
                }
                else if (weight < 4) {
                  if (weight in priority)
                    priority[weight].push(course);
                  else
                    priority[weight] = [course];
                }
              }
            }
            maxres:
              for (let tier of Object.values(priority)) {
                if (tier.length === 0)
                  continue;
                for (let item of tier) {
                  results.add(item);
                  if (results.size >= 5)
                    break maxres;
                }
              }

            response(Array.from(results).splice(0, 5));
          }
        },
        appendTo: '#course-holder'
    });
  });
});

function setSchoolValue() {
  let sid = $("#sid")[0].value;
  console.log(sid);
  if (!!sid && sid.match(/^\d+$/))
  {
    let schoolInput = $("#school");
    let targetSid = parseInt(sid);
    console.log(targetSid);
    for (let college of college_list) {
      console.log(college_data[college]["sid"]);
      if (college_data[college]["sid"] === targetSid)
        return schoolInput[0].value = college;
    }
  }

}