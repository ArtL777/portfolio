// Постоянная мета-прогрессия (roguelite-цикл, ТЗ "полноценная доработка"):
// в отличие от ProgressManager (прокачка внутри забега, сгорает при смерти)
// и StatsManager (статистика для отображения), это единственное место, где
// хранится то, что действительно "остаётся" после смерти — валюта, постоянные
// улучшения и реликвии. Персистентно через localStorage, отдельный ключ.
import { pushCloudSave } from './YandexSDK.js';

const STORAGE_KEY = 'bossRush.meta.v1';

// Тиры постоянных статов — цена растёт линейно за тир, максимум 5 тиров на
// стат (не бесконечно, иначе позже игра станет тривиальной и потеряет смысл
// сессионной прокачки поверх этой).
const MAX_TIER = 5;
const TIER_BASE_COST = 25;
const TIER_COST_STEP = 20;
const DASH_UNLOCK_COST = 90;

export function permanentUpgradeCost(tier) {
  // tier — текущий уровень (0..4), цена следующего тира.
  return TIER_BASE_COST + tier * TIER_COST_STEP;
}

// Реликвии — пассивные эффекты, разблокируются один раз за ядра, экипируется
// только одна за раз (выбор делается в MetaScene) — даёт вариативность забега
// без отдельного экрана выбора перед боем (ТЗ п.2 "разные варианты развития").
export const RELICS = [
  {
    id: 'secondWind',
    label: 'ВТОРОЕ ДЫХАНИЕ',
    description: 'Смертельный удар раз за забег оставляет 1 HP вместо гибели',
    cost: 120
  },
  {
    id: 'lifesteal',
    label: 'ВАМПИРИЗМ',
    description: 'Каждый удар лечит на 8% нанесённого урона',
    cost: 100
  },
  {
    id: 'berserk',
    label: 'ЯРОСТЬ',
    description: '+25% урона, пока HP ниже 30%',
    cost: 100
  }
];

class MetaManager {
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
    this.cores = parsed?.cores ?? 0;
    this.permanent = {
      damage: parsed?.permanent?.damage ?? 0,
      maxHp: parsed?.permanent?.maxHp ?? 0,
      critChance: parsed?.permanent?.critChance ?? 0,
      moveSpeed: parsed?.permanent?.moveSpeed ?? 0
    };
    this.dashUnlocked = parsed?.dashUnlocked ?? false;
    this.unlockedRelics = parsed?.unlockedRelics ?? [];
    this.equippedRelic = parsed?.equippedRelic ?? null;
    this.tutorialSeen = parsed?.tutorialSeen ?? false;
  }

  save() {
    const payload = {
      cores: this.cores,
      permanent: this.permanent,
      dashUnlocked: this.dashUnlocked,
      unlockedRelics: this.unlockedRelics,
      equippedRelic: this.equippedRelic,
      tutorialSeen: this.tutorialSeen
    };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch {
      // localStorage недоступен — прогресс просто не переживёт перезагрузку.
    }
    // Облачное сохранение (Yandex Games) — best-effort, см. YandexSDK.js.
    pushCloudSave(STORAGE_KEY, payload);
  }

  addCores(amount) {
    this.cores += amount;
    this.save();
  }

  canBuyStat(stat) {
    return this.permanent[stat] < MAX_TIER && this.cores >= permanentUpgradeCost(this.permanent[stat]);
  }

  buyStat(stat) {
    if (!this.canBuyStat(stat)) return false;
    this.cores -= permanentUpgradeCost(this.permanent[stat]);
    this.permanent[stat] += 1;
    this.save();
    return true;
  }

  canBuyDash() {
    return !this.dashUnlocked && this.cores >= DASH_UNLOCK_COST;
  }

  buyDash() {
    if (!this.canBuyDash()) return false;
    this.cores -= DASH_UNLOCK_COST;
    this.dashUnlocked = true;
    this.save();
    return true;
  }

  isRelicUnlocked(id) {
    return this.unlockedRelics.includes(id);
  }

  canBuyRelic(id) {
    const relic = RELICS.find((r) => r.id === id);
    return !!relic && !this.isRelicUnlocked(id) && this.cores >= relic.cost;
  }

  buyRelic(id) {
    if (!this.canBuyRelic(id)) return false;
    const relic = RELICS.find((r) => r.id === id);
    this.cores -= relic.cost;
    this.unlockedRelics.push(id);
    if (!this.equippedRelic) this.equippedRelic = id;
    this.save();
    return true;
  }

  equipRelic(id) {
    if (id !== null && !this.isRelicUnlocked(id)) return;
    this.equippedRelic = id;
    this.save();
  }

  // Флаги для Player/CombatManager — только сама экипированная реликвия,
  // остальные два всегда false (одновременно активна только одна, см. equipRelic).
  getEquippedRelicFlags() {
    return {
      secondWind: this.equippedRelic === 'secondWind',
      lifesteal: this.equippedRelic === 'lifesteal',
      berserk: this.equippedRelic === 'berserk'
    };
  }

  markTutorialSeen() {
    if (this.tutorialSeen) return;
    this.tutorialSeen = true;
    this.save();
  }
}

export const metaManager = new MetaManager();
export const META_MAX_TIER = MAX_TIER;
export const META_DASH_COST = DASH_UNLOCK_COST;
