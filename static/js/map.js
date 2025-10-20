class InteractiveMap {
    constructor(containerId, imageId) {
        this.container = document.getElementById(containerId);
        this.image = document.getElementById(imageId);
        
        if (!this.container || !this.image) {
            console.error('❌ Контейнер или изображение карты не найдены!');
            return;
        }
        
        this.isDragging = false;
        this.startX = 0;
        this.startY = 0;
        this.translateX = 0;
        this.translateY = 0;
        this.scale = 0.5; // Начальный масштаб - уменьшена
        
        this.minScale = 0.1; // Можно сильнее отдалять
        this.maxScale = 8;   // Можно сильнее приближать
        
        this.init();
    }
    
    init() {
        console.log('🗺️ Инициализация карты...');
        
        // Ждем загрузки изображения
        if (this.image.complete) {
            this.setupMap();
        } else {
            this.image.onload = () => this.setupMap();
        }
        
        this.image.onerror = () => {
            console.error('❌ Ошибка загрузки изображения карты');
        };
    }
    
    setupMap() {
        console.log('🖼️ Изображение карты загружено');
        
        // Настройка стилей
        this.image.style.cursor = 'grab';
        this.image.style.transformOrigin = '0 0';
        this.image.style.userSelect = 'none';
        
        // Применяем начальный масштаб
        this.applyTransform(0, 0, this.scale);
        
        // Настройка событий
        this.setupEventListeners();
        this.setupControls();
        
        console.log('✅ Карта инициализирована. Масштаб:', this.scale);
    }
    
    setupEventListeners() {
        // Мышь
        this.container.addEventListener('mousedown', this.handleMouseDown.bind(this));
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        document.addEventListener('mouseup', this.handleMouseUp.bind(this));
        
        // Касания (для мобильных)
        this.container.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        document.addEventListener('touchend', this.handleTouchEnd.bind(this));
        
        // Колесо мыши
        this.container.addEventListener('wheel', this.handleWheel.bind(this), { passive: false });
        
        // Предотвращение контекстного меню
        this.container.addEventListener('contextmenu', (e) => e.preventDefault());
    }
    
    setupControls() {
        // Кнопка сброса
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetTransform());
        }
        
        // Кнопка увеличения
        const zoomInBtn = document.getElementById('zoomInBtn');
        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => this.zoom(0.3));
        }
        
        // Кнопка уменьшения
        const zoomOutBtn = document.getElementById('zoomOutBtn');
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => this.zoom(-0.3));
        }
        
        console.log('🎛️ Кнопки управления подключены');
    }
    
    handleMouseDown(e) {
        // Игнорируем правую кнопку мыши
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
        const delta = Math.sign(e.deltaY) * -0.15; // Более плавный zoom
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
        
        // Вычисляем смещение для zoom к курсору
        const offsetX = clientX - containerRect.left - rect.left;
        const offsetY = clientY - containerRect.top - rect.top;
        
        const newX = transform.x - (newScale - this.scale) * offsetX / this.scale;
        const newY = transform.y - (newScale - this.scale) * offsetY / this.scale;
        
        this.applyTransform(newX, newY, newScale);
        
        console.log('🔍 Масштаб изменен:', this.scale.toFixed(2));
    }
    
    applyTransform(x, y, scale) {
        const clamped = this.clampTranslation(x, y, scale);
        
        // Применяем трансформацию
        this.image.style.transform = `translate(${clamped.x}px, ${clamped.y}px) scale(${scale})`;
        this.scale = scale;
        
        // Обновляем состояние кнопок
        this.updateButtonsState();
    }
    
    clampTranslation(x, y, scale) {
        const containerRect = this.container.getBoundingClientRect();
        const imgRect = this.image.getBoundingClientRect();
        
        const scaledWidth = this.image.naturalWidth * scale;
        const scaledHeight = this.image.naturalHeight * scale;
        
        // Вычисляем границы
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
        this.scale = 0.5; // Возвращаем к начальному уменьшенному виду
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

// Автоматическая инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM загружен, инициализируем карту...');
    
    // Даем небольшую задержку для полной загрузки
    setTimeout(() => {
        window.map = new InteractiveMap('mapContainer', 'mapImage');
        
        if (window.map) {
            console.log('✅ Карта успешно создана');
            console.log('🎮 Управление:');
            console.log('   - Перетаскивание: зажать левую кнопку мыши');
            console.log('   - Масштаб: колесо мыши или кнопки +/-');
            console.log('   - Сброс: кнопка ⟲');
        }
    }, 100);
});