window.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.container');
  const img = document.getElementById('zoomable');

  let scale = 1;
  let left = 0; // позиция изображения
  let top = 0;

  let isDragging = false;
  let startX = 0;
  let startY = 0;

  let containerWidth = container.clientWidth;
  let containerHeight = container.clientHeight;

  // Обновляем размеры контейнера при изменении окна
  window.addEventListener('resize', () => {
    containerWidth = container.clientWidth;
    containerHeight = container.clientHeight;
    clampPosition();
    updateStyle();
  });

  // Изначальная установка масштаба при загрузке изображения
  img.onload = () => {
    // Установка минимального масштаба — максимально отдалено
    scale = 0.1;

    // Расчет начальной позиции, чтобы изображение было по центру
    const scaledWidth = img.naturalWidth * scale;
    const scaledHeight = img.naturalHeight * scale;
    left = (containerWidth - scaledWidth) / 2;
    top = (containerHeight - scaledHeight) / 2;

    updateStyle();
  };

  function updateStyle() {
    img.style.width = `${img.naturalWidth * scale}px`;
    img.style.height = `${img.naturalHeight * scale}px`;
    img.style.left = `${left}px`;
    img.style.top = `${top}px`;
  }

  function clampPosition() {
    const scaledWidth = img.naturalWidth * scale;
    const scaledHeight = img.naturalHeight * scale;

    // Ограничение по горизонтали
    if (scaledWidth <= containerWidth) {
      left = (containerWidth - scaledWidth) / 2;
    } else {
      left = Math.min(0, Math.max(containerWidth - scaledWidth, left));
    }

    // Ограничение по вертикали
    if (scaledHeight <= containerHeight) {
      top = (containerHeight - scaledHeight) / 2;
    } else {
      top = Math.min(0, Math.max(containerHeight - scaledHeight, top));
    }
  }

  // Масштабирование относительно курсора
  container.addEventListener('wheel', (e) => {
    e.preventDefault();
    const zoomFactor = 0.1;
    const prevScale = scale;

    if (e.deltaY < 0) {
      scale += zoomFactor;
    } else {
      scale -= zoomFactor;
    }
    scale = Math.max(0.1, scale);

    // Расчет точки масштабирования относительно курсора
    const rect = img.getBoundingClientRect();
    const offsetXCursor = e.clientX - rect.left;
    const offsetYCursor = e.clientY - rect.top;

    // Корректировка позиции так, чтобы точка масштабирования оставалась на месте
    left -= (scale - prevScale) * offsetXCursor;
    top -= (scale - prevScale) * offsetYCursor;

    clampPosition();
    updateStyle();
  });

  // Обработка начала перетаскивания
  img.addEventListener('mousedown', (e) => {
    e.preventDefault();
    isDragging = true;
    startX = e.clientX - left;
    startY = e.clientY - top;
    img.style.cursor = 'grabbing';
  });

  // Обработка отпускания мыши
  document.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      img.style.cursor = 'grab';
    }
  });

  // Обработка движения мыши при перетаскивании
  document.addEventListener('mousemove', (e) => {
    if (isDragging) {
      left = e.clientX - startX;
      top = e.clientY - startY;
      clampPosition();
      updateStyle();
    }
  });
});