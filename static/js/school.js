$(document).ready(function() {
	console.log('document ready')
    createPage();
  	/* Change style of elements on window resize */
  	$(window).resize(function() {
      sizer();
    });
    function sizer() {
      $(".banner").width(document.documentElement.clientWidth - 12);
      if ($(".create").hasClass('clicked')) {
        /* Normal site */
        if (document.documentElement.clientWidth > 975) {
          $(".create").css({
            width: "675px",
            height: $(".create").hasClass('enter')?($(".cform").height() + 10) + "px":"190px"
          });
        }
        /* Mobile site */
        else {
          if (document.documentElement.clientWidth <= 375)
            $(".postbtn").css("width",(document.documentElement.clientWidth-67)+"px");
          else
            $(".postbtn").css("width","308px");
          $(".create").css({
            width:(document.documentElement.clientWidth-36)+"px",
            height:$(".create").hasClass('enter')?($(".cform").height() + 10) + "px":"375px"
          });
        }
      }
    }

    /* Setting color of SVG icons and changing their color for hover effects */
  	function changeColorSVG(elem, diffColor, pathSelector='svg.add-icon > ellipse,svg.create-icon > path.bubble',attr='fill') {
  		if (pathSelector == "none")
  			var toChange = elem;
  		else
  			var toChange = elem.find(pathSelector);
  		if (!toChange || !toChange.css(attr))
  			return false;
  		c = toChange.css(attr);
  		if (c.length == 7)
  			c = [parseInt(c.substring(1,3),16),parseInt(c.substring(3,5),16),parseInt(c.substring(5,7),16)];
  		else
  			c = c.match(/[0-9]+/g);

  		var newColor = "rgb("+Math.max(parseInt(c[0])+diffColor,0).toString()+","+Math.max(parseInt(c[1])+diffColor,0).toString()+","+Math.max(parseInt(c[2])+diffColor,0).toString() + ")";

  		toChange.css(attr,newColor);
  	}
  	function setColorSVG(elem, color, pathSelector='svg.add-icon > ellipse,svg.create-icon > path.bubble', attr='fill') {
  		elem.find(pathSelector).css(attr,color);
  	}

  	/* SVG icons */
  	

  	$(".create").hover(function(){
  		changeColorSVG($(this),-30);
  	}, function(){
  		changeColorSVG($(this),30);
  	});
  	$(".create").click(function() {
  		$(this).addClass('clicked');
  		$(this).unbind('click');
  		$(this).unbind('hover');
      displayPostTypes();
  	});
    input = "<input class='cfield' type='text'>";
    time = "<span class='tlabel'>Meeting Day</span><input readonly name='Date' id='Date' class='cfield cdate required' type='text'><div class='tholder'><span class='tlabel'>Start Time</span><input class='cfield ctime required' name='StartTime' id='StartTime' type='time' placeholder='--:-- --'></div><div class='tholder'><span class='tlabel'>End Time</span><input class='cfield ctime' name='EndTime' id='EndTime' type='time' placeholder='--:-- --'></div>";

    textarea = "<textarea id='Body' name='Body' class='cfield'></textarea>";
    radio = '<div class="aradio-holder"> <label class="cont"> <input class="aradio" type="radio" checked="checked" value="Test" name="Kind"> <span class="checkmark">Test</span> </label> <label class="cont"> <input class="aradio" type="radio" value="Homework" name="Kind"> <span class="checkmark">Homework</span> </label> <label class="cont"> <input class="aradio" type="radio" value="Notes" name="Kind"> <span class="checkmark">Notes</span> </label> <label class="cont"> <input class="aradio" type="radio" value="Essay/Report" name="Kind"> <span class="checkmark">Essay/Report</span> </label> <label class="cont"> <input class="aradio" type="radio" value="Project" name="Kind"> <span class="checkmark">Project</span> </label> </div>'

    function createPage() {
      fetchPosts();
      var si = '<div class="panel-icon-holder"><svg class="panel-icon" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" id="Layer_1" x="0px" y="0px" viewBox="0 0 512 512" style="enable-background:new 0 0 512 512;" xml:space="preserve" width="512px" height="512px"> <g> <g> <g> <path d="M187.733,315.733c0,4.71,3.823,8.533,8.533,8.533H230.4c4.71,0,8.533-3.823,8.533-8.533v-51.2 c0-4.71-3.823-8.533-8.533-8.533h-34.133c-4.71,0-8.533,3.823-8.533,8.533V315.733z M204.8,273.067h17.067V307.2H204.8V273.067z" fill="#FFFFFF"/> <path d="M196.267,221.867H230.4c4.71,0,8.533-3.823,8.533-8.533v-51.2c0-4.71-3.823-8.533-8.533-8.533h-34.133 c-4.71,0-8.533,3.823-8.533,8.533v51.2C187.733,218.044,191.556,221.867,196.267,221.867z M204.8,170.667h17.067V204.8H204.8 V170.667z" fill="#FFFFFF"/> <path d="M132.395,160.913L256,86.75l123.605,74.163c1.374,0.828,2.893,1.22,4.386,1.22c2.901,0,5.726-1.476,7.322-4.139 c2.432-4.045,1.118-9.284-2.918-11.708L264.533,71.97V17.067H307.2v17.067h-25.6c-4.71,0-8.533,3.823-8.533,8.533 c0,4.71,3.823,8.533,8.533,8.533h34.133c4.71,0,8.533-3.823,8.533-8.533V8.533c0-4.71-3.823-8.533-8.533-8.533H256 c-4.71,0-8.533,3.823-8.533,8.533V71.97l-123.861,74.317c-4.036,2.423-5.35,7.663-2.918,11.708 C123.102,162.031,128.358,163.345,132.395,160.913z" fill="#FFFFFF"/> <path d="M93.867,324.267c4.71,0,8.533-3.823,8.533-8.533v-51.2c0-4.71-3.823-8.533-8.533-8.533H59.733 c-4.71,0-8.533,3.823-8.533,8.533V281.6c0,4.71,3.823,8.533,8.533,8.533s8.533-3.823,8.533-8.533v-8.533h17.067v42.667 C85.333,320.444,89.156,324.267,93.867,324.267z" fill="#FFFFFF"/> <path d="M153.6,435.2V187.733c0-4.71-3.823-8.533-8.533-8.533c-4.71,0-8.533,3.823-8.533,8.533V435.2 c0,4.71,3.823,8.533,8.533,8.533C149.777,443.733,153.6,439.91,153.6,435.2z" fill="#FFFFFF"/> <path d="M110.933,477.867h290.133c4.71,0,8.533-3.823,8.533-8.533s-3.823-8.533-8.533-8.533h-76.8v-85.333h8.533 c4.71,0,8.533-3.823,8.533-8.533s-3.823-8.533-8.533-8.533H179.2c-4.71,0-8.533,3.823-8.533,8.533s3.823,8.533,8.533,8.533h8.533 V460.8h-76.8c-4.71,0-8.533,3.823-8.533,8.533S106.223,477.867,110.933,477.867z M264.533,426.667 c4.71,0,8.533-3.823,8.533-8.533s-3.823-8.533-8.533-8.533v-34.133H307.2V460.8h-42.667V426.667z M204.8,375.467h42.667V409.6 c-4.71,0-8.533,3.823-8.533,8.533s3.823,8.533,8.533,8.533V460.8H204.8V375.467z" fill="#FFFFFF"/> <path d="M452.267,366.933h-34.133c-4.71,0-8.533,3.823-8.533,8.533v51.2c0,4.71,3.823,8.533,8.533,8.533h34.133 c4.71,0,8.533-3.823,8.533-8.533v-51.2C460.8,370.756,456.977,366.933,452.267,366.933z M443.733,418.133h-17.067V384h17.067 V418.133z" fill="#FFFFFF"/> <path d="M452.267,264.533h-34.133c-4.71,0-8.533,3.823-8.533,8.533v51.2c0,4.71,3.823,8.533,8.533,8.533h34.133 c4.71,0,8.533-3.823,8.533-8.533v-51.2C460.8,268.356,456.977,264.533,452.267,264.533z M443.733,315.733h-17.067V281.6h17.067 V315.733z" fill="#FFFFFF"/> <path d="M435.2,494.933H76.8c-4.71,0-8.533,3.823-8.533,8.533S72.09,512,76.8,512h358.4c4.71,0,8.533-3.823,8.533-8.533 S439.91,494.933,435.2,494.933z" fill="#FFFFFF"/> <path d="M503.467,187.733c-4.71,0-8.533,3.823-8.533,8.533v8.533h-93.867c-4.71,0-8.533,3.823-8.533,8.533 c0,4.71,3.823,8.533,8.533,8.533h93.867v281.6c0,4.71,3.823,8.533,8.533,8.533s8.533-3.823,8.533-8.533v-307.2 C512,191.556,508.177,187.733,503.467,187.733z" fill="#FFFFFF"/> <path d="M273.067,315.733c0,4.71,3.823,8.533,8.533,8.533h34.133c4.71,0,8.533-3.823,8.533-8.533v-51.2 c0-4.71-3.823-8.533-8.533-8.533H281.6c-4.71,0-8.533,3.823-8.533,8.533V315.733z M290.133,273.067H307.2V307.2h-17.067V273.067z " fill="#FFFFFF"/> <path d="M85.333,418.133c0-1.109-0.486-110.933-42.667-110.933C0.486,307.2,0,417.024,0,418.133 c0,20.608,14.686,37.837,34.133,41.805v43.529c0,4.71,3.823,8.533,8.533,8.533c4.71,0,8.533-3.823,8.533-8.533v-43.529 C70.647,455.97,85.333,438.741,85.333,418.133z M42.667,443.733c-14.114,0-25.6-11.486-25.6-25.6 c0-42.513,11.418-93.867,25.6-93.867c14.182,0,25.6,51.354,25.6,93.867C68.267,432.247,56.781,443.733,42.667,443.733z" fill="#FFFFFF"/> <path d="M375.467,435.2v-256c0-4.71-3.823-8.533-8.533-8.533s-8.533,3.823-8.533,8.533v256c0,4.71,3.823,8.533,8.533,8.533 S375.467,439.91,375.467,435.2z" fill="#FFFFFF"/> <path d="M281.6,221.867h34.133c4.71,0,8.533-3.823,8.533-8.533v-51.2c0-4.71-3.823-8.533-8.533-8.533H281.6 c-4.71,0-8.533,3.823-8.533,8.533v51.2C273.067,218.044,276.89,221.867,281.6,221.867z M290.133,170.667H307.2V204.8h-17.067 V170.667z" fill="#FFFFFF"/> <path d="M8.533,298.667c4.71,0,8.533-3.823,8.533-8.533v-68.267h93.867c4.71,0,8.533-3.823,8.533-8.533 c0-4.71-3.823-8.533-8.533-8.533H17.067v-8.533c0-4.71-3.823-8.533-8.533-8.533S0,191.556,0,196.267v93.867 C0,294.844,3.823,298.667,8.533,298.667z" fill="#FFFFFF"/> </g> </g> </g> <g> </g> <g> </g> <g> </g> <g> </g> <g> </g> <g> </g> <g> </g> <g> </g> <g> </g> <g> </g> <g> </g> <g> </g> <g> </g> <g> </g> <g> </g> </svg></div>';
      var ai = '<div class="add-icon-holder"><svg class="add-icon" version="1.1" id="Layer_0_xA0_Image_1_" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="33.996px" height="33.996px" viewBox="0 0 33.996 33.996" enable-background="new 0 0 33.996 33.996" xml:space="preserve"> <ellipse fill="#000000" cx="16.874" cy="17.08" rx="16.874" ry="16.916"/> <polygon fill="#FFFFFF" points="14.915,14.915 14.915,10.165 18.915,10.165 18.915,14.915 24.081,14.915 24.081,19.248 18.998,19.248 18.915,23.915 14.915,23.915 14.915,19.165 9.832,19.082 9.832,15.082 "/> </svg> </div>';
      var ci = '<div class="create-icon-holder"><svg class="create-icon" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="60px" height="60px" viewBox="0 0 60 60" enable-background="new 0 0 60 60" xml:space="preserve"> <path class="bubble" d="M43.667,41.126c0.001-0.036,0.003-0.072,0.005-0.108l0.201-0.318c4.525-1.719,7.74-6.094,7.74-11.223v-7.182 c0-6.627-5.371-12-12-12H22.887c-6.627,0-12,5.373-12,12v7.182c0,6.627,5.373,12,12,12h11.9c0,0,3.45,4.15,8.937,6.703"/> <path fill="#FFFFFF" d="M6.411,42.41l-0.667-2.924L5.646,39.51c0.229-0.07,2.018-0.73,2.284-4.098C3.12,32.83,0,27.729,0,22.182V15 C0,6.729,6.729,0,15,0h16.727c8.271,0,15,6.729,15,15v7.182c0,8.271-6.729,15-15,15H21.141c-2.061,2.107-7.171,6.658-14.094,8.16 L6.411,42.41z"/> <path class="bubble" d="M10.942,33.723l-0.201-0.318C6.215,31.686,3,27.31,3,22.182V15C3,8.373,8.373,3,15,3h16.727c6.627,0,12,5.373,12,12v7.182 c0,6.627-5.373,12-12,12H19.828c0,0-2.508,3.825-8.94,5.839"/> <circle fill="#FFFFFF" cx="12.375" cy="18.5" r="3.625"/> <circle fill="#FFFFFF" cx="23.375" cy="18.5" r="3.625"/> <circle fill="#FFFFFF" cx="34.375" cy="18.5" r="3.625"/> </svg> </div>';
      /* Set up banner */
      $(".banner").width(document.documentElement.clientWidth - 12);
      $(".banner").prepend(si);
      $(".banner").find('path').css('fill','black');
      $(".banner").css('visibility','visible');

      /* Create new post button */
      var create = $("<div class='create'>" + ai + ci + "</div>");
      $(".container").prepend(create);
      setColorSVG(create,'#d25a77');
      create.append("<span class='create-content btn btn-primary'>New Post</span>");
    }
  	function newPost(labels=['Title','Content','Course'],fields=['Title','Body','Course'],types=[input,textarea,input],required=[true,false,false],btntxt="Post",optionaltxt="Optional") {
  		$(".create").empty();
      $(".create").addClass('enter');
      $(".create").append("<form class='cform' method='post' ></form>");

      // Add all form fields
      for (var i = 0; i < fields.length; ++i) {
        $(".cform").append("<label class='description'>"+labels[i]+(required[i]?" <font color='red'>*</font>":" <p class='notice'>("+optionaltxt+")</p>")+"</label>"+types[i]);
        if (types[i] != time && types[i] != textarea)
          $($("label.description")[i]).nextAll(".cfield").attr({id: fields[i],name: fields[i]});
        if (required[i])
          $($("label.description")[i]).nextAll(".cfield").addClass('required');
      }
      // Submit and cancel buttons
      $(".cform").append('<button id="cancelForm" class="button_text">back</button><button id="saveForm" disabled class="button_text" name="submit">' + btntxt + '</button>');
  		
      // Animate opening of form
      $("div.create.clicked").animate({"border-radius": "0px","border-width": "1px","border-color": "gray",
        "height": ($(".cform").height() + 10) + "px"},
  			500, function() {
          // Execute after animation
          $(".create").css({"border-style":"solid","cursor":"initial"});
          $(".cform").css("visibility","visible");

          // Datepicker plugin
          $(".cdate").datepicker({minDate:0,dateFormat: "DD - mm/dd/y",onSelect:function(i,o){$(this).datepicker('option','dateFormat','DD - mm/dd/y');var d=new Date(i),t=new Date(),tm=new Date();tm.setDate(t.getDate()+1);if((d.getMonth()!=t.getMonth()||d.getYear()!=t.getYear())&&(d.getMonth()!=tm.getMonth()||d.getYear()!=tm.getYear()))return;if(t.getDate() == d.getDate())$(this).datepicker('option','dateFormat',"T'od'a'y' - mm/dd/y"); else if(tm.getDate() == d.getDate())$(this).datepicker('option','dateFormat',"T'omo'rr'o'w - mm/dd/y");adjustTLs();}});

          // If input[type=time] not supported, use timepicker plugin
          if ($(".ctime").length > 0 && $(".ctime")[0].type != "time") {
            $(".ctime").attr("type","text")
            $(".ctime").timepicker({step:15, 'scrollDefault': 'now' });
          }

          // Cancel form event handler
          $("#cancelForm").click(displayPostTypes);

          // Enable submit button if required fields are filled
          $(".cfield.required").on("input",function(e){var f=true;$(".cfield.required").each(function(){if(!$.trim(this.value).length)f=false;});$("#saveForm").prop("disabled",f?false:true);});
  		});
  	}
    function adjustTLs()
    {
      var STEP=15;
      if($(".cdate").val().indexOf("Today")== -1)
        return;
      var d=new Date();
      d.setMinutes(d.getMinutes()+(STEP-(d.getMinutes()%STEP))+STEP);
      setExtremaTime(d,$("#StartTime"));
    }
    function setExtremaTime(time,obj,ext="min")
    {
      var h=time.getHours(),m=time.getMinutes();s=(h<10?"0"+h:h)+":"+(m<10?"0"+m:m);
      console.log(s);
      if (obj.attr("type")=="time")
        obj.attr(ext,s);
      else
        obj.timepicker('option',ext+"Time",time);
    }

    function displayPostTypes() {
      $(".create").empty();
      $(".create").removeClass("enter");
      $(".create").css("border-style","dashed");
      $(".create").animate({
        width: document.documentElement.clientWidth > 975? "675px":(document.documentElement.clientWidth-36)+"px",
        height: document.documentElement.clientWidth > 975? "190px":"375px",
        "border-radius": "15px","border-width": "3px","border-color": "#b3b3b3"},
        600, function() {
          $(this).append("<div class='button-holder' id='1'></div>");
          $(this).append("<div class='button-holder' id='2'></div>");
          $("#1.button-holder").append("<span class='pb-header'>Ask for help</span>");
          $("#1.button-holder").append("<button id='lb' class='postbtn'>" + lecture_icon + "<span class='btn-content'> Request to have a class attended</span></button>");
          $("#1.button-holder").append("<button id='rb' class='postbtn'>" + request_icon + "<span class='btn-content'> Request an assignment</span></button>");
          $("#2.button-holder").append("<span class='pb-header'>Make money by contributing</span>");
          $("#2.button-holder").append("<button id='cb' style='background:#af4c7e;' class='postbtn'>" + toclass_icon + "<span class='btn-content'> Offer to attend a class</span></button>");
          $("#2.button-holder").append("<button id='ob' style='background:#af4c7e;' class='postbtn'>" + offer_icon + "<span class='btn-content'> Offer an assignment</span></button>");
          $(".postbtn").hover(function(){changeColorSVG($(this),-30,"none","background");},function(){changeColorSVG($(this),30,"none","background");});
          $("#ob").click(function(e){
            newPost(["Assignment Title","Course Code","Assignment Type","Description"],['Title','Course','Kind','Body'],[input,input,radio,textarea],[true,true,true,false],"Next");
            $("#ptype").val("Assignment");
            focusField($(".cfield").first());
          });
          $("#rb").click(function(e){
            newPost(["Assignment Title","Course Code","Assignment Type","Description"],['Title','Course','Kind','Body'],[input,input,radio,textarea],[true,true,true,false]);
            $("#ptype").val("Assignment Request");
            focusField($(".cfield").first());
          });
          $("#lb").click(function(e){
            newPost(["Course Code","When is your class?","Details"],['Course','Time','Body'],[input,time,textarea],[true,true,false],"Post","Recommended");
            $("#ptype").val("Lecture Request");
            focusField($(".cfield").first());
          });
          sizer();
      });
      return false;
    }

    function fetchPosts() {
      $(".container").append("<ul class='posts'></ul>")
      $.post("/getposts", {"sid":JSON.stringify(sid)}, function(data) {
        var posts = $.parseJSON(data);

        if (Object.keys(posts).length == 0)
          return noPosts();
        for (pid in posts)
          appendPost(pid, posts[pid]);
      });
    }

    function noPosts() {
      $(".container").append("<div class='noposts'><h3>Here are some things you can do:</h3><ul style='list-style: square;margin-left: 20px;font-size: 13pt;'>\
        <li><a>Request to have a class attended</a></li>\
        <li><a>Request an assignment</a></li>\
        <li><a>Offer to attend a class</a></li>\
        <li><a>Offer an assignment</a></li>\
        </div>")
    }

    function appendPost(pid, post_data) {
      $(".posts").append("<li class='post-holder'><span class='post-title'>" + post_data['title'] + "</span> <span class='post-time'>" + post_data['time'] + "</span></li>")
    }


});