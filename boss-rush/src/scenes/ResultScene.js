import Phaser from 'phaser';
import { GAME_WIDTH, GAME_HEIGHT, TEXT, FONT } from '../config/constants.js';
import { ResultPanel } from '../ui/ResultPanel.js';
import { PixelCard } from '../ui/PixelCard.js';
import { SoundManager } from '../managers/SoundManager.js';
import { progressManager } from '../managers/ProgressManager.js';
import { TOTAL_BOSSES } from '../managers/BossManager.js';
import { HudPanels } from '../ui/HudPanels.js';
import { metaManager } from '../managers/MetaManager.js';
import { statsManager } from '../managers/StatsManager.js';
import { showInterstitialAd } from '../managers/YandexSDK.js';

// Межстраничная реклама — не на каждый переход (было бы навязчиво), а на
// "естественных" паузах между забегами (начать заново / выйти в меню /
// New Game+), не чаще раза в AD_EVERY_N_RUNS забегов.
const AD_EVERY_N_RUNS = 3;
// Переход между сценами НЕ ДОЛЖЕН зависеть от рекламы — даже если
// showInterstitialAd() (у которой уже есть свой внутренний таймаут, см.
// YandexSDK.js) когда-нибудь не вызовет onDone вообще, игрок не должен
// застрять на экране результата навсегда. Второй, более короткий и
// полностью независимый предохранитель прямо здесь — минимальный риск для
// самого важного перехода в игре важнее идеальной чистоты кода.
function maybeShowInterstitial(onDone) {
  if (statsManager.runsPlayed > 0 && statsManager.runsPlayed % AD_EVERY_N_RUNS === 0) {
    let done = false;
    const finish = () => { if (done) return; done = true; onDone(); };
    setTimeout(finish, 9000);
    showInterstitialAd(finish);
  } else {
    onDone();
  }
}

const CARD_WIDTH = 600;
const CARD_HEIGHT = 140;
const CARD_GAP = 26;
const CARDS_START_Y = 340;
const REROLL_COST = 15;

export class ResultScene extends Phaser.Scene {
  constructor() {
    super('ResultScene');
  }

  create(data) {
    HudPanels.hide();
    const {
      result = 'defeat', bossIndex = 0, timeTaken = 0, coinsEarned = 0,
      coresEarned = 0, ngPlusCycle = 0, newAchievements = []
    } = data || {};
    const soundManager = new SoundManager();
    this.cards = [];

    if (result === 'victory') {
      soundManager.victory();
      // Баг: после 5-го босса игра зацикливалась обратно на Слизня. Финальная
      // победа — отдельный экран без карточки улучшения (следующего боя не будет).
      if (bossIndex + 1 >= TOTAL_BOSSES) {
        this.createFinalVictoryScreen(coinsEarned, coresEarned, ngPlusCycle, newAchievements, soundManager);
      } else {
        this.createVictoryScreen(bossIndex, timeTaken, coinsEarned, coresEarned, ngPlusCycle, newAchievements, soundManager);
      }
    } else {
      soundManager.defeat();
      new ResultPanel(this, {
        title: 'ПОРАЖЕНИЕ',
        subtitle: `+${coresEarned} ¤ ядер  (всего: ${metaManager.cores})`,
        buttonLabel: '[ ПОПРОБОВАТЬ СНОВА ]',
        titleColor: TEXT.danger,
        onButtonClick: () => {
          soundManager.buttonClick();
          maybeShowInterstitial(() => this.scene.start('GameScene', { bossIndex: 0 }));
        }
      });
      this.showAchievementBanner(newAchievements);
    }
  }

  // Победа → награда → выбор улучшения → следующий босс (П.39/П.40), всё на одном экране:
  // выбор карточки одновременно применяет улучшение и запускает следующий бой.
  createVictoryScreen(bossIndex, timeTaken, coinsEarned, coresEarned, ngPlusCycle, newAchievements, soundManager) {
    this.add.text(GAME_WIDTH / 2, 70, 'БОСС ПОБЕЖДЁН!', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '32px',
      color: TEXT.success,
      fontStyle: 'bold'
    }).setOrigin(0.5);

