// Базовое разрешение арены (портретная ориентация под Яндекс Игры).
// Вся игровая логика опирается на эти значения, а не на реальный размер canvas.
export const GAME_WIDTH = 720;
export const GAME_HEIGHT = 1280;

// Единая палитра прототипа (П.27) — чтобы не плодить случайные цвета по файлам.
export const COLORS = {
  background: 0x0d0d14,
  arenaFill: 0x161622,
  arenaBorder: 0x35354e,
  panelFill: 0x1b1b28,
  panelBorder: 0x35354e,
  player: 0x3fa9ff,
  playerOutline: 0x1c6fb8,
  bossHpFill: 0xe74c3c,
  playerHpFill: 0x3fa9ff,
  barBg: 0x14141d,
  accent: 0xffcc00,
  danger: 0xff5555,

  // Опасные зоны у всех боссов — из одного семейства красного, чтобы
  // "красное = опасно" читалось одинаково независимо от того, чья это атака.
  dangerLow: 0xff8844,
  dangerMid: 0xff4444,
  dangerHigh: 0xff2266
};

// Пиксельный шрифт интерфейса (переработка ТЗ п.5) — предыдущий вариант
// (системный Arial Black) отклонён как "не пиксельный, обычный веб-шрифт".
// Самохостинг вместо CDN (см. @font-face в index.html) — Яндекс Игры грузятся
// в песочнице с ограниченным доступом к сети, внешний CDN рискует не
// подгрузиться при реальной публикации. Два шрифта, не один: 'Press Start 2P'
// (аркадный, 8×8-пиксельная сетка на символ) читается только на коротких
// строках КРУПНЫМ размером — используется для заголовков/HP-чисел/таймера/
// кнопок. Для описаний и длинных подписей та же плотность текста в Press
// Start 2P превращается в нечитаемую кашу, поэтому body — 'Pixelify Sans':
// тоже пиксельная эстетика, но спроектирован для читаемости в UI мелким кеглем.
export const FONT = {
  display: '"Press Start 2P", monospace',
  body: '"Pixelify Sans", monospace'
};

export const TEXT = {
  primary: '#ffffff',
  muted: '#9aa0b4',
  accent: '#ffcc00',
  danger: '#ff5555',
  success: '#7CFC9C'
};
