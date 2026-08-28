import { pushCloudSave } from './YandexSDK.js';

// Настройки игрока (ТЗ "Окно 3: SETTINGS") — отдельный персистентный слой,
// как MetaManager/StatsManager, но про предпочтения показа/звука, а не прогресс.
const STORAGE_KEY = 'bossRush.settings.v1';

// Требования платформы п.2.14: языки, реально переведённые целиком (см. поле
// "Игра переведена на" в кабинете разработчика — там указан только русский).
// EN-словарь в SettingsModal.js — это ЧАСТИЧНЫЙ перевод только текста самого
// окна настроек, не всей игры, поэтому НЕ считается полноценным поддерживаемым
// языком для автоопределения: если бы applyDetectedLanguage подставляла 'en'
// при языке интерфейса Яндекса = английский, игра показывала бы смесь
// непереведённого русского текста и переведённого окна настроек — это хуже,
// чем последовательный русский (и по документации тоже считается провалом
// модерации: "если хотя бы один язык не переключился полностью — отклонена").
const SUPPORTED_LANGUAGES = ['ru'];
const DEFAULT_LANGUAGE = 'ru';

class SettingsManager {
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
    this.musicVolume = parsed?.musicVolume ?? 0.6;
    this.sfxVolume = parsed?.sfxVolume ?? 0.8;
    this.masterMute = parsed?.masterMute ?? false;
    this.screenShake = parsed?.screenShake ?? true;
    this.vibration = parsed?.vibration ?? true;
    // Полный перевод игры на EN не входит в этот этап (сотни строк по всей
    // игре) — переключатель персистентно хранит выбор и уже переводит текст
    // самих новых модальных окон (см. src/ui/*Modal.js), остальной интерфейс
    // остаётся на русском до отдельного этапа локализации.
    this.language = parsed?.language ?? DEFAULT_LANGUAGE;
    // Если игрок САМ переключил язык через UI (setLanguage) — его выбор не
    // должен затираться автоопределением при следующем запуске (см.
    // applyDetectedLanguage ниже и требование п.2.14: "acceptable if language
    // remains cached after refresh if developer implemented caching").
    this.languageManuallySet = parsed?.languageManuallySet ?? false;
  }

  save() {
    const payload = {
      musicVolume: this.musicVolume,
      sfxVolume: this.sfxVolume,
      masterMute: this.masterMute,
      screenShake: this.screenShake,
      vibration: this.vibration,
      language: this.language,
      languageManuallySet: this.languageManuallySet
    };
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch {
      // localStorage недоступен — настройки просто не переживут перезагрузку.
    }
    // Облачное сохранение (Yandex Games) — best-effort, см. YandexSDK.js.
    pushCloudSave(STORAGE_KEY, payload);
  }

  setMusicVolume(value) {
    this.musicVolume = Math.max(0, Math.min(1, value));
    this.save();
  }

  setSfxVolume(value) {
    this.sfxVolume = Math.max(0, Math.min(1, value));
    this.save();
  }

  toggleMute() {
    this.masterMute = !this.masterMute;
    this.save();
    return this.masterMute;
  }

  toggleScreenShake() {
    this.screenShake = !this.screenShake;
    this.save();
    return this.screenShake;
  }

  toggleVibration() {
    this.vibration = !this.vibration;
    this.save();
    return this.vibration;
  }

  setLanguage(lang) {
    this.language = lang;
    this.languageManuallySet = true;
    this.save();
  }

  // Вызывается один раз при старте игры (main.js, ДО первого рендера сцены —
  // см. п.2.14) с языком интерфейса Яндекс Игр (ysdk.environment.i18n.lang).
  // Ручной выбор игрока в настройках имеет приоритет и не перезаписывается.
  // Неподдерживаемый/отсутствующий язык — откат на DEFAULT_LANGUAGE (полностью
  // переведённый), а не молчаливое сохранение чего попало.
  applyDetectedLanguage(lang) {
    if (this.languageManuallySet) return;
    const resolved = SUPPORTED_LANGUAGES.includes(lang) ? lang : DEFAULT_LANGUAGE;
    if (resolved === this.language) return;
    this.language = resolved;
    this.save();
  }

  // Итоговая громкость SFX с учётом мьюта (SoundManager умножает на это).
  effectiveSfxVolume() {
    return this.masterMute ? 0 : this.sfxVolume;
  }
}

export const settingsManager = new SettingsManager();
