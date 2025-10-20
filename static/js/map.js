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
        this.scale = 0.3; // Еще более уменьшена изначально
        
        this.minScale = 0.1; // Можно очень сильно отдалять
        this.maxScale = 8;
        
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
        
        // Колесо мыши
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
                this.resetTransform();
            };
            resetBtn.style.cursor = 'pointer';
        }
        
        if (zoomInBtn) {
            zoomInBtn.onclick = () => {
                console.log('➕ Кнопка УВЕЛИЧЕНИЕ нажата!');
                this.zoom(0.4);
            };
            zoomInBtn.style.cursor = 'pointer';
        }
        
        if (zoomOutBtn) {
            zoomOutBtn.onclick = () => {
                console.log('➖ Кнопка УМЕНЬШЕНИЕ нажата!');
                this.zoom(-0.4);
            };
            zoomOutBtn.style.cursor = 'pointer';
        }
        
        // Обновляем состояние кнопок
        this.updateButtonsState();
    }
    
    handleMouseDown(e) {
        if (e.button !== 0) return;
        e.preventDefault();
        this.startDragging(e.clientX, e.clientY);
    }
    
    handleMouseMove(e) {
        if (!this.isDragging) return;
        e.preventDefault();
        this.drag(e.clientX, e.clientY);
    }
    
    handleMouseUp() {
        this.stopDragging();
    }
    
    handleTouchStart(e) {
        if (e.touches.length === 1) {
            e.preventDefault();
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
    }
    
    handleWheel(e) {
        e.preventDefault();
        const delta = Math.sign(e.deltaY) * -0.2;
        this.zoom(delta, e.clientX, e.clientY);
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
    
    zoom(delta, clientX = null, clientY = null) {
        const newScale = Math.max(this.minScale, Math.min(this.maxScale, this.scale + delta));
        
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
        
        const newX = transform.x - (newScale - this.scale) * offsetX / this.scale;
        const newY = transform.y - (newScale - this.scale) * offsetY / this.scale;
        
        this.applyTransform(newX, newY, newScale);
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
            zoomInBtn.disabled = this.scale >= this.maxScale;
            zoomInBtn.style.opacity = this.scale >= this.maxScale ? '0.5' : '1';
        }
        
        if (zoomOutBtn) {
            zoomOutBtn.disabled = this.scale <= this.minScale;
            zoomOutBtn.style.opacity = this.scale <= this.minScale ? '0.5' : '1';
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
            console.log('   - Колесо: масштаб');
            console.log('   - Кнопки: управление');
        }
    }, 100);
});