    this.add.text(GAME_WIDTH / 2, 112, `Время: ${timeTaken} сек.`, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '16px',
      color: TEXT.muted
    }).setOrigin(0.5);

    this.add.text(GAME_WIDTH / 2, 138, `+${coinsEarned} монет · +${coresEarned} ¤ядер`, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '15px',
      color: TEXT.accent,
      fontStyle: 'bold'
    }).setOrigin(0.5);

    // Явный список текущей прокачки — жалоба: "не понятно сохраняются ли улучшения".
    const summary = progressManager.getSummaryLines();
    if (summary.length > 0) {
      this.add.text(GAME_WIDTH / 2, 165, `Уже прокачано: ${summary.join(', ')}`, {
        fontFamily: FONT.body, resolution: 3,
        fontSize: '12px',
        color: TEXT.muted,
        wordWrap: { width: GAME_WIDTH - 80 },
        align: 'center'
      }).setOrigin(0.5);
    }

    this.chooseLabel = this.add.text(GAME_WIDTH / 2, 210, 'Выберите улучшение:', {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '17px',
      color: TEXT.muted
    }).setOrigin(0.5);

    this.rerollButton = this.add.text(GAME_WIDTH / 2, 240, `[ РЕРОЛЛ · ${REROLL_COST} монет ]`, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '13px',
      color: progressManager.coins >= REROLL_COST ? TEXT.accent : '#555a6b'
    }).setOrigin(0.5);
    if (progressManager.coins >= REROLL_COST) {
      this.rerollButton.setInteractive({ useHandCursor: true });
      this.rerollButton.on('pointerover', () => this.rerollButton.setScale(1.06));
      this.rerollButton.on('pointerout', () => this.rerollButton.setScale(1));
      this.rerollButton.on('pointerdown', () => {
        if (progressManager.coins < REROLL_COST) return;
        progressManager.coins -= REROLL_COST;
        soundManager.buttonClick();
        this.rerollButton.setColor(progressManager.coins >= REROLL_COST ? TEXT.accent : '#555a6b');
        if (progressManager.coins < REROLL_COST) this.rerollButton.disableInteractive();
        this.drawUpgradeCards(bossIndex, coinsEarned, coresEarned, ngPlusCycle, newAchievements, soundManager);
      });
    }

    this.drawUpgradeCards(bossIndex, coinsEarned, coresEarned, ngPlusCycle, newAchievements, soundManager);
    this.showAchievementBanner(newAchievements);
  }

  // Отдельный метод, а не инлайн в createVictoryScreen — реролл (ТЗ п.2,
  // "разнообразие забегов") вызывает его повторно, каждый раз удаляя старые
  // карточки (PixelCard.destroy) и рисуя новый случайный набор.
  drawUpgradeCards(bossIndex, coinsEarned, coresEarned, ngPlusCycle, newAchievements, soundManager) {
    this.cards.forEach((card) => card.destroy());
    this.cards = [];

    const choices = progressManager.rollUpgradeChoices(3);
    choices.forEach((upgrade, index) => {
      const y = CARDS_START_Y + index * (CARD_HEIGHT + CARD_GAP);
      const card = new PixelCard(this, GAME_WIDTH / 2, y, CARD_WIDTH, CARD_HEIGHT, {
        title: upgrade.label,
        description: upgrade.description,
        iconKey: upgrade.id,
        onSelect: () => {
          soundManager.buttonClick();
          progressManager.applyUpgrade(upgrade.id);
          this.scene.start('GameScene', { bossIndex: bossIndex + 1, ngPlusCycle });
        }
      });
      this.cards.push(card);
    });
  }

  // Все TOTAL_BOSSES боссов повержены — забег завершён. Вместо жёсткого конца
  // теперь два варианта (ТЗ п.3 "контент после первого прохождения"): выйти
  // в меню или продолжить New Game+ с усиленными боссами на той же прокачке.
  createFinalVictoryScreen(coinsEarned, coresEarned, ngPlusCycle, newAchievements, soundManager) {
    // Курсор y считается динамически от реальной высоты каждой строки
    // (Phaser Text.height уже учитывает перенос строк) — при увеличении
    // шрифта строки просто раздвигаются вниз, а не наезжают друг на друга
    // (жалоба: "мелкие надписи", разгон в 3-4 раза мог не влезть на фикс. y).
    let y = 90;
    const title = this.add.text(GAME_WIDTH / 2, y, 'ИГРА ПРОЙДЕНА!', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '32px',
      color: TEXT.success,
      fontStyle: 'bold'
    }).setOrigin(0.5, 0);
    y += title.height + 18;

    const subtitle = this.add.text(GAME_WIDTH / 2, y, ngPlusCycle > 0 ? `Цикл New Game+${ngPlusCycle} пройден` : 'Все боссы повержены', {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '26px',
      color: TEXT.muted
    }).setOrigin(0.5, 0);
    y += subtitle.height + 18;

    const coinsText = this.add.text(GAME_WIDTH / 2, y, `+${coinsEarned} монет · +${coresEarned} ¤ядер  (всего: ${metaManager.cores})`, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '24px',
      color: TEXT.accent,
      fontStyle: 'bold',
      wordWrap: { width: GAME_WIDTH - 60 },
      align: 'center'
    }).setOrigin(0.5, 0);
    y += coinsText.height + 22;

    const summary = progressManager.getSummaryLines();
    if (summary.length > 0) {
      const summaryText = this.add.text(GAME_WIDTH / 2, y, `Итоговая прокачка: ${summary.join(', ')}`, {
        fontFamily: FONT.body, resolution: 3,
        fontSize: '22px',
        color: TEXT.primary,
        wordWrap: { width: GAME_WIDTH - 60 },
        align: 'center',
        lineSpacing: 6
      }).setOrigin(0.5, 0);
      y += summaryText.height + 22;
    }

    // Кнопки закреплены не жёстко, а не выше текста над ними — если контент
    // вырос сильнее обычного (длинная сводка прокачки), кнопки сами уедут ниже.
    const buttonsTop = Math.max(GAME_HEIGHT / 2 + 20, y + 30);

    const continueButton = this.add.text(GAME_WIDTH / 2, buttonsTop, `[ NEW GAME+${ngPlusCycle + 1} ]`, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '24px',
      color: TEXT.accent,
      fontStyle: 'bold'
    }).setOrigin(0.5).setInteractive({ useHandCursor: true });
    continueButton.on('pointerover', () => continueButton.setScale(1.08));
    continueButton.on('pointerout', () => continueButton.setScale(1));
    continueButton.on('pointerdown', () => {
      soundManager.buttonClick();
      // Прокачка забега (progressManager) сохраняется в NG+ намеренно — это и
      // есть награда за продолжение, боссы компенсируют это своим усилением
      // (BossManager NG_PLUS_STEP), поэтому progressManager НЕ сбрасывается здесь.
      maybeShowInterstitial(() => this.scene.start('GameScene', { bossIndex: 0, ngPlusCycle: ngPlusCycle + 1 }));
    });

    const button = this.add.text(GAME_WIDTH / 2, buttonsTop + 60, '[ В МЕНЮ ]', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '18px',
      color: TEXT.primary,
      fontStyle: 'bold'
    }).setOrigin(0.5).setInteractive({ useHandCursor: true });

    button.on('pointerover', () => button.setScale(1.08));
    button.on('pointerout', () => button.setScale(1));
    button.on('pointerdown', () => {
      soundManager.buttonClick();
      progressManager.reset();
      maybeShowInterstitial(() => this.scene.start('MenuScene'));
    });

    this.showAchievementBanner(newAchievements);
  }

  // Достижения, полученные в этом забеге (ТЗ п.4) — короткий список внизу
  // экрана результата, не отдельный модальный тост (тот бы отвлекал от самого
  // важного — награды и выбора улучшения).
  showAchievementBanner(newAchievements) {
    if (!newAchievements || newAchievements.length === 0) return;
    const text = newAchievements.map((a) => `[ДОСТИЖЕНИЕ] ${a.label}`).join('   ');
    this.add.text(GAME_WIDTH / 2, GAME_HEIGHT - 40, text, {
      fontFamily: FONT.body, resolution: 3,
      fontSize: '13px',
      color: TEXT.accent,
      wordWrap: { width: GAME_WIDTH - 60 },
      align: 'center'
    }).setOrigin(0.5);
  }
}
