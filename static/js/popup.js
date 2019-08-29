function createAccountPopup(title)
{
  return createPopup(title, title);
}

function createPopup(titleText, submitText)
{
  hideSidebar();
  $(".popup").remove();
  const popup = $(`
    <div class="popup">
      <div class="close-icon-holder">
        <img class="close-icon" src="/img/close.png" alt="close">
      </div>
      <div class="popup-header">${titleText}</div>
      <form class="popup-form">
        <div class="popup-fields">
        </div>
        <button class="popup-submit">${submitText}</button>
      </form>
    </div>
  `);
  $("body").append(popup);
  darkenPage();
  popup.fadeIn(200);
  $(".close-icon-holder").click(destroyPopup);
  return popup;
}


function addField(popup, label, type, currentValue="", name=label)
{
  popup.find(".popup-fields").append(`
    <div class="popup-form-field">
      <div class="popup-form-field-label">${label}</div>
      <input class="popup-form-field-input text" type="${type}" name="${name}" value="${currentValue}">
    </div>
  `);
}

function addTextBox(popup, label, name=label)
{
  popup.find(".popup-fields").append(`
    <div class="popup-form-field">
      <div class="popup-form-field-label">${label}</div>
      <textarea class="popup-form-field-input text" name="${name}"></textarea>
    </div>
  `);
}

function ensurePasswordsMatch(popup, passwordInputName, confirmPasswordInputName, errorMsg="Passwords must match")
{
  let p1 = popup.find(`input[name=${passwordInputName}]`);
  let p2 = popup.find(`input[name=${confirmPasswordInputName}]`);
  console.log(p1);
  p1.on('input', () => {
    console.log(p1.val());
    if (p1.val() !== p2.val() && p2.val() !== "")
      spawnErrorMsg(popup, errorMsg);
    else
      clearErrorMsgs(popup);
  });
  p2.on('input', () => {
    console.log(p2.val());
    if (p1.val() !== p2.val())
      spawnErrorMsg(popup, errorMsg);
    else
      clearErrorMsgs(popup);
  });
}

function addCaptcha(popup)
{
  popup.find(".popup-fields").append(`
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    <div class="g-recaptcha" data-sitekey="6LdSAK8UAAAAAGIgE-kVzCyinUVXQAtKNr8Hhuq_
"></div>
  `);
}

function addRepeatableField(popup, label, type, name=label)
{
  let r = $(`
    <div class="popup-form-field">
      <div class="popup-form-field-label">${label}</div>
      <input class="popup-form-field-input" type="${type}" name="${name + "1"}">
    </div>
  `);
  let b = $(`<div style="display: inline-block" class="link">ADD</div>`)
    .click(()=>{
      for (let i = 2; i < 10; i++)
      {
        if ($(`input.popup-form-field-input[name="${name + i.toString()}"]`).length === 0)
        {
          $(`<input class="popup-form-field-input" style="margin-top: 10px;" type="${type}" name="${name + i.toString()}">`)
            .insertAfter(`input.popup-form-field-input[name="${name + (i - 1).toString()}"]`);
          break;
        }
      }
    });
  popup.find(".popup-fields").append(r.append(b));
}

function assignValues(popup, data)
{
  for (let key in data)
  {
    popup.find("input[name=" + key + "]").val(data[key]);
  }
}

function addSubmitAction(popup, action)
{
  popup.find(".popup-submit").click(action);
  popup.find(".popup-form").submit(action);
}

function getFormData(popup)
{
  const raw_data = popup.find(".popup-form").serializeArray();
  let form_data = {};
  for (let i = 0; i < raw_data.length; i++)
  {
    form_data[raw_data[i]['name'].toLowerCase()] = raw_data[i]['value'];
  }
  return form_data;
}

function changeCloseAction(popup, closeaction)
{
  popup.find(".close-icon-holder").click(() => {
    destroyPopup();
    closeaction();
  });
}

function destroyPopup()
{
  lightenPage();
  $(".popup").fadeOut(200, "swing", () => $(this).remove());
}

function clearErrorMsgs(popup)
{
  if (typeof popup === "undefined")
    $(".popup-error").remove();
  else
    popup.find("div.popup-error").remove();
}

function submitForm(popup)
{
  location.reload();
}

function spawnErrorMsg(popup, errorMsg, label=null)
{
  clearErrorMsgs(popup);
  let location = label == null ? popup.find("input").last()
                               : popup.find(`[name="${label}"]`);
  $(`<div class="popup-error">${errorMsg}</div>`).insertAfter(location);
}

function notice(text, seconds=2500)
{
  $("body").append(`
    <div class='notice'>
      <div class='notice-text'>${text}</div>
      <div id="close-notice-btn" class="close-icon-holder">
        <img class="close-notice" src="/img/close.png" alt="close">
      </div>
    </div>
  `);
  let n = $(".notice");
  $("#close-notice-btn").click(() => n.remove());
  n.fadeIn();
  setTimeout(()=>{
    n.fadeOut(() => n.remove());
  }, seconds);
}
