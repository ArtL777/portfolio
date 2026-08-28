import Phaser from 'phaser';
import { GAME_WIDTH, GAME_HEIGHT, COLORS, TEXT, FONT } from '../config/constants.js';
import { SoundManager } from '../managers/SoundManager.js';
import { progressManager } from '../managers/ProgressManager.js';
import { statsManager } from '../managers/StatsManager.js';
import { TOTAL_BOSSES } from '../managers/BossManager.js';
import { HudPanels } from '../ui/HudPanels.js';
import { drawPixelPanel } from '../ui/pixelShapes.js';
import { metaManager } from '../managers/MetaManager.js';
import { openBossGallery, BOSS_ICON_ASSETS } from '../ui/BossGalleryModal.js';
import { openLeaderboard } from '../ui/LeaderboardModal.js';
import { openSettings } from '../ui/SettingsModal.js';
import { notifyGameReady } from '../managers/YandexSDK.js';

// Компоновка на всю высоту канваса (ТЗ п.3): раньше всё содержимое было
// зажато в средней трети экрана, а сверху/снизу пустовало. Теперь три блока
// (лого+заголовок, статистика, кнопка) равномерно распределены по вертикали.
const STATS_PANEL = { width: 580, top: 470, height: 380 };
// Тот же арт, что и фон арены Голема (GameScene, ключ 'arenaBgGolem') — берём
// отдельным ключом вместо переиспользования: сцены грузят независимо, а
// каменные руины с двумя стражами лучше всего читаются как "эпичный портал
// перед боем" на экране меню (запрос "красивый дизайн фон меню" из
// имеющихся файлов, без новых ассетов).
const MENU_BG_KEY = 'menuBgRuins';

export class MenuScene extends Phaser.Scene {
  constructor() {
    super('MenuScene');
  }

  preload() {
    this.load.image(MENU_BG_KEY, 'assets/images/arena_bg_golem.png');
    // Иконки боссов для окна БЕСТИАРИЙ — те же файлы, что грузит GameScene под
    // другими ключами (см. комментарий у BOSS_ICON_ASSETS), нужен именно
    // spritesheet с framwWidth/Height, иначе картинкой станет вся полоса кадров.
    BOSS_ICON_ASSETS.forEach(({ key, path, frameWidth, frameHeight }) => {
      if (this.textures.exists(key)) return;
      if (frameWidth) this.load.spritesheet(key, path, { frameWidth, frameHeight });
      else this.load.image(key, path);
    });
  }

  create() {
    // Боевые HUD-панели — только для GameScene; на других экранах не нужны
    // (они HTML-элементы вне канваса, сами по себе между сценами не гаснут).
    HudPanels.hide();
    this.soundManager = new SoundManager();
    this.activeModal = null;

    // Сигнал платформе "игра прогрузилась и в неё можно играть" (обязателен
    // для модерации Яндекс Игр) — вызывается один раз при первом попадании
    // в меню, notifyGameReady() сам гарантирует однократность.
    notifyGameReady();

    this.drawBackground();

    // Пульсация заголовка (ТЗ: "эффект пульсации свечения") — лёгкий scale-твин
    // вместо шейдера/glow-текстуры, которых в проекте нет.
    this.titleText = this.add.text(GAME_WIDTH / 2, 350, 'BOSS RUSH', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '52px',
      color: TEXT.primary,
      fontStyle: 'bold'
    }).setOrigin(0.5);
    this.tweens.add({
      targets: this.titleText,
      scale: 1.06,
      duration: 1400,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut'
    });

    this.add.text(GAME_WIDTH / 2, 400, 'Победи босса за 60 секунд!', {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '20px',
      color: TEXT.muted
    }).setOrigin(0.5);

