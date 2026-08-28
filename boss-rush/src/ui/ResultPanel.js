import { GAME_WIDTH, GAME_HEIGHT, COLORS, TEXT, FONT } from '../config/constants.js';
import { drawPixelPanel } from './pixelShapes.js';

export class ResultPanel {
  constructor(scene, { title, subtitle = '', buttonLabel, titleColor = TEXT.primary, onButtonClick }) {
    const panelWidth = 520;
    const panelHeight = 320;
    const panelX = (GAME_WIDTH - panelWidth) / 2;
    const panelY = GAME_HEIGHT / 2 - panelHeight / 2 - 30;

    drawPixelPanel(scene, panelX, panelY, panelWidth, panelHeight, {
      notch: 14,
      fill: COLORS.panelFill,
      border: COLORS.panelBorder
    });

    scene.add.text(GAME_WIDTH / 2, panelY + 90, title, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '32px',
      color: titleColor,
      fontStyle: 'bold'
    }).setOrigin(0.5);

    if (subtitle) {
      scene.add.text(GAME_WIDTH / 2, panelY + 150, subtitle, {
        fontFamily: FONT.body, resolution: 3,
        fontSize: '22px',
        color: TEXT.muted
      }).setOrigin(0.5);
    }

    const button = scene.add.text(GAME_WIDTH / 2, panelY + panelHeight - 60, buttonLabel, {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '18px',
      color: TEXT.accent,
      fontStyle: 'bold'
    }).setOrigin(0.5).setInteractive({ useHandCursor: true });

    button.on('pointerover', () => button.setScale(1.08));
    button.on('pointerout', () => button.setScale(1));
    button.on('pointerdown', onButtonClick);
  }
}
