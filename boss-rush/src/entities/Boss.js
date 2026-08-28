import Phaser from 'phaser';
import { settingsManager } from '../managers/SettingsManager.js';

// Визуальный размер и хитбокс считаются НЕЗАВИСИМО: если завязать их друг на
// друга (как раньше), увеличение картинки на телефоне автоматически раздувает
// и хитбокс. HITBOX_RATIO подобран по видимому силуэту существа в кадре —
// даёт мировой радиус столкновений ≈0.27×radius (уменьшено с 0.42 — жалоба:
// контактный урон срабатывал раньше, чем спрайты визуально соприкасались).
// Так как world-радиус хитбокса = radius×HITBOX_RATIO/baseScale×baseScale = radius×HITBOX_RATIO,
// он НЕ зависит от frameWidth конкретного арта — формула одинаково работает
// для любого текстур-кадра (64×64 у Голема, 130×69 у Дракона и т.д.).
const HITBOX_RATIO = 13 / 48;
const VISUAL_BOOST = 1.4;
// Атаки боссов чаще (ТЗ п.2): сокращаем паузу между атаками на ~15% для всех
// боссов разом, не трогая ни warning отдельных атак (игрок всё ещё успевает
// среагировать), ни их индивидуальный баланс урона/радиуса.
const ATTACK_FREQUENCY_MULTIPLIER = 0.85;

export class Boss {
  constructor(scene, x, y, {
    name = 'Boss',
    maxHp = 100,
    damage = 10,
    speed = 0,
    attackCooldown = 2000,
    radius = 60,
    // Каркас паттерна атак общий для всех боссов (П.26): наследники передают
    // только свою последовательность типов и параметры каждой атаки.
    attackSequence = [],
    attackConfig = {},
    pauseMs = 1000,
    cleanupMs = 150,
    // Фазы босса (П.42): на каждом пороге HP пауза между атаками сокращается —
    // бой механически ускоряется без раздувания HP. thresholds — доли от maxHp,
    // по умолчанию 100%→70%→40% (3 фазы); для простого босса можно передать [].
    phaseThresholds = [0.7, 0.4],
    phaseSpeedup = 0.82,
    // Собственный арт босса (П.43): статичные спрайты (см. bosses/*.js) —
    // используются, если не задан animations.idle (см. ниже).
    textureKey,
    frameWidth,
    frameHeight,
    // Центр хитбокса в локальных координатах кадра (П.43: видимый силуэт не
    // всегда совпадает с геометрическим центром кадра — например, для нового
    // арта Слизня центр силуэта смещён вверх). По умолчанию — центр кадра.
    hitboxCenterX = frameWidth / 2,
    hitboxCenterY = frameHeight / 2,
    // Полноценные покадровые анимации (idle/hit/death + именованные анимации
    // атак через attackConfig[type].animKey). Если не задано — используется
    // статичный арт с tween-эффектами (текущее поведение для Golem/Dragon/etc).
    animations = null
  } = {}) {
    this.scene = scene;
    this.name = name;
    this.maxHp = maxHp;
    this.hp = maxHp;
    this.damage = damage;
    this.speed = speed;
    this.attackCooldown = attackCooldown;

    this.attackSequence = attackSequence;
    this.attackConfig = attackConfig;
    this.pauseMs = pauseMs * ATTACK_FREQUENCY_MULTIPLIER;
    this.cleanupMs = cleanupMs;
    this.phaseThresholds = phaseThresholds;
    this.phaseSpeedup = phaseSpeedup;
    this.currentPhase = 1;
    this.onPhaseChange = null;
    this.animations = animations;

    // scale определяет визуальный размер (радиус задаёт иерархию "кто крупнее"),
    // хитбокс — отдельная величина (см. HITBOX_RATIO), не зависящая от VISUAL_BOOST.
    this.baseScale = (radius * 2 * VISUAL_BOOST) / frameWidth;
    this.bodyRadiusLocal = (radius * HITBOX_RATIO) / this.baseScale;
    // Насколько визуальный силуэт (VISUAL_BOOST) шире физического тела
    // (HITBOX_RATIO) — на столько нужно не пускать босса к краю арены в
    // chaseHorizontally/chaseTowards, иначе тело останавливается у самой
    // границы (setCollideWorldBounds), а спрайт всё равно вылезает за неё
    // визуально (жалоба: дракон залезает в нижнюю HUD-панель на подходе к краю).
    this.moveMargin = Math.max(0, radius * (VISUAL_BOOST - HITBOX_RATIO));

    if (animations?.idle) {
      // Полноценная покадровая анимация (П.43): idle крутится в цикле, атаки/урон/
      // смерть — одноразовые анимации, после которых спрайт возвращается в idle.
      this.sprite = scene.add.sprite(x, y, animations.idle.key, 0).setScale(this.baseScale);
      this.sprite.play(this.ensureAnim(animations.idle));
    } else {
      // Статичный арт: вместо покадровой анимации — лёгкое "дыхание" масштабом,
      // чтобы босс не выглядел мёртвым кадром.
      this.sprite = scene.add.sprite(x, y, textureKey).setScale(this.baseScale);
      this.idleTween = scene.tweens.add({
        targets: this.sprite,
        scale: this.baseScale * 1.04,
        duration: 900,
        yoyo: true,
        repeat: -1,
        ease: 'Sine.easeInOut'
      });
    }

    // Физическое тело нужно, чтобы игрок не проходил сквозь босса (collider
    // в GameScene) — immovable + pushable=false, т.к. игрок не должен толкать босса.
    scene.physics.add.existing(this.sprite);
    // setCircle без явного offset НЕ центрирует круг для прямоугольного кадра —
    // координаты считаются от левого верхнего угла кадра, поэтому центр
    // задаём сами через hitboxCenterX/Y (по умолчанию — геометрический центр кадра).
    this.sprite.body.setCircle(
      this.bodyRadiusLocal,
      hitboxCenterX - this.bodyRadiusLocal,
      hitboxCenterY - this.bodyRadiusLocal
    );
    this.sprite.body.setImmovable(true);
    this.sprite.body.pushable = false;
    this.sprite.body.setCollideWorldBounds(true);

    this.player = null;
    this.arena = null;
    this.onPlayerHit = null;
    this.onSpecialWarning = null;
    this.onAttackStart = null;
    this.lastAttackType = null;
    this.pendingTimer = null;
    this.activeTween = null;
    this.activeZone = null;
    this.activeProjectile = null;
  }