    // Постоянная валюта видна сразу в меню (ТЗ п.7 "понятное отображение
    // текущего прогресса") — то, ради чего имеет смысл начинать новый забег.
    this.add.text(GAME_WIDTH / 2, 434, `¤ ЯДРА: ${metaManager.cores}`, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '15px',
      color: TEXT.accent,
      fontStyle: 'bold'
    }).setOrigin(0.5);

    this.createStatsPanel();

    const button = this.add.text(GAME_WIDTH / 2, GAME_HEIGHT - 220, '[ НАЧАТЬ БОЙ ]', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '32px',
      color: TEXT.accent,
      fontStyle: 'bold'
    }).setOrigin(0.5).setInteractive({ useHandCursor: true });

    button.on('pointerover', () => button.setScale(1.08));
    button.on('pointerout', () => button.setScale(1));
    button.on('pointerdown', () => {
      this.soundManager.buttonClick();
      progressManager.reset();
      // Плавный переход (ТЗ: "запускает плавный fade-out переход в GameScene")
      // вместо мгновенного scene.start — камера гаснет, и только затем сцена
      // стартует, так что первый кадр боя не "выстреливает" внезапно.
      this.cameras.main.fadeOut(280, 13, 13, 20);
      this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
        // Баг: scene.start('GameScene') БЕЗ data не сбрасывает предыдущие данные —
        // Phaser молча переиспользует последний переданный bossIndex (например,
        // 4 после полного прохождения), и бой начинался не с первого босса.
        this.scene.start('GameScene', { bossIndex: 0 });
      });
    });

    // Магазин постоянных улучшений/реликвий/достижений (ТЗ п.1/п.7) — вторая,
    // менее заметная кнопка, чтобы "НАЧАТЬ БОЙ" оставалась главным акцентом.
    const shopButton = this.add.text(GAME_WIDTH / 2, GAME_HEIGHT - 160, '[ МАГАЗИН ]', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '18px',
      color: TEXT.primary,
      fontStyle: 'bold'
    }).setOrigin(0.5).setInteractive({ useHandCursor: true });

    shopButton.on('pointerover', () => shopButton.setScale(1.08));
    shopButton.on('pointerout', () => shopButton.setScale(1));
    shopButton.on('pointerdown', () => {
      this.soundManager.buttonClick();
      this.scene.start('MetaScene');
    });

    this.createNavButtons();
  }

  // Целиковая картинка "каменные руины" на весь канвас (тот же приём, что
  // GameScene.drawCustomBackground) + затемняющая плашка для читаемости текста
  // поверх + очень медленный Ken Burns pan/zoom вместо статичной картинки —
  // это и есть "лёгкий эффект параллакса" из ТЗ без тайлового шва (арт не
  // предназначен для бесшовного повтора, поэтому не TileSprite).
  drawBackground() {
    const { width, height } = this.textures.get(MENU_BG_KEY).getSourceImage();
    const baseScale = Math.max(GAME_WIDTH / width, GAME_HEIGHT / height) * 1.08;
    const bg = this.add.image(GAME_WIDTH / 2, GAME_HEIGHT / 2, MENU_BG_KEY).setScale(baseScale);

    this.tweens.add({
      targets: bg,
      scale: baseScale * 1.1,
      x: GAME_WIDTH / 2 - 18,
      duration: 14000,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut'
    });

    this.add.rectangle(GAME_WIDTH / 2, GAME_HEIGHT / 2, GAME_WIDTH, GAME_HEIGHT, 0x0a0a12, 0.62);
  }

  // Три новые кнопки навигации (ТЗ "Окна 1/2/3") — компактный ряд под
  // магазином, чтобы не спорить с "НАЧАТЬ БОЙ" за главный акцент экрана.
  createNavButtons() {
    const y = GAME_HEIGHT - 108;
    const items = [
      { label: '[ БЕСТИАРИЙ ]', open: () => this.openModal(openBossGallery) },
      { label: '[ ЛИДЕРБОРД ]', open: () => this.openModal(openLeaderboard) },
      { label: '[ НАСТРОЙКИ ]', open: () => this.openModal(openSettings, { onReset: () => this.scene.restart() }) }
    ];
    const spacing = 240;
    const startX = GAME_WIDTH / 2 - spacing;

    items.forEach((item, i) => {
      const btn = this.add.text(startX + i * spacing, y, item.label, {
        fontFamily: FONT.body, resolution: 3,
        fontSize: '19px',
        color: TEXT.muted,
        fontStyle: 'bold'
      }).setOrigin(0.5).setInteractive({ useHandCursor: true });
      btn.on('pointerover', () => btn.setScale(1.08).setColor(TEXT.primary));
      btn.on('pointerout', () => btn.setScale(1).setColor(TEXT.muted));
      btn.on('pointerdown', () => {
        this.soundManager.buttonClick();
        item.open();
      });
    });
  }

  // Единая точка открытия модалок (ТЗ: "как правильно организовать менеджер
  // окон в Phaser 3") — закрывает предыдущее окно перед открытием нового
  // (клики по нескольким кнопкам подряд не плодят наложенные друг на друга
  // оверлеи) и сама снимает ссылку через onClose, когда окно закрывается
  // крестиком/кликом по фону, а не через эту же функцию.
  openModal(openFn, extraOptions = {}) {
    this.activeModal?.close();
    // modal ссылается на себя же внутри onClose — замыкание разрешается только
    // когда close() реально сработает (позже, после fade-out твина), к тому
    // моменту this.activeModal уже указывает именно на этот же экземпляр, если
    // окно успели не переоткрыть — сравнение по ссылке защищает от гонки:
    // старое окно, ещё доигрывающее fade-out, не должно затирать новое.
    const modal = openFn(this, {
      soundManager: this.soundManager,
      ...extraOptions,
      onClose: () => { if (this.activeModal === modal) this.activeModal = null; }
    });
    this.activeModal = modal;
  }

  // Блок статистики игрока (ТЗ п.3) — читает персистентные данные из
  // StatsManager (переживают перезагрузку страницы, в отличие от ProgressManager).
  createStatsPanel() {
    const { width, top, height } = STATS_PANEL;
    const left = (GAME_WIDTH - width) / 2;

    drawPixelPanel(this, left, top, width, height, { notch: 14, fill: COLORS.panelFill, border: COLORS.panelBorder });

    this.add.text(GAME_WIDTH / 2, top + 38, 'СТАТИСТИКА', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '22px',
      color: TEXT.accent,
      fontStyle: 'bold'
    }).setOrigin(0.5);

    const rows = [
      ['Забегов сыграно', `${statsManager.runsPlayed}`],
      ['Лучший результат', `${statsManager.bestBossesBeaten} / ${TOTAL_BOSSES} боссов`],
      ['Полных прохождений', `${statsManager.fullClears}`],
      ['Лучший цикл NG+', `${statsManager.bestNgPlusCycle}`]
    ];

    const rowsTop = top + 88;
    const rowHeight = (height - 108) / rows.length;
    rows.forEach(([label, value], index) => {
      const y = rowsTop + index * rowHeight + rowHeight / 2;
      this.add.text(left + 32, y, label, {
        fontFamily: FONT.body, resolution: 3,
        fontSize: '18px',
        color: TEXT.muted
      }).setOrigin(0, 0.5);
      this.add.text(left + width - 32, y, value, {
        fontFamily: FONT.display, resolution: 3,
        fontSize: '20px',
        color: TEXT.primary,
        fontStyle: 'bold'
      }).setOrigin(1, 0.5);
      if (index < rows.length - 1) {
        this.add.rectangle(GAME_WIDTH / 2, y + rowHeight / 2, width - 48, 1, COLORS.panelBorder, 0.6);
      }
    });
  }
}
