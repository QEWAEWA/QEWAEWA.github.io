// Плавный скролл для якорных ссылок
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Анимация появления элементов при скролле
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Инициализация анимаций при загрузке
document.addEventListener('DOMContentLoaded', function() {
    // Добавляем стили для анимированных элементов
    const animationCSS = `
        .fade-in-up {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .fade-in-up.visible {
            opacity: 1;
            transform: translateY(0);
        }
        
        .fade-in-left {
            opacity: 0;
            transform: translateX(-30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .fade-in-left.visible {
            opacity: 1;
            transform: translateX(0);
        }
        
        .fade-in-right {
            opacity: 0;
            transform: translateX(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .fade-in-right.visible {
            opacity: 1;
            transform: translateX(0);
        }
    `;
    
    const style = document.createElement('style');
    style.textContent = animationCSS;
    document.head.appendChild(style);
    
    // Назначаем анимации элементам
    document.querySelectorAll('.character-btn').forEach(el => {
        el.classList.add('fade-in-up');
        observer.observe(el);
    });
    
    document.querySelectorAll('.profile-info').forEach(el => {
        el.classList.add('fade-in-left');
        observer.observe(el);
    });
    
    document.querySelectorAll('.accordion-item').forEach(el => {
        el.classList.add('fade-in-right');
        observer.observe(el);
    });
    
    document.querySelectorAll('.container-btn').forEach(el => {
        el.classList.add('fade-in-up');
        observer.observe(el);
    });
});