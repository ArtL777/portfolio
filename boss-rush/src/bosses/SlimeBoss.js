import { Boss } from '../entities/Boss.js';
import { COLORS } from '../config/constants.js';

// Паттерн не случайный: фиксированная последовательность типов атак (П.17).
// Случайна только позиция опасной зоны — она берётся из текущей позиции игрока.
const ATTACK_SEQUENCE = ['melee', 'ranged', 'melee', 'special'];

// Снаряд ("блёб"): один спрайт-лист на 4 кадра — первые два кадры (0-1) это
// полёт (лёгкая пульсация капли), последние два (2-3) — сплющивание об цель.
// Используется и для 'ranged', и для усиленной 'special' атаки.
const SLIME_PROJECTILE = {
  travel: { key: 'slimeBlob', animKey: 'slimeBlobTravel', end: 1, frameRate: 6, repeat: -1 },
  impact: { key: 'slimeBlob', animKey: 'slimeBlobImpact', start: 2, end: 3, frameRate: 10, repeat: 0 },
  visualScale: 0.65
};

const ATTACK_CONFIG = {
  // Ближняя атака: зона появляется на самом боссе (targetMode: 'self') — он
  // бьёт по всем, кто рядом, а не через всю арену. warning = длительность
  // анимации замаха (3 кадра @ 8fps = 375мс) + небольшой запас на удержание
  // финальной позы — раньше запас был 175мс, и было заметно, что зона ещё
  // "думает" уже после того, как слизень закончил бить.
  melee: {
    warning: 475,
    radius: 85,
    damage: 15,
    color: COLORS.dangerMid,
    targetMode: 'self',
    animKey: 'melee'
  },
  // Дальняя атака: замах на месте + летящий снаряд до зоны у игрока —
  // урон наносится синхронно с "приземлением" снаряда.
  ranged: {
    warning: 900,
    radius: 70,
    damage: 15,
    color: COLORS.dangerLow,
    animKey: 'ranged',
    projectile: SLIME_PROJECTILE
  },
  special: {
    warning: 1300,
    radius: 130,
    damage: 30,
    color: COLORS.dangerHigh,
    warningBanner: true,
    animKey: 'ranged',
    projectile: SLIME_PROJECTILE
  }
};

// Покадровые анимации (П.43, нарисованы вручную в Piskel, 32×32/кадр, CC0 —
// авторские рисунки пользователя проекта). idle крутится в цикле, остальные —
// одноразовые, после чего Boss сам возвращает спрайт в idle.
const SLIME_ANIMATIONS = {
  idle: { key: 'slimeIdle', end: 2, frameRate: 5, repeat: -1 },
  hit: { key: 'slimeHit', end: 2, frameRate: 8, repeat: 0 },
  death: { key: 'slimeDeath', end: 3, frameRate: 6, repeat: 0 },
  melee: { key: 'slimeMelee', end: 2, frameRate: 8, repeat: 0 },
  ranged: { key: 'slimeRanged', end: 2, frameRate: 8, repeat: 0 }
};

export class SlimeBoss extends Boss {
  constructor(scene, x, y) {
    super(scene, x, y, {
      name: 'Слизень',
      maxHp: 460, // -8% (баланс, ТЗ п.1)
      damage: 15,
      speed: 0,
      attackCooldown: 2000,
      radius: 70,
      attackSequence: ATTACK_SEQUENCE,
      attackConfig: ATTACK_CONFIG,
      pauseMs: 1000,
      frameWidth: 32,
      frameHeight: 32,
      // Видимый силуэт нового арта смещён относительно геометрического центра
      // кадра (проверено по альфа-каналу: bbox ~(1,5)-(30,24) в кадре 32×32) —
      // без этой поправки хитбокс уезжал вниз от тела примерно на треть радиуса.
      hitboxCenterX: 15.5,
      hitboxCenterY: 14.5,
      animations: SLIME_ANIMATIONS
    });
  }
}
