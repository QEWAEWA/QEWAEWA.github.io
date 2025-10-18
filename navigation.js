const pages = [
  "Главная",
  "О нас",
  "Услуги",
  "Контакты",
  "Блог",
  "Часто задаваемые вопросы",
  // добавьте сюда названия страниц
];

const searchInput = document.getElementById('search');
const suggestionsBox = document.getElementById('suggestions');

searchInput.addEventListener('input', () => {
  const query = searchInput.value.toLowerCase();
  suggestionsBox.innerHTML = '';

  if (query.length === 0) {
    suggestionsBox.style.display = 'none';
    return;
  }

  const filteredPages = pages.filter(page => page.toLowerCase().includes(query));

  if (filteredPages.length === 0) {
    suggestionsBox.style.display = 'none';
    return;
  }

  filteredPages.forEach(page => {
    const div = document.createElement('div');
    div.className = 'suggestion-item';
    div.textContent = page;

    div.addEventListener('click', () => {
      searchInput.value = page;
      suggestionsBox.style.display = 'none';
      // Можно добавить действие по переходу, например:
      // window.location.href = `/${page}.html`;
    });

    suggestionsBox.appendChild(div);
  });

  suggestionsBox.style.display = 'block';
});