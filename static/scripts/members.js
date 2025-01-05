const sidebar = document.querySelector(".sidebar");
const toggle = document.querySelector(".sidebar-toggler");

toggle.addEventListener("click", () => {
  sidebar.classList.toggle("close");
});