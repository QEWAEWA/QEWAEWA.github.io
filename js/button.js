const buttons = document.querySelectorAll('.bottom-right-links .btn');

buttons.forEach((btn, index) => {
  btn.addEventListener('mouseenter', () => {
    // Увеличиваем текущую кнопку
    btn.style.transform = 'scale(1.2)';
    // Смещаем соседние кнопки
    buttons.forEach((other, idx) => {
      if (other !== btn) {
        if (idx < index) {
          // слева
          other.style.transform = 'translateX(-10px)';
        } else {
          // справа
          other.style.transform = 'translateX(10px)';
        }
      }
    });
  });

  btn.addEventListener('mouseleave', () => {
    // Возвращаем всё к исходному состоянию
    btn.style.transform = '';
    buttons.forEach(other => {
      other.style.transform = '';
    });
  });
});