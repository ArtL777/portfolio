import Phaser from 'phaser';
import { GAME_WIDTH, GAME_HEIGHT, COLORS, TEXT, FONT } from '../config/constants.js';
import { Player } from '../entities/Player.js';
import { GameManager } from '../managers/GameManager.js';
import { BossManager, TOTAL_BOSSES } from '../managers/BossManager.js';
import { CombatManager } from '../managers/CombatManager.js';
import { HealthBar } from '../ui/HealthBar.js';
import { TimerText } from '../ui/TimerText.js';
import { TouchControls } from '../ui/TouchControls.js';
import { SoundManager } from '../managers/SoundManager.js';
import { progressManager } from '../managers/ProgressManager.js';
import { statsManager } from '../managers/StatsManager.js';
import { HudPanels } from '../ui/HudPanels.js';
import { drawPixelPanel } from '../ui/pixelShapes.js';
import { metaManager } from '../managers/MetaManager.js';
import { achievementTracker } from '../managers/Achievements.js';
import { spawnFloatingText } from '../ui/FloatingText.js';
import { hitSpark } from '../ui/hitSpark.js';
import { settingsManager } from '../managers/SettingsManager.js';
import { notifyGameplayStart, notifyGameplayStop, submitLeaderboardScore } from '../managers/YandexSDK.js';

// Порог ширины окна, с которого показываются боковые HTML HUD-панели (см.
// @media в index.html — значение должно совпадать с тем, что там). Ниже
// порога панели скрыты (мобильный/узкий экран), и HUD остаётся внутри канваса,
// как было раньше — портретный режим под Яндекс Игры не должен пострадать.
const HUD_BREAKPOINT = 1300;

// Арена уже canvas: сверху и снизу оставлен отступ под UI (HP-бары, таймер).
const ARENA = { x: 40, y: 160, width: GAME_WIDTH - 80, height: GAME_HEIGHT - 320 };
const BATTLE_DURATION = 60;
const RESULT_TRANSITION_DELAY = 900;

// Контактный урон за долгое "прижимание" к боссу: небольшой и не чаще раза в CONTACT_INTERVAL.
const CONTACT_DAMAGE = 5;
const CONTACT_INTERVAL = 700;

// Награда за победу (П.39): база + бонус за оставшееся время (чем быстрее — тем больше монет).
const VICTORY_BASE_COINS = 20;

// Постоянная валюта (roguelite-цикл) — начисляется за КАЖДЫЙ забег, победный
// или нет (даже поражение продвигает мета-прогрессию, чтобы забег никогда не
// ощущался потраченным впустую). За боссов, побеждённых в этом забеге, плюс
// бонус за полное прохождение и множитель за цикл NG+.
const CORES_PER_BOSS = 4;
const CORES_FULL_CLEAR_BONUS = 25;
// Комбо-попап (ТЗ "сделай бои сочнее") — показывается не на каждый удар,
// а на круглых порогах, иначе он бы мельтешил и раздражал, а не радовал.
const COMBO_POPUP_STEP = 5;

// Свой фон под конкретного босса (П.43, по индексу в BossManager) — целиковая
// картинка на весь экран вместо процедурного пола. Кому фона не досталось —
// использует общий процедурный (см. drawProceduralArena).
const CUSTOM_BACKGROUNDS = { 0: 'arenaBgSlime', 1: 'arenaBgGolem', 2: 'arenaBgDragon', 3: 'arenaBgRobot', 4: 'arenaBgWorm' };

export class GameScene extends Phaser.Scene {
  constructor() {
    super('GameScene');
  }