  get x() {
    return this.sprite.x;
  }

  get y() {
    return this.sprite.y;
  }

  takeDamage(amount) {
    this.hp = Math.max(0, this.hp - amount);
    this.checkPhaseTransition();
  }

  // Пока hp пробивает очередной порог, переходим на следующую фазу — цикл,
  // а не if, на случай если один удар сразу пробьёт несколько порогов подряд.
  checkPhaseTransition() {
    while (
      this.currentPhase - 1 < this.phaseThresholds.length &&
      this.hp / this.maxHp <= this.phaseThresholds[this.currentPhase - 1] &&
      !this.isDead()
    ) {
      this.currentPhase += 1;
      this.pauseMs *= this.phaseSpeedup;
      this.onPhaseChange?.(this.currentPhase);
    }
  }

  // --- Покадровые анимации (П.43) ---

  // Регистрирует Phaser-анимацию один раз (глобальный AnimationManager переживает
  // рестарт сцены между боями) и возвращает её ключ.
  ensureAnim(cfg) {
    const animKey = cfg.animKey ?? cfg.key;
    if (!this.scene.anims.exists(animKey)) {
      this.scene.anims.create({
        key: animKey,
        frames: this.scene.anims.generateFrameNumbers(cfg.key, { start: cfg.start ?? 0, end: cfg.end }),
        frameRate: cfg.frameRate,
        repeat: cfg.repeat ?? -1
      });
    }
    return animKey;
  }

