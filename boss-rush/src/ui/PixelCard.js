import { FONT } from '../config/constants.js';
import { notchedPoints, drawPixelPanel } from './pixelShapes.js';

// Карточка улучшения в стиле pixel-art UI (переработка ТЗ п.6) — предыдущая
// версия ("реалистичный камень", см. git history StoneCard.js) была прямо
// отклонена как несоответствующая пиксельной эстетике игры. Вместо градиента
// и скруглений — ступенчатая (нотч) рамка, плоская заливка, мелкая иконка
// улучшения, собранная из пиксельных квадратов без внешних ассетов.
const BORDER = 0x35354e;
const BORDER_HOVER = 0xffcc00;
const FILL = 0x1b1b28;
const ICON_SLOT_FILL = 0x14141d;
const ACCENT = 0xffcc00;
const TITLE_COLOR = '#ffe9a8';
const DESC_COLOR = '#c9c4b3';
const NOTCH = 10;

// Иконки — 8×8 пиксельная сетка, '#' = закрашенная клетка. Простые узнаваемые
// силуэты вместо внешнего арта: меч (урон), сердце (HP), молния (скорость
// атаки), стрелка (скорость), искра (крит), два росчерка (рывок).
const ICONS = {
  damage: ['.......#', '......#.', '.....#..', '....#...', '..###...', '.#......', '#.......', '........'],
  maxHp: ['.##..##.', '########', '########', '.######.', '..####..', '...##...', '........', '........'],
  attackSpeed: ['....##..', '...##...', '..##....', '.#####..', '....##..', '...##...', '..##....', '........'],
  moveSpeed: ['..#.....', '.##.....', '..##....', '...##...', '..##....', '.##.....', '..#.....', '........'],
  critChance: ['...##...', '...##...', '.#.##.#.', '##....##', '.#.##.#.', '...##...', '...##...', '........'],
  dash: ['.#...#..', '..#...#.', '...#...#', '..#...#.', '.#...#..', '........', '........', '........'],
  default: ['...##...', '..####..', '.######.', '########', '########', '.######.', '..####..', '...##...']
};

function drawIcon(scene, key, centerX, centerY, cell) {
  const pattern = ICONS[key] ?? ICONS.default;
  const size = pattern.length * cell;
  const originX = centerX - size / 2;
  const originY = centerY - size / 2;
  const g = scene.add.graphics();
  g.fillStyle(ACCENT, 1);
  pattern.forEach((row, ry) => {
    for (let rx = 0; rx < row.length; rx++) {
      if (row[rx] === '#') {
        g.fillRect(originX + rx * cell, originY + ry * cell, cell, cell);
      }
    }
  });
  return g;
}

export class PixelCard {
  constructor(scene, x, y, width, height, { title, description, iconKey, onSelect }) {
    // Все созданные объекты трекаются, чтобы карточку можно было полностью
    // убрать со сцены одним вызовом destroy() — нужно для реролла улучшений
    // (ТЗ п.2 "разнообразие забегов"): старые карточки удаляются, новые
    // перерисовываются на их месте.
    const objects = [];
    this.objects = objects;

    const left = x - width / 2;
    const top = y - height / 2;
    const outerPoints = notchedPoints(left, top, width, height, NOTCH);
    const { borderG, fillG } = drawPixelPanel(scene, left, top, width, height, { notch: NOTCH, fill: FILL, border: BORDER });
    objects.push(borderG, fillG);

    // Небольшая внутренняя тень сверху — плоская тёмная полоса под верхним
    // краем, простой способ дать карточке ощущение объёма без градиентов
    // (градиенты явно запрещены в ТЗ для этого экрана).
    const shadow = scene.add.graphics();
    shadow.fillStyle(0x000000, 0.25);
    shadow.fillRect(left + NOTCH, top + NOTCH, width - NOTCH * 2, 6);
    objects.push(shadow);

    // Пиксельные декоративные точки по углам — маленький акцент, не перегружает.
    const dots = scene.add.graphics();
    dots.fillStyle(ACCENT, 0.9);
    const dotSize = 4;
    [[left + 3, top + 3], [left + width - 3 - dotSize, top + 3],
      [left + 3, top + height - 3 - dotSize], [left + width - 3 - dotSize, top + height - 3 - dotSize]]
      .forEach(([dx, dy]) => dots.fillRect(dx, dy, dotSize, dotSize));
    objects.push(dots);

    // Иконка слева в собственном ступенчатом слоте — крупная, узнаваемая.
    const iconSlotSize = height - 32;
    const iconSlotX = left + 24;
    const iconSlotY = top + (height - iconSlotSize) / 2;
    const iconSlot = scene.add.graphics();
    iconSlot.fillStyle(ICON_SLOT_FILL, 1);
    iconSlot.fillPoints(notchedPoints(iconSlotX, iconSlotY, iconSlotSize, iconSlotSize, 6), true);
    iconSlot.lineStyle(2, BORDER, 1);
    iconSlot.strokePoints(notchedPoints(iconSlotX, iconSlotY, iconSlotSize, iconSlotSize, 6), true);
    objects.push(iconSlot);
    const icon = drawIcon(scene, iconKey, iconSlotX + iconSlotSize / 2, iconSlotY + iconSlotSize / 2, Math.floor(iconSlotSize / 10));
    objects.push(icon);

    const textX = iconSlotX + iconSlotSize + 24;
    const textWidth = left + width - 24 - textX;

    objects.push(scene.add.text(textX, top + height / 2 - 22, title, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '15px',
      color: TITLE_COLOR
    }).setOrigin(0, 0.5));

    objects.push(scene.add.text(textX, top + height / 2 + 16, description, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '15px',
      color: DESC_COLOR,
      wordWrap: { width: textWidth },
      lineSpacing: 4
    }).setOrigin(0, 0.5));

    // Выделение при наведении/выборе — мигающая яркая рамка вместо простого
    // затемнения (пиксельный UI обычно выделяет через контраст рамки, не альфу).
    const highlight = scene.add.graphics();
    highlight.lineStyle(3, BORDER_HOVER, 1);
    highlight.strokePoints(outerPoints, true);
    highlight.setAlpha(0);
    objects.push(highlight);
    let blinkTween = null;

    const hitZone = scene.add.rectangle(x, y, width + 8, height + 8, 0x000000, 0)
      .setInteractive({ useHandCursor: true });
    objects.push(hitZone);
    hitZone.on('pointerover', () => {
      blinkTween = scene.tweens.add({ targets: highlight, alpha: { from: 0.4, to: 1 }, duration: 260, yoyo: true, repeat: -1 });
    });
    hitZone.on('pointerout', () => {
      blinkTween?.stop();
      blinkTween = null;
      highlight.setAlpha(0);
    });
    hitZone.on('pointerdown', onSelect);

    this._blinkTweenRef = () => blinkTween;
  }

  destroy() {
    this._blinkTweenRef?.()?.stop();
    this.objects.forEach((obj) => obj.destroy());
  }
}
