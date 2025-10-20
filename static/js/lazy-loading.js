class LazyLoader {
    constructor() {
        this.observer = null;
        this.init();
    }
    
    init() {
        this.createObserver();
        this.observeImages();
        this.addLoadingStyles();
    }
    
    createObserver() {
        const observerOptions = {
            root: null,
            rootMargin: '50px 0px', // Начинаем загружать заранее
            threshold: 0.1
        };
        
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadImage(entry.target);
                    this.observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
    }
    
    observeImages() {
        // Находим все изображения с data-src
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        lazyImages.forEach(img => {
            // Добавляем плейсхолдер
            this.addPlaceholder(img);
            this.observer.observe(img);
        });
        
        // Также обрабатываем background images
        const lazyBackgrounds = document.querySelectorAll('[data-bg]');
        lazyBackgrounds.forEach(bg => {
            this.observer.observe(bg);
        });
    }
    
    addPlaceholder(img) {
        // Сохраняем оригинальные размеры
        const width = img.getAttribute('width') || '300';
        const height = img.getAttribute('height') || '400';
        
        // Добавляем класс для стилизации
        img.classList.add('lazy-loading');
        
        // Устанавливаем плейсхолдер
        if (!img.src) {
            img.src = this.createPlaceholderSVG(width, height);
        }
    }
    
    createPlaceholderSVG(width, height) {
        // Создаем SVG плейсхолдер
        return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='${width}' height='${height}' viewBox='0 0 ${width} ${height}'%3E%3Crect width='100%25' height='100%25' fill='%232a241c'/%3E%3Cpath d='M${width/2} ${height/3} L${width/3} ${2*height/3} L${2*width/3} ${2*height/3} Z' fill='%23332c24'/%3E%3Ctext x='50%25' y='85%25' text-anchor='middle' fill='%23d4a06a' font-family='Arial' font-size='14'%3EЗагрузка...%3C/text%3E%3C/svg%3E`;
    }
    
    loadImage(img) {
        const src = img.getAttribute('data-src');
        if (!src) return;
        
        // Показываем индикатор загрузки
        img.classList.add('lazy-loading');
        img.classList.remove('lazy-loaded');
        
        const imageLoader = new Image();
        
        imageLoader.onload = () => {
            // Плавная замена изображения
            img.src = src;
            img.classList.remove('lazy-loading');
            img.classList.add('lazy-loaded');
            
            // Удаляем data-src атрибут
            img.removeAttribute('data-src');
            
            // Запускаем кастомное событие
            img.dispatchEvent(new Event('lazyloaded'));
        };
        
        imageLoader.onerror = () => {
            console.error('Ошибка загрузки изображения:', src);
            img.classList.remove('lazy-loading');
            img.classList.add('lazy-error');
        };
        
        imageLoader.src = src;
    }
    
    loadBackground(element) {
        const bgUrl = element.getAttribute('data-bg');
        if (!bgUrl) return;
        
        const imageLoader = new Image();
        
        imageLoader.onload = () => {
            element.style.backgroundImage = `url(${bgUrl})`;
            element.classList.add('lazy-loaded');
            element.removeAttribute('data-bg');
        };
        
        imageLoader.onerror = () => {
            console.error('Ошибка загрузки фонового изображения:', bgUrl);
            element.classList.add('lazy-error');
        };
        
        imageLoader.src = bgUrl;
    }
    
    addLoadingStyles() {
        const lazyCSS = `
            .lazy-loading {
                background: linear-gradient(90deg, #2a241c 25%, #332c24 50%, #2a241c 75%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                border-radius: 8px;
            }
            
            @keyframes loading {
                0% {
                    background-position: 200% 0;
                }
                100% {
                    background-position: -200% 0;
                }
            }
            
            .lazy-loaded {
                opacity: 0;
                animation: fadeIn 0.5s ease-in-out forwards;
            }
            
            @keyframes fadeIn {
                to {
                    opacity: 1;
                }
            }
            
            .lazy-error {
                border: 2px dashed var(--nair-border);
                background: var(--nair-card-bg);
            }
            
            /* Специфичные стили для карточек персонажей */
            .character-btn.lazy-loading {
                min-height: 400px;
            }
            
            .profile-art.lazy-loading {
                min-height: 500px;
            }
        `;
        
        const style = document.createElement('style');
        style.textContent = lazyCSS;
        document.head.appendChild(style);
    }
    
    // Метод для принудительной загрузки всех изображений
    loadAll() {
        const images = document.querySelectorAll('img[data-src]');
        images.forEach(img => this.loadImage(img));
        
        const backgrounds = document.querySelectorAll('[data-bg]');
        backgrounds.forEach(bg => this.loadBackground(bg));
    }
    
    // Метод для обновления наблюдателя (если добавились новые изображения)
    update() {
        this.observeImages();
    }
}

// Инициализация ленивой загрузки
document.addEventListener('DOMContentLoaded', function() {
    window.lazyLoader = new LazyLoader();
});

// Автоматическая обработка динамически добавленных изображений
if (typeof MutationObserver !== 'undefined') {
    const mutationObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        const newImages = node.querySelectorAll ? node.querySelectorAll('img[data-src]') : [];
                        const newBackgrounds = node.querySelectorAll ? node.querySelectorAll('[data-bg]') : [];
                        
                        if (window.lazyLoader) {
                            newImages.forEach(img => window.lazyLoader.observer.observe(img));
                            newBackgrounds.forEach(bg => window.lazyLoader.observer.observe(bg));
                        }
                    }
                });
            }
        });
    });
    
    mutationObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
}