  // Одноразовая анимация (атака/урон/смерть), после которой спрайт сам
  // возвращается в idle-цикл — если только босс не мёртв.
  playOnce(cfg, onComplete) {
    const animKey = this.ensureAnim(cfg);
    this.sprite.play(animKey);
    this.sprite.once(`animationcomplete-${animKey}`, () => {
      onComplete?.();
      if (!this.isDead() && this.animations?.idle) {
        this.sprite.play(this.ensureAnim(this.animations.idle));
      }
    });
  }

  flashHit() {
    if (this.animations?.hit) {
      this.playOnce(this.animations.hit);
      this.scene.tweens.add({ targets: this.sprite, scale: this.baseScale * 1.1, duration: 90, yoyo: true });
      return;
    }
    this.sprite.setTintFill(0xffffff);
    this.scene.tweens.add({ targets: this.sprite, scale: this.baseScale * 1.1, duration: 90, yoyo: true });
    this.scene.time.delayedCall(90, () => this.sprite.clearTint());
  }

  // Единая точка визуальной смерти босса — реальная анимация, если она есть
  // у конкретного босса, иначе старый tween затухания/уменьшения.
  die() {
    if (this.animations?.death) {
      this.playOnce(this.animations.death);
      return;
    }
    this.scene.tweens.add({ targets: this.sprite, alpha: 0, scale: 0, duration: 500 });
  }

  attack() {}

  update(time, delta) {}

  isDead() {
    return this.hp <= 0;
  }

  // Прижимает точку преследования к внутренней части арены (см. moveMargin) —
  // без this.arena (паттерн ещё не запущен) возвращает координату как есть.
  clampChaseTargetX(x) {
    if (!this.arena) return x;
    return Phaser.Math.Clamp(x, this.arena.x + this.moveMargin, this.arena.x + this.arena.width - this.moveMargin);
  }

  clampChaseTargetY(y) {
    if (!this.arena) return y;
    return Phaser.Math.Clamp(y, this.arena.y + this.moveMargin, this.arena.y + this.arena.height - this.moveMargin);
  }

  // Медленное горизонтальное преследование игрока через Arcade Body —
  // общий строительный блок для боссов, которые умеют двигаться (П.25, П.41).
  chaseHorizontally(target, deadZone = 6) {
    const dx = this.clampChaseTargetX(target.x) - this.sprite.x;
    if (Math.abs(dx) < deadZone) {
      this.sprite.body.setVelocityX(0);
    } else {
      this.sprite.body.setVelocityX(Math.sign(dx) * this.speed);
    }
  }

  // Полноценное преследование по X и Y (в отличие от chaseHorizontally выше).
  // Арт у босса один — лицом к игроку (дизайн-решение), поэтому вертикальное
  // движение спрайт никак не отражает; flipX переключается только по знаку
  // горизонтальной скорости, чтобы босс "смотрел" в сторону движения.
  chaseTowards(target, deadZone = 6) {
    const dx = this.clampChaseTargetX(target.x) - this.sprite.x;
    const dy = this.clampChaseTargetY(target.y) - this.sprite.y;
    const distance = Math.hypot(dx, dy);
    if (distance < deadZone) {
      this.sprite.body.setVelocity(0, 0);
      return;
    }
    this.sprite.body.setVelocity((dx / distance) * this.speed, (dy / distance) * this.speed);
    if (Math.abs(dx) > deadZone) this.sprite.setFlipX(dx < 0);
  }

  // --- Атака по паттерну (общий каркас для всех боссов, П.26) ---

  startPattern(player, arena = null) {
    if (this.attackSequence.length === 0) return;
    this.player = player;
    this.arena = arena;
    this.scheduleNextAttack();
  }

  stopPattern() {
    this.pendingTimer?.remove(false);
    this.activeTween?.stop();
    this.activeZone?.destroy();
    // Снаряд в полёте (П.43): если resolveCircleAttack не успел сработать
    // (босс умер/бой закончился раньше), снаряд иначе остаётся сиротой
    // навсегда летящим по арене — его тоже нужно убрать.
    this.activeProjectile?.destroy();
    this.idleTween?.stop();
    this.pendingTimer = null;
    this.activeTween = null;
    this.activeZone = null;
    this.activeProjectile = null;
  }

