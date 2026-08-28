import { FONT } from '../config/constants.js';

export class HealthBar {
  constructor(scene, x, y, width, height, { color = 0x2ecc71, backgroundColor = 0x1c1c24 } = {}) {
    this.width = width;

    this.background = scene.add.rectangle(x, y, width, height, backgroundColor)
      .setOrigin(0, 0.5)
      .setStrokeStyle(2, 0x333344);
    this.fill = scene.add.rectangle(x, y, width, height, color).setOrigin(0, 0.5);
    this.valueText = scene.add.text(x + width / 2, y, '', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '15px',
      color: '#ffffff',
      fontStyle: 'bold'
    }).setOrigin(0.5);
  }

  setValue(current, max) {
    const ratio = Math.max(0, Math.min(1, current / max));
    this.fill.displayWidth = this.width * ratio;
    this.valueText.setText(`${Math.max(0, Math.ceil(current))} / ${max}`);
  }
}
