import Phaser from 'phaser';
import { FONT } from '../config/constants.js';

// Переиспользуемый всплывающий текст (ТЗ "сделай бои сочнее" — числа урона,
// комбо, крит) — раньше похожая анимация (КРИТ!) была захардкожена прямо в
// GameScene.showCritFeedback; теперь один общий хелпер для урона/комбо/крита,
// чтобы не плодить одинаковые tween-блоки по всей сцене.
export function spawnFloatingText(scene, x, y, text, {
  color = '#ffffff',
  fontSize = '20px',
  rise = 50,
  duration = 550,
  scaleFrom = 0.7,
  jitterX = 18
} = {}) {
  const offsetX = Phaser.Math.Between(-jitterX, jitterX);
  const obj = scene.add.text(x + offsetX, y - 20, text, {
    fontFamily: FONT.display,
    resolution: 3,
    fontSize,
    color,
    fontStyle: 'bold'
  }).setOrigin(0.5).setScale(scaleFrom).setDepth(1000);

  scene.tweens.add({
    targets: obj,
    y: obj.y - rise,
    scale: 1,
    alpha: 0,
    duration,
    ease: 'Cubic.easeOut',
    onComplete: () => obj.destroy()
  });
  return obj;
}
