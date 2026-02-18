function toggleSidebar() {
    const sb = document.getElementById("mySidebar");
    const overlay = document.getElementById("overlay");
    const isOpen = sb.classList.contains("active");

    if (isOpen) {
        sb.classList.remove("active");
        overlay.style.display = "none";
    } else {
        sb.classList.add("active");
        overlay.style.display = "block";
    }
}

var dropdowns = document.getElementsByClassName("dropdown-btn");

for (var i = 0; i < dropdowns.length; i++) {
    dropdowns[i].addEventListener("click", function () {
        var container = this.nextElementSibling;
        const icon = this.querySelector('.fa-caret-down');

        if (!container.style.maxHeight || container.style.maxHeight === "0px") {
            container.style.maxHeight = container.scrollHeight + "px";
            icon.style.transform = "rotate(180deg)";
        } else {
            container.style.maxHeight = "0px";
            icon.style.transform = "rotate(0deg)";
        }
    });
}
