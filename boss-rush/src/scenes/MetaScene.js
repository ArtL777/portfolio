import Phaser from 'phaser';
import { GAME_WIDTH, GAME_HEIGHT, COLORS, TEXT, FONT } from '../config/constants.js';
import { SoundManager } from '../managers/SoundManager.js';
import { metaManager, permanentUpgradeCost, RELICS, META_MAX_TIER, META_DASH_COST } from '../managers/MetaManager.js';
import { ACHIEVEMENTS, achievementTracker } from '../managers/Achievements.js';
import { HudPanels } from '../ui/HudPanels.js';
import { drawPixelPanel } from '../ui/pixelShapes.js';

// Экран траты постоянной валюты (ТЗ п.1 "меню, где игрок может её тратить" +
// п.7 "меню должно стать частью игрового прогресса") — отдельная сцена, а не
// раздел MenuScene, чтобы не захламлять стартовый экран (там всё ещё должна
// быть одна понятная кнопка "начать бой", см. MenuScene).
const STAT_ROWS = [
  { stat: 'damage', label: 'УРОН', perTier: '+2 урона' },
  { stat: 'maxHp', label: 'MAX HP', perTier: '+15 HP' },
  { stat: 'critChance', label: 'ШАНС КРИТА', perTier: '+3%' },
  { stat: 'moveSpeed', label: 'СКОРОСТЬ', perTier: '+4%' }
];

const CONTENT_LEFT = 48;
const LABEL_WRAP_WIDTH = 440;
const BUTTON_ZONE_WIDTH = 150;

export class MetaScene extends Phaser.Scene {
  constructor() {
    super('MetaScene');
  }

  create() {
    HudPanels.hide();
    this.soundManager = new SoundManager();

    this.add.text(GAME_WIDTH / 2, 36, 'МАГАЗИН', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '28px',
      color: TEXT.primary,
      fontStyle: 'bold'
    }).setOrigin(0.5);

