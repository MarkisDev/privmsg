function togglePopup(){
    document.getElementById("popup-1").classList.toggle("active");
    }

    var active = document.querySelector(".password");
    document.addEventListener('DOMContentLoaded', function () {
      var checkbox = document.querySelector('input[type="checkbox"]');
      checkbox.addEventListener('change', function () {
        if (checkbox.checked) {
          // do this
          active.classList.remove("remove");
        } else {
          // do that              
          active.classList.add("remove");
        }
      });
    });