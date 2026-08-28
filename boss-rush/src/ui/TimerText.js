import { FONT } from '../config/constants.js';

export class TimerText {
  constructor(scene, x, y) {
    this.text = scene.add.text(x, y, '', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '26px',
      color: '#ffffff',
      fontStyle: 'bold'
    }).setOrigin(1, 0);
  }

  setValue(seconds) {
    const clamped = Math.max(0, Math.ceil(seconds));
    this.text.setText(`TIME: ${clamped}`);
    this.text.setColor(clamped <= 10 ? '#ff5555' : '#ffffff');
  }
}
