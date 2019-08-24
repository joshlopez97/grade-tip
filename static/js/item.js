function getSimpleItem(title, subtitle)
{
  return $(`
  <div class="box-item-holder">
    <div class="box-item">
      <div class="box-item-title">${title}</div>
      <div class="box-item-subtitle">${subtitle}</div>
    </div>
  </div>
`);
}