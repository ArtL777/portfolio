import { GAME_WIDTH, COLORS, TEXT, FONT } from '../config/constants.js';
import { Modal } from './Modal.js';
import { drawPixelPanel } from './pixelShapes.js';
import { statsManager } from '../managers/StatsManager.js';
import { TOTAL_BOSSES } from '../managers/BossManager.js';

// Порядок и ключи текстур ДОЛЖНЫ совпадать с BOSS_CLASSES в BossManager.js
// (Slime, Golem, Dragon, Robot, SpaceWorm) — сами классы боссов сюда не
// импортируются намеренно: Boss конструктор создаёт спрайт+physics body и
// ожидает живую боевую сцену, разворачивать полноценного босса ради иконки
// в меню было бы лишним весом ради одной картинки.
const BOSS_INFO = [
  { name: 'Слизень', iconKey: 'galleryIconSlime', frame: 0 },
  { name: 'Голем', iconKey: 'galleryIconGolem', frame: 0 },
  { name: 'Дракон', iconKey: 'galleryIconDragon', frame: 0 },
  { name: 'Робот', iconKey: 'galleryIconRobot', frame: 0 },
  { name: 'Космический червь', iconKey: 'galleryIconWorm', frame: 0 }
];

// Заранее объявляем ключи текстур, которые должна загрузить сцена-владелец
// (см. MenuScene.preload) — экспортируем, чтобы список путей жил в одном месте.
export const BOSS_ICON_ASSETS = [
  { key: 'galleryIconSlime', path: 'assets/images/slime_idle.png', frameWidth: 32, frameHeight: 32 },
  { key: 'galleryIconGolem', path: 'assets/images/golem_idle.png', frameWidth: 64, frameHeight: 64 },
  { key: 'galleryIconDragon', path: 'assets/images/dragon_idle.png', frameWidth: 64, frameHeight: 64 },
  { key: 'galleryIconRobot', path: 'assets/images/robot_idle.png', frameWidth: 64, frameHeight: 64 },
  { key: 'galleryIconWorm', path: 'assets/images/worm_idle.png', frameWidth: 64, frameHeight: 64 }
];

function formatTime(seconds) {
  if (seconds === undefined || seconds === null) return '—';
  return `${seconds} сек.`;
}

