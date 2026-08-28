import Phaser from 'phaser';
import { pullCloudSave, getPlatformLanguage } from './managers/YandexSDK.js';

// Синглтоны менеджеров (MetaManager/StatsManager/Achievements/SettingsManager)
// читают localStorage синхронно в конструкторе, а конструируются они при
// первом импорте — то есть внутри import('./config/gameConfig.js') ниже (он
// тянет сцены, те тянут менеджеры). Поэтому облачное сохранение и язык
// платформы подтягиваются СНАЧАЛА (await), а импорт конфигурации — уже ПОСЛЕ:
// иначе поздний ответ от Яндекс Игр пришёл бы, когда менеджеры уже прочитали
// localStorage/применили дефолтный язык без него. timeout — чтобы медленная/
// недоступная сеть не задерживала старт игры.
function withTimeout(promise, ms) {
  return Promise.race([promise, new Promise((resolve) => setTimeout(resolve, ms))]);
}

// §1.6 требований платформы: браузерное контекстное меню (правый клик /
// долгий тап) не должно всплывать над игровой областью — иначе оно перекрывает
// канвас поверх геймплея. Вешается на #game-container, а не на весь document,
// чтобы не трогать элементы вне игры (их сейчас нет, но так безопаснее).
document.getElementById('game-container')?.addEventListener('contextmenu', (e) => e.preventDefault());

async function boot() {
  const [, platformLang] = await Promise.all([
    withTimeout(pullCloudSave(), 2500).catch(() => {}),
    withTimeout(getPlatformLanguage(), 2500).catch(() => null)
  ]);
  // Требование платформы п.2.14: автоопределение языка должно произойти ДО
  // первого рендера, а не в процессе игры — поэтому settingsManager
  // импортируется и применяет язык здесь, ДО import('./config/gameConfig.js')
  // (тот тянет сцены, которые уже читают settingsManager.language при create()).
  const { settingsManager } = await import('./managers/SettingsManager.js');
  if (platformLang) settingsManager.applyDetectedLanguage(platformLang);

  const { gameConfig } = await import('./config/gameConfig.js');
  // eslint-disable-next-line no-new
  new Phaser.Game(gameConfig);
}

boot();
