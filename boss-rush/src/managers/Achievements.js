// Достижения (ТЗ "полноценная доработка", п.4) — персистентный список через
// localStorage, отдельный от MetaManager: другая природа данных (булевы флаги
// "случилось раз в жизни", а не тратимая валюта/тиры) и проверяется в других
// местах кода, отдельный модуль читается понятнее, чем всё в одном файле.
import { pushCloudSave } from './YandexSDK.js';

const STORAGE_KEY = 'bossRush.achievements.v1';

export const ACHIEVEMENTS = [
  {
    id: 'first_blood',
    label: 'ПЕРВАЯ КРОВЬ',
    description: 'Победи любого босса'
  },
  {
    id: 'no_damage',
    label: 'БЕЗ ЕДИНОЙ ЦАРАПИНЫ',
    description: 'Победи босса, не получив урона'
  },
  {
    id: 'speedrun',
    label: 'МОЛНИЕНОСНО',
    description: 'Победи босса быстрее чем за 15 секунд'
  },
  {
    id: 'full_clear',
    label: 'ВСЕ БОССЫ ПАЛИ',
    description: 'Пройди все 5 боссов за один забег'
  },
  {
    id: 'new_game_plus',
    label: 'ПО НОВОЙ',
    description: 'Начни цикл New Game+'
  },
  {
    id: 'veteran',
    label: 'ВЕТЕРАН',
    description: 'Сыграй 10 забегов'
  },
  {
    id: 'specialist',
    label: 'СПЕЦИАЛИЗАЦИЯ',
    description: 'Прокачай одно улучшение до 3+ уровня за забег'
  },
  {
    id: 'collector',
    label: 'КОЛЛЕКЦИОНЕР',
    description: 'Разблокируй все реликвии'
  }
];

class AchievementTracker {
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
    this.unlocked = new Set(Array.isArray(parsed) ? parsed : []);
  }

  save() {
    const payload = [...this.unlocked];
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch {
      // localStorage недоступен — достижения просто не сохранятся.
    }
    pushCloudSave(STORAGE_KEY, payload);
  }

  isUnlocked(id) {
    return this.unlocked.has(id);
  }

  // Возвращает true, только если достижение разблокировано ИМЕННО сейчас
  // (не было раньше) — вызывающий код использует это, чтобы показать тост
  // только один раз, а не при каждой повторной проверке условия.
  unlock(id) {
    if (this.unlocked.has(id)) return false;
    this.unlocked.add(id);
    this.save();
    return true;
  }

  // Пакетная проверка условий, зависящих от исхода забега — вызывается один
  // раз из GameScene.endBattle. Возвращает массив ОПРЕДЕЛЕНИЙ новых достижений
  // (не просто id) — ResultScene показывает их название/описание сразу.
  checkRunEnd({ result, bossIndex, timeTaken, noDamage, totalBosses, ngPlusCycle, runsPlayed }) {
    const newly = [];
    const tryUnlock = (id) => {
      if (this.unlock(id)) newly.push(ACHIEVEMENTS.find((a) => a.id === id));
    };

    if (result === 'victory') {
      tryUnlock('first_blood');
      if (noDamage) tryUnlock('no_damage');
      if (timeTaken <= 15) tryUnlock('speedrun');
      if (bossIndex + 1 >= totalBosses) tryUnlock('full_clear');
      if (ngPlusCycle > 0) tryUnlock('new_game_plus');
    }
    if (runsPlayed >= 10) tryUnlock('veteran');

    return newly;
  }
}

export const achievementTracker = new AchievementTracker();