export function openBossGallery(scene, { soundManager, onClose }) {
  const modal = new Modal(scene, { width: 560, height: 560, title: 'БЕСТИАРИЙ', onClose });
  let index = 0;

  const iconY = modal.contentTop + 130;
  const nameY = iconY + 140;

  function isUnlocked(i) {
    return i === 0 || statsManager.bestBossesBeaten >= i;
  }

  function draw() {
    modal.clearContent();
    const info = BOSS_INFO[index];
    const unlocked = isUnlocked(index);

    // Слот под иконку — тот же ступенчатый приём, что и у PixelCard.
    const slotSize = 220;
    const slotX = GAME_WIDTH / 2 - slotSize / 2;
    const slotY = iconY - slotSize / 2;
    const { borderG, fillG } = drawPixelPanel(scene, slotX, slotY, slotSize, slotSize, {
      notch: 14, fill: COLORS.barBg, border: COLORS.panelBorder
    });
    modal.trackAll([borderG, fillG]);

    const icon = scene.add.image(GAME_WIDTH / 2, iconY, info.iconKey, info.frame);
    const srcSize = Math.max(icon.width, icon.height);
    icon.setDisplaySize((icon.width / srcSize) * (slotSize - 24), (icon.height / srcSize) * (slotSize - 24));
    if (!unlocked) icon.setTint(0x101010).setAlpha(0.85);
    else {
      scene.tweens.add({ targets: icon, scale: icon.scale * 1.05, duration: 900, yoyo: true, repeat: -1, ease: 'Sine.easeInOut' });
    }
    modal.track(icon);

    modal.track(scene.add.text(GAME_WIDTH / 2, nameY, unlocked ? info.name.toUpperCase() : '???', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '26px',
      color: unlocked ? TEXT.primary : TEXT.muted,
      fontStyle: 'bold'
    }).setOrigin(0.5));

    if (!unlocked) {
      modal.track(scene.add.text(GAME_WIDTH / 2, nameY + 42, 'LOCKED', {
        fontFamily: FONT.display, resolution: 3,
        fontSize: '18px',
        color: TEXT.danger,
        fontStyle: 'bold'
      }).setOrigin(0.5));
      modal.track(scene.add.text(GAME_WIDTH / 2, nameY + 82, 'Победите предыдущего босса,\nчтобы открыть', {
        fontFamily: FONT.body, resolution: 3,
        fontSize: '16px',
        color: TEXT.muted,
        align: 'center',
        lineSpacing: 6
      }).setOrigin(0.5));
    } else {
      // Индикатор сложности — пиксельные квадраты, часть закрашена по индексу
      // босса (первый — самый лёгкий, последний — самый сложный).
      const pipCount = 5;
      const pipSize = 16;
      const pipGap = 7;
      const totalW = pipCount * pipSize + (pipCount - 1) * pipGap;
      const pipStartX = GAME_WIDTH / 2 - totalW / 2;
      const labelY = nameY + 48;
      const pipY = labelY + 26;
      modal.track(scene.add.text(GAME_WIDTH / 2, labelY, 'СЛОЖНОСТЬ', {
        fontFamily: FONT.body, resolution: 3,
        fontSize: '16px',
        color: TEXT.muted
      }).setOrigin(0.5));
      const pipsG = scene.add.graphics();
      for (let i = 0; i < pipCount; i++) {
        const filled = i <= index;
        pipsG.fillStyle(filled ? COLORS.accent : COLORS.barBg, 1);
        pipsG.fillRect(pipStartX + i * (pipSize + pipGap), pipY, pipSize, pipSize);
        pipsG.lineStyle(2, COLORS.panelBorder, 1);
        pipsG.strokeRect(pipStartX + i * (pipSize + pipGap), pipY, pipSize, pipSize);
      }
      modal.track(pipsG);

      const bestTime = statsManager.bestBossTimes[index];
      modal.track(scene.add.text(GAME_WIDTH / 2, pipY + 56, `Лучшее время победы: ${formatTime(bestTime)}`, {
        fontFamily: FONT.body, resolution: 3,
        fontSize: '18px',
        color: TEXT.accent
      }).setOrigin(0.5));
    }

    modal.track(scene.add.text(GAME_WIDTH / 2, modal.contentBottom - 18, `${index + 1} / ${TOTAL_BOSSES}`, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '15px',
      color: TEXT.muted
    }).setOrigin(0.5));

    prevArrow.setAlpha(index > 0 ? 1 : 0.3);
    prevArrow.disableInteractive();
    if (index > 0) prevArrow.setInteractive({ useHandCursor: true });
    nextArrow.setAlpha(index < BOSS_INFO.length - 1 ? 1 : 0.3);
    nextArrow.disableInteractive();
    if (index < BOSS_INFO.length - 1) nextArrow.setInteractive({ useHandCursor: true });
  }

  const prevArrow = scene.add.text(modal.contentLeft + 10, iconY, '<', {
    fontFamily: FONT.display, resolution: 3,
    fontSize: '28px',
    color: TEXT.primary,
    fontStyle: 'bold'
  }).setOrigin(0.5);
  prevArrow.on('pointerover', () => prevArrow.setScale(1.2));
  prevArrow.on('pointerout', () => prevArrow.setScale(1));
  prevArrow.on('pointerdown', () => {
    if (index <= 0) return;
    index -= 1;
    soundManager.buttonClick();
    draw();
  });
  modal.panelObjects.push(prevArrow);

  const nextArrow = scene.add.text(modal.left + modal.width - 38, iconY, '>', {
    fontFamily: FONT.display, resolution: 3,
    fontSize: '28px',
    color: TEXT.primary,
    fontStyle: 'bold'
  }).setOrigin(0.5);
  nextArrow.on('pointerover', () => nextArrow.setScale(1.2));
  nextArrow.on('pointerout', () => nextArrow.setScale(1));
  nextArrow.on('pointerdown', () => {
    if (index >= BOSS_INFO.length - 1) return;
    index += 1;
    soundManager.buttonClick();
    draw();
  });
  modal.panelObjects.push(nextArrow);

  draw();
  modal.open();
  return modal;
}