  preload() {
    this.load.image('arenaFloor', 'assets/images/arena_floor.png');
    this.load.image('arenaWater', 'assets/images/arena_water.png');
    this.load.image('decorFlower', 'assets/images/decor_flower.png');
    // Свой фон под конкретных боссов (см. CUSTOM_BACKGROUNDS) — остальные
    // боссы пока используют общий процедурный фон выше.
    this.load.image('arenaBgSlime', 'assets/images/arena_bg_slime.png');
    this.load.image('arenaBgGolem', 'assets/images/arena_bg_golem.png');
    this.load.image('arenaBgDragon', 'assets/images/arena_bg_dragon.png');
    this.load.image('arenaBgRobot', 'assets/images/arena_bg_robot.png');
    this.load.image('arenaBgWorm', 'assets/images/arena_bg_worm.png');
    this.load.spritesheet('playerKnight', 'assets/images/player_knight.png', { frameWidth: 48, frameHeight: 32 });
    // Собственный арт под каждого босса (П.43) — источники см. в комментариях bosses/*.js.
    // Слизень — полноценные покадровые анимации (нарисованы вручную, 32×32/кадр).
    this.load.spritesheet('slimeIdle', 'assets/images/slime_idle.png', { frameWidth: 32, frameHeight: 32 });
    this.load.spritesheet('slimeHit', 'assets/images/slime_hit.png', { frameWidth: 32, frameHeight: 32 });
    this.load.spritesheet('slimeMelee', 'assets/images/slime_melee.png', { frameWidth: 32, frameHeight: 32 });
    this.load.spritesheet('slimeRanged', 'assets/images/slime_ranged.png', { frameWidth: 32, frameHeight: 32 });
    this.load.spritesheet('slimeBlob', 'assets/images/slime_blob.png', { frameWidth: 32, frameHeight: 32 });
    this.load.spritesheet('slimeDeath', 'assets/images/slime_death.png', { frameWidth: 32, frameHeight: 32 });
    // Голем — тоже покадровые анимации (нарисованы вручную, 64×64/кадр).
    this.load.spritesheet('golemIdle', 'assets/images/golem_idle.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('golemSlam', 'assets/images/golem_slam.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('golemGroundPound', 'assets/images/golem_groundpound.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('golemHit', 'assets/images/golem_hit.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('golemDeath', 'assets/images/golem_death.png', { frameWidth: 64, frameHeight: 64 });
    // Эффекты в зоне атаки (не тело босса) — растущие шипы вместо жёлтого
    // круга у 'fast' и падающий камень-снаряд у 'groundPound'.
    this.load.spritesheet('golemSpike', 'assets/images/golem_spike.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('golemRock', 'assets/images/golem_rock.png', { frameWidth: 64, frameHeight: 64 });
    // Дракон — покадровые анимации (нарисованы на заказ вручную, 64×64/кадр):
    // idle, урон, смерть, каст огня (перед атакой) и отдельный снаряд-шар.
    this.load.spritesheet('dragonIdle', 'assets/images/dragon_idle.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('dragonHit', 'assets/images/dragon_hit.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('dragonDeath', 'assets/images/dragon_death.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('dragonBreath', 'assets/images/dragon_breath.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('dragonFireball', 'assets/images/dragon_fireball.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('dragonFireBreath', 'assets/images/dragon_fire_breath.png', { frameWidth: 64, frameHeight: 64 });
    // Космический червь — idle, шипы из-под земли (наземный эффект) и общая
    // анимация "вынырнуть и ударить" для burrowStrike/emerge (П.43).
    this.load.spritesheet('wormIdle', 'assets/images/worm_idle.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('wormSpike', 'assets/images/worm_spike.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('wormTeleport', 'assets/images/worm_teleport.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('wormHit', 'assets/images/worm_hit.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('wormDeath', 'assets/images/worm_death.png', { frameWidth: 64, frameHeight: 64 });
    // Робот — idle, заряд пушки + снаряд-баллон, лазер (растёт в зоне), мина (П.43).
    this.load.spritesheet('robotIdle', 'assets/images/robot_idle.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('robotCharge', 'assets/images/robot_charge.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('robotShot', 'assets/images/robot_shot.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('robotLaser', 'assets/images/robot_laser.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('robotMine', 'assets/images/robot_mine.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('robotHit', 'assets/images/robot_hit.png', { frameWidth: 64, frameHeight: 64 });
    this.load.spritesheet('robotDeath', 'assets/images/robot_death.png', { frameWidth: 64, frameHeight: 64 });
  }

  create(data) {
    const bossIndex = data?.bossIndex ?? 0;
    const ngPlusCycle = data?.ngPlusCycle ?? 0;
    this.useSidePanels = window.matchMedia(`(min-width: ${HUD_BREAKPOINT}px)`).matches;

    this.gameManager = new GameManager();
    this.gameManager.currentBossIndex = bossIndex;
    this.gameManager.ngPlusCycle = ngPlusCycle;
    this.gameManager.timeLeft = BATTLE_DURATION;

    this.bossManager = new BossManager();
    this.combatManager = new CombatManager();
    this.soundManager = new SoundManager();
    notifyGameplayStart();

    // Отслеживаем "чистый" бой (без урона) и серию попаданий подряд — для
    // достижения "без единой царапины" и комбо-попапов (ТЗ: сочность боя).
    this.noDamageTaken = true;
    this.combo = 0;

    this.physics.world.setBounds(ARENA.x, ARENA.y, ARENA.width, ARENA.height);
    this.drawArena(bossIndex);

    const boss = this.bossManager.createBoss(this, bossIndex, GAME_WIDTH / 2, ARENA.y + 140, ngPlusCycle);
    this.gameManager.currentBoss = boss;
    // Статы игрока каждый бой пересобираются из текущих улучшений забега (П.39).
    this.player = new Player(
      this,
      GAME_WIDTH / 2,
      ARENA.y + ARENA.height - 140,
      progressManager.getPlayerConfig()
    );
    this.createUi(boss, bossIndex);
    this.touchControls = new TouchControls(this, { dashEnabled: progressManager.dashUnlocked });
    this.createInput();

    boss.onPlayerHit = (damage) => this.handlePlayerHit(damage);
    boss.onSpecialWarning = () => this.showWarningBanner();
    boss.onAttackStart = () => this.soundManager.bossAttack();
    boss.onPhaseChange = (phase) => this.showPhaseBanner(phase);
    boss.startPattern(this.player, ARENA);

    // Хитбокс босса блокирует игрока (не проходит насквозь); при долгом
    // "прижимании" — небольшой урон, но не чаще CONTACT_INTERVAL.
    this.lastContactDamageTime = -Infinity;
    this.physics.add.collider(this.player.sprite, boss.sprite, () => this.handleBossContact());

    this.timerEvent = this.time.addEvent({ delay: 1000, loop: true, callback: () => this.tickTimer() });

    // Онбординг (ТЗ п.6) — только для самого первого забега в жизни, коротко
    // и без остановки игры: бой уже идёт, подсказки сами гаснут через пару секунд.
    if (!metaManager.tutorialSeen) this.showOnboarding();
  }

  // Три коротких баннера подряд вместо одного длинного туториала — каждый
  // виден несколько секунд и сам угасает, ничего не блокирует и не требует
  // подтверждения от игрока (ТЗ: "короткое и ненавязчивое обучение").
  showOnboarding() {
    metaManager.markTutorialSeen();
    const steps = [
      'WASD / СТРЕЛКИ — ДВИЖЕНИЕ',
      'ПРОБЕЛ / ТАП — АТАКА ВБЛИЗИ',
      'ЗОНЫ НА ЗЕМЛЕ — УКЛОНЯЙСЯ!'
    ];
    steps.forEach((text, i) => {
      this.time.delayedCall(i * 2200, () => {
        if (this.gameManager.isGameOver) return;
        this.showFeedback(text, TEXT.accent);
      });
    });
  }

  drawArena(bossIndex) {
    const bgKey = CUSTOM_BACKGROUNDS[bossIndex];
    if (bgKey) {
      this.drawCustomBackground(bgKey);
    } else {
      this.drawProceduralArena();
    }
  }

  // Цельная картинка на весь канвас вместо процедурного пола (П.43) — своя
  // рамка (лес/каньон) уже нарисована в самом арте, отдельную обводку арены
  // поверх не рисуем. Масштаб — "cover": заполняет экран без искажений
  // пропорций, лишнее обрезается по границам канваса (Phaser это делает сам).
  drawCustomBackground(key) {
    const { width, height } = this.textures.get(key).getSourceImage();
    const scale = Math.max(GAME_WIDTH / width, GAME_HEIGHT / height);
    this.add.image(GAME_WIDTH / 2, GAME_HEIGHT / 2, key).setScale(scale);
  }

  // Пол арены — Kenney "Roguelike RPG Pack" (CC0, public/assets/images/*): травяной
  // тайл замощён TileSprite и обрезан по скруглённым углам маской; пруд и цветы —
  // чисто декоративные элементы поверх, без физики, для более живой сцены.
  drawProceduralArena() {
    const floor = this.add.tileSprite(
      ARENA.x + ARENA.width / 2,
      ARENA.y + ARENA.height / 2,
      ARENA.width,
      ARENA.height,
      'arenaFloor'
    );

    const maskShape = this.make.graphics({ x: 0, y: 0 }, false);
    maskShape.fillStyle(0xffffff);
    maskShape.fillRoundedRect(ARENA.x, ARENA.y, ARENA.width, ARENA.height, 28);
    floor.setMask(maskShape.createGeometryMask());

    // Пруд и цветочные грядки размещены в средней полосе арены, подальше от
    // нижних углов — там сейчас джойстик и кнопка атаки (не перекрываем их).
    this.drawPond(ARENA.x + 130, ARENA.y + 480, 90, 60);

    [
      [ARENA.x + 100, ARENA.y + 100],
      [ARENA.x + ARENA.width - 100, ARENA.y + 100],
      [ARENA.x + ARENA.width - 110, ARENA.y + 480],
      [ARENA.x + ARENA.width / 2 + 60, ARENA.y + ARENA.height - 220]
    ].forEach(([fx, fy]) => this.drawFlowerPatch(fx, fy));

    const g = this.add.graphics();
    g.lineStyle(2, COLORS.arenaBorder, 1);
    g.strokeRoundedRect(ARENA.x, ARENA.y, ARENA.width, ARENA.height, 28);
  }

  drawPond(x, y, radiusX, radiusY) {
    const water = this.add.tileSprite(x, y, radiusX * 2, radiusY * 2, 'arenaWater');
    const maskShape = this.make.graphics({ x: 0, y: 0 }, false);
    maskShape.fillStyle(0xffffff);
    maskShape.fillEllipse(x, y, radiusX * 2, radiusY * 2);
    water.setMask(maskShape.createGeometryMask());

    this.add.ellipse(x, y, radiusX * 2, radiusY * 2, 0x000000, 0).setStrokeStyle(3, 0x2a7a7a, 0.8);
  }

  // Тайл цветов задуман как замащиваемый (края специально притемнены под
  // соседние тайлы) — как одиночный спрайт он показывает обрезанный край,
  // поэтому кладём его маленькой замощённой заплаткой, как пруд и пол.
  drawFlowerPatch(x, y, size = 48) {
    const patch = this.add.tileSprite(x, y, size, size, 'decorFlower');
    const maskShape = this.make.graphics({ x: 0, y: 0 }, false);
    maskShape.fillStyle(0xffffff);
    maskShape.fillRoundedRect(x - size / 2, y - size / 2, size, size, 10);
    patch.setMask(maskShape.createGeometryMask());
  }

  drawPanel(x, y, width, height) {
    drawPixelPanel(this, x, y, width, height, { notch: 12, fill: COLORS.panelFill, border: COLORS.panelBorder });
  }

  createUi(boss, bossIndex) {
    // Desktop-композиция (переработка интерфейса): на широком экране HP боссов/
    // игрока, таймер, статистика и список улучшений живут в HTML-панелях по
    // бокам канваса (см. index.html), а не внутри игрового поля — самого
    // канваса это не касается, он остаётся тем же портретным 720×1280.
    // На узком/мобильном экране панели скрыты (CSS), и HUD рисуется в канвасе,
    // как и раньше — без этой ветки мобильная версия осталась бы без HUD вовсе.
    HudPanels.hide();
    if (this.useSidePanels) {
      HudPanels.showBattle();
      HudPanels.setBossHp(boss.name.toUpperCase(), boss.hp, boss.maxHp);
      HudPanels.setPlayerHp(this.player.hp, this.player.maxHp);
      HudPanels.setLevel(bossIndex, TOTAL_BOSSES);
      HudPanels.setTimer(this.gameManager.timeLeft);
      HudPanels.setStats(progressManager.getPlayerConfig());
      HudPanels.setUpgrades(progressManager.getSummaryLines());
    } else {
      this.drawPanel(30, 20, GAME_WIDTH - 60, 100);
      this.add.text(GAME_WIDTH / 2, 45, boss.name.toUpperCase(), {
        fontFamily: FONT.display, resolution: 3,
        fontSize: '20px',
        color: TEXT.primary,
        fontStyle: 'bold'
      }).setOrigin(0.5);
      // Явный счётчик "какой сейчас босс" — жалоба: "не понятно когда босс переходит на следующий этап".
      this.add.text(GAME_WIDTH / 2, 66, `БОСС ${bossIndex + 1} / ${TOTAL_BOSSES}`, {
        fontFamily: FONT.body, resolution: 3,
        fontSize: '13px',
        color: TEXT.muted
      }).setOrigin(0.5);

      this.bossHealthBar = new HealthBar(this, 60, 87, 600, 22, { color: COLORS.bossHpFill, backgroundColor: COLORS.barBg });
      this.bossHealthBar.setValue(boss.hp, boss.maxHp);

      this.timerText = new TimerText(this, GAME_WIDTH - 60, 45);
      this.timerText.setValue(this.gameManager.timeLeft);

      this.drawPanel(30, GAME_HEIGHT - 100, GAME_WIDTH - 60, 80);
      this.add.text(60, GAME_HEIGHT - 88, 'HP', { fontFamily: FONT.body, resolution: 3, fontSize: '15px', color: TEXT.muted });
      this.playerHealthBar = new HealthBar(this, 60, GAME_HEIGHT - 62, 400, 22, { color: COLORS.playerHpFill, backgroundColor: COLORS.barBg });
      this.playerHealthBar.setValue(this.player.hp, this.player.maxHp);
    }

    // Внутри арены (не в узком зазоре между панелью и ареной, куда баннер
    // раньше наполовину проваливался под нижний край верхней панели).
    this.warningBackdrop = this.add.rectangle(GAME_WIDTH / 2, ARENA.y + 38, 220, 40, 0x000000, 0.55)
      .setAlpha(0);
    this.warningText = this.add.text(GAME_WIDTH / 2, ARENA.y + 38, 'WARNING', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '24px',
      color: TEXT.danger,
      fontStyle: 'bold'
    }).setOrigin(0.5).setAlpha(0);

    this.feedbackText = this.add.text(GAME_WIDTH / 2, GAME_HEIGHT / 2, '', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '36px',
      color: TEXT.primary,
      fontStyle: 'bold'
    }).setOrigin(0.5).setAlpha(0);
  }

  // Три маленьких моста между игровыми данными и HUD (канвас или HTML-панель,
  // см. useSidePanels в create()) — чтобы места, где меняется HP/таймер, не
  // дублировали ветвление "какой сейчас режим отображения" сами по себе.
  updateBossHp(boss) {
    if (this.useSidePanels) {
      HudPanels.setBar('hud-boss-bar', boss.hp, boss.maxHp);
    } else {
      this.bossHealthBar.setValue(boss.hp, boss.maxHp);
    }
  }

  updatePlayerHp() {
    if (this.useSidePanels) {
      HudPanels.setPlayerHp(this.player.hp, this.player.maxHp);
    } else {
      this.playerHealthBar.setValue(this.player.hp, this.player.maxHp);
    }
  }

  updateTimer() {
    if (this.useSidePanels) {
      HudPanels.setTimer(this.gameManager.timeLeft);
    } else {
      this.timerText.setValue(this.gameManager.timeLeft);
    }
  }

  createInput() {
    this.cursors = this.input.keyboard.createCursorKeys();
    this.wasd = this.input.keyboard.addKeys('W,A,S,D');
    this.input.keyboard.on('keydown-SPACE', () => this.tryPlayerAttack());
    this.input.keyboard.on('keydown-SHIFT', () => this.tryPlayerDash());

    // Второй активный поинтер — чтобы можно было одновременно держать
    // джойстик и тапать по кнопке атаки на мобильном (П.31).
    this.input.addPointer(2);

    this.input.on('pointerdown', (pointer) => {
      if (this.touchControls.isInJoystickZone(pointer)) {
        this.touchControls.beginJoystick(pointer);
        return;
      }
      if (this.touchControls.isInDashZone(pointer)) {
        this.tryPlayerDash();
        return;
      }
      // Тап по кнопке атаки или в любом другом месте арены — атака (П.10: ЛКМ/тап).
      this.tryPlayerAttack();
    });
    this.input.on('pointermove', (pointer) => this.touchControls.updateJoystick(pointer));
    this.input.on('pointerup', (pointer) => this.touchControls.endJoystick(pointer));
    this.input.on('pointerupoutside', (pointer) => this.touchControls.endJoystick(pointer));
  }

  update(time, delta) {
    if (this.gameManager.isGameOver) return;
    this.player.move(this.readMovementInput());
    this.gameManager.currentBoss.update(time, delta);
  }

  // Слой ввода изолирован от Player: сцена читает клавиатуру и джойстик,
  // Player знает только итоговый вектор направления (П.31). Player.move()
  // сам нормализует вектор, поэтому клавиатуру и джойстик можно просто сложить.
  readMovementInput() {
    let x = 0;
    let y = 0;
    if (this.cursors.left.isDown || this.wasd.A.isDown) x -= 1;
    if (this.cursors.right.isDown || this.wasd.D.isDown) x += 1;
    if (this.cursors.up.isDown || this.wasd.W.isDown) y -= 1;
    if (this.cursors.down.isDown || this.wasd.S.isDown) y += 1;

    const touch = this.touchControls.getVector();
    x += touch.x;
    y += touch.y;

    return { x, y };
  }

  tryPlayerAttack() {
    if (this.gameManager.isGameOver) return;

    const boss = this.gameManager.currentBoss;
    const result = this.player.tryAttack(boss, this.time.now);
    if (!result.success) return;

    this.combatManager.damageBoss(boss, result.damage);
    this.updateBossHp(boss);
    this.soundManager.hit();

    // Сочность боя (ТЗ п.5): числа урона, искры попадания, комбо-счётчик.
    spawnFloatingText(this, boss.x, boss.y - 30, `-${result.damage}`, {
      color: result.isCrit ? TEXT.accent : '#ffffff',
      fontSize: result.isCrit ? '24px' : '18px'
    });
    hitSpark(this, boss.x, boss.y, result.isCrit ? 0xffcc00 : 0xffffff);
    if (result.isCrit) this.showCritFeedback(boss.x, boss.y);

    this.combo += 1;
    if (this.combo > 0 && this.combo % COMBO_POPUP_STEP === 0) {
      spawnFloatingText(this, this.player.x, this.player.y - 50, `x${this.combo} КОМБО`, {
        color: TEXT.success,
        fontSize: '18px',
        rise: 60
      });
    }

    // Реликвия "Вампиризм" — лечит долей нанесённого урона (ТЗ: реликвии как
    // способ разнообразить забег).
    if (this.player.relics.lifesteal) {
      this.player.hp = Math.min(this.player.maxHp, this.player.hp + Math.round(result.damage * 0.08));
      this.updatePlayerHp();
    }

    // Проверка победы выполняется сразу после урона (П.22), не отложенно.
    if (boss.isDead()) {
      this.endBattle('victory', 'boss-defeated');
    }
  }

  tryPlayerDash() {
    if (this.gameManager.isGameOver) return;
    this.player.tryDash(this.time.now);
  }

  showCritFeedback(x, y) {
    const text = this.add.text(x, y - 40, 'КРИТ!', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '20px',
      color: TEXT.accent,
      fontStyle: 'bold'
    }).setOrigin(0.5);
    this.tweens.add({ targets: text, y: y - 80, alpha: 0, duration: 600, onComplete: () => text.destroy() });
  }

  handleBossContact() {
    if (this.gameManager.isGameOver) return;

    const now = this.time.now;
    if (now - this.lastContactDamageTime < CONTACT_INTERVAL) return;
    this.lastContactDamageTime = now;

    this.handlePlayerHit(CONTACT_DAMAGE);
  }

  handlePlayerHit(damage) {
    if (this.gameManager.isGameOver) return;

    this.noDamageTaken = false;
    this.combo = 0;
    spawnFloatingText(this, this.player.x, this.player.y - 30, `-${damage}`, { color: TEXT.danger, fontSize: '18px' });

    // "Второе дыхание" (реликвия) может спасти от летального урона — тогда
    // бой не завершается, игрок остаётся на 1 HP (см. CombatManager.damagePlayer).
    const saved = this.combatManager.damagePlayer(this.player, damage);
    this.updatePlayerHp();
    this.soundManager.playerDamage();
    // Тумблер "Vibration" (ТЗ "Окно 3: GAMEPLAY") — есть не на всех устройствах,
    // navigator.vibrate просто отсутствует на десктопе/iOS, поэтому проверяем перед вызовом.
    if (settingsManager.vibration && navigator.vibrate) navigator.vibrate(80);

    if (saved) {
      this.showFeedback('ВТОРОЕ ДЫХАНИЕ!', TEXT.accent);
      return;
    }

    if (this.player.hp <= 0) {
      this.endBattle('defeat', 'player-defeated');
    }
  }

  tickTimer() {
    if (this.gameManager.isGameOver) return;

    this.gameManager.timeLeft = Math.max(0, this.gameManager.timeLeft - 1);
    this.updateTimer();

    const boss = this.gameManager.currentBoss;
    if (this.gameManager.timeLeft <= 0 && !boss.isDead()) {
      this.endBattle('defeat', 'timeout');
    }
  }

  showWarningBanner() {
    this.warningText.setAlpha(1);
    this.warningBackdrop.setAlpha(1);
    this.tweens.add({ targets: [this.warningText, this.warningBackdrop], alpha: 0, duration: 800, delay: 300 });
  }

  // Смена фазы (П.42): отдельная от WARNING надпись — не про конкретную атаку,
  // а про то, что дальше бой пойдёт быстрее (пауза между атаками боссом уже сокращена).
  showPhaseBanner(phase) {
    const boss = this.gameManager.currentBoss;
    this.showFeedback(`ФАЗА ${phase}`, TEXT.danger);
    this.tweens.add({ targets: boss.sprite, scale: boss.baseScale * 1.35, duration: 200, yoyo: true });
  }

  showFeedback(text, color) {
    this.feedbackText.setText(text).setColor(color).setAlpha(1).setScale(0.8);
    this.tweens.add({ targets: this.feedbackText, scale: 1, alpha: 0, duration: 900, ease: 'Cubic.easeOut' });
  }

  // Единая точка завершения боя: флаг isGameOver гарантирует, что после
  // Victory/Defeat никакие повторные события не изменят исход (П.36).
  endBattle(result, reason) {
    if (this.gameManager.isGameOver) return;
    this.gameManager.isGameOver = true;
    this.gameManager.result = result;

    this.player.sprite.body.setVelocity(0, 0);
    this.timerEvent.remove(false);

    const boss = this.gameManager.currentBoss;
    boss.stopPattern();

    let coinsEarned = 0;

    if (result === 'victory') {
      coinsEarned = VICTORY_BASE_COINS + this.gameManager.timeLeft;
      progressManager.addCoins(coinsEarned);
      this.soundManager.bossDefeated();
      this.showFeedback('BOSS DEFEATED!', TEXT.success);
      boss.die();
    } else {
      // Забег прогрессии сбрасывается при поражении (session-only, П.45 — сохранения отдельным этапом).
      progressManager.reset();
      this.showFeedback(reason === 'timeout' ? "TIME'S UP" : 'ПОРАЖЕНИЕ', TEXT.danger);
    }

    const timeTaken = BATTLE_DURATION - this.gameManager.timeLeft;
    const ngPlusCycle = this.gameManager.ngPlusCycle;
    if (result === 'victory') progressManager.totalTimeElapsed += timeTaken;
    statsManager.recordRun({
      result,
      bossIndex: this.gameManager.currentBossIndex,
      coinsEarned,
      totalBosses: TOTAL_BOSSES,
      ngPlusCycle,
      timeTaken,
      totalTimeElapsed: progressManager.totalTimeElapsed
    });

    // Постоянная валюта капает за любой исход (ТЗ: забег не должен ощущаться
    // потраченным впустую) — за реально побеждённых в этом забеге боссов.
    const bossesBeatenThisRun = result === 'victory'
      ? this.gameManager.currentBossIndex + 1
      : this.gameManager.currentBossIndex;
    const fullClear = result === 'victory' && bossesBeatenThisRun >= TOTAL_BOSSES;
    const coresEarned = bossesBeatenThisRun * CORES_PER_BOSS
      + (fullClear ? CORES_FULL_CLEAR_BONUS : 0)
      + bossesBeatenThisRun * ngPlusCycle * 2;
    metaManager.addCores(coresEarned);

    notifyGameplayStop();
    // Лидерборд Яндекс Игр — только за реальное полное прохождение (та же
    // метрика, что и локальный лидерборд, см. LeaderboardModal): меньше
    // секунд = лучше, technical name должен существовать в кабинете разработчика.
    if (fullClear) submitLeaderboardScore(progressManager.totalTimeElapsed);

    const newAchievements = achievementTracker.checkRunEnd({
      result,
      bossIndex: this.gameManager.currentBossIndex,
      timeTaken,
      noDamage: this.noDamageTaken,
      totalBosses: TOTAL_BOSSES,
      ngPlusCycle,
      runsPlayed: statsManager.runsPlayed
    });

    this.time.delayedCall(RESULT_TRANSITION_DELAY, () => {
      this.scene.start('ResultScene', {
        result,
        bossIndex: this.gameManager.currentBossIndex,
        timeTaken,
        coinsEarned,
        coresEarned,
        ngPlusCycle,
        newAchievements
      });
    });
  }
}
