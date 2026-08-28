import { GAME_WIDTH, COLORS, TEXT, FONT } from '../config/constants.js';
import { Modal } from './Modal.js';
import { statsManager } from '../managers/StatsManager.js';
import { fetchLeaderboardEntries } from '../managers/YandexSDK.js';

// ALL TIME сначала пытается показать настоящий мировой лидерборд через
// Yandex Games SDK (см. fetchLeaderboardEntries) — на самой платформе, с
// настроенным в кабинете разработчика лидербордом, это реальные другие
// игроки. Если SDK недоступен (локальная разработка, другой хостинг) или
// лидерборд не настроен — тихо падаем обратно на честную личную историю
// полных прохождений этого игрока (statsManager.runHistory), без фейковых
// чужих имён. WEEKLY — всегда локальный (недельного лидерборда в кабинете нет).
const WEEK_MS = 7 * 24 * 60 * 60 * 1000;

function formatTime(totalSeconds) {
  const m = Math.floor(totalSeconds / 60);
  const s = Math.round(totalSeconds) % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}

function formatDate(ts) {
  const d = new Date(ts);
  return `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}`;
}

export function openLeaderboard(scene, { soundManager, onClose }) {
  const modal = new Modal(scene, { width: 600, height: 620, title: 'ЛИДЕРБОРД', onClose });
  let tab = 'all';
  let remoteEntries = null;
  let remoteRequested = false;
  // Отдельно от remoteEntries: null и "запрос ещё не завершился" — РАЗНЫЕ
  // состояния (баг был именно тут: fetchLeaderboardEntries вполне легитимно
  // резолвится в null, когда лидерборд недоступен — не только пока грузится
  // — а прежняя проверка "remoteEntries === null" считала это одним и тем
  // же и держала "Загрузка..." на экране даже после ответа сервера).
  let remoteSettled = false;

  const tabsY = modal.contentTop + 10;
  const sourceLabelY = tabsY + 26;
  const listTop = sourceLabelY + 26;

  function localEntriesForTab() {
    const source = statsManager.runHistory;
    const filtered = tab === 'weekly' ? source.filter((e) => Date.now() - e.ts <= WEEK_MS) : source;
    return [...filtered].sort((a, b) => a.totalTime - b.totalTime).slice(0, 10);
  }

  function loadRemoteIfNeeded() {
    if (remoteRequested) return;
    remoteRequested = true;
    fetchLeaderboardEntries(10).then((entries) => {
      remoteEntries = entries;
      remoteSettled = true;
      if (tab === 'all') draw();
    });
  }

  function drawTabButton(x, label, key) {
    const active = tab === key;
    const btn = scene.add.text(x, tabsY, label, {
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
      soundManager.buttonClick();
      draw();
    });
    modal.track(btn);
  }

  function drawRow(y, rowHeight, rank, name, scoreLabel, isLast) {
    const placeColor = rank === 1 ? TEXT.accent : rank <= 3 ? TEXT.primary : TEXT.muted;

    modal.track(scene.add.text(modal.contentLeft + 14, y + rowHeight / 2, `#${rank}`, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '14px',
      color: placeColor,
      fontStyle: 'bold'
    }).setOrigin(0, 0.5));

    modal.track(scene.add.text(modal.contentLeft + 70, y + rowHeight / 2, name, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '14px',
      color: TEXT.primary
    }).setOrigin(0, 0.5));

    modal.track(scene.add.text(modal.left + modal.width - 44, y + rowHeight / 2, scoreLabel, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '15px',
      color: placeColor,
      fontStyle: 'bold'
    }).setOrigin(1, 0.5));

    if (!isLast) {
      modal.track(scene.add.rectangle(GAME_WIDTH / 2, y + rowHeight - 2, modal.contentWidth, 1, COLORS.panelBorder, 0.6));
    }
  }

  function drawEmpty(message) {
    modal.track(scene.add.text(GAME_WIDTH / 2, listTop + 100, message, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '15px',
      color: TEXT.muted,
      align: 'center',
      wordWrap: { width: modal.contentWidth }
    }).setOrigin(0.5));
  }

  function draw() {
    modal.clearContent();
    drawTabButton(GAME_WIDTH / 2 - 70, '[ ALL TIME ]', 'all');
    drawTabButton(GAME_WIDTH / 2 + 70, '[ WEEKLY ]', 'weekly');

    if (tab === 'all') loadRemoteIfNeeded();
    const useRemote = tab === 'all' && Array.isArray(remoteEntries) && remoteEntries.length > 0;

    modal.track(scene.add.text(GAME_WIDTH / 2, sourceLabelY, useRemote ? 'МИРОВОЙ РЕЙТИНГ' : 'ЛИЧНЫЕ РЕЗУЛЬТАТЫ (НА ЭТОМ УСТРОЙСТВЕ)', {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '11px',
      color: '#6a6f83'
    }).setOrigin(0.5));

    if (useRemote) {
      const rowHeight = 40;
      remoteEntries.forEach((entry, i) => {
        drawRow(listTop + i * rowHeight, rowHeight, entry.rank ?? i + 1, entry.name, formatTime(entry.score), i === remoteEntries.length - 1);
      });
      return;
    }

    if (tab === 'all' && !remoteSettled && !statsManager.runHistory.length) {
      // Ждём ответ от Яндекса (ещё не settled) и локальных данных тоже нет —
      // не показываем "пока нет прохождений" раньше времени, чтобы не мигало.
      drawEmpty('Загрузка...');
      return;
    }

    const entries = localEntriesForTab();
    if (entries.length === 0) {
      drawEmpty('Пока нет полных прохождений.\nПройдите всех боссов, чтобы попасть в список!');
      return;
    }

    const rowHeight = 40;
    entries.forEach((entry, i) => {
      const ngLabel = entry.ngPlusCycle > 0 ? `  ·  NG+${entry.ngPlusCycle}` : '';
      drawRow(listTop + i * rowHeight, rowHeight, i + 1, `Вы  ·  ${formatDate(entry.ts)}${ngLabel}`, formatTime(entry.totalTime), i === entries.length - 1);
    });

    // Отдельная плашка внизу с личным лучшим результатом (ТЗ: "плашка внизу с
    // текущим результатом и местом самого игрока") — здесь это то же самое,
    // т.к. весь список и есть результаты игрока, но выделяем рекорд отдельно.
    const best = entries[0];
    modal.track(scene.add.rectangle(GAME_WIDTH / 2, modal.contentBottom - 26, modal.contentWidth, 1, COLORS.panelBorder, 0.9));
    modal.track(scene.add.text(GAME_WIDTH / 2, modal.contentBottom - 6, `Личный рекорд: ${formatTime(best.totalTime)}`, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '13px',
      color: TEXT.accent
    }).setOrigin(0.5));
  }

  draw();
  modal.open();
  return modal;
}
