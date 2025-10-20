class InteractiveMap {
    constructor(container, image) {
        this.container = container;
        this.image = image;
        
        this.isDragging = false;
        this.startX = 0;
        this.startY = 0;
        this.translateX = 0;
        this.translateY = 0;
        this.scale = 1;
        
        this.minScale = 0.3;
        this.maxScale = 10;
        
        this.initialDistance = 0;
        this.initialScale = 1;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.resetTransform();
    }
    
    setupEventListeners() {
        // Мышь
        this.container.addEventListener('mousedown', this.handleMouseDown.bind(this));
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        document.addEventListener('mouseup', this.handleMouseUp.bind(this));
        
        // Касания
        this.container.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false });
        document.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
        document.addEventListener('touchend', this.handleTouchEnd.bind(this));
        
        // Колесо мыши
        this.container.addEventListener('wheel', this.handleWheel.bind(this), { passive: false });
        
        // Сброс при изменении размера окна
        window.addEventListener('resize', this.debounce(this.resetTransform.bind(this), 250));
    }
    
    handleMouseDown(e) {
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
        } else if (e.touches.length === 2) {
            e.preventDefault();
            this.startPinch(e.touches);
        }
    }
    
    handleTouchMove(e) {
        if (e.touches.length === 1 && this.isDragging) {
            e.preventDefault();
            this.drag(e.touches[0].clientX, e.touches[0].clientY);
        } else if (e.touches.length === 2) {
            e.preventDefault();
            this.pinch(e.touches);
        }
    }
    
    handleTouchEnd() {
        this.stopDragging();
    }
    
    handleWheel(e) {
        e.preventDefault();
        const delta = Math.sign(e.deltaY) * -0.2; // Инвертируем для привычного zoom
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
    
    startPinch(touches) {
        this.initialDistance = this.getTouchDistance(touches);
        this.initialScale = this.scale;
    }
    
    pinch(touches) {
        if (touches.length !== 2) return;
        
        const currentDistance = this.getTouchDistance(touches);
        const scaleFactor = currentDistance / this.initialDistance;
        let newScale = this.initialScale * scaleFactor;
        
        // Ограничение масштаба
        newScale = Math.max(this.minScale, Math.min(this.maxScale, newScale));
        
        // Масштабирование относительно центра жеста
        const center = this.getTouchCenter(touches);
        this.zoomToScale(newScale, center.x, center.y);
    }
    
    zoom(delta, clientX, clientY) {
        const newScale = Math.max(this.minScale, Math.min(this.maxScale, this.scale + delta));
        this.zoomToScale(newScale, clientX, clientY);
    }
    
    zoomToScale(newScale, clientX, clientY) {
        const transform = this.getCurrentTransform();
        const rect = this.image.getBoundingClientRect();
        const containerRect = this.container.getBoundingClientRect();
        
        // Вычисляем смещение для zoom к курсору
        const offsetX = clientX - containerRect.left - rect.left;
        const offsetY = clientY - containerRect.top - rect.top;
        
        const scaleRatio = newScale / this.scale;
        const newX = transform.x - (newScale - this.scale) * offsetX / this.scale;
        const newY = transform.y - (newScale - this.scale) * offsetY / this.scale;
        
        this.applyTransform(newX, newY, newScale);
    }
    
    applyTransform(x, y, scale) {
        const clamped = this.clampTranslation(x, y, scale);
        this.image.style.transform = `translate(${clamped.x}px, ${clamped.y}px) scale(${scale})`;
        this.scale = scale;
    }
    
    clampTranslation(x, y, scale) {
        const rect = this.image.getBoundingClientRect();
        const containerRect = this.container.getBoundingClientRect();
        
        const scaledWidth = rect.width * (scale / this.scale);
        const scaledHeight = rect.height * (scale / this.scale);
        
        const maxX = Math.min(0, containerRect.width - scaledWidth);
        const maxY = Math.min(0, containerRect.height - scaledHeight);
        
        return {
            x: Math.max(maxX, Math.min(0, x)),
            y: Math.max(maxY, Math.min(0, y))
        };
    }
    
    getCurrentTransform() {
        const style = window.getComputedStyle(this.image);
        const matrix = new DOMMatrixReadOnly(style.transform);
        return {
            x: matrix.m41,
            y: matrix.m42,
            scale: matrix.a
        };
    }
    
    getTouchDistance(touches) {
        const dx = touches[0].clientX - touches[1].clientX;
        const dy = touches[0].clientY - touches[1].clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    getTouchCenter(touches) {
        const containerRect = this.container.getBoundingClientRect();
        return {
            x: (touches[0].clientX + touches[1].clientX) / 2 - containerRect.left,
            y: (touches[0].clientY + touches[1].clientY) / 2 - containerRect.top
        };
    }
    
    resetTransform() {
        this.scale = this.minScale;
        this.applyTransform(0, 0, this.scale);
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Автоматическая инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.map-container');
    const image = document.querySelector('.map-image');
    
    if (container && image) {
        new InteractiveMap(container, image);
    }
});