const toggleBtn = document.getElementById('menu-toggle');
const menu = document.getElementById('side-menu');

toggleBtn.addEventListener('click', () => {
  menu.classList.toggle('open');
});

// Можно закрывать меню при клике вне его
document.addEventListener('click', (e) => {
  if (menu.classList.contains('open') && !menu.contains(e.target) && e.target !== toggleBtn) {
    menu.classList.remove('open');
  }
});