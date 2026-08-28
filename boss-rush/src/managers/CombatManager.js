export class CombatManager {
  // Возвращает true, если сработала реликвия "Второе дыхание" (смертельный
  // удар оставил 1 HP вместо гибели) — GameScene показывает отдельный фидбек
  // и не завершает бой в этом случае.
  damagePlayer(player, amount) {
    const wouldDie = player.hp - amount <= 0;
    if (wouldDie && player.relics.secondWind && !player.secondWindUsed) {
      player.secondWindUsed = true;
      player.hp = 1;
      player.flashHit();
      return true;
    }
    player.hp = Math.max(0, player.hp - amount);
    player.flashHit();
    return false;
  }

  damageBoss(boss, amount) {
    boss.takeDamage(amount);
    boss.flashHit();
  }
}
