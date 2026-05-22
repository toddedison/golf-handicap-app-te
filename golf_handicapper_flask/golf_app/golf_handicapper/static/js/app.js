// The Golf Handicapper — app.js
document.addEventListener('DOMContentLoaded', function () {

  // File size guard (replaces jQuery bind in _form2_html.erb)
  var pictureInput = document.getElementById('picture');
  if (pictureInput) {
    pictureInput.addEventListener('change', function () {
      if (this.files && this.files[0]) {
        var sizeMB = this.files[0].size / 1024 / 1024;
        if (sizeMB > 5) {
          alert('Maximum file size is 5MB. Please choose a smaller file.');
          this.value = '';
        }
      }
    });
  }

  // Simple date-picker hint (replaces jQuery UI datepicker)
  // Sets input type="date" on fields marked data-behavior="datepicker"
  document.querySelectorAll('[data-behavior~=datepicker]').forEach(function (el) {
    el.setAttribute('type', 'date');
    el.setAttribute('placeholder', 'yyyy-mm-dd');
  });

});
