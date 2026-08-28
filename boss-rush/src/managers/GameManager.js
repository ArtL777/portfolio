export class GameManager {
  constructor() {
    this.currentBossIndex = 0;
    this.currentBoss = null;
    this.isGameOver = false;
    this.timeLeft = 60;
    this.result = null;
    // New Game+ (roguelite-цикл): 0 — первое прохождение, 1+ — повторные
    // круги с усиленными боссами (см. BossManager.NG_PLUS_STEP).
    this.ngPlusCycle = 0;
  }
}
