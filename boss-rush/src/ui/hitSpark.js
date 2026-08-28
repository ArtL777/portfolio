import Phaser from 'phaser';

// Лёгкая вспышка попадания (ТЗ "сделай бои сочнее" — feedback попадания) —
// сознательно НЕ переиспользует Boss.groundImpactEffect (та версия с тряской
// камеры и 6 осколками задумана как редкое "земля вздрогнула" для спец-атак;
// на каждый обычный удар это было бы слишком много, брифинг явно просит не
// добавлять бессмысленные эффекты). Здесь — 4 маленьких искры без тряски.
export function hitSpark(scene, x, y, color = 0xffffff) {
  const count = 4;
  for (let i = 0; i < count; i++) {
    const angle = (Math.PI * 2 * i) / count + Phaser.Math.FloatBetween(-0.3, 0.3);
    const dist = Phaser.Math.FloatBetween(14, 28);
    const chip = scene.add.rectangle(x, y, 4, 4, color).setDepth(999);
    scene.tweens.add({
      targets: chip,
      x: x + Math.cos(angle) * dist,
      y: y + Math.sin(angle) * dist,
      alpha: 0,
      duration: 220,
      ease: 'Cubic.easeOut',
      onComplete: () => chip.destroy()
    });
  }
}
