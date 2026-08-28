// Мост между Phaser-сценами и HTML HUD-панелями за пределами канваса
// (переработка интерфейса: desktop-композиция LEFT HUD | GAME | RIGHT HUD).
// Панели — обычные DOM-элементы (см. index.html #hud-left/#hud-right), не
// Phaser-объекты, поэтому они переживают смену сцен сами по себе — каждая
// сцена явно вызывает show()/hide() в своём create().
//
// Весь текст, который меняется по ходу игры, обёрнут в <span class="crisp">
// (см. index.html) — это CSS-приём супersэмплинга (2× кегль + zoom:0.5),
// без него пиксельный шрифт на мелком кегле HTML-панелей выглядел мыльным
// (жалоба пользователя, скриншоты). Обёртка — только вокруг самого текста,
// не вокруг контейнера с margin/border/padding, иначе zoom ужал бы и их.
const hudLeft = document.getElementById('hud-left');
const hudRight = document.getElementById('hud-right');

// Цвета продублированы из COLORS (constants.js) в CSS-hex — здесь чистый DOM,
// без доступа к Phaser-палитре, но значения те же самые, не придуманы заново.
const COLOR_HEX = {
  bossHpFill: '#e74c3c',
  playerHpFill: '#3fa9ff',
  barBg: '#14141d'
};

function barHtml(id, colorHex) {
  return `
    <div class="pixel-bar"><div class="pixel-bar__fill" id="${id}" style="width:100%;background:${colorHex}"></div></div>
    <span class="hud-row__value"><span class="crisp" id="${id}-text"></span></span>
  `;
}

export const HudPanels = {
  // Вызывается один раз из GameScene.create() — строит статичный скелет,
  // дальше только точечные обновления текста/ширины баров.
  showBattle() {
    if (!hudLeft || !hudRight) return;
    hudLeft.innerHTML = `
      <div class="pixel-box">
        <div class="pixel-box__title"><span class="crisp">БОСС</span></div>
        <div class="hud-row">
          <div class="hud-row__label"><span class="crisp" id="hud-boss-name">—</span></div>
          ${barHtml('hud-boss-bar', COLOR_HEX.bossHpFill)}
        </div>
      </div>
      <div class="pixel-box">
        <div class="pixel-box__title"><span class="crisp">ИГРОК</span></div>
        <div class="hud-row">
          <div class="hud-row__label"><span class="crisp">HP</span></div>
          ${barHtml('hud-player-bar', COLOR_HEX.playerHpFill)}
        </div>
      </div>
      <div class="pixel-box">
        <div class="pixel-box__title"><span class="crisp">УРОВЕНЬ</span></div>
        <div class="hud-row__value" style="text-align:left;margin-top:0;font-size:16px">
          <span class="crisp" id="hud-level"></span>
        </div>
      </div>
    `;
    hudRight.innerHTML = `
      <div class="pixel-box">
        <div class="pixel-box__title"><span class="crisp">ТАЙМЕР</span></div>
        <div class="hud-row__value" style="text-align:left;margin-top:0;font-size:22px">
          <span class="crisp" id="hud-timer" style="color:#fff"></span>
        </div>
        <div class="pixel-divider"></div>
        <div class="pixel-box__title"><span class="crisp">СТАТИСТИКА</span></div>
        <div id="hud-stats"></div>
        <div class="pixel-divider"></div>
        <div class="pixel-box__title"><span class="crisp">УЛУЧШЕНИЯ</span></div>
        <div id="hud-upgrades"><div class="upgrade-empty"><span class="crisp">Пока нет</span></div></div>
      </div>
    `;
  },

  setBossHp(name, hp, maxHp) {
    const nameEl = document.getElementById('hud-boss-name');
    if (nameEl) nameEl.textContent = name;
    this.setBar('hud-boss-bar', hp, maxHp);
  },

  setPlayerHp(hp, maxHp) {
    this.setBar('hud-player-bar', hp, maxHp);
  },

  setBar(id, current, max) {
    const fill = document.getElementById(id);
    const text = document.getElementById(`${id}-text`);
    if (!fill || !text) return;
    const ratio = Math.max(0, Math.min(1, current / max));
    fill.style.width = `${ratio * 100}%`;
    text.textContent = `${Math.max(0, Math.ceil(current))} / ${max}`;
  },

  setLevel(bossIndex, totalBosses) {
    const el = document.getElementById('hud-level');
    if (el) el.textContent = `БОСС ${bossIndex + 1} / ${totalBosses}`;
  },

  setTimer(seconds) {
    const el = document.getElementById('hud-timer');
    if (!el) return;
    const clamped = Math.max(0, Math.ceil(seconds));
    el.textContent = clamped;
    el.style.color = clamped <= 10 ? '#ff5555' : '#ffffff';
  },

  // stats — реальные боевые параметры игрока (progressManager.getPlayerConfig()),
  // без выдуманных характеристик, которых нет в коде.
  setStats({ damage, critChance, speed }) {
    const el = document.getElementById('hud-stats');
    if (!el) return;
    const speedMult = (speed / 300).toFixed(2);
    el.innerHTML = `
      <div class="stat-line"><span class="crisp">Урон</span><span class="stat-line__value crisp">${damage}</span></div>
      <div class="stat-line"><span class="crisp">Крит</span><span class="stat-line__value crisp">${Math.round(critChance * 100)}%</span></div>
      <div class="stat-line"><span class="crisp">Скорость</span><span class="stat-line__value crisp">x${speedMult}</span></div>
    `;
  },

  // lines — те же строки, что и progressManager.getSummaryLines() (уже
  // используются на ResultScene) — не дублируем логику форматирования.
  setUpgrades(lines) {
    const el = document.getElementById('hud-upgrades');
    if (!el) return;
    el.innerHTML = lines.length
      ? lines.map((line) => `<div class="upgrade-item"><span class="crisp">${line}</span></div>`).join('')
      : '<div class="upgrade-empty"><span class="crisp">Пока нет</span></div>';
  },

  hide() {
    if (hudLeft) hudLeft.innerHTML = '';
    if (hudRight) hudRight.innerHTML = '';
  }
};
