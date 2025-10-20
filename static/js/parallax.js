class ParallaxEffect {
    constructor() {
        this.mouseX = 0;
        this.mouseY = 0;
        this.isEnabled = true;
        this.init();
    }
    
    init() {
        // Слушаем движение мыши
        document.addEventListener('mousemove', (e) => {
            if (!this.isEnabled) return;
            
            this.mouseX = (e.clientX - window.innerWidth / 2) * 0.01;
            this.mouseY = (e.clientY - window.innerHeight / 2) * 0.01;
            
            this.applyParallax();
        });
        
        // Отключаем на мобильных устройствах
        if ('ontouchstart' in window) {
            this.isEnabled = false;
        }
        
        // Добавляем CSS для плавности
        this.addParallaxCSS();
    }
    
    applyParallax() {
        // Параллакс для карточек персонажей
        document.querySelectorAll('.character-btn').forEach((card, index) => {
            const delay = index * 0.1;
            const moveX = this.mouseX * (1 + delay);
            const moveY = this.mouseY * (1 + delay);
            
            card.style.transform = `
                perspective(1000px) 
                rotateY(${moveX}deg) 
                rotateX(${-moveY}deg) 
                scale3d(1, 1, 1)
            `;
        });
        
        // Параллакс для элементов навигации
        document.querySelectorAll('.nav-link').forEach((link, index) => {
            const moveX = this.mouseX * 0.3;
            const moveY = this.mouseY * 0.3;
            
            link.style.transform = `translateX(${moveX}px) translateY(${moveY}px)`;
        });
        
        // Параллакс для кнопок
        document.querySelectorAll('.container-btn').forEach((btn, index) => {
            const moveX = this.mouseX * 0.5;
            const moveY = this.mouseY * 0.5;
            
            btn.style.transform = `translateX(${moveX}px) translateY(${moveY}px)`;
        });
        
        // Легкий параллакс для фоновых элементов
        document.querySelectorAll('.profile-art').forEach(art => {
            const moveX = this.mouseX * 2;
            const moveY = this.mouseY * 2;
            
            art.style.transform = `translateX(${moveX}px) translateY(${moveY}px)`;
        });
    }
    
    addParallaxCSS() {
        const parallaxCSS = `
            .character-btn {
                transition: transform 0.5s cubic-bezier(0.23, 1, 0.32, 1);
            }
            
            .nav-link {
                transition: transform 0.3s ease;
            }
            
            .container-btn {
                transition: transform 0.4s ease;
            }
            
            .profile-art {
                transition: transform 0.6s ease;
            }
            
            /* Отключение параллакса на мобильных */
            @media (max-width: 768px) {
                .character-btn,
                .nav-link,
                .container-btn,
                .profile-art {
                    transform: none !important;
                }
            }
        `;
        
        const style = document.createElement('style');
        style.textContent = parallaxCSS;
        document.head.appendChild(style);
    }
    
    // Метод для ручного включения/выключения
    enable() {
        this.isEnabled = true;
    }
    
    disable() {
        this.isEnabled = false;
        // Сбрасываем трансформации
        document.querySelectorAll('.character-btn, .nav-link, .container-btn, .profile-art').forEach(el => {
            el.style.transform = '';
        });
    }
}

// Инициализация параллакса
document.addEventListener('DOMContentLoaded', function() {
    window.parallax = new ParallaxEffect();
});