import Phaser from 'phaser';
import { GAME_WIDTH, COLORS, TEXT, FONT } from '../config/constants.js';
import { Modal } from './Modal.js';
import { settingsManager } from '../managers/SettingsManager.js';
import { metaManager } from '../managers/MetaManager.js';
import { statsManager } from '../managers/StatsManager.js';
import { achievementTracker } from '../managers/Achievements.js';
import { progressManager } from '../managers/ProgressManager.js';

// Минимальный словарь ТОЛЬКО для текста этого окна (см. SettingsManager.js —
// полная локализация всей игры на EN отдельным этапом не входит в эту
// доработку) — переключатель [RU]/[EN] реально работает и переводит хотя бы
// то, что показывает сам себе, а не просто визуально мигает без эффекта.
const STRINGS = {
  ru: {
    title: 'НАСТРОЙКИ', audio: 'AUDIO', gameplay: 'GAMEPLAY',
    music: 'MUSIC', sfx: 'SOUND FX', mute: 'MASTER MUTE',
    shake: 'SCREEN SHAKE', vibration: 'VIBRATION', language: 'ЯЗЫК / LANGUAGE',
    reset: 'RESET DATA', resetConfirm: 'Точно сбросить весь прогресс?', yes: '[ YES ]', no: '[ NO ]',
    on: 'ON', off: 'OFF', resetDone: 'ПРОГРЕСС СБРОШЕН',
    credits: 'Robot sprites: Vircon32 (Carra), CC-BY 4.0, opengameart.org'
  },
  en: {
    title: 'SETTINGS', audio: 'AUDIO', gameplay: 'GAMEPLAY',
    music: 'MUSIC', sfx: 'SOUND FX', mute: 'MASTER MUTE',
    shake: 'SCREEN SHAKE', vibration: 'VIBRATION', language: 'LANGUAGE / ЯЗЫК',
    reset: 'RESET DATA', resetConfirm: 'Really reset all progress?', yes: '[ YES ]', no: '[ NO ]',
    on: 'ON', off: 'OFF', resetDone: 'PROGRESS RESET',
    credits: 'Robot sprites: Vircon32 (Carra), CC-BY 4.0, opengameart.org'
  }
};

