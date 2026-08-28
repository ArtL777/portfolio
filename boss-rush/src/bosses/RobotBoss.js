import { Boss } from '../entities/Boss.js';
import { COLORS } from '../config/constants.js';

// Робот: снаряды, вертикальный лазер (уклон по X, а не по Y — иначе как у
// Дракона) и мины на случайных точках арены (П.25). Сам робот не двигается —
// это "турель", механически отличается от преследующих боссов (П.41).
const ATTACK_SEQUENCE = ['projectile', 'laser', 'projectile', 'mine'];

// Снаряд-баллон, вылетающий из пушки робота и взрывающийся у цели (П.43).
// Кадры 0-2 — полёт (заряженный наконечник светится), 3-5 — взрыв и пыль.
// origin: 'boss' (по умолчанию) — снаряд стартует от самого робота, как выстрел.
const ROBOT_PROJECTILE = {
  travel: { key: 'robotShot', animKey: 'robotShotFly', end: 2, frameRate: 9, repeat: -1 },
  impact: { key: 'robotShot', animKey: 'robotShotBlast', start: 3, end: 5, frameRate: 9, repeat: 0 }
};

// Растущий лазерный луч вместо плоского прямоугольника (П.43) — растягивается
// на всю высоту арены через displaySize в telegraphLine (Boss.js), сам спрайт
// узкий и высокий. Кадры 0-4 — луч нарастает, 5 — полная мощность (держится
// до момента урона). visualWidth раньше был 46 — при растяжении квадратного
// 64×64 кадра на всю высоту арены (960px, ×15) такая узкая ширина сплющивала
// картинку в уродливую тонкую полоску; расширил и увеличил толщину хитбокса
// в тон, чтобы визуал совпадал с реальной опасной зоной.
const ROBOT_LASER_EFFECT = {
  travel: { key: 'robotLaser', animKey: 'robotLaserGrow', end: 4, frameRate: 5, repeat: 0 },
  impact: { key: 'robotLaser', animKey: 'robotLaserFull', start: 5, end: 5, frameRate: 5, repeat: 0 },
  visualWidth: 360
};

// Мина: тикающая бомба на месте зоны (origin: 'target'). Своего взрыва не
// прислано — переиспользуем взрыв снаряда робота (robotShot, кадры 3-5),
// тематически подходит (та же "техника" робота) и уже загружен.
const ROBOT_MINE_EFFECT = {
  travel: { key: 'robotMine', animKey: 'robotMineTick', end: 3, frameRate: 3, repeat: -1 },
  impact: { key: 'robotShot', animKey: 'robotShotBlast', start: 3, end: 5, frameRate: 9, repeat: 0 },
  origin: 'target'
};

const ATTACK_CONFIG = {
  projectile: {
    warning: 750, // заряд пушки: 5 кадров @10fps = 500мс + запас на удержание
    radius: 75,
    damage: 16,
    color: COLORS.dangerMid,
    animKey: 'projectile',
    projectile: ROBOT_PROJECTILE
  },
  laser: {
    warning: 1200, // луч: 5 кадров @5fps = 1000мс роста + запас
    thickness: 140,
    damage: 22,
    color: COLORS.dangerLow,
    shape: 'line',
    orientation: 'vertical',
    lineEffect: ROBOT_LASER_EFFECT
  },
  mine: {
    warning: 1800,
    radius: 90,
    damage: 25,
    color: COLORS.dangerHigh,
    targetMode: 'random',
    warningBanner: true,
    jumpCue: true,
    projectile: ROBOT_MINE_EFFECT
  }
};

// Покадровые анимации (П.43, нарисованы вручную в Piskel, 64×64/кадр).
const ROBOT_ANIMATIONS = {
  idle: { key: 'robotIdle', end: 2, frameRate: 3, repeat: -1 },
  projectile: { key: 'robotCharge', animKey: 'robotChargeUp', end: 4, frameRate: 10, repeat: 0 },
  hit: { key: 'robotHit', end: 2, frameRate: 7, repeat: 0 },
  death: { key: 'robotDeath', end: 5, frameRate: 7, repeat: 0 }
};

// Арт (П.43): "Robot sprites" by Vircon32 (Carra) — CC-BY 4.0.
// https://opengameart.org/content/robot-sprites
export class RobotBoss extends Boss {
  constructor(scene, x, y) {
    super(scene, x, y, {
      name: 'Робот',
      maxHp: 598, // -8% (баланс, ТЗ п.1)
      damage: 18,
      speed: 0,
      attackCooldown: 1600,
      radius: 72,
      attackSequence: ATTACK_SEQUENCE,
      attackConfig: ATTACK_CONFIG,
      pauseMs: 1000,
      frameWidth: 64,
      frameHeight: 64,
      // Силуэт смещён вверх от геометрического центра кадра (bbox по
      // альфа-каналу idle-кадра ≈(19,10)-(43,39) в кадре 64×64).
      hitboxCenterX: 31,
      hitboxCenterY: 24.5,
      animations: ROBOT_ANIMATIONS
    });
  }
}
