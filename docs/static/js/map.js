class InteractiveMap {
    constructor(containerId, imageId) {
        console.log('🗺️ Инициализация карты...');
        
        this.container = document.getElementById(containerId);
        this.image = document.getElementById(imageId);
        
        if (!this.container || !this.image) {
            console.error('❌ Элементы карты не найдены!');
            return;
        }
        
        this.isDragging = false;
        this.startX = 0;
        this.startY = 0;
        this.translateX = 0;
        this.translateY = 0;
        this.scale = 0.3; // Начальный масштаб
        
        this.minScale = 0.1; // Минимальный масштаб
        this.maxScale = 8;   // Максимальный масштаб
        
        // Настройки плавности
        this.zoomSensitivity = 0.08;    // Чувствительность колеса мыши
        this.buttonZoomStep = 0.15;     // Шаг для кнопок
        this.zoomAnimation = true;      // Плавная анимация
        
        this.init();
    }
    
    init() {
        console.log('🔄 Настройка карты...');
        
        // Сразу настраиваем кнопки
        this.setupControls();
        
        // Ждем загрузки изображения
        if (this.image.complete) {
            this.setupMap();
        } else {
            this.image.onload = () => this.setupMap();
            this.image.onerror = () => console.error('❌ Ошибка загрузки изображения');
        }
    }
    
    setupMap() {
        console.log('🖼️ Изображение загружено');
        
        // Настройка стилей
        this.image.style.cursor = 'grab';
        this.image.style.transformOrigin = '0 0';
        this.image.style.userSelect = 'none';
        
        // Добавляем плавный переход для масштабирования
        if (this.zoomAnimation) {
            this.image.style.transition = 'transform 0.3s ease-out';
        }
        
        // Применяем начальный масштаб
        this.applyTransform(0, 0, this.scale);
        
        // Настройка событий
        this.setupEventListeners();
        
        console.log('✅ Карта готова. Масштаб:', this.scale);
    }
    
    setupEventListeners() {
        // Мышь
        this.container.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        document.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        document.addEventListener('mouseup', () => this.handleMouseUp());
        
        // Касания
        this.container.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: false });
        document.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: false });
        document.addEventListener('touchend', () => this.handleTouchEnd());
        
        // Колесо мыши с плавным zoom
        this.container.addEventListener('wheel', (e) => this.handleWheel(e), { passive: false });
    }
    
    setupControls() {
        console.log('🎛️ Настройка кнопок управления...');
        
        // Находим кнопки
        const resetBtn = document.getElementById('resetBtn');
        const zoomInBtn = document.getElementById('zoomInBtn');
        const zoomOutBtn = document.getElementById('zoomOutBtn');
        
        console.log('Найдены кнопки:', {
            reset: !!resetBtn,
            zoomIn: !!zoomInBtn,
            zoomOut: !!zoomOutBtn
        });
        
        // Проверяем и добавляем обработчики
        if (resetBtn) {
            resetBtn.onclick = () => {
                console.log('🔄 Кнопка СБРОС нажата!');
                this.smoothReset();
            };
            resetBtn.style.cursor = 'pointer';
        }
        
        if (zoomInBtn) {
            zoomInBtn.onclick = () => {
                console.log('➕ Кнопка УВЕЛИЧЕНИЕ нажата!');
                this.smoothZoom(this.buttonZoomStep);
            };
            zoomInBtn.style.cursor = 'pointer';
        }
        
        if (zoomOutBtn) {
            zoomOutBtn.onclick = () => {
                console.log('➖ Кнопка УМЕНЬШЕНИЕ нажата!');
                this.smoothZoom(-this.buttonZoomStep);
            };
            zoomOutBtn.style.cursor = 'pointer';
        }
        
        // Обновляем состояние кнопок
        this.updateButtonsState();
    }
    
    handleMouseDown(e) {
        if (e.button !== 0) return;
        e.preventDefault();
        
        // Отключаем анимацию при перетаскивании для мгновенного отклика
        this.image.style.transition = 'none';
        this.startDragging(e.clientX, e.clientY);
    }
    
    handleMouseMove(e) {
        if (!this.isDragging) return;
        e.preventDefault();
        this.drag(e.clientX, e.clientY);
    }
    
    handleMouseUp() {
        this.stopDragging();
        
        // Включаем анимацию обратно
        if (this.zoomAnimation) {
            setTimeout(() => {
                this.image.style.transition = 'transform 0.3s ease-out';
            }, 50);
        }
    }
    
    handleTouchStart(e) {
        if (e.touches.length === 1) {
            e.preventDefault();
            this.image.style.transition = 'none';
            this.startDragging(e.touches[0].clientX, e.touches[0].clientY);
        }
    }
    
    handleTouchMove(e) {
        if (e.touches.length === 1 && this.isDragging) {
            e.preventDefault();
            this.drag(e.touches[0].clientX, e.touches[0].clientY);
        }
    }
    
    handleTouchEnd() {
        this.stopDragging();
        if (this.zoomAnimation) {
            setTimeout(() => {
                this.image.style.transition = 'transform 0.3s ease-out';
            }, 50);
        }
    }
    
    handleWheel(e) {
        e.preventDefault();
        
        // Плавный zoom с небольшой чувствительностью
        const delta = Math.sign(e.deltaY) * -this.zoomSensitivity;
        this.smoothZoom(delta, e.clientX, e.clientY);
    }
    
    startDragging(clientX, clientY) {
        this.isDragging = true;
        this.startX = clientX;
        this.startY = clientY;
        
        const transform = this.getCurrentTransform();
        this.translateX = transform.x;
        this.translateY = transform.y;
        
        this.image.style.cursor = 'grabbing';
    }
    
    drag(clientX, clientY) {
        const dx = clientX - this.startX;
        const dy = clientY - this.startY;
        
        const newX = this.translateX + dx;
        const newY = this.translateY + dy;
        
        this.applyTransform(newX, newY, this.scale);
    }
    
    stopDragging() {
        this.isDragging = false;
        this.image.style.cursor = 'grab';
    }
    
    // Плавное масштабирование
    smoothZoom(delta, clientX = null, clientY = null) {
        const targetScale = Math.max(this.minScale, Math.min(this.maxScale, this.scale + delta));
        
        // Если масштаб не изменился, выходим
        if (targetScale === this.scale) return;
        
        // Включаем анимацию для плавного zoom
        if (this.zoomAnimation) {
            this.image.style.transition = 'transform 0.3s ease-out';
        }
        
        // Если координаты не указаны, zoom к центру
        if (clientX === null || clientY === null) {
            const rect = this.container.getBoundingClientRect();
            clientX = rect.left + rect.width / 2;
            clientY = rect.top + rect.height / 2;
        }
        
        const transform = this.getCurrentTransform();
        const rect = this.image.getBoundingClientRect();
        const containerRect = this.container.getBoundingClientRect();
        
        const offsetX = clientX - containerRect.left - rect.left;
        const offsetY = clientY - containerRect.top - rect.top;
        
        const newX = transform.x - (targetScale - this.scale) * offsetX / this.scale;
        const newY = transform.y - (targetScale - this.scale) * offsetY / this.scale;
        
        this.applyTransform(newX, newY, targetScale);
        
        console.log('🔍 Масштаб:', this.scale.toFixed(2));
    }
    
    // Плавный сброс
    smoothReset() {
        if (this.zoomAnimation) {
            this.image.style.transition = 'transform 0.5s ease-out';
        }
        
        this.scale = 0.3;
        this.applyTransform(0, 0, this.scale);
        
        // Возвращаем обычную анимацию после сброса
        setTimeout(() => {
            if (this.zoomAnimation) {
                this.image.style.transition = 'transform 0.3s ease-out';
            }
        }, 500);
    }
    
    applyTransform(x, y, scale) {
        const clamped = this.clampTranslation(x, y, scale);
        
        this.image.style.transform = `translate(${clamped.x}px, ${clamped.y}px) scale(${scale})`;
        this.scale = scale;
        
        this.updateButtonsState();
    }
    
    clampTranslation(x, y, scale) {
        const containerRect = this.container.getBoundingClientRect();
        const scaledWidth = this.image.naturalWidth * scale;
        const scaledHeight = this.image.naturalHeight * scale;
        
        const maxX = Math.min(0, containerRect.width - scaledWidth);
        const maxY = Math.min(0, containerRect.height - scaledHeight);
        
        return {
            x: Math.max(maxX, Math.min(0, x)),
            y: Math.max(maxY, Math.min(0, y))
        };
    }
    
    getCurrentTransform() {
        const style = window.getComputedStyle(this.image);
        if (!style.transform || style.transform === 'none') {
            return { x: 0, y: 0, scale: this.scale };
        }
        
        const matrix = new DOMMatrixReadOnly(style.transform);
        return {
            x: matrix.m41,
            y: matrix.m42,
            scale: matrix.a
        };
    }
    
    resetTransform() {
        console.log('🔄 Сброс карты');
        this.scale = 0.3;
        this.applyTransform(0, 0, this.scale);
    }
    
    updateButtonsState() {
        const zoomInBtn = document.getElementById('zoomInBtn');
        const zoomOutBtn = document.getElementById('zoomOutBtn');
        
        if (zoomInBtn) {
            const canZoomIn = this.scale < this.maxScale;
            zoomInBtn.disabled = !canZoomIn;
            zoomInBtn.style.opacity = canZoomIn ? '1' : '0.5';
            zoomInBtn.title = canZoomIn ? 'Увеличить' : 'Максимальный масштаб';
        }
        
        if (zoomOutBtn) {
            const canZoomOut = this.scale > this.minScale;
            zoomOutBtn.disabled = !canZoomOut;
            zoomOutBtn.style.opacity = canZoomOut ? '1' : '0.5';
            zoomOutBtn.title = canZoomOut ? 'Уменьшить' : 'Минимальный масштаб';
        }
    }
}

// Автоматическая инициализация
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Инициализация карты...');
    
    setTimeout(() => {
        window.map = new InteractiveMap('mapContainer', 'mapImage');
        
        if (window.map.container) {
            console.log('✅ Карта успешно инициализирована!');
            console.log('🎮 Используйте:');
            console.log('   - ЛКМ: перетаскивание');
            console.log('   - Колесо: плавный масштаб');
            console.log('   - Кнопки: плавное управление');
        }
    }, 100);
});