export function openSettings(scene, { soundManager, onReset, onClose }) {
  const modal = new Modal(scene, { width: 580, height: 600, title: STRINGS[settingsManager.language].title, onClose });
  let tab = 'audio';
  let confirmingReset = false;

  function t() {
    return STRINGS[settingsManager.language];
  }

  function drawTabButton(x, key, label) {
    const active = tab === key;
    const btn = scene.add.text(x, modal.contentTop + 8, `[ ${label} ]`, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '14px',
      color: active ? TEXT.accent : TEXT.muted,
      fontStyle: 'bold'
    }).setOrigin(0.5).setInteractive({ useHandCursor: true });
    btn.on('pointerover', () => { if (!active) btn.setScale(1.08); });
    btn.on('pointerout', () => btn.setScale(1));
    btn.on('pointerdown', () => {
      if (tab === key) return;
      tab = key;
      confirmingReset = false;
      soundManager.buttonClick();
      draw();
    });
    modal.track(btn);
  }

  // Слайдер 0..1 — трек + заполнение + перетаскиваемая ручка. Клик/драг по
  // треку сразу выставляет значение под курсором.
  function drawSlider(y, label, value, onChange) {
    const trackX = modal.contentLeft + 160;
    const trackWidth = modal.contentWidth - 160 - 50;
    const trackHeight = 10;

    modal.track(scene.add.text(modal.contentLeft, y + trackHeight / 2, label, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '20px',
      color: TEXT.primary
    }).setOrigin(0, 0.5));

    const trackBg = scene.add.rectangle(trackX + trackWidth / 2, y + trackHeight / 2, trackWidth, trackHeight, COLORS.barBg)
      .setStrokeStyle(2, COLORS.panelBorder);
    modal.track(trackBg);
    const fill = scene.add.rectangle(trackX, y + trackHeight / 2, Math.max(2, trackWidth * value), trackHeight, COLORS.accent)
      .setOrigin(0, 0.5);
    modal.track(fill);

    const valueLabel = scene.add.text(trackX + trackWidth + 14, y + trackHeight / 2, `${Math.round(value * 100)}%`, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '13px',
      color: TEXT.muted
    }).setOrigin(0, 0.5);
    modal.track(valueLabel);

    const hit = scene.add.rectangle(trackX + trackWidth / 2, y + trackHeight / 2, trackWidth, 28, 0x000000, 0)
      .setInteractive({ useHandCursor: true });
    scene.input.setDraggable(hit);
    modal.track(hit);

    const applyFromPointer = (pointer) => {
      const localX = Phaser.Math.Clamp((pointer.x - trackX) / trackWidth, 0, 1);
      fill.setSize(Math.max(2, trackWidth * localX), trackHeight);
      valueLabel.setText(`${Math.round(localX * 100)}%`);
      onChange(localX);
    };
    hit.on('pointerdown', (pointer) => applyFromPointer(pointer));
    hit.on('drag', (pointer) => applyFromPointer(pointer));
  }

  function drawToggle(y, label, active, onToggle) {
    modal.track(scene.add.text(modal.contentLeft, y, label, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '20px',
      color: TEXT.primary
    }).setOrigin(0, 0.5));

    const btn = scene.add.text(modal.left + modal.width - 44, y, active ? `[ ${t().on} ]` : `[ ${t().off} ]`, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '13px',
      color: active ? TEXT.success : TEXT.muted,
      fontStyle: 'bold'
    }).setOrigin(1, 0.5).setInteractive({ useHandCursor: true });
    btn.on('pointerover', () => btn.setScale(1.08));
    btn.on('pointerout', () => btn.setScale(1));
    btn.on('pointerdown', () => {
      soundManager.buttonClick();
      onToggle();
      draw();
    });
    modal.track(btn);
  }

  function drawAudioTab() {
    let y = modal.contentTop + 60;
    drawSlider(y, t().music, settingsManager.musicVolume, (v) => settingsManager.setMusicVolume(v));
    y += 50;
    drawSlider(y, t().sfx, settingsManager.sfxVolume, (v) => settingsManager.setSfxVolume(v));
    y += 60;
    drawToggle(y, t().mute, settingsManager.masterMute, () => settingsManager.toggleMute());
  }

  function drawGameplayTab() {
    let y = modal.contentTop + 60;
    drawToggle(y, t().shake, settingsManager.screenShake, () => settingsManager.toggleScreenShake());
    y += 46;
    drawToggle(y, t().vibration, settingsManager.vibration, () => settingsManager.toggleVibration());
    y += 56;

    modal.track(scene.add.text(modal.contentLeft, y, t().language, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '20px',
      color: TEXT.primary
    }).setOrigin(0, 0.5));
    ['ru', 'en'].forEach((lang, i) => {
      const active = settingsManager.language === lang;
      const btn = scene.add.text(modal.left + modal.width - 44 - i * 70, y, `[ ${lang.toUpperCase()} ]`, {
        fontFamily: FONT.display, resolution: 3,
        fontSize: '13px',
        color: active ? TEXT.accent : TEXT.muted,
        fontStyle: 'bold'
      }).setOrigin(1, 0.5).setInteractive({ useHandCursor: true });
      btn.on('pointerover', () => { if (!active) btn.setScale(1.08); });
      btn.on('pointerout', () => btn.setScale(1));
      btn.on('pointerdown', () => {
        if (active) return;
        soundManager.buttonClick();
        settingsManager.setLanguage(lang);
        modal.titleText?.setText(t().title);
        draw();
      });
      modal.track(btn);
    });
    y += 70;

    modal.track(scene.add.rectangle(GAME_WIDTH / 2, y, modal.contentWidth, 1, COLORS.panelBorder, 0.7));
    y += 40;

    if (!confirmingReset) {
      const resetBtn = scene.add.text(GAME_WIDTH / 2, y, `[ ${t().reset} ]`, {
        fontFamily: FONT.display, resolution: 3,
        fontSize: '15px',
        color: TEXT.danger,
        fontStyle: 'bold'
      }).setOrigin(0.5).setInteractive({ useHandCursor: true });
      resetBtn.on('pointerover', () => resetBtn.setScale(1.08));
      resetBtn.on('pointerout', () => resetBtn.setScale(1));
      resetBtn.on('pointerdown', () => {
        soundManager.buttonClick();
        confirmingReset = true;
        draw();
      });
      modal.track(resetBtn);
    } else {
      modal.track(scene.add.text(GAME_WIDTH / 2, y, t().resetConfirm, {
        fontFamily: FONT.body, resolution: 3,
        fontSize: '14px',
        color: TEXT.danger,
        wordWrap: { width: modal.contentWidth },
        align: 'center'
      }).setOrigin(0.5));
      y += 34;

      const yesBtn = scene.add.text(GAME_WIDTH / 2 - 60, y, t().yes, {
        fontFamily: FONT.display, resolution: 3,
        fontSize: '15px',
        color: TEXT.danger,
        fontStyle: 'bold'
      }).setOrigin(0.5).setInteractive({ useHandCursor: true });
      yesBtn.on('pointerover', () => yesBtn.setScale(1.1));
      yesBtn.on('pointerout', () => yesBtn.setScale(1));
      yesBtn.on('pointerdown', () => {
        soundManager.buttonClick();
        performReset();
      });
      modal.track(yesBtn);

      const noBtn = scene.add.text(GAME_WIDTH / 2 + 60, y, t().no, {
        fontFamily: FONT.display, resolution: 3,
        fontSize: '15px',
        color: TEXT.primary,
        fontStyle: 'bold'
      }).setOrigin(0.5).setInteractive({ useHandCursor: true });
      noBtn.on('pointerover', () => noBtn.setScale(1.1));
      noBtn.on('pointerout', () => noBtn.setScale(1));
      noBtn.on('pointerdown', () => {
        soundManager.buttonClick();
        confirmingReset = false;
        draw();
      });
      modal.track(noBtn);
    }

    // §3.5 требований платформы: видимая атрибуция для CC-BY-ассета (спрайты
    // робота, см. bosses/RobotBoss.js) — лицензия требует указания авторства
    // ГДЕ используется работа, а не только в комментарии исходного кода,
    // который игрок/модератор не видит.
    modal.track(scene.add.text(GAME_WIDTH / 2, modal.contentBottom - 6, t().credits, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '11px',
      color: '#6a6f83'
    }).setOrigin(0.5));
  }

  // Прогресс (валюта, постоянные улучшения, реликвии, достижения, статистика,
  // лидерборд) стирается — сами настройки звука/языка НАМЕРЕННО не трогаются,
  // "сбросить прогресс" и "сбросить мои предпочтения интерфейса" — разные ожидания.
  function performReset() {
    ['bossRush.meta.v1', 'bossRush.stats.v1', 'bossRush.achievements.v1'].forEach((key) => {
      try { localStorage.removeItem(key); } catch { /* localStorage недоступен */ }
    });
    metaManager.load();
    statsManager.load();
    achievementTracker.load();
    progressManager.reset();
    confirmingReset = false;
    onReset?.();
    draw();
  }

  function draw() {
    modal.clearContent();
    drawTabButton(GAME_WIDTH / 2 - 95, 'audio', t().audio);
    drawTabButton(GAME_WIDTH / 2 + 95, 'gameplay', t().gameplay);
    if (tab === 'audio') drawAudioTab();
    else drawGameplayTab();
  }

  draw();
  modal.open();
  return modal;
}
