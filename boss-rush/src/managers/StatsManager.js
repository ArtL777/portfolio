// Статистика игрока между сессиями (ТЗ п.3 "добавь блок со статистикой
// игрока") — в отличие от ProgressManager (прокачка внутри одного забега,
// сбрасывается при поражении/новом заходе), это лёгкий персистентный слой
// поверх localStorage: переживает перезагрузку страницы и обновляется по
// каждому завершённому забегу (см. GameScene.endBattle).
import { pushCloudSave } from './YandexSDK.js';

const STORAGE_KEY = 'bossRush.stats.v1';
// Сколько последних полных прохождений хранить для таблицы лидеров (ТЗ
// "Окно 2: LEADERBOARD") — этого достаточно и для ALL TIME топ-10, и для
// фильтра WEEKLY, без неограниченного роста localStorage.
const MAX_RUN_HISTORY = 30;

class StatsManager {
  constructor() {
    this.load();
  }

  load() {
    let parsed = null;
    try {
      parsed = JSON.parse(localStorage.getItem(STORAGE_KEY));
    } catch {
      parsed = null;
    }
    this.runsPlayed = parsed?.runsPlayed ?? 0;
    this.bestBossesBeaten = parsed?.bestBossesBeaten ?? 0;
    this.fullClears = parsed?.fullClears ?? 0;
    this.totalCoins = parsed?.totalCoins ?? 0;
    this.bestNgPlusCycle = parsed?.bestNgPlusCycle ?? 0;
    // Лучшее (минимальное) время убийства каждого босса — { [bossIndex]: секунды }
    // (ТЗ "Окно 1: BOSS GALLERY" — "лучший рекорд времени победы над ним").
    this.bestBossTimes = parsed?.bestBossTimes ?? {};
    // История полных прохождений — { ts, totalTime, ngPlusCycle } (ТЗ
    // "Окно 2: LEADERBOARD"). Никакой реальный Yandex Games SDK лидерборд в
    // проекте пока не подключён (нет multiplayer-бэкенда) — это личный локальный
    // рекорд-лист игрока на этом устройстве, а не список других игроков; при
    // подключении настоящего Yandex Leaderboards API эта история станет
    // источником данных для отправки (см. LeaderboardModal.js).
    this.runHistory = Array.isArray(parsed?.runHistory) ? parsed.runHistory : [];
  }

  save() {
    const payload = {
      runsPlayed: this.runsPlayed,
      bestBossesBeaten: this.bestBossesBeaten,
      fullClears: this.fullClears,
      totalCoins: this.totalCoins,
      bestNgPlusCycle: this.bestNgPlusCycle,
      bestBossTimes: this.bestBossTimes,
      runHistory: this.runHistory
    };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch {
      // localStorage недоступен (приватный режим и т.п.) — статистика просто не сохранится.
    }
    pushCloudSave(STORAGE_KEY, payload);
  }

  // bossIndex — индекс босса, с которым завершился бой (0-based); result — 'victory'/'defeat'.
  recordRun({ result, bossIndex, coinsEarned, totalBosses, ngPlusCycle = 0, timeTaken = 0, totalTimeElapsed = 0 }) {
    const bossesBeaten = result === 'victory' ? bossIndex + 1 : bossIndex;
    this.runsPlayed += 1;
    this.totalCoins += coinsEarned;
    this.bestBossesBeaten = Math.max(this.bestBossesBeaten, bossesBeaten);

    const fullClear = result === 'victory' && bossIndex + 1 >= totalBosses;
    if (result === 'victory') {
      const prevBest = this.bestBossTimes[bossIndex];
      if (prevBest === undefined || timeTaken < prevBest) this.bestBossTimes[bossIndex] = timeTaken;
    }
    if (fullClear) {
      this.fullClears += 1;
      this.bestNgPlusCycle = Math.max(this.bestNgPlusCycle, ngPlusCycle + 1);
      this.runHistory.unshift({ ts: Date.now(), totalTime: totalTimeElapsed, ngPlusCycle });
      if (this.runHistory.length > MAX_RUN_HISTORY) this.runHistory.length = MAX_RUN_HISTORY;
    }
    this.save();
  }
}

export const statsManager = new StatsManager();
