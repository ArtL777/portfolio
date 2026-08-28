// Общая геометрия для ступенчатых (нотч) пиксельных панелей — единый визуальный
// язык вместо скруглённых fillRoundedRect (ТЗ переработки интерфейса, п.4:
// "не используй... минималистичные rounded cards"). Используется и HUD-панелями
// в канвасе, и карточками улучшений, и панелью результата — один приём, не три разных.
export function notchedPoints(x, y, w, h, notch) {
  return [
    { x, y: y + notch },
    { x: x + notch, y },
    { x: x + w - notch, y },
    { x: x + w, y: y + notch },
    { x: x + w, y: y + h - notch },
    { x: x + w - notch, y: y + h },
    { x: x + notch, y: y + h },
    { x, y: y + h - notch }
  ];
}

// Рисует двухслойную ступенчатую панель (бортик + заливка), как в PixelCard/
// HUD-панелях — возвращает graphics-объекты на случай, если вызывающий код
// захочет их потом уничтожить/анимировать.
export function drawPixelPanel(scene, x, y, w, h, { notch = 10, fill, border } = {}) {
  const borderG = scene.add.graphics();
  borderG.fillStyle(border, 1);
  borderG.fillPoints(notchedPoints(x - 4, y - 4, w + 8, h + 8, notch + 3), true);

  const fillG = scene.add.graphics();
  fillG.fillStyle(fill, 1);
  fillG.fillPoints(notchedPoints(x, y, w, h, notch), true);

  return { borderG, fillG };
}
