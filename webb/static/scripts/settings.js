const sidebar = document.querySelector(".sidebar");
const toggle = document.querySelector(".sidebar-toggler");

toggle.addEventListener("click", () => {
  sidebar.classList.toggle("close");
});
document.querySelector('.sidebar-toggler').addEventListener('click', function() {
  const closeButton = document.querySelector('.close');
  setTimeout(() => {
      closeButton.style.fontSize = '1rem'; 
  }, 400); 
});