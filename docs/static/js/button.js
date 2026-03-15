// Адаптивный скрипт для кнопок с поддержкой сенсорных устройств
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.bottom-right-links .btn, .container-btn');
    
    buttons.forEach((btn, index) => {
        // Поддержка мыши
        btn.addEventListener('mouseenter', () => {
            handleButtonInteraction(btn, buttons, index, 'hover');
        });
        
        btn.addEventListener('mouseleave', () => {
            handleButtonInteraction(btn, buttons, index, 'leave');
        });
        
        // Поддержка касания для мобильных устройств
        btn.addEventListener('touchstart', (e) => {
            handleButtonInteraction(btn, buttons, index, 'hover');
            e.preventDefault();
        }, { passive: false });
        
        btn.addEventListener('touchend', (e) => {
            handleButtonInteraction(btn, buttons, index, 'leave');
            e.preventDefault();
        }, { passive: false });
    });
    
    function handleButtonInteraction(btn, buttons, index, action) {
        if (action === 'hover') {
            // Увеличиваем текущую кнопку
            btn.style.transform = 'scale(1.2)';
            btn.style.zIndex = '10';
            
            // Смещаем соседние кнопки (только на больших экранах)
            if (window.innerWidth > 768) {
                buttons.forEach((other, idx) => {
                    if (other !== btn) {
                        if (idx < index) {
                            other.style.transform = 'translateX(-10px)';
                        } else {
                            other.style.transform = 'translateX(10px)';
                        }
                    }
                });
            }
        } else if (action === 'leave') {
            // Возвращаем всё к исходному состоянию
            btn.style.transform = '';
            btn.style.zIndex = 'auto';
            buttons.forEach(other => {
                other.style.transform = '';
            });
        }
    }
});

// Обработка вертикальной ориентации на мобильных устройств
window.addEventListener('orientationchange', function() {
    console.log('Ориентация изменена на:', window.orientation);
    // Перезагружаем для лучшего отображения
    setTimeout(() => {
        window.scrollTo(0, 0);
    }, 100);
});