  scheduleNextAttack() {
    if (this.isDead()) return;
    this.pendingTimer = this.scene.time.delayedCall(this.pauseMs, () => this.performAttack());
  }

  // Случайный выбор следующей атаки вместо жёсткого цикла (ТЗ п.2: атаки
  // должны ощущаться непредсказуемыми) — но без повтора только что сыгранной
  // атаки подряд, чтобы не было "прилипания" к одному паттерну. Повторы одного
  // типа в attackSequence (напр. ['melee','ranged','melee','special']) при этом
  // сохраняют смысл: они по-прежнему делают этот тип более вероятным.
  pickNextAttackType() {
    if (this.attackSequence.length <= 1) return this.attackSequence[0];
    let type;
    do {
      type = this.attackSequence[Phaser.Math.Between(0, this.attackSequence.length - 1)];
    } while (type === this.lastAttackType);
    return type;
  }

  performAttack() {
    if (this.isDead()) return;
    const type = this.pickNextAttackType();
    this.lastAttackType = type;
    const config = this.attackConfig[type];

    this.onAttackStart?.();
    this.maybeTeleport(config);
    // Замах/заброс проигрывается сразу (не в момент импакта) — так у реальных
    // покадровых анимаций есть время быть увиденными игроком до срабатывания зоны.
    if (config.animKey && this.animations?.[config.animKey]) {
      this.playOnce(this.animations[config.animKey]);
    }

    if (config.shape === 'line') {
      this.telegraphLine(config);
    } else {
      this.telegraphCircle(config);
    }
  }

  // "Появление из-под земли" (П.25): вместо непрерывного движения босс мгновенно
  // переносится в новую точку арены перед атакой — либо случайную, либо рядом с игроком.
  maybeTeleport(config) {
    if (!config.teleport || !this.arena) return;

    const margin = 90;
    const minX = this.arena.x + margin;
    const maxX = this.arena.x + this.arena.width - margin;
    const minY = this.arena.y + margin;
    const maxY = this.arena.y + this.arena.height - margin;

    let x;
    let y;
    if (config.teleportNearPlayer && this.player) {
      x = Phaser.Math.Clamp(this.player.x + Phaser.Math.Between(-30, 30), minX, maxX);
      y = Phaser.Math.Clamp(this.player.y + Phaser.Math.Between(-30, 30), minY, maxY);
    } else {
      x = Phaser.Math.Between(minX, maxX);
      y = Phaser.Math.Between(minY, maxY);
    }

    this.sprite.body.reset(x, y);
  }

  // Куда ставить опасную зону: на игрока (по умолчанию), в случайную точку
  // арены ("мины"), либо на самого босса (после teleport — "вылез и ударил",
  // либо ближняя атака — зона на месте самого босса).
  pickTargetPosition(config) {
    if (config.targetMode === 'random' && this.arena) {
      const margin = 60;
      return {
        x: Phaser.Math.Between(this.arena.x + margin, this.arena.x + this.arena.width - margin),
        y: Phaser.Math.Between(this.arena.y + margin, this.arena.y + this.arena.height - margin)
      };
    }
    if (config.targetMode === 'self') {
      return { x: this.sprite.x, y: this.sprite.y };
    }
    return { x: this.player.x, y: this.player.y };
  }

