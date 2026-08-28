import { Boss } from '../entities/Boss.js';
import { COLORS } from '../config/constants.js';

// Космический червь: вместо непрерывного преследования — телепорт по арене и
// "появление из-под земли" рядом с игроком перед ударом (П.25).
const ATTACK_SEQUENCE = ['spike', 'burrowStrike', 'spike', 'emerge'];

// Шипы из-под земли в случайной точке арены (targetMode: 'random' — эффект
// растёт не на самом боссе, поэтому это отдельный "наземный" projectile с
// origin: 'target', а не анимация самого спрайта). Лист прислан вместе с
// кадром покоящегося червя (кадр 0) — по просьбе не используем его здесь,
// только кадры 1-5 (нарастающий бугорок → красные шипы).
const WORM_SPIKE_EFFECT = {
  travel: { key: 'wormSpike', animKey: 'wormSpikeGrow', start: 1, end: 3, frameRate: 5, repeat: 0 },
  impact: { key: 'wormSpike', animKey: 'wormSpikeBurst', start: 4, end: 5, frameRate: 8, repeat: 0 },
  origin: 'target'
};

// "Вынырнуть из-под земли и ударить" (burrowStrike и emerge, П.25) — обе атаки
// телепортируют самого босса на новую точку (targetMode: 'self'), поэтому
// прогрыз земли играется прямо на спрайте босса через animKey, а не как
// отдельный ground-effect. Один и тот же лист/анимация переиспользуется для
// обеих атак — по просьбе пользователя.
const WORM_EMERGE_ANIM = { key: 'wormTeleport', animKey: 'wormEmerge', end: 6, frameRate: 10, repeat: 0 };

const ATTACK_CONFIG = {
  // Шипы бьют в случайной точке арены — сюрприз без привязки к игроку.
  spike: {
    warning: 700,
    radius: 80,
    damage: 18,
    color: COLORS.dangerMid,
    targetMode: 'random',
    projectile: WORM_SPIKE_EFFECT
  },
  // Червь ныряет в случайное место арены и тут же бьёт оттуда — короткое
  // предупреждение, т.к. сама телепортация уже подсказывает "где".
  burrowStrike: {
    warning: 500,
    radius: 85,
    damage: 20,
    color: COLORS.dangerLow,
    targetMode: 'self',
    teleport: true,
    animKey: 'burrowStrike'
  },
  // Специальная: ныряет почти под игрока и наносит большой урон по area.
  emerge: {
    warning: 900,
    radius: 130,
    damage: 35,
    color: COLORS.dangerHigh,
    targetMode: 'self',
    teleport: true,
    teleportNearPlayer: true,
    warningBanner: true,
    jumpCue: true,
    animKey: 'emerge'
  }
};

// Покадровые анимации (П.43, нарисованы вручную в Piskel, 64×64/кадр).
const WORM_ANIMATIONS = {
  idle: { key: 'wormIdle', end: 3, frameRate: 3, repeat: -1 },
  hit: { key: 'wormHit', end: 2, frameRate: 8, repeat: 0 },
  death: { key: 'wormDeath', end: 4, frameRate: 5, repeat: 0 },
  burrowStrike: WORM_EMERGE_ANIM,
  emerge: WORM_EMERGE_ANIM
};

export class SpaceWormBoss extends Boss {
  constructor(scene, x, y) {
    super(scene, x, y, {
      name: 'Космический червь',
      maxHp: 690, // -8% (баланс, ТЗ п.1)
      damage: 22,
      speed: 0,
      attackCooldown: 2000,
      radius: 68,
      attackSequence: ATTACK_SEQUENCE,
      attackConfig: ATTACK_CONFIG,
      pauseMs: 900,
      frameWidth: 64,
      frameHeight: 64,
      // Силуэт (bbox по альфа-каналу idle-кадра) ≈(15,5)-(44,52) в кадре 64×64.
      hitboxCenterX: 29.5,
      hitboxCenterY: 28.5,
      animations: WORM_ANIMATIONS
    });
  }
}
