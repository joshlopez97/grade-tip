$(document).ready(function() {
  $(window).on('load',function(){
    var current_position = 0;
    var file_indices = [];
    var imgs = [];
    var rotations = [];
    var rotater = 0;
    var doc_ext = ['docx', 'pptx', 'pdf'];
    var loading = $("<img class='loading' src='static/img/loading.gif'>")
    var error = $("<p class='error'>There was an error opening your file</p>")

    var maxwidth = 400;
    var maxheight = 500;
    var cachedwidth = 0;
    var cachedheight = 0;
    var jcrop_api;
    var canvas;
    var context;
    var image;
    var real_height;

    var prefsize;

    $("#file").change(function() {
      console.log(imgs)
      show($("#preview"));
      file_indices = [];
      rotations = [];
      var allpaths = {};
      $("#preview").append(loading);
      for (i = 0; i < this.files.length; i++) {
        console.log(this.files[i]);
        if (this.files[i].type == 'application/pdf') {
          imgs = imgs.concat(toImages(this.files[i]));
          console.log('after edit: ' + imgs);
        }
        else
          imgs.append(this.files[i]);
      }
      for (i = 0; i < imgs.length; i++) {
        file_indices.push(i);
        rotations.push(0);
      }
      console.log(file_indices)
      console.log(rotations)

      console.log(imgs)
      $(".loading").remove();
      loadImage(this, current_position);
    });

    function toImages(file) {
      var formData = new FormData();
      var paths = [];
      console.log(file);
      console.log(file.name)
      formData.append("file", file, file.name);
      formData.append("upload_file", true);
      console.log(formData)
      $.ajax({
        type: "POST",
        url: "/toimages",
        xhr: function () { return $.ajaxSettings.xhr(); },
        success: function (data) {
          paths = Array.from($.parseJSON(data)['paths']);
        },
        error: function (error) {
          $(".loading").remove();
          $("#preview").append(error);
        },
        async: false,
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        timeout: 60000
      });
      return paths;
    }
    function loadImage(input, index) {
        console.log('loadImage ' + index)
        var i = file_indices[index];
        if (!imgs || !imgs[i])
          return;
        var reader = new FileReader();
        canvas = null;
        if (typeof imgs[i] === 'string' || imgs[i] instanceof String) {
          image = new Image();
          image.onload = function(e) {
            if (current_position == 0) {
              $('#x1').val("0");
              $('#y1').val("0");
              asp_ratio = maxwidth / this.width;
              var rh = this.height * asp_ratio;
              var crop_ratio = 150 / rh;
              $('#x2').val(Math.round(this.width).toString());
              $('#y2').val(Math.round(this.height * crop_ratio).toString());
              $('#preview_index').val(current_position);
            }
            validateImage();
            if (rotations[i] > 0) {
              rotate_img();
            }
          }
          image.src = imgs[i];
        }
        else {
          reader.onload = function(e) {
            image = new Image();
            image.onload = function(e) {
              if (current_position == 0) {
                $('#x1').val("0");
                $('#y1').val("0");
                asp_ratio = maxwidth / this.width;
                var rh = this.height * asp_ratio;
                var crop_ratio = 150 / rh;
                $('#x2').val(Math.round(this.width).toString());
                $('#y2').val(Math.round(this.height * crop_ratio).toString());
                $('#preview_index').val(current_position);
              }
              validateImage();
              if (rotations[i] > 0) {
                rotate_img();
              }
            }
            image.src = e.target.result;
          }
          reader.readAsDataURL(imgs[i]);
        }
        update_pages(index);
    }

    function dataURLtoBlob(dataURL) {
      console.log('dataURLtoBlob')
      var BASE64_MARKER = ';base64,';
      if (dataURL.indexOf(BASE64_MARKER) == -1) {
        var parts = dataURL.split(',');
        var contentType = parts[0].split(':')[1];
        var raw = decodeURIComponent(parts[1]);

        return new Blob([raw], {
          type: contentType
        });
      }
      var parts = dataURL.split(BASE64_MARKER);
      var contentType = parts[0].split(':')[1];
      var raw = window.atob(parts[1]);
      var rawLength = raw.length;
      var uInt8Array = new Uint8Array(rawLength);
      for (var i = 0; i < rawLength; ++i) {
        uInt8Array[i] = raw.charCodeAt(i);
      }

      return new Blob([uInt8Array], {
        type: contentType
      });
    }

    function validateImage() {
      console.log('validateImage')
      if (canvas != null) {
        console.log('  creating image')
        image = new Image();
        image.onload = restartJcrop;
        image.src = canvas.toDataURL('image/png');
      } else restartJcrop();
    }

    function restartJcrop() {
        console.log('restartJcrop')
        if (canvas != null) {
            console.log('  canvas W: ' + canvas.width + ' H: ' + canvas.height);
            console.log('  image W: ' + image.width + ' H: ' + image.height);
        }
        if (jcrop_api != null) {
            jcrop_api.destroy();
        }
        $("#views").empty();
        $("#views").append("<canvas id=\"canvas\">");
        canvas = $("#canvas")[0];
        context = canvas.getContext("2d");
        canvas.width = image.width;
        canvas.height = image.height;
        context.drawImage(image, 0, 0);
        var asp_ratio = maxwidth / image.width;
        real_height = asp_ratio * image.height;
        jcropConfig(maxwidth, image.height * asp_ratio)
      clearcanvas();
    }

    function clearcanvas() {
        console.log('clearcanvas')
        prefsize = {
            x: 0,
            y: 0,
            w: canvas.width,
            h: canvas.height,
        };
    }

    function decrement() {
        if (current_position != 0) {
            current_position -= 1;
            return true;
        }
        return false;
    }
    function increment() {
        if (current_position != paths.length - 1) {
            current_position += 1;
            return true;
        }
        return false;
    }
    function update_pages(index) {
        var enumeration = [];
        for (i = 0; i < file_indices.length; i++) {
            enumeration.push(i)
        }
        var page = enumeration[index] + 1;
        $('#page-num').text(page + " of " + file_indices.length);
    }
    function remove_img() {
        if (file_indices.length == 1) {
            return;
        }
        file_indices.splice(current_position, 1);
        if (current_position != 0) {
            prev_file();
        }
        else {
            loadImage(document.getElementById("file"), current_position);
        }
    }
    function rotate_img() {
        var i = file_indices[current_position];
        console.log('rotate ' + rotations[i])
        if (canvas == null) {
            validateImage();
        }
        var midpt_horiz = $(canvas).width() / 2;
        if (rotations[i] == 90 || rotations[i] == 270) {
          var scaler = maxwidth / $(canvas).height();
          console.log(scaler)
          $(canvas).css({ width: ($(canvas).width() * scaler) + "px", height: $(canvas).height() * scaler + "px"});
        } else if ($(canvas).width() / $(canvas).height() < maxwidth / maxheight) {
          var scaler = maxheight / $(canvas).height();
          $(canvas).css({ width: ($(canvas).width() * scaler) + "px", height: $(canvas).height() * scaler + "px"});
        } else {
          var scaler = maxwidth / $(canvas).width();
          $(canvas).css({ width: ($(canvas).width() * scaler) + "px", height: $(canvas).height() * scaler + "px"});
        }
        $(canvas).css({'transform': "translate(-50%,-50%) rotate(" + rotations[i] + "deg)", 'transform-origin': 'center'});
    }

    function cancelRotate() {
        while (rotater != 0) {
            document.getElementById("rotate-upload").click();
        }
    }

    function next_file() {
        var input = document.getElementById("file");
        if (current_position < file_indices.length - 1) {
            current_position++;
            update_pages(current_position);
            loadImage(input, current_position);
        }
    }

    function prev_file() {
        var input = document.getElementById("file");
        if (current_position > 0) {
            current_position--;
            update_pages(current_position);
            loadImage(input, current_position);
        }
    }
    function show(e) {
      e.css('display', 'inline-block');
    }
    function hide(e) {
      e.css('display', 'none');
    }
    function jcropConfig(w, h) {
      $("#canvas").Jcrop({
          minSize: [w, 150],
          maxSize: [w, 150],
          onRelease: clearcanvas,
          boxWidth: maxwidth,
          boxHeight: maxheight,
          bgColor: ''
          }, function() {
              jcrop_api = this;
          }
      );
    }
    $("#left-button").click(prev_file);
    $("#right-button").click(next_file);
    $("#del-upload").click(remove_img);
    $("#rotate-upload").click(function(){
        var i = file_indices[current_position];
        rotater = (rotater + 90) % 360;
        rotations[i] = (rotations[i] + 90) % 360;
        rotate_img();
    });
    $("#confirm-docs").click(function(){
        document.getElementById("files_kept").value = file_indices;
        document.getElementById("form").submit();
    });
    $('.ub').hover(function() {$(this).css('opacity', 1);}, function() {$(this).css('opacity', 0.75);});

  });
});