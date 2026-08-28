import { metaManager } from './MetaManager.js';

// Прогрессия за забег (П.39): монеты + улучшения между боями. Хранится только
// в памяти вкладки — сбрасывается при поражении и при новом заходе из меню.
// Постоянная часть (валюта, разблокировки) — в MetaManager (localStorage),
// эта прокачка — временный слой поверх неё на один забег.
export const UPGRADE_POOL = [
  {
    id: 'damage',
    label: '+ УРОН',
    description: '+3 к урону атаки',
    apply: (state) => { state.upgrades.damage += 1; }
  },
  {
    id: 'maxHp',
    label: '+ MAX HP',
    description: '+20 к максимальному HP (и лечит на столько же)',
    apply: (state) => { state.upgrades.maxHp += 1; }
  },
  {
    id: 'attackSpeed',
    label: '+ СКОРОСТЬ АТАКИ',
    description: '-8% к перезарядке атаки',
    apply: (state) => { state.upgrades.attackSpeed += 1; }
  },
  {
    id: 'moveSpeed',
    label: '+ СКОРОСТЬ',
    description: '+6% к скорости передвижения',
    apply: (state) => { state.upgrades.moveSpeed += 1; }
  },
  {
    id: 'critChance',
    label: '+ ШАНС КРИТА',
    description: '+5% шанс удара x2 урона',
    apply: (state) => { state.upgrades.critChance += 1; }
  },
  {
    id: 'dash',
    label: 'РЫВОК',
    description: 'Открывает рывок (SHIFT на ПК / кнопка на тач)',
    apply: (state) => { state.dashUnlocked = true; },
    isAvailable: (state) => !state.dashUnlocked && !metaManager.dashUnlocked
  }
];

class ProgressManager {
  constructor() {
    this.reset();
  }

  reset() {
    this.coins = 0;
    this.upgrades = { damage: 0, maxHp: 0, attackSpeed: 0, moveSpeed: 0, critChance: 0 };
    this.dashUnlocked = false;
    // Суммарное время всех побеждённых боссов ЗА ВЕСЬ ЗАБЕГ (в отличие от
    // GameManager.timeLeft, который сбрасывается на каждом новом боссе) —
    // источник для таблицы лидеров (ТЗ "Окно 2: LEADERBOARD", см. GameScene.endBattle).
    this.totalTimeElapsed = 0;
  }

  addCoins(amount) {
    this.coins += amount;
  }

  rollUpgradeChoices(count = 3) {
    const pool = UPGRADE_POOL.filter((u) => !u.isAvailable || u.isAvailable(this));
    const shuffled = [...pool].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, count);
  }

  applyUpgrade(id) {
    const upgrade = UPGRADE_POOL.find((u) => u.id === id);
    upgrade?.apply(this);
  }

  // Читаемый список накопленных улучшений — чтобы игроку было явно видно,
  // что прокачка сохраняется между боями (жалоба: "не понятно сохраняются ли улучшения").
  getSummaryLines() {
    const u = this.upgrades;
    const lines = [];
    if (u.damage > 0) lines.push(`Урон: +${u.damage * 3}`);
    if (u.maxHp > 0) lines.push(`Max HP: +${u.maxHp * 20}`);
    if (u.attackSpeed > 0) lines.push(`Скорость атаки: ур. ${u.attackSpeed}`);
    if (u.moveSpeed > 0) lines.push(`Скорость: +${u.moveSpeed * 6}%`);
    if (u.critChance > 0) lines.push(`Шанс крита: +${u.critChance * 5}%`);
    if (this.dashUnlocked) lines.push('Рывок: открыт');
    return lines;
  }

  // Итоговые боевые параметры игрока с учётом всех купленных улучшений —
  // GameScene просто передаёт это в конструктор Player на каждый новый бой.
  // Постоянные тиры (MetaManager, roguelite-цикл) — база, сессионные карточки
  // прокачки (this.upgrades) — надстройка поверх неё на один забег.
  getPlayerConfig() {
    const u = this.upgrades;
    const m = metaManager.permanent;
    return {
      maxHp: 100 + m.maxHp * 15 + u.maxHp * 20,
      damage: 10 + m.damage * 2 + u.damage * 3,
      speed: 300 * (1 + m.moveSpeed * 0.04 + u.moveSpeed * 0.06),
      attackCooldown: Math.round(400 * 0.92 ** u.attackSpeed),
      critChance: m.critChance * 0.03 + u.critChance * 0.05,
      canDash: this.dashUnlocked || metaManager.dashUnlocked,
      relics: metaManager.getEquippedRelicFlags()
    };
  }
}

export const progressManager = new ProgressManager();
