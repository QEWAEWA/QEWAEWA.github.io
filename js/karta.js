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
    scale = 0.1;
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

    if (scaledWidth <= containerWidth) {
      left = (containerWidth - scaledWidth) / 2;
    } else {
      left = Math.min(0, Math.max(containerWidth - scaledWidth, left));
    }

    if (scaledHeight <= containerHeight) {
      top = (containerHeight - scaledHeight) / 2;
    } else {
      top = Math.min(0, Math.max(containerHeight - scaledHeight, top));
    }
  }

  // Масштабирование
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

    const rect = img.getBoundingClientRect();
    const offsetXCursor = e.clientX - rect.left;
    const offsetYCursor = e.clientY - rect.top;

    left -= (scale - prevScale) * offsetXCursor;
    top -= (scale - prevScale) * offsetYCursor;

    clampPosition();
    updateStyle();
  });

  // Обработка мышиных событий
  function onMouseDown(e) {
    e.preventDefault();
    isDragging = true;
    startX = e.clientX - left;
    startY = e.clientY - top;
    img.style.cursor = 'grabbing';
  }

  function onMouseUp() {
    if (isDragging) {
      isDragging = false;
      img.style.cursor = 'grab';
    }
  }

  function onMouseMove(e) {
    if (isDragging) {
      left = e.clientX - startX;
      top = e.clientY - startY;
      clampPosition();
      updateStyle();
    }
  }

  // Обработка сенсорных событий
  function onTouchStart(e) {
    if (e.touches.length === 1) {
      isDragging = true;
      startX = e.touches[0].clientX - left;
      startY = e.touches[0].clientY - top;
    }
  }

  function onTouchEnd() {
    if (isDragging) {
      isDragging = false;
    }
  }

  function onTouchMove(e) {
    if (isDragging && e.touches.length === 1) {
      left = e.touches[0].clientX - startX;
      top = e.touches[0].clientY - startY;
      clampPosition();
      updateStyle();
    }
  }

  // Назначение событий
  img.addEventListener('mousedown', onMouseDown);
  document.addEventListener('mouseup', onMouseUp);
  document.addEventListener('mousemove', onMouseMove);

  // Сенсорные события
  img.addEventListener('touchstart', onTouchStart, { passive: false });
  document.addEventListener('touchend', onTouchEnd);
  document.addEventListener('touchcancel', onTouchEnd);
  document.addEventListener('touchmove', onTouchMove, { passive: false });
});