    this.coresText = this.add.text(GAME_WIDTH / 2, 74, '', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '18px',
      color: TEXT.accent,
      fontStyle: 'bold'
    }).setOrigin(0.5);

    // Список (постоянные улучшения/реликвии/достижения) вырос при увеличении
    // шрифта в 2.5-3 раза (жалоба: "текст слишком мелкий") настолько, что
    // перестал помещаться на одном экране без скролла — поэтому контент
    // теперь живёт в прокручиваемой области между заголовком и кнопкой НАЗАД,
    // а не просто рисуется на всю высоту сцены, как раньше.
    this.viewportTop = 104;
    this.viewportBottom = GAME_HEIGHT - 96;

    const maskShape = this.make.graphics({ x: 0, y: 0 }, false);
    maskShape.fillStyle(0xffffff);
    maskShape.fillRect(0, this.viewportTop, GAME_WIDTH, this.viewportBottom - this.viewportTop);
    this.contentLayer = this.add.container(0, 0);
    this.contentLayer.setMask(maskShape.createGeometryMask());

    this.drawScrollHints();
    this.drawBackButton();
    this.redraw();

    this.input.on('wheel', (pointer, over, dx, dy) => this.scrollBy(-dy * 0.6));
    this.input.on('pointermove', (pointer) => {
      if (!pointer.isDown) return;
      this.scrollBy(pointer.y - pointer.prevPosition.y);
    });
  }

  refreshCores() {
    this.coresText.setText(`ЯДРА: ${metaManager.cores}`);
  }

  // Стрелки вверх/вниз по центру экрана над и под прокручиваемой областью —
  // показываются только когда реально есть что прокручивать в эту сторону,
  // рисуются треугольниками (не текстовым символом — символы стрелок не
  // входят в объявленный unicode-range самохостящихся шрифтов, см. index.html).
  drawScrollHints() {
    this.hintUp = this.add.triangle(GAME_WIDTH / 2, this.viewportTop - 14, 0, 12, 20, 12, 10, 0, COLORS.accent).setAlpha(0);
    this.hintDown = this.add.triangle(GAME_WIDTH / 2, this.viewportBottom + 14, 0, 0, 20, 0, 10, 12, COLORS.accent).setAlpha(0);
  }

  // Затираем/показываем интерактивность строк, ушедших за пределы видимой
  // области — без этого их hit-зоны остаются кликабельными поверх заголовка
  // или кнопки "НАЗАД", даже когда сама строка невидима под маской.
  updateContentInteractivity() {
    const buffer = 40;
    this.contentLayer.list.forEach((obj) => {
      if (!obj.input) return;
      const worldY = obj.y + this.contentLayer.y;
      obj.input.enabled = worldY > this.viewportTop - buffer && worldY < this.viewportBottom + buffer;
    });
  }

  scrollBy(delta) {
    const viewportHeight = this.viewportBottom - this.viewportTop;
    const maxScroll = Math.max(0, this.contentBottom - this.viewportTop - viewportHeight);
    this.contentLayer.y = Phaser.Math.Clamp(this.contentLayer.y + delta, -maxScroll, 0);
    this.updateContentInteractivity();
    this.hintUp.setAlpha(this.contentLayer.y < -4 ? 0.85 : 0);
    this.hintDown.setAlpha(this.contentLayer.y > -maxScroll + 4 ? 0.85 : 0);
  }

  redraw() {
    this.contentLayer.removeAll(true);
    this.refreshCores();

    let y = this.viewportTop + 10;
    y = this.drawSectionTitle(y, 'ПОСТОЯННЫЕ УЛУЧШЕНИЯ');
    STAT_ROWS.forEach((row) => { y = this.drawStatRow(y, row); });
    y = this.drawDashRow(y);

    y += 20;
    y = this.drawSectionTitle(y, 'РЕЛИКВИИ (экипирована 1)');
    RELICS.forEach((relic) => { y = this.drawRelicRow(y, relic); });

    y += 20;
    y = this.drawSectionTitle(y, 'ДОСТИЖЕНИЯ');
    ACHIEVEMENTS.forEach((ach) => { y = this.drawAchievementRow(y, ach); });

    // +20 запаса снизу, чтобы последняя строка не липла к самому краю маски.
    this.contentBottom = y + 20;
    // Сохраняем текущую позицию прокрутки (не прыгаем в начало списка после
    // каждой покупки), но переприжимаем её к новым границам — высота строк
    // может чуть измениться (например, текст кнопки "купить" -> "МАКС").
    this.scrollBy(0);
  }

  drawSectionTitle(y, text) {
    const t = this.add.text(40, y, text, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '13px',
      color: TEXT.accent,
      fontStyle: 'bold'
    });
    this.contentLayer.add(t);
    return y + 34;
  }

  drawRowPanel(y, height) {
    const { borderG, fillG } = drawPixelPanel(this, 30, y, GAME_WIDTH - 60, height, {
      notch: 8, fill: COLORS.panelFill, border: COLORS.panelBorder
    });
    this.contentLayer.add(borderG);
    this.contentLayer.add(fillG);
  }

  // Общий приём для всех "label + под-текст + кнопка справа" строк — высота
  // панели считается ОТ реального размера текста (Phaser.Text.height уже
  // учитывает fontSize/lineSpacing/перенос строк), а не захардкожена, иначе
  // при таком крупном шрифте текст просто вылезал бы за рамку панели.
  drawLabelSubRow(y, { label, sub, btnLabel, btnColor, onBuy, buyable }) {
    const padTop = 20;
    const gapMid = 8;
    const padBottom = 20;

    const labelText = this.add.text(CONTENT_LEFT, 0, label, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '30px',
      color: TEXT.primary,
      wordWrap: { width: LABEL_WRAP_WIDTH }
    });
    const subText = this.add.text(CONTENT_LEFT, 0, sub, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '22px',
      color: TEXT.muted,
      wordWrap: { width: LABEL_WRAP_WIDTH },
      lineSpacing: 4
    });

    const height = padTop + labelText.height + gapMid + subText.height + padBottom;
    this.drawRowPanel(y, height);

    labelText.setPosition(CONTENT_LEFT, y + padTop);
    subText.setPosition(CONTENT_LEFT, y + padTop + labelText.height + gapMid);
    this.contentLayer.add(labelText);
    this.contentLayer.add(subText);

    const btn = this.add.text(GAME_WIDTH - 40, y + height / 2, btnLabel, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '22px',
      color: btnColor,
      fontStyle: 'bold',
      align: 'right',
      wordWrap: { width: BUTTON_ZONE_WIDTH }
    }).setOrigin(1, 0.5);
    this.contentLayer.add(btn);

    if (onBuy) {
      const hit = this.add.rectangle(GAME_WIDTH - 40 - BUTTON_ZONE_WIDTH / 2, y + height / 2, BUTTON_ZONE_WIDTH, height, 0x000000, 0)
        .setInteractive({ useHandCursor: buyable });
      this.contentLayer.add(hit);
      if (buyable) {
        hit.on('pointerover', () => btn.setScale(1.08));
        hit.on('pointerout', () => btn.setScale(1));
        hit.on('pointerdown', onBuy);
      }
    }

    return y + height + 14;
  }

  drawStatRow(y, row) {
    const tier = metaManager.permanent[row.stat];
    const maxed = tier >= META_MAX_TIER;
    const canBuy = metaManager.canBuyStat(row.stat);

    return this.drawLabelSubRow(y, {
      label: `${row.label}  (ур. ${tier}/${META_MAX_TIER})`,
      sub: row.perTier,
      btnLabel: maxed ? 'МАКС' : `${permanentUpgradeCost(tier)} ¤`,
      btnColor: maxed ? TEXT.muted : (canBuy ? TEXT.accent : '#555a6b'),
      buyable: canBuy,
      onBuy: maxed ? null : () => {
        if (!metaManager.buyStat(row.stat)) return;
        this.soundManager.buttonClick();
        this.redraw();
      }
    });
  }

  drawDashRow(y) {
    if (metaManager.dashUnlocked) return y;
    const canBuy = metaManager.canBuyDash();

    return this.drawLabelSubRow(y, {
      label: 'РЫВОК',
      sub: 'Открывает рывок навсегда, во всех забегах',
      btnLabel: `${META_DASH_COST} ¤`,
      btnColor: canBuy ? TEXT.accent : '#555a6b',
      buyable: canBuy,
      onBuy: () => {
        if (!metaManager.buyDash()) return;
        this.soundManager.buttonClick();
        this.redraw();
      }
    });
  }

  drawRelicRow(y, relic) {
    const unlocked = metaManager.isRelicUnlocked(relic.id);
    const equipped = metaManager.equippedRelic === relic.id;

    let btnLabel;
    let interactive = true;
    if (!unlocked) {
      btnLabel = `${relic.cost} ¤`;
      interactive = metaManager.canBuyRelic(relic.id);
    } else if (equipped) {
      btnLabel = 'ЭКИПИРОВАНО';
      interactive = false;
    } else {
      btnLabel = 'ЭКИПИРОВАТЬ';
    }

    return this.drawLabelSubRow(y, {
      label: relic.label,
      sub: relic.description,
      btnLabel,
      btnColor: equipped ? TEXT.success : (interactive ? TEXT.accent : '#555a6b'),
      buyable: interactive,
      onBuy: !interactive ? null : () => {
        if (!unlocked) {
          if (!metaManager.buyRelic(relic.id)) return;
          if (RELICS.every((r) => metaManager.isRelicUnlocked(r.id))) achievementTracker.unlock('collector');
        } else {
          metaManager.equipRelic(relic.id);
        }
        this.soundManager.buttonClick();
        this.redraw();
      }
    });
  }

  drawAchievementRow(y, ach) {
    const unlocked = achievementTracker.isUnlocked(ach.id);
    const padTop = 16;
    const gapMid = 6;
    const padBottom = 16;
    const icon = unlocked ? '[X]' : '[ ]';

    const label = this.add.text(CONTENT_LEFT, 0, `${icon} ${ach.label}`, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '26px',
      color: unlocked ? TEXT.accent : TEXT.muted,
      fontStyle: unlocked ? 'bold' : 'normal',
      wordWrap: { width: GAME_WIDTH - 60 - CONTENT_LEFT * 2 }
    });
    const desc = this.add.text(CONTENT_LEFT, 0, ach.description, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '20px',
      color: '#6a6f83',
      wordWrap: { width: GAME_WIDTH - 60 - CONTENT_LEFT * 2 },
      lineSpacing: 4
    });

    const height = padTop + label.height + gapMid + desc.height + padBottom;
    this.drawRowPanel(y, height);

    label.setPosition(CONTENT_LEFT, y + padTop);
    desc.setPosition(CONTENT_LEFT, y + padTop + label.height + gapMid);
    this.contentLayer.add(label);
    this.contentLayer.add(desc);

    return y + height + 10;
  }

  drawBackButton() {
    const button = this.add.text(GAME_WIDTH / 2, GAME_HEIGHT - 30, '[ НАЗАД ]', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '18px',
      color: TEXT.primary,
      fontStyle: 'bold'
    }).setOrigin(0.5).setInteractive({ useHandCursor: true }).setDepth(10);

    button.on('pointerover', () => button.setScale(1.08));
    button.on('pointerout', () => button.setScale(1));
    button.on('pointerdown', () => {
      this.soundManager.buttonClick();
      this.scene.start('MenuScene');
    });
  }
}