  // Снаряд, летящий к цели за время предупреждения (config.projectile, П.43) —
  // визуально связывает "дальнюю" анимацию заброса с точкой удара. origin
  // определяет, откуда он стартует: 'boss' (по умолчанию) — от текущей позиции
  // босса, как бросок рукой; 'target' — прямо в точке зоны, без перелёта,
  // просто нарастающий эффект (шипы из-под земли); 'sky' — падает сверху вниз
  // прямо на зону (валун), стартуя на skyOffset пикселей выше цели.
  // displaySize — растянуть спрайт до фиксированных пикселей (не пропорционально
  // scale) вместо простого масштаба: нужно для лазера, который должен покрыть
  // всю высоту/ширину арены, а не просто увеличиться как круглый снаряд.
  spawnProjectile(projConfig, targetX, targetY, duration, displaySize) {
    const travelKey = this.ensureAnim(projConfig.travel);
    const origin = projConfig.origin ?? 'boss';
    const startX = origin === 'boss' ? this.sprite.x : targetX;
    const startY = origin === 'sky' ? targetY - (projConfig.skyOffset ?? 200)
      : origin === 'boss' ? this.sprite.y : targetY;

    const proj = this.scene.add.sprite(startX, startY, projConfig.travel.key, projConfig.travel.start ?? 0)
      .setScale(this.baseScale * (projConfig.visualScale ?? 1));
    if (displaySize) proj.setDisplaySize(displaySize.width, displaySize.height);
    proj.play(travelKey);
    if (origin !== 'target') {
      this.scene.tweens.add({ targets: proj, x: targetX, y: targetY, duration, ease: projConfig.ease ?? 'Linear' });
    }
    this.activeProjectile = proj;
    return proj;
  }

  resolveProjectile(proj, projConfig) {
    const impactKey = this.ensureAnim(projConfig.impact);
    proj.play(impactKey);
    proj.once(`animationcomplete-${impactKey}`, () => {
      proj.destroy();
      if (this.activeProjectile === proj) this.activeProjectile = null;
    });
  }

  // Анимация удара для боссов БЕЗ реальных покадровых анимаций (fallback,
  // легаси-tween). Для анимированных боссов вся выразительность уже в
  // performAttack()/spawnProjectile() — здесь просто ничего не делаем.
  playAttackAnim() {
    this.scene.tweens.add({ targets: this.sprite, scale: this.baseScale * 1.2, duration: 100, yoyo: true });
  }

  // Эффект "земля вздрогнула" (config.groundImpact, П.43) — чисто кодовый,
  // без ассетов: осколки камня, разлетающиеся из точки удара, ударная волна
  // кольцом и лёгкая тряска камеры. Общий для всех боссов, не только Голема.
  groundImpactEffect(x, y, config) {
    // Тумблер "Screen Shake" (ТЗ "Окно 3: GAMEPLAY") — сама эффект-графика
    // (осколки, ударная волна) не зависит от настройки, трясётся только камера.
    if (settingsManager.screenShake) this.scene.cameras.main.shake(160, 0.006);

    const shock = this.scene.add.circle(x, y, config.radius, config.color, 0)
      .setStrokeStyle(4, config.color, 0.85)
      .setScale(0.15);
    this.scene.tweens.add({
      targets: shock,
      scale: 1.15,
      alpha: 0,
      duration: 350,
      ease: 'Cubic.easeOut',
      onComplete: () => shock.destroy()
    });

    const debrisCount = 6;
    for (let i = 0; i < debrisCount; i++) {
      const angle = Phaser.Math.FloatBetween(0, Math.PI * 2);
      const dist = Phaser.Math.FloatBetween(0, config.radius * 0.8);
      const chipX = x + Math.cos(angle) * dist;
      const chipY = y + Math.sin(angle) * dist;
      const chip = this.scene.add.rectangle(chipX, chipY, 6, 6, 0x6b6b6b)
        .setRotation(Phaser.Math.FloatBetween(0, Math.PI));
      this.scene.tweens.add({
        targets: chip,
        y: chipY - Phaser.Math.Between(20, 45),
        alpha: 0,
        duration: 400,
        delay: Phaser.Math.Between(0, 60),
        ease: 'Cubic.easeOut',
        onComplete: () => chip.destroy()
      });
    }
  }

  playTelegraphCues(config) {
    if (config.warningBanner) this.onSpecialWarning?.();
    if (config.jumpCue) {
      this.scene.tweens.add({ targets: this.sprite, scale: this.baseScale * 1.3, duration: 150, yoyo: true });
    }
  }

  pulseZone(zone) {
    this.activeZone = zone;
    this.activeTween = this.scene.tweens.add({
      targets: zone,
      alpha: 0.4,
      duration: 300,
      yoyo: true,
      repeat: -1
    });
  }

