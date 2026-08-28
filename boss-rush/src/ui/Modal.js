import { GAME_WIDTH, GAME_HEIGHT, COLORS, TEXT, FONT } from '../config/constants.js';
import { drawPixelPanel } from './pixelShapes.js';

// Общий каркас модальных окон поверх MenuScene (ТЗ: "Все модальные окна
// должны открываться как оверлеи... пиксельная каменная рамка с зелёными
// рунами... крестик [X] для закрытия"). BossGalleryModal/LeaderboardModal/
// SettingsModal — все три построены на этом классе, чтобы затемнение,
// рамка, крестик и анимация открытия/закрытия не дублировались в каждом.
//
// Все дочерние объекты рисуются в АБСОЛЮТНЫХ координатах сцены (как и весь
// остальной UI в проекте, см. MetaScene/PixelCard) — Graphics.x/y здесь
// используется только как аддитивный сдвиг для входной анимации (slide+fade),
// не как origin для масштабирования, поэтому Container с локальными
// координатами не нужен.
const RUNE_GREEN = 0x4ce27a;
const PANEL_NOTCH = 16;
const SLIDE_OFFSET = -22;

export class Modal {
  constructor(scene, { width, height, title, onClose } = {}) {
    this.scene = scene;
    this.width = width;
    this.height = height;
    this.left = (GAME_WIDTH - width) / 2;
    this.top = (GAME_HEIGHT - height) / 2;
    this.onClose = onClose;
    this.contentObjects = [];

    this.backdrop = scene.add.rectangle(GAME_WIDTH / 2, GAME_HEIGHT / 2, GAME_WIDTH, GAME_HEIGHT, 0x000000, 0)
      .setInteractive();
    // Клик по затемнению закрывает окно (стандартное поведение поповера),
    // но не должен "проваливаться" дальше в кнопки меню под ним — Phaser
    // сам останавливает propagation для interactive-объектов сверху стека.
    this.backdrop.on('pointerdown', () => this.close());

    this.panelObjects = [];
    const { borderG, fillG } = drawPixelPanel(scene, this.left, this.top, width, height, {
      notch: PANEL_NOTCH, fill: COLORS.panelFill, border: COLORS.panelBorder
    });
    this.panelObjects.push(borderG, fillG);

    // Зелёные рунические акценты по углам рамки (ТЗ: "каменная рамка с
    // зелёными рунами") — простые пиксельные глифы вместо внешнего тайлсета,
    // тем же приёмом, что иконки в PixelCard.
    this.drawRuneCorners();

    if (title) {
      this.titleText = scene.add.text(GAME_WIDTH / 2, this.top + 34, title, {
        fontFamily: FONT.display, resolution: 3,
        fontSize: '20px',
        color: TEXT.accent,
        fontStyle: 'bold'
      }).setOrigin(0.5);
      this.panelObjects.push(this.titleText);
    }

    this.closeButton = scene.add.text(this.left + width - 28, this.top + 26, '[X]', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '16px',
      color: TEXT.danger,
      fontStyle: 'bold'
    }).setOrigin(0.5).setInteractive({ useHandCursor: true });
    this.closeButton.on('pointerover', () => this.closeButton.setScale(1.15));
    this.closeButton.on('pointerout', () => this.closeButton.setScale(1));
    this.closeButton.on('pointerdown', () => this.close());
    this.panelObjects.push(this.closeButton);

    // Контентная область под заголовком — content-модули (BossGalleryModal и
    // т.д.) рисуют внутри этих границ.
    this.contentTop = this.top + (title ? 64 : 26);
    this.contentLeft = this.left + 28;
    this.contentWidth = width - 56;
    this.contentBottom = this.top + height - 24;

    // open() не вызывается здесь автоматически: content-модули (BossGalleryModal
    // и т.д.) сначала дорисовывают своё содержимое (стрелки, вкладки, строки) в
    // this.panelObjects/track(), и только потом сами вызывают modal.open(),
    // чтобы всё окно целиком (рамка + контент) появлялось одной анимацией.
  }

  drawRuneCorners() {
    const glyph = [
      ['.#.', '#.#', '.#.'],
      ['##.', '.#.', '.##'],
      ['#.#', '.#.', '#.#']
    ];
    const cell = 4;
    const positions = [
      [this.left + 10, this.top + 10],
      [this.left + this.width - 10 - glyph[0].length * cell, this.top + 10],
      [this.left + 10, this.top + this.height - 10 - glyph.length * cell],
      [this.left + this.width - 10 - glyph[0].length * cell, this.top + this.height - 10 - glyph.length * cell]
    ];
    positions.forEach(([px, py], i) => {
      const pattern = glyph[i % glyph.length];
      const g = this.scene.add.graphics();
      g.fillStyle(RUNE_GREEN, 0.85);
      pattern.forEach((row, ry) => {
        for (let rx = 0; rx < row.length; rx++) {
          if (row[rx] === '#') g.fillRect(px + rx * cell, py + ry * cell, cell, cell);
        }
      });
      this.panelObjects.push(g);
    });
  }

  // Content-модули регистрируют свои объекты здесь, чтобы close()/redraw
  // могли их корректно удалить вместе с рамкой.
  track(obj) {
    this.contentObjects.push(obj);
    return obj;
  }

  trackAll(objs) {
    objs.forEach((o) => this.track(o));
  }

  // Удаляет только контентные объекты (для перерисовки вкладок/страниц
  // внутри окна), оставляя саму рамку и крестик на месте.
  clearContent() {
    this.contentObjects.forEach((o) => o.destroy());
    this.contentObjects = [];
  }

  open() {
    const all = [...this.panelObjects, ...this.contentObjects];
    all.forEach((obj) => {
      obj.setAlpha(0);
      obj.y += SLIDE_OFFSET;
    });
    this.backdrop.setAlpha(0);
    this.scene.tweens.add({ targets: this.backdrop, alpha: 0.72, duration: 160 });
    this.scene.tweens.add({
      targets: all,
      alpha: 1,
      y: `-=${SLIDE_OFFSET}`,
      duration: 220,
      ease: 'Back.easeOut'
    });
  }

  close() {
    if (this.closed) return;
    this.closed = true;
    const all = [...this.panelObjects, ...this.contentObjects];
    this.scene.tweens.add({ targets: this.backdrop, alpha: 0, duration: 150 });
    this.scene.tweens.add({
      targets: all,
      alpha: 0,
      duration: 150,
      onComplete: () => {
        this.backdrop.destroy();
        all.forEach((obj) => obj.destroy());
        this.onClose?.();
      }
    });
  }
}
