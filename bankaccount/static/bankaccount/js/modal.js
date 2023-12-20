var modal = document.querySelector(".modal");
    var trigger = document.querySelector(".trigger");
    var closeButton = document.querySelector(".close-button");

    function toggleModal() {
        modal.classList.toggle("show-modal");
    }

    function windowOnClick(event) {
        if (event.target === modal) {
            toggleModal();
        }
    }

//    trigger.addEventListener("click", function (event) {
//        event.preventDefault();
//        toggleModal();
//    });

    trigger.addEventListener("click", toggleModal);
    closeButton.addEventListener("click", toggleModal);
    window.addEventListener("click", windowOnClick)

//    form.addEventListener("keydown", function (event) {
//        if (event.key === "Enter" && event.target.tagName !== "BUTTON") {
//            event.preventDefault();
//            return false;
//        }
//    });