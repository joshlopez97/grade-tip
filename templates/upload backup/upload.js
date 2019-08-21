$(document).ready(function() {
  $(window).on('load',function(){
    var current_position = 0;
    var file_indices = [];
    var files = [];
    var rotations = [];
    var rotater = 0;
    var doc_ext = ['docx', 'pptx', 'pdf'];
    var autopreview = true;

    var crop_max_width = 350;
    var crop_max_height = 1000;
    var jcrop_api;
    var canvas;
    var context;
    var image;
    var real_height;

    var prefsize;

    $("#file").change(function() {
      files = this.files;
      showElem("preview");
      showElem("preview-pane")
      file_indices = [];
      rotations = [];
      for (i = 0; i < this.files.length; i++) {
        file_indices.push(i);
        rotations.push(0);
      }
      loadImage(this, current_position);
    });

    function updatePreview(c) {
        autopreview = false;
        $('#cropped-preview').attr('src', image.src);
        $pcnt = $('#preview-pane .preview-container');
        $pimg = $('#preview-pane .preview-container img');
        xsize = $pcnt.width();
        ysize = $pcnt.height();
        asp_ratio = image.width / 350;
        console.log(asp_ratio);
        $('#x1').val(Math.round(0).toString());
        $('#y1').val(Math.round(c.y * asp_ratio).toString());
        $('#x2').val(Math.round(image.width).toString());
        $('#y2').val(Math.round((c.y + c.h) * asp_ratio).toString());
        $('#preview_index').val(current_position);
        getPreview();

        if (parseInt(c.w) > 0) {
            var rx = xsize / c.w;
            var ry = ysize / c.h;

            $pimg.css({
                width: Math.round(rx * 350) + 'px',
                height: Math.round(ry * real_height) + 'px',
                marginLeft: '-' + Math.round(rx * c.x) + 'px',
                marginTop: '-' + Math.round(ry * c.y) + 'px'
            });
        }
    }
    function getPreview() {
      var formData = new FormData();
      formData.append("x1",$("#x1").val());
      formData.append("y1",$("#y1").val());
      formData.append("x2",$("#x2").val());
      formData.append("y2",$("#y2").val());
      formData.append("preview_index",$("#preview_index").val());
      formData.append("file", files[current_position], files[current_position].name);
      formData.append("upload_file", true);
      $.ajax({
        type: "POST",
        url: "/getpreview",
        xhr: function () { return $.ajaxSettings.xhr(); },
        success: function (data) {
            // your callback here
        },
        error: function (error) {
            // handle error
        },
        async: true,
        data: formData,
        cache: false,
        contentType: false,
        processData: false,
        timeout: 60000
    });
    }
    function loadImage(input, index) {
        console.log('loadImage')
        var i = file_indices[index];
        if (input.files && input.files[i]) {
            var reader = new FileReader();
            canvas = null;
            reader.onload = function(e) {
                image = new Image();
                image.onload = function(e) {
                    if (current_position == 0 && autopreview) {
                        $('#x1').val("0");
                        $('#y1').val("0");
                        asp_ratio = 350 / this.width;
                        var rh = this.height * asp_ratio;
                        var crop_ratio = 150 / rh;
                        $('#x2').val(Math.round(this.width).toString());
                        $('#y2').val(Math.round(this.height * crop_ratio).toString());
                        $('#preview_index').val(current_position);
                        getPreview();
                    }
                    validateImage();
                    if (rotations[i] > 0) {
                        rotate_img();
                    }
                }
                image.src = e.target.result;
                if (current_position == 0 && autopreview) {
                    $('#cropped-preview').attr('src', e.target.result);
                }
            }
        update_pages(index);
        reader.readAsDataURL(input.files[i]);
        }
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
        var asp_ratio = 350 / image.width;
        real_height = asp_ratio * image.height;
        $('#preview-pane').css({ width: '362px', height: '162px' });
        console.log('  asp_ratio: ' + asp_ratio)
        $('#use-preview').css('top', ((image.height * asp_ratio / 2) + 220) + "px");
        jcropConfig(350, image.height * asp_ratio)
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
        hideElem('use-preview');
    }

    function selectcanvas(coords) {
        console.log('selectcanvas x:' + coords.x + ' y:' + coords.y + ' sz:' + coords.w + '*' + coords.h)
        prefsize = {
            x: Math.round(0),
            y: Math.round(coords.y),
            w: Math.round(coords.w),
            h: Math.round(coords.h)
        };
        showElem('use-preview');
        $('#use-preview').css('top', ((image.height * asp_ratio / 2) + 220) + "px");
        $('#use-preview').click(function() {
            updatePreview(coords);
        });
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
        var midpt_horiz = parseFloat(canvas.style.width) / 2;
        if (rotations[i] == 90 || rotations[i] == 270) {
            var asp_ratio = 350 / parseFloat(canvas.style.height);
            var dx = midpt_horiz - (midpt_horiz * asp_ratio);
            $(canvas).css({ width: (350 * asp_ratio) + "px", height: "350px" });
            var dy = (parseFloat(canvas.style.width) / 2) - (parseFloat(canvas.style.height) / 2);
        } else {
            var asp_ratio = 350 / parseFloat(canvas.style.width);
            var dx = 0;
            var dy = 0;
            $(canvas).css({ width: "350px", height: (350 * asp_ratio) + "px" });
        }
        $('#use-preview').css('top', ((350 * asp_ratio / 2) + 220) + "px");
        canvas.style.transform = "translate(-50%,-50%) rotate(" + rotations[i] + "deg)";
        canvas.style['transform-origin'] = "center";
    }

    function cancelRotate() {
        while (rotater != 0) {
            document.getElementById("rotate-upload").click();
        }
    }

    function applyRotate() {
        canvas.width = image.height;
        canvas.height = image.width;
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.translate(image.height / 2, image.width / 2);
        context.rotate(Math.PI / 2);
        context.drawImage(image, -image.width / 2, -image.height / 2);
        validateImage();
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
    function showElem(id) {
        console.log('showing ' + id)
        document.getElementById(id).style.display = "block";
    }
    function hideElem(id) {
        console.log('hiding ' + id)
        document.getElementById(id).style.display = "none";
    }
    function jcropConfig(w, h) {
        $("#canvas").Jcrop({
            minSize: [w, 150],
            maxSize: [w, 150],
            onSelect: selectcanvas,
            onRelease: clearcanvas,
            boxWidth: crop_max_width,
            boxHeight: crop_max_height,
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