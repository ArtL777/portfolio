import Phaser from 'phaser';

// Кадр спрайт-листа Knight (Kenney/itch character pack, П.43): 48×32px,
// строка 0 — idle-анимация (7 кадров).
const FRAME_WIDTH = 48;
const FRAME_HEIGHT = 32;
const IDLE_ANIM_KEY = 'playerIdle';
const ATTACK_ANIM_KEY = 'playerAttack';

// Видимый персонаж в кадре мельче самого кадра (место под анимацию атаки) —
// хитбокс подогнан под силуэт персонажа, а не под весь кадр, иначе игрок
// упирается в босса/границы задолго до того, как спрайты визуально соприкоснутся.
const DISPLAY_SCALE = 2.8;
const COLLISION_RADIUS = 15;
const BODY_RADIUS_LOCAL = COLLISION_RADIUS / DISPLAY_SCALE;

const DASH_SPEED_MULTIPLIER = 3;
const DASH_DURATION = 150;
const DASH_COOLDOWN = 2200;

export class Player {
  constructor(scene, x, y, {
    maxHp = 100,
    damage = 10,
    speed = 300,
    attackCooldown = 400,
    attackRange = 150,
    critChance = 0,
    canDash = false,
    // Реликвии (MetaManager, roguelite-цикл): пассивные эффекты, максимум одна
    // экипирована за раз. secondWind/lifesteal обрабатываются в CombatManager/
    // GameScene (там есть доступ и к игроку, и к боссу), berserk — здесь,
    // потому что это чистый модификатор урона в момент атаки.
    relics = {}
  } = {}) {
    this.scene = scene;
    this.maxHp = maxHp;
    this.hp = maxHp;
    this.damage = damage;
    this.speed = speed;
    this.attackCooldown = attackCooldown;
    this.attackRange = attackRange;
    this.critChance = critChance;
    this.canDash = canDash;
    this.relics = relics;
    this.secondWindUsed = false;
    this.lastAttackTime = -Infinity;
    this.lastDashTime = -Infinity;
    this.dashUntil = 0;
    this.lastMoveDir = { x: 0, y: 1 };
    this.baseScale = DISPLAY_SCALE;

    if (!scene.anims.exists(IDLE_ANIM_KEY)) {
      scene.anims.create({
        key: IDLE_ANIM_KEY,
        frames: scene.anims.generateFrameNumbers('playerKnight', { start: 0, end: 6 }),
        frameRate: 6,
        repeat: -1
      });
    }
    if (!scene.anims.exists(ATTACK_ANIM_KEY)) {
      // Строка 4 (кадры 56-69) — замах мечом с эффектом взмаха.
      scene.anims.create({
        key: ATTACK_ANIM_KEY,
        frames: scene.anims.generateFrameNumbers('playerKnight', { start: 56, end: 69 }),
        frameRate: 24,
        repeat: 0
      });
    }

    this.sprite = scene.add.sprite(x, y, 'playerKnight', 0)
      .setScale(DISPLAY_SCALE)
      .play(IDLE_ANIM_KEY);
    scene.physics.add.existing(this.sprite);
    this.sprite.body.setCircle(
      BODY_RADIUS_LOCAL,
      FRAME_WIDTH / 2 - BODY_RADIUS_LOCAL,
      FRAME_HEIGHT / 2 - BODY_RADIUS_LOCAL
    );
    this.sprite.body.setCollideWorldBounds(true);
  }

  get x() {
    return this.sprite.x;
  }

  get y() {
    return this.sprite.y;
  }

  // input — вектор направления {x, y} в диапазоне [-1, 1], скорость Arcade Body
  // уже не зависит от FPS (px/сек), поэтому отдельный delta здесь не нужен.
  move(input) {
    // Во время рывка обычное движение не перебивает заданную рывком скорость.
    if (this.scene.time.now < this.dashUntil) return;

    const velocity = new Phaser.Math.Vector2(input.x, input.y);
    if (velocity.length() > 0) {
      velocity.normalize();
      this.lastMoveDir = { x: velocity.x, y: velocity.y };
    }
    velocity.scale(this.speed);
    this.sprite.body.setVelocity(velocity.x, velocity.y);

    if (velocity.x !== 0) this.sprite.setFlipX(velocity.x < 0);
  }

  // Улучшение "Рывок" (П.39): короткий импульс скорости в последнем
  // направлении движения, с перезарядкой. Недоступен, пока не открыт.
  tryDash(time) {
    if (!this.canDash) return false;
    if (time - this.lastDashTime < DASH_COOLDOWN) return false;

    this.lastDashTime = time;
    this.dashUntil = time + DASH_DURATION;

    const dir = this.lastMoveDir;
    const dashSpeed = this.speed * DASH_SPEED_MULTIPLIER;
    this.sprite.body.setVelocity(dir.x * dashSpeed, dir.y * dashSpeed);

    this.scene.tweens.add({ targets: this.sprite, alpha: 0.4, duration: DASH_DURATION, yoyo: true });
    return true;
  }

  tryAttack(target, time) {
    if (time - this.lastAttackTime < this.attackCooldown) return { success: false };

    const distance = Phaser.Math.Distance.Between(this.x, this.y, target.x, target.y);
    if (distance > this.attackRange) return { success: false };

    this.lastAttackTime = time;
    const isCrit = Math.random() < this.critChance;
    let damage = isCrit ? this.damage * 2 : this.damage;
    // Реликвия "Ярость" — +25% урона, пока HP ниже 30% (ТЗ: "разные варианты
    // развития" — билд "на грани смерти" отличается от осторожной игры).
    if (this.relics.berserk && this.hp / this.maxHp < 0.3) {
      damage = Math.round(damage * 1.25);
    }

    this.scene.tweens.add({ targets: this.sprite, scale: this.baseScale * 1.25, duration: 90, yoyo: true });
    this.sprite.play(ATTACK_ANIM_KEY);
    this.sprite.once(`animationcomplete-${ATTACK_ANIM_KEY}`, () => this.sprite.play(IDLE_ANIM_KEY));

    return { success: true, damage, isCrit };
  }

  flashHit() {
    this.sprite.setTintFill(0xff3333);
    this.scene.time.delayedCall(120, () => this.sprite.clearTint());
  }
}
