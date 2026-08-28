import { Boss } from '../entities/Boss.js';
import { COLORS } from '../config/constants.js';

// Дракон: огненные снаряды (круглые зоны) + атака по линии — широкая огненная
// волна во всю ширину арены, от которой нужно уклоняться вертикально (П.25).
const ATTACK_SEQUENCE = ['fireball', 'quickFlame', 'fireball', 'fireBreath'];

// Снаряд-шар, вылетающий изо рта дракона (П.43, тот же приём, что ROBOT_PROJECTILE
// в RobotBoss.js). Кадры 0-2 — компактный растущий огонь в полёте (закольцованы,
// пока снаряд летит), 3-4 — удар о землю: сначала растекается, потом гаснет с искрами/дымом.
const DRAGON_PROJECTILE = {
  travel: { key: 'dragonFireball', animKey: 'dragonFireballFly', end: 2, frameRate: 9, repeat: -1 },
  impact: { key: 'dragonFireball', animKey: 'dragonFireballBurst', start: 3, end: 4, frameRate: 9, repeat: 0 }
};

// Огненная волна (П.43, добавлено 2026-08-19: пользователь прислал 8-кадровый
// .piskel "FireBreath", 64×64/кадр). travel — первые 4 кадра, зациклены на
// время предупреждения (растущее пламя); impact — полный 8-кадровый проигрыш
// один раз в момент удара (repeat:0 обязателен — resolveProjectile ждёт
// animationcomplete, чтобы уничтожить спрайт; зацикленная анимация никогда
// не завершится и оставит спрайт-сироту навсегда). visualWidth растягивает
// текстуру ЗАМЕТНО шире физической толщины стены (config.thickness=110) —
// та же пропорция, что у лазера робота (ROBOT_LASER_EFFECT: 360 при
// thickness 140) — иначе прижатая по высоте текстура выглядит тонкой линией,
// а не полноценной стеной огня. Сама зона урона (thickness) НЕ трогается —
// ТЗ явно просило не сужать саму стену.
const DRAGON_FIRE_BREATH_EFFECT = {
  travel: { key: 'dragonFireBreath', animKey: 'dragonFireBreathGrow', end: 3, frameRate: 11, repeat: -1 },
  impact: { key: 'dragonFireBreath', animKey: 'dragonFireBreathFull', end: 7, frameRate: 11, repeat: 0 },
  visualWidth: 280
};

const ATTACK_CONFIG = {
  // animKey: 'breath' + тот же снаряд-шар — теперь и у quickFlame (ТЗ:
  // "использовать ту же анимацию, что для фаербола, для другой атаки более
  // быстрой") — это уменьшенная/ускоренная версия того же броска: warning
  // вдвое короче, снаряд летит быстрее (Boss.spawnProjectile использует
  // config.warning как длительность перелёта), урон и радиус меньше.
  fireball: {
    warning: 800,
    radius: 85,
    damage: 18,
    color: COLORS.dangerMid,
    animKey: 'breath',
    projectile: DRAGON_PROJECTILE
  },
  quickFlame: {
    warning: 400,
    radius: 60,
    damage: 15,
    color: COLORS.dangerLow,
    animKey: 'breath',
    projectile: DRAGON_PROJECTILE
  },
  fireBreath: {
    warning: 1200,
    thickness: 110,
    damage: 35,
    color: COLORS.dangerHigh,
    shape: 'line',
    warningBanner: true,
    jumpCue: true,
    lineEffect: DRAGON_FIRE_BREATH_EFFECT
  }
};

// Покадровые анимации (П.43, нарисованы на заказ в Piskel, 64×64/кадр).
const DRAGON_ANIMATIONS = {
  idle: { key: 'dragonIdle', end: 17, frameRate: 9, repeat: -1 },
  breath: { key: 'dragonBreath', animKey: 'dragonBreathCast', end: 3, frameRate: 9, repeat: 0 },
  hit: { key: 'dragonHit', end: 2, frameRate: 8, repeat: 0 },
  death: { key: 'dragonDeath', end: 4, frameRate: 7, repeat: 0 }
};

export class DragonBoss extends Boss {
  constructor(scene, x, y) {
    super(scene, x, y, {
      name: 'Дракон',
      maxHp: 644, // -8% (баланс, ТЗ п.1)
      damage: 20,
      speed: 120,
      attackCooldown: 1800,
      radius: 75,
      attackSequence: ATTACK_SEQUENCE,
      attackConfig: ATTACK_CONFIG,
      pauseMs: 900,
      frameWidth: 64,
      frameHeight: 64,
      animations: DRAGON_ANIMATIONS
    });
  }

  // Летает за игроком по всей площадке (X и Y), как Голем — не только
  // по горизонтали (было раньше через chaseHorizontally).
  update(time, delta) {
    if (!this.player || this.isDead()) return;
    this.chaseTowards(this.player);
  }
}
