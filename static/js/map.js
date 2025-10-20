class InteractiveMap {
    constructor(containerId, imageId) {
        console.log('🗺️ Начинаем инициализацию карты...');
        
        this.container = document.getElementById(containerId);
        this.image = document.getElementById(imageId);
        
        console.log('Контейнер:', this.container);
        console.log('Изображение:', this.image);
        
        if (!this.container) {
            console.error('❌ Контейнер карты не найден! ID:', containerId);
            return;
        }
        
        if (!this.image) {
            console.error('❌ Изображение карты не найдено! ID:', imageId);
            return;
        }
        
        this.isDragging = false;
        this.startX = 0;
        this.startY = 0;
        this.translateX = 0;
        this.translateY = 0;
        this.scale = 0.1; // Начальный масштаб - уменьшена
        
        this.minScale = 0.1;
        this.maxScale = 12;
        
        this.init();
    }
    
    init() {
        console.log('🔄 Инициализация карты...');
        
        // Ждем загрузки изображения
        if (this.image.complete) {
            this.setupMap();
        } else {
            this.image.addEventListener('load', () => this.setupMap());
            this.image.addEventListener('error', () => {
                console.error('❌ Ошибка загрузки изображения карты');
            });
        }
    }
    
    setupMap() {
        console.log('🖼️ Изображение карты загружено, настраиваем...');
        
        // Настройка стилей
        this.image.style.cursor = 'grab';
        this.image.style.transformOrigin = '0 0';
        this.image.style.userSelect = 'none';
        this.image.style.webkitUserSelect = 'none';
        
        // Применяем начальный масштаб
        this.applyTransform(0, 0, this.scale);
        
        // Настройка событий
        this.setupEventListeners();
        this.setupControls();
        
        console.log('✅ Карта полностью инициализирована');
    }
    
    setupEventListeners() {
        console.log('🎯 Настройка событий мыши и касаний...');
        
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
        
        console.log('✅ События настроены');
    }
    
    setupControls() {
        console.log('🎛️ Настройка кнопок управления...');
        
        // Находим кнопки по ID
        this.resetBtn = document.getElementById('resetBtn');
        this.zoomInBtn = document.getElementById('zoomInBtn');
        this.zoomOutBtn = document.getElementById('zoomOutBtn');
        
        console.log('Кнопка сброса:', this.resetBtn);
        console.log('Кнопка увеличения:', this.zoomInBtn);
        console.log('Кнопка уменьшения:', this.zoomOutBtn);
        
        // Проверяем и настраиваем кнопки
        if (this.resetBtn) {
            this.resetBtn.addEventListener('click', () => {
                console.log('🔄 Кнопка сброса нажата');
                this.resetTransform();
            });
            console.log('✅ Кнопка сброса подключена');
        } else {
            console.error('❌ Кнопка сброса не найдена!');
        }
        
        if (this.zoomInBtn) {
            this.zoomInBtn.addEventListener('click', () => {
                console.log('➕ Кнопка увеличения нажата');
                this.zoom(0.3);
            });
            console.log('✅ Кнопка увеличения подключена');
        } else {
            console.error('❌ Кнопка увеличения не найдена!');
        }
        
        if (this.zoomOutBtn) {
            this.zoomOutBtn.addEventListener('click', () => {
                console.log('➖ Кнопка уменьшения нажата');
                this.zoom(-0.3);
            });
            console.log('✅ Кнопка уменьшения подключена');
        } else {
            console.error('❌ Кнопка уменьшения не найдена!');
        }
        
        // Обновляем состояние кнопок
        this.updateButtonsState();
        
        console.log('🎛️ Все кнопки настроены');
    }
    
    handleMouseDown(e) {
        if (e.button !== 0) return; // Только левая кнопка мыши
        
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
        const delta = Math.sign(e.deltaY) * -0.15;
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
        
        console.log(`🔍 Zoom: ${this.scale.toFixed(2)} -> ${newScale.toFixed(2)}`);
        
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
    }
    
    applyTransform(x, y, scale) {
        const clamped = this.clampTranslation(x, y, scale);
        
        this.image.style.transform = `translate(${clamped.x}px, ${clamped.y}px) scale(${scale})`;
        this.scale = scale;
        
        // Обновляем состояние кнопок
        this.updateButtonsState();
        
        console.log(`🔄 Transform: translate(${clamped.x.toFixed(1)}px, ${clamped.y.toFixed(1)}px) scale(${scale.toFixed(2)})`);
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
        console.log('🔄 Сброс карты к начальному состоянию');
        this.scale = 0.5;
        this.applyTransform(0, 0, this.scale);
    }
    
    updateButtonsState() {
        if (this.zoomInBtn) {
            const canZoomIn = this.scale < this.maxScale;
            this.zoomInBtn.disabled = !canZoomIn;
            this.zoomInBtn.style.opacity = canZoomIn ? '1' : '0.5';
            this.zoomInBtn.title = canZoomIn ? 'Увеличить' : 'Максимальный масштаб';
        }
        
        if (this.zoomOutBtn) {
            const canZoomOut = this.scale > this.minScale;
            this.zoomOutBtn.disabled = !canZoomOut;
            this.zoomOutBtn.style.opacity = canZoomOut ? '1' : '0.5';
            this.zoomOutBtn.title = canZoomOut ? 'Уменьшить' : 'Минимальный масштаб';
        }
        
        console.log(`🎛️ Состояние кнопок: ZoomIn=${!this.zoomInBtn?.disabled}, ZoomOut=${!this.zoomOutBtn?.disabled}`);
    }
}

// Глобальная функция для ручного вызова (на всякий случай)
window.resetMap = function() {
    if (window.map) {
        window.map.resetTransform();
    } else {
        console.error('❌ Карта не инициализирована!');
    }
};

window.zoomIn = function() {
    if (window.map) {
        window.map.zoom(0.3);
    } else {
        console.error('❌ Карта не инициализирована!');
    }
};

window.zoomOut = function() {
    if (window.map) {
        window.map.zoom(-0.3);
    } else {
        console.error('❌ Карта не инициализирована!');
    }
};

// Автоматическая инициализация
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM полностью загружен');
    console.log('🚀 Запуск инициализации карты...');
    
    // Небольшая задержка для гарантии
    setTimeout(() => {
        window.map = new InteractiveMap('mapContainer', 'mapImage');
        
        if (window.map && window.map.container) {
            console.log('✅ Карта успешно создана и готова к использованию!');
            console.log('🎮 Доступные действия:');
            console.log('   - Перетаскивание: зажать левую кнопку мыши на карте');
            console.log('   - Масштаб: колесо мыши или кнопки +/-');
            console.log('   - Сброс: кнопка ⟲');
        } else {
            console.error('❌ Не удалось создать карту!');
        }
    }, 100);
});

console.log('🗺️ Скрипт карты загружен, ожидаем DOM...');