const container = document.querySelector('.map-container');
const img = document.querySelector('.map-image');

let isDragging = false;
let startX = 0;
let startY = 0;
let translateX = 0;
let translateY = 0;
let scale = 1;

const minScale = 0.8;
const maxScale = 10;

// Начальные установки при загрузке
window.addEventListener('load', () => {
  scale = minScale;
  img.style.transform = `translate(0px, 0px) scale(${scale})`;
});

// Обработка касаний и мыши
function getTransform() {
  const style = window.getComputedStyle(img);
  const matrix = new DOMMatrixReadOnly(style.transform);
  return { x: matrix.m41, y: matrix.m42, scale: matrix.a };
}

// Начало взаимодействия
function startInteraction(e) {
  isDragging = true;
  if (e.type.startsWith('touch')) {
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
  } else {
    startX = e.clientX;
    startY = e.clientY;
  }
  const { x, y } = getTransform();
  translateX = x;
  translateY = y;
}

// Конец взаимодействия
function endInteraction() {
  isDragging = false;
}

// Перетаскивание
function moveInteraction(e) {
  if (!isDragging) return;
  let currentX, currentY;
  if (e.type.startsWith('touch')) {
    currentX = e.touches[0].clientX;
    currentY = e.touches[0].clientY;
  } else {
    currentX = e.clientX;
    currentY = e.clientY;
  }
  const dx = currentX - startX;
  const dy = currentY - startY;

  const containerRect = container.getBoundingClientRect();
  const rect = img.getBoundingClientRect();
  const width = rect.width;
  const height = rect.height;
  const { x, y } = clampTranslate(translateX + dx, translateY + dy, width, height, containerRect.width, containerRect.height);

  img.style.transform = `translate(${x}px, ${y}px) scale(${scale})`;
}

// Ограничение перемещения
function clampTranslate(x, y, width, height, containerW, containerH) {
  const clampedX = Math.min(0, Math.max(x, containerW - width));
  const clampedY = Math.min(0, Math.max(y, containerH - height));
  return { x: clampedX, y: clampedY };
}

// Масштабирование жестами (pinch)
let initialDistance = 0;
let initialScale = scale;

function getDistance(touches) {
  const dx = touches[0].clientX - touches[1].clientX;
  const dy = touches[0].clientY - touches[1].clientY;
  return Math.hypot(dx, dy);
}

function startPinch(e) {
  if (e.touches.length === 2) {
    initialDistance = getDistance(e.touches);
    initialScale = scale;
  }
}

function pinchMove(e) {
  if (e.touches.length === 2) {
    const currentDistance = getDistance(e.touches);
    let newScale = initialScale * (currentDistance / initialDistance);
    if (newScale < minScale) newScale = minScale;
    if (newScale > maxScale) newScale = maxScale;

    // Центр жеста
    const rect = img.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    const centerX = (e.touches[0].clientX + e.touches[1].clientX) / 2 - containerRect.left;
    const centerY = (e.touches[0].clientY + e.touches[1].clientY) / 2 - containerRect.top;

    // Новое смещение для масштабирования относительно центра
    const offsetX = centerX - rect.left;
    const offsetY = centerY - rect.top;

    const prevTransform = getTransform();
    const newX = prevTransform.x - (newScale - prevTransform.scale) * offsetX / prevTransform.scale;
    const newY = prevTransform.y - (newScale - prevTransform.scale) * offsetY / prevTransform.scale;

    const width = rect.width * (newScale / prevTransform.scale);
    const height = rect.height * (newScale / prevTransform.scale);
    const { x, y } = clampTranslate(newX, newY, width, height, containerRect.width, containerRect.height);

    img.style.transform = `translate(${x}px, ${y}px) scale(${newScale})`;
    scale = newScale;
  }
}

// Обработчики
container.addEventListener('mousedown', startInteraction);
container.addEventListener('touchstart', (e) => {
  startInteraction(e);
  startPinch(e);
});
document.addEventListener('mouseup', endInteraction);
document.addEventListener('touchend', endInteraction);
document.addEventListener('touchcancel', endInteraction);
container.addEventListener('mousemove', moveInteraction);
container.addEventListener('touchmove', (e) => {
  moveInteraction(e);
  startPinch(e);
  if (e.touches.length === 2) {
    pinchMove(e);
  }
});

// Масштаб по колесику мыши
container.addEventListener('wheel', (e) => {
  e.preventDefault();

  const delta = Math.sign(e.deltaY);
  const prevScale = scale;
  let newScale = scale - delta * 0.1;

  if (newScale < minScale) newScale = minScale;
  if (newScale > maxScale) newScale = maxScale;

  const rect = img.getBoundingClientRect();
  const containerRect = container.getBoundingClientRect();

  const offsetX = e.clientX - containerRect.left - rect.left;
  const offsetY = e.clientY - containerRect.top - rect.top;

  const newX = getTransform().x - (newScale - prevScale) * offsetX / prevScale;
  const newY = getTransform().y - (newScale - prevScale) * offsetY / prevScale;

  const width = rect.width * (newScale / prevScale);
  const height = rect.height * (newScale / prevScale);
  const { x, y } = clampTranslate(newX, newY, width, height, containerRect.width, containerRect.height);

  img.style.transform = `translate(${x}px, ${y}px) scale(${newScale})`;
  scale = newScale;
});