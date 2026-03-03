// Улучшенная навигация с поддержкой мобильных устройств
document.addEventListener('DOMContentLoaded', function() {
    // Поиск
    const searchInput = document.querySelector('.search-input');
    const suggestionsDiv = document.querySelector('.suggestions');
    
    // Данные для поиска
    const searchItems = [
        { text: 'Главная', href: 'index.html' },
        { text: 'Карта', href: 'karta.html' },
        { text: 'Магия', href: 'magic.html' },
        { text: 'Экономика', href: 'economy.html' },
        { text: 'Система прокачки', href: 'leveling.html' },
        { text: 'Анкеты', href: 'ankety.html' },
        { text: 'Лор', href: 'lor.html' }
    ];
    
    // Обработка поиска
    searchInput.addEventListener('input', function(e) {
        const value = e.target.value.toLowerCase().trim();
        
        if (value.length === 0) {
            suggestionsDiv.style.display = 'none';
            return;
        }
        
        const filtered = searchItems.filter(item => 
            item.text.toLowerCase().includes(value)
        );
        
        if (filtered.length === 0) {
            suggestionsDiv.style.display = 'none';
            return;
        }
        
        suggestionsDiv.innerHTML = filtered.map(item => `
            <div class="suggestion-item" onclick="window.location.href='${item.href}'">
                ${item.text}
            </div>
        `).join('');
        suggestionsDiv.style.display = 'block';
    });
    
    // Закрытие подсказок при клике вне
    document.addEventListener('click', function(e) {
        if (!e.target.classList.contains('search-input')) {
            suggestionsDiv.style.display = 'none';
        }
    });
    
    // Определение активной страницы
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === 'index.html')) {
            link.classList.add('active');
        }
    });
});