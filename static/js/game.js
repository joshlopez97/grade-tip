$(document).ready(function() {
  $(window).on('load', function() {
    var player = $('<img id="player" src="static/img/rocket2.gif">');
    var wings = $('<img id="wings" src="static/img/blank.png"></img>')
    var meteor = $('<img class="meteor" src="static/img/meteor.gif">');
    var incoming = $('<img class="incoming" src="static/img/alert.gif">');
    var score = $("<span class='score'>0</span>");
    var explode = $("<img class='explode' src='static/img/explosion.gif'>");
    var gameover = $("<img class='gameover' src='static/img/gamover.gif'>");
    var gamebegin = $("<img class='gamebegin' src='static/img/gamebegin.png'>");
    var play = $("<button class='play'></button>")
    var gameWidth = $("#game").width();
    var gameHeight = $("#game").height();
    var dodged = -1;
    var game;

    /* Speed / Difficulty Config */
    var METEOR_SPEED, METEOR_WAIT, METEOR_SHOWER_WAIT, MIN_ANGLE_INCR, MAX_ANGLE_INCR, MAX_METEOR_SIZE, RAND_ANGLE, ACCELERATION;
    var lives = 3;
    $("#game").append(play);
    gamebegin.css({'top':(gameHeight/2)-100,'left':(gameWidth/2)-250});
    $("#game").append(gamebegin);
    $("#game").on('mousemove', function(e){
      if ($("#player").length > 0)
        movePlayer(e);
    });
    $(".play").click(function(){beginGame();})
    function randomBetween(min,max){return Math.floor(Math.random()*(max-min+1)+min);}
    function cornerAngle(angle){return (angle>40&&angle<50)||(angle>130&&angle<140)||(angle>220&&angle<230)||(angle>310&&angle<320);}
    function beginGame() {
      cleanUp();
      $("#game").append(player);
      $("#game").append(wings);
      $("#game").append(score);
      game = setInterval(function(){
        dodged++;
        if (dodged > 0) {
          updateScore(dodged);
          increaseDifficulty();
          if (dodged % 10 == 0){
            levelUp()
          }
        }

        meteorShower();
      }, METEOR_SHOWER_WAIT);
    }
    function meteorShower() {
      var start = randomBetween(0,360);
      console.log('WAVE: SPEED=' + METEOR_SPEED + ', mn=' + MIN_ANGLE_INCR + ', mx=' + MAX_ANGLE_INCR);
      for (i = start, j = 1; i < 360+start-randomBetween(MIN_ANGLE_INCR,MAX_ANGLE_INCR); i +=randomBetween(MIN_ANGLE_INCR,MAX_ANGLE_INCR),j++) {
        var straight = RAND_ANGLE? !!randomBetween(0,1):true;
        var sz = randomBetween(10,MAX_METEOR_SIZE);
        console.log('  ' + j + '.) angle='+i+'° sz=' +sz);
        addMeteor(i%360, straight, sz);
      }
    }
    function updateScore(dodged) {
      score.remove();
      score.text(dodged);
      $("#game").append(score);
    }
    function levelUp() {
      resetSpeed();
      ACCELERATION -= 0.02;
      RAND_ANGLE = true;
      addMeteor(180,true,60,3500);
    }
    function increaseDifficulty() {
      METEOR_SHOWER_WAIT = Math.max(METEOR_SHOWER_WAIT*ACCELERATION, 750);
      METEOR_WAIT = Math.max(METEOR_WAIT*ACCELERATION, 750);
      METEOR_SPEED = Math.max(METEOR_SPEED*ACCELERATION, 900);
      MIN_ANGLE_INCR = Math.max(MIN_ANGLE_INCR*0.97,22);
      MAX_ANGLE_INCR = Math.max(MAX_ANGLE_INCR*0.96,40);
      MAX_METEOR_SIZE = Math.min(MAX_METEOR_SIZE*1.01,33);
    }
    function cleanUp() {
      $(".gamebegin").remove();
      $(".gameover").remove();
      $(".play").remove();
      score.text(0);
      dodged = -1;
      resetSpeed();
      MIN_ANGLE_INCR = 85;
      MAX_ANGLE_INCR = 110;
      MAX_METEOR_SIZE = 30;
      RAND_ANGLE = false;
      ACCELERATION = 0.94;
    }
    function resetSpeed() {
      METEOR_SPEED = 2600;
      METEOR_WAIT = 2000;
      METEOR_SHOWER_WAIT = 4000;
    }
    function isCollide(b) {
      var a = document.getElementById('player');
      var c = document.getElementById('wings');
      if (a && c)
        return !(
          ((a.y + (a.height * 0.7)) < (b.y)) ||
          ((a.y + 10) > (b.y + b.height * 0.9)) ||
          ((a.x + (a.width * 0.5)) < b.x) ||
          ((a.x + (a.width * 0.5)) > (b.x + b.height))
        ) || !(
          ((c.y + c.height) < (b.y)) ||
          (c.y > (b.y + b.height * 0.9)) ||
          (c.x + c.width < b.x) ||
          (c.x > b.x + b.height)
        );
      else
        return false;
    }
    function addMeteor(angle, straight=false, size=23, speed=METEOR_SPEED) {
      angle = angle%360;
      // if (straight && cornerAngle(angle))
      //   straight = false;
      var centerX = gameWidth / 2, centerY = gameHeight / 2;
      var posX = centerX - size, posY = centerY - size;
      var horizRadius = centerX + size, vertRadius = centerY + size;
      var smallHoriz = centerX, smallVert = centerY;
      var alertX = centerX - (size*0.85), alertY = centerY - (size*0.85);

      var rotation = angle;
      var animationTop = Math.sin(angle * (Math.PI / 180)) * (gameWidth * 1.8);
      var animationLeft = Math.cos(angle * (Math.PI / 180)) * (gameWidth * 1.8);
      if (angle < 45 || angle > 315){
        alertX = gameWidth - (size*0.85*2);
        alertY = Math.min(Math.max(alertY+Math.tan(angle * (Math.PI / 180)) * smallVert,0),gameHeight-(size*0.85*2));
        posX += horizRadius;
        posY  = Math.min(Math.max(posY+Math.tan(angle * (Math.PI / 180)) * vertRadius,0),gameHeight-(size*2));
        if (straight) {
          rotation = 0;
          animationTop = 0;
          animationLeft = gameWidth * 1.8;
          alertY = posY;
        }
      } else if (angle > 135 && angle < 225) {
        alertX = 0;
        alertY = Math.min(Math.max(alertY-Math.tan(angle * (Math.PI / 180)) * smallVert,0),gameHeight-(size*0.85*2));
        posX -= horizRadius;
        posY = Math.min(Math.max(posY-Math.tan(angle * (Math.PI / 180)) * vertRadius,0),gameHeight-(size*2));
        if (straight) {
          rotation = 180;
          animationTop = 0;
          animationLeft = gameWidth * -1.8;
          alertY = posY;
        }
      } else if (angle >= 45 && angle <= 135) {
        alertX = Math.min(Math.max(alertX+(smallHoriz / Math.tan(angle * (Math.PI / 180))),0),gameWidth-(size*0.85*2));
        alertY = gameHeight - (size*0.85*2);
        posX = Math.min(Math.max(posX+(horizRadius / Math.tan(angle * (Math.PI / 180))),0),gameWidth-(size*2));
        posY += vertRadius;
        if (straight) {
          rotation = 90;
          animationTop = gameWidth * 1.8;
          animationLeft = 0;
          alertX = posX;
        }
      } else {
        alertX = Math.min(Math.max(alertX-(smallHoriz / Math.tan(angle * (Math.PI / 180))),0),gameWidth-(size*0.85*2));
        alertY = 0;
        posX = Math.min(Math.max(posX-(horizRadius / Math.tan(angle * (Math.PI / 180))),0),gameWidth-(size*2));
        posY -= vertRadius;
        if (straight) {
          rotation = 270;
          animationTop = gameWidth * -1.8;
          animationLeft = 0;
          alertX = posX;
        }
      }
      var meteor = $('<img class="meteor" src="static/img/meteor.gif">');
      var incoming = $('<img class="incoming" src="static/img/alert.gif">');
      meteor.css({
        transform: "rotate(" + rotation + "deg)",
        top: posY + "px",
        left: posX + "px"
      });
      meteor.height(size*2);
      incoming.height(size*2*0.85);
      incoming.css({
        transform: "rotate(" + rotation + "deg)",
        top: alertY + "px",
        left: alertX + "px"
      });
      $("#game").append(meteor);
      $("#game").append(incoming);
      setTimeout(function () {
        incoming.remove();
        var timer = setInterval(function() {
          if (isCollide(meteor[0]))
            destroyPlayer();
        }, 5)
        meteor.animate({
          top: "-=" + animationTop + "px",
          left: "-=" + animationLeft + "px"},
          speed, function() {
            clearInterval(timer);
            meteor.remove();
        });
      },METEOR_WAIT);
    }

    function addIncoming(pos, incoming) {
      incoming.css('top',pos.top + "px");
      incoming.css('left',pos.left + "px");
      $(".incoming-holder").append(incoming);
    }

    function destroyPlayer() {
      for (let m of $(".meteor"))
        m.remove();
      var pos = $("#player").position();
      restartAnim(explode);
      explode.css({
        top: pos.top - (90 - ($("#player").height() / 2)) + 'px',
        left: pos.left - (90 - ($("#player").width() / 2)) + 'px'
      });
      setTimeout(function () {
        $("#game").append(explode);
      },0);
      restartAnim(gameover);
      gameover.css({'top':(gameHeight/2)-100,'left':(gameWidth/2)-250});
      setTimeout(function () {
        $("#game").append(gameover);
        explode.remove();
      },1100);
      $("#player").remove();
      $("#wings").remove();
      clearInterval(game);
      $("#game").append(play);
      $(".play").click(function(){beginGame();})
    }

    function restartAnim(elem) {
      var src = elem.attr('src');
      elem.attr('src','');
      elem.attr('src',src);
    }
    function movePlayer(e) {
      var x = parseInt(e.pageX) - ((document.documentElement.clientWidth - $("#game").width()) / 2) - 40
      var y = parseInt(e.pageY) - $("#game").offset().top - 30
      $("#player").css({
          left: x + "px",
          top: y + "px"
      }, 5);
      $("#wings").css({
          left: (x + 8) + "px",
          top: (y + 36) + "px"
      }, 5);
    }
  });
});