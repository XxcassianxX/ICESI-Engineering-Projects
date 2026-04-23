function toggleDropdown() {
    const menu = document.getElementById("userDropdown");
    if (!menu) return;
    menu.classList.toggle("open");
}

document.addEventListener("click", function (event) {
    const trigger = document.querySelector(".user-trigger");
    const menu = document.getElementById("userDropdown");

    if (!menu || !trigger) return;

    if (!trigger.contains(event.target) && !menu.contains(event.target)) {
        menu.classList.remove("open");
    }
});