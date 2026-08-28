import { Boss } from '../entities/Boss.js';
import { COLORS } from '../config/constants.js';

// Голем медленнее и бьёт реже, но каждый удар ощутимо больнее Слизня (П.25, П.41).
const ATTACK_SEQUENCE = ['slam', 'fast', 'slam', 'groundPound'];

// Растущие каменные шипы — общие для 'fast' и 'slam' (П.43). Не тело
// босса — отдельный объект, растущий прямо в точке зоны (origin: 'target',
// без перелёта). Авторский fps в файле — 3 (длительность всей анимации
// ~1.3с), но обе атаки короче — проигрываем в 2 раза быстрее (frameRate: 6).
const GOLEM_SPIKE_PROJECTILE = {
  travel: { key: 'golemSpike', animKey: 'golemSpikeGrow', end: 2, frameRate: 6, repeat: 0 },
  impact: { key: 'golemSpike', animKey: 'golemSpikeBurst', start: 3, end: 3, frameRate: 6, repeat: 0 },
  origin: 'target'
};

// Падающий камень для 'groundPound' (П.43) — валится сверху на зону (origin:
// 'sky') и раскалывается синхронно с моментом урона/тряски земли. Кадры
// 0-4 — приближение и появление трещин, 5-7 — раскол и пыль (8 кадров @8fps).
const GOLEM_ROCK_PROJECTILE = {
  travel: { key: 'golemRock', animKey: 'golemRockFall', end: 4, frameRate: 8, repeat: 0 },
  impact: { key: 'golemRock', animKey: 'golemRockShatter', start: 5, end: 7, frameRate: 8, repeat: 0 },
  origin: 'sky',
  skyOffset: 220,
  visualScale: 0.9
};

const ATTACK_CONFIG = {
  // slam/groundPound — это удары оземь: земля "вздрагивает" (осколки + тряска
  // камеры, groundImpact в Boss.js), словно голем ей управляет. fast — короткий
  // тычок, не про землю, поэтому эффекта не получает.
  // warning = длительность анимации замаха + небольшой запас на удержание
  // финальной позы. Раньше warning не был связан с длительностью анимации —
  // голем успевал закончить замах и постоять секунду, прежде чем зона реально
  // срабатывала (жалоба: атака визуально отделена от урона).
  slam: {
    warning: 700, // анимация 3 кадра @5fps = 600мс + 100мс запаса
    radius: 110,
    damage: 25,
    color: COLORS.dangerMid,
    animKey: 'slam',
    groundImpact: true,
    projectile: GOLEM_SPIKE_PROJECTILE
  },
  fast: {
    warning: 650, // шипы: 3 кадра @6fps = 500мс роста + короткая пауза на пике
    radius: 80,
    damage: 20,
    color: COLORS.dangerLow,
    projectile: GOLEM_SPIKE_PROJECTILE
  },
  groundPound: {
    warning: 900, // камень: 5 кадров @8fps = 625мс падения + пауза + раскол в момент урона
    radius: 170,
    damage: 40,
    color: COLORS.dangerHigh,
    warningBanner: true,
    animKey: 'groundPound',
    groundImpact: true,
    projectile: GOLEM_ROCK_PROJECTILE
  }
};

// Покадровые анимации (П.43, нарисованы вручную в Piskel, 64×64/кадр).
const GOLEM_ANIMATIONS = {
  idle: { key: 'golemIdle', end: 2, frameRate: 3, repeat: -1 },
  slam: { key: 'golemSlam', end: 2, frameRate: 5, repeat: 0 },
  groundPound: { key: 'golemGroundPound', end: 2, frameRate: 4, repeat: 0 },
  hit: { key: 'golemHit', end: 2, frameRate: 10, repeat: 0 },
  death: { key: 'golemDeath', end: 4, frameRate: 5, repeat: 0 }
};

export class GolemBoss extends Boss {
  constructor(scene, x, y) {
    super(scene, x, y, {
      name: 'Голем',
      maxHp: 736, // -8% (баланс, ТЗ п.1)
      damage: 25,
      speed: 60,
      attackCooldown: 2500,
      radius: 80,
      attackSequence: ATTACK_SEQUENCE,
      attackConfig: ATTACK_CONFIG,
      pauseMs: 1300,
      frameWidth: 64,
      frameHeight: 64,
      // Видимый силуэт смещён вверх от геометрического центра кадра (bbox по
      // альфа-каналу idle-кадра ≈(9,6)-(58,43) в кадре 64×64) — без поправки
      // хитбокс уезжал бы вниз от тела.
      hitboxCenterX: 33.5,
      hitboxCenterY: 24.5,
      animations: GOLEM_ANIMATIONS
    });
  }

  // Преследует игрока по всей площадке (X и Y), не только по горизонтали.
  update(time, delta) {
    if (!this.player || this.isDead()) return;
    this.chaseTowards(this.player);
  }
}
