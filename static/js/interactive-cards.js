class InteractiveCards {
    constructor() {
        this.cards = [];
        this.init();
    }
    
    init() {
        this.setupCards();
        this.addCardStyles();
    }
    
    setupCards() {
        document.querySelectorAll('.character-btn').forEach((card, index) => {
            this.cards.push(card);
            
            // 3D эффект при наведении
            card.addEventListener('mousemove', (e) => {
                this.handleCardHover(e, card);
            });
            
            card.addEventListener('mouseleave', () => {
                this.handleCardLeave(card);
            });
            
            // Клик по карточке
            card.addEventListener('click', (e) => {
                this.handleCardClick(e, card);
            });
            
            // Добавляем индикатор кликабельности
            card.style.cursor = 'pointer';
            card.title = 'Нажмите для просмотра анкеты';
        });
    }
    
    handleCardHover(e, card) {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateY = (x - centerX) / 15;
        const rotateX = (centerY - y) / 15;
        
        // Позиция свечения
        const glowX = (x / rect.width) * 100;
        const glowY = (y / rect.height) * 100;
        
        card.style.transform = `
            perspective(1000px) 
            rotateX(${rotateX}deg) 
            rotateY(${rotateY}deg) 
            scale3d(1.05, 1.05, 1.05)
        `;
        
        // Динамическое свечение
        card.style.setProperty('--glow-x', `${glowX}%`);
        card.style.setProperty('--glow-y', `${glowY}%`);
    }
    
    handleCardLeave(card) {
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
        card.style.transition = 'transform 0.5s ease, box-shadow 0.5s ease';
    }
    
    handleCardClick(e, card) {
        // Добавляем анимацию клика
        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(0.95, 0.95, 0.95)';
        
        setTimeout(() => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
        }, 150);
        
        // Можно добавить дополнительную логику при клике
        const characterName = card.querySelector('.character-name').textContent;
        console.log(`Выбран персонаж: ${characterName}`);
        
        // Показываем уведомление, если подключена система уведомлений
        if (window.showNotification) {
            window.showNotification(`Открывается анкета: ${characterName}`, 'info');
        }
    }
    
    addCardStyles() {
        const cardCSS = `
            .character-btn {
                position: relative;
                overflow: hidden;
                transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
            }
            
            .character-btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: radial-gradient(
                    circle at var(--glow-x, 50%) var(--glow-y, 50%),
                    rgba(212, 160, 106, 0.2) 0%,
                    transparent 50%
                );
                opacity: 0;
                transition: opacity 0.3s ease;
                pointer-events: none;
            }
            
            .character-btn:hover::before {
                opacity: 1;
            }
            
            .character-btn:active {
                transition: transform 0.1s ease;
            }
            
            .character-name {
                transition: all 0.3s ease;
            }
            
            .character-btn:hover .character-name {
                transform: translateY(-5px);
                text-shadow: 0 0 15px rgba(212, 160, 106, 0.5);
            }
        `;
        
        const style = document.createElement('style');
        style.textContent = cardCSS;
        document.head.appendChild(style);
    }
    
    // Метод для программного выбора карточки
    selectCard(characterId) {
        const card = document.querySelector(`[data-character="${characterId}"]`);
        if (card) {
            this.handleCardClick(new Event('click'), card);
        }
    }
}

// Инициализация интерактивных карточек
document.addEventListener('DOMContentLoaded', function() {
    window.interactiveCards = new InteractiveCards();
});