  finishZone(zone) {
    this.pendingTimer = this.scene.time.delayedCall(this.cleanupMs, () => {
      zone.destroy();
      if (this.activeZone === zone) this.activeZone = null;
      this.scheduleNextAttack();
    });
  }

  // Круглая опасная зона. Предупреждение обязательно предшествует урону (П.16):
  // сначала зона, и только после задержки config.warning — урон.
  telegraphCircle(config) {
    const { x: targetX, y: targetY } = this.pickTargetPosition(config);
    this.playTelegraphCues(config);

    const zone = this.scene.add.circle(targetX, targetY, config.radius, config.color, 0.18)
      .setStrokeStyle(3, config.color, 0.9);
    this.pulseZone(zone);

    const projectile = config.projectile
      ? this.spawnProjectile(config.projectile, targetX, targetY, config.warning)
      : null;

    this.pendingTimer = this.scene.time.delayedCall(
      config.warning,
      () => this.resolveCircleAttack(zone, targetX, targetY, config, projectile)
    );
  }

  resolveCircleAttack(zone, x, y, config, projectile) {
    this.activeTween?.stop();
    zone.setFillStyle(config.color, 0.6);
    // Легаси-tween нужен только боссам без реальной анимации атаки — иначе
    // будет накладываться поверх уже проигранной покадровой анимации.
    if (!config.animKey) this.playAttackAnim();
    if (projectile) this.resolveProjectile(projectile, config.projectile);
    if (config.groundImpact) this.groundImpactEffect(x, y, config);

    const distance = Phaser.Math.Distance.Between(this.player.x, this.player.y, x, y);
    if (distance <= config.radius) {
      this.onPlayerHit?.(config.damage);
    }

    this.finishZone(zone);
  }

  // Линейная опасная зона на всю ширину (горизонтальная, уклон по Y) или на всю
  // высоту арены (вертикальная, уклон по X) — config.orientation переключает вид.
  telegraphLine(config) {
    const arena = this.arena ?? {
      x: 0, y: 0, width: this.scene.scale.width, height: this.scene.scale.height
    };
    const vertical = config.orientation === 'vertical';
    const coord = vertical ? this.player.x : this.player.y;
    const centerX = vertical ? coord : arena.x + arena.width / 2;
    const centerY = vertical ? arena.y + arena.height / 2 : coord;
    this.playTelegraphCues(config);

    const zone = vertical
      ? this.scene.add.rectangle(coord, arena.y + arena.height / 2, config.thickness, arena.height, config.color, 0.18)
      : this.scene.add.rectangle(arena.x + arena.width / 2, coord, arena.width, config.thickness, config.color, 0.18);
    zone.setStrokeStyle(3, config.color, 0.9);
    this.pulseZone(zone);

    // lineEffect растёт прямо в зоне (origin: 'target' внутри spawnProjectile),
    // растянут на всю длину линии вместо стандартного uniform-масштаба.
    const effect = config.lineEffect
      ? this.spawnProjectile(
        { ...config.lineEffect, origin: 'target' },
        centerX,
        centerY,
        config.warning,
        { width: vertical ? config.lineEffect.visualWidth : arena.width, height: vertical ? arena.height : config.lineEffect.visualWidth }
      )
      : null;

    this.pendingTimer = this.scene.time.delayedCall(
      config.warning,
      () => this.resolveLineAttack(zone, coord, config, vertical, effect)
    );
  }

  resolveLineAttack(zone, coord, config, vertical, effect) {
    this.activeTween?.stop();
    zone.setFillStyle(config.color, 0.6);
    if (!config.animKey) this.playAttackAnim();
    if (effect) this.resolveProjectile(effect, config.lineEffect);

    const playerCoord = vertical ? this.player.x : this.player.y;
    if (Math.abs(playerCoord - coord) <= config.thickness / 2) {
      this.onPlayerHit?.(config.damage);
    }

    this.finishZone(zone);
  }
}
