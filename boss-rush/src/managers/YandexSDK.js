// Интеграция Yandex Games SDK (ТЗ: "подготовь к релизу"). Всё в этом файле —
// best-effort: игра ДОЛЖНА нормально работать и локально (npm run dev), и на
// любом хостинге вне Яндекс Игр, где window.YaGames вообще не существует —
// поэтому каждый метод по умолчанию тихо ничего не делает вместо ошибки.
// Скрипт SDK подключается в index.html: <script src="https://yandex.ru/games/sdk/v2">.
//
// Технические имена лидерборда и ключи облачных сохранений нужно завести в
// личном кабинете разработчика Яндекс Игр ДО публикации — см. LEADERBOARD_NAME
// ниже. Без созданного лидерборда submitScore/fetchLeaderboard просто
// молча ничего не делают (см. try/catch), игра от этого не ломается.
import { suspendAudio, resumeAudio } from './SoundManager.js';

export const LEADERBOARD_NAME = 'bossRushBestTime';
const PLAYER_DATA_KEYS = ['bossRush.meta.v1', 'bossRush.stats.v1', 'bossRush.achievements.v1', 'bossRush.settings.v1'];

let readyPromise = null;
let ysdk = null;

// init() лениво запускает YaGames.init() один раз и переиспользует тот же
// промис при повторных вызовах — вызывать можно из любого места сколько
// угодно раз, реальная инициализация SDK произойдёт один раз.
export function initYandexSDK() {
  if (readyPromise) return readyPromise;

  if (typeof window === 'undefined' || !window.YaGames) {
    // Скрипт SDK не подгрузился (не на Яндекс Игры, оффлайн, блокировщик) —
    // это НЕ ошибка приложения, просто все фичи ниже становятся no-op.
    readyPromise = Promise.resolve(null);
    return readyPromise;
  }

  // Таймаут ОБЯЗАТЕЛЕН: readyPromise — общий на всё приложение синглтон,
  // все вызовы (лидерборд, реклама, облако) ждут именно его. Если сам
  // YaGames.init() зависнет без ответа (подтверждено локально: вне их
  // iframe — нет "родителя" для postMessage — SDK иногда не резолвит И не
  // реджектит init() вовсе), без гонки с таймаутом ЛЮБОЙ вызов SDK в игре
  // завис бы навсегда, а не только первый. На реальной платформе Яндекс
  // Игр родитель есть всегда, и init() резолвится быстро — таймаут там
  // никогда не сработает.
  const initTimeout = new Promise((resolve) => setTimeout(() => resolve(null), 5000));
  readyPromise = Promise.race([window.YaGames.init(), initTimeout])
    .then((sdk) => {
      ysdk = sdk;
      return sdk;
    })
    .catch((err) => {
      console.warn('[YandexSDK] init failed, продолжаем без SDK:', err);
      return null;
    });
  return readyPromise;
}

// Требование платформы п.2.14: автоопределение языка ДОЛЖНО происходить через
// SDK во время запуска (проверяется debug-панелью — индикатор "文" должен стать
// зелёным сразу при старте, а не через какое-то время после). environment —
// синхронное поле объекта sdk (не промис), доступно сразу после инициализации,
// поэтому отдельного таймаута тут не нужно — initYandexSDK() уже защищён своим.
// ISO 639-1 код ('ru', 'en', ...) — см. https://yandex.ru/dev/games/doc/ru/sdk/sdk-environment.
export async function getPlatformLanguage() {
  const sdk = await initYandexSDK();
  return sdk?.environment?.i18n?.lang ?? null;
}

// Обязательный вызов для прохождения модерации Яндекс Игр — сигнализирует
// платформе, что игра прогрузилась и в неё можно играть (иначе висит их
// собственный экран загрузки поверх игры). Вызывается один раз из MenuScene
// при самом первом старте (см. MenuScene.create()).
let loadingReadyCalled = false;
export async function notifyGameReady() {
  if (loadingReadyCalled) return;
  loadingReadyCalled = true;
  const sdk = await initYandexSDK();
  try {
    sdk?.features?.LoadingAPI?.ready?.();
  } catch (err) {
    console.warn('[YandexSDK] LoadingAPI.ready failed:', err);
  }
}

// GameplayAPI start/stop — сообщает платформе, когда игрок реально играет
// (не в меню/магазине), используется в их аналитике вовлечённости.
export async function notifyGameplayStart() {
  const sdk = await initYandexSDK();
  try {
    sdk?.features?.GameplayAPI?.start?.();
  } catch (err) {
    console.warn('[YandexSDK] GameplayAPI.start failed:', err);
  }
}

export async function notifyGameplayStop() {
  const sdk = await initYandexSDK();
  try {
    sdk?.features?.GameplayAPI?.stop?.();
  } catch (err) {
    console.warn('[YandexSDK] GameplayAPI.stop failed:', err);
  }
}

// Полноэкранная межстраничная реклама — вызывающий код сам решает, когда
// уместно её показать (см. ResultScene: не чаще раза в несколько забегов).
// onDone вызывается ПОСЛЕ закрытия/ошибки/офлайна рекламы — переход между
// сценами должен идти именно оттуда, а не сразу после вызова этой функции.
export async function showInterstitialAd(onDone) {
  const sdk = await initYandexSDK();
  if (!sdk?.adv?.showFullscreenAdv) {
    onDone?.();
    return;
  }
  // §4.7 требований платформы: звук игры должен паузиться на время показа
  // рекламы. suspendAudio/resumeAudio — общий AudioContext (см. SoundManager.js),
  // не завязан на rAF игрового цикла, поэтому без явной паузы мог бы звучать
  // поверх/вместе с самим рекламным роликом.
  suspendAudio();
  // onDone гарантированно вызывается РОВНО один раз — либо из колбэка SDK,
  // либо (если за FALLBACK_MS ни onClose, ни onError вообще не пришли —
  // подтверждено локально: вне их iframe showFullscreenAdv иногда не зовёт
  // НИ ОДИН колбэк) из таймаута. Без этого игрок застревал бы на экране
  // результата навсегда, если реклама технически "показалась", но SDK не
  // смог сообщить об этом обратно (например, поп-ап реклама заблокирована
  // блокировщиком без явной ошибки).
  let done = false;
  const finish = () => {
    if (done) return;
    done = true;
    resumeAudio();
    onDone?.();
  };
  const fallbackTimer = setTimeout(finish, 8000);
  try {
    sdk.adv.showFullscreenAdv({
      callbacks: {
        onClose: () => { clearTimeout(fallbackTimer); finish(); },
        onError: () => { clearTimeout(fallbackTimer); finish(); }
      }
    });
  } catch (err) {
    clearTimeout(fallbackTimer);
    console.warn('[YandexSDK] showFullscreenAdv failed:', err);
    finish();
  }
}

// Лидерборд — technical name должен существовать в кабинете разработчика
// (тип "числовой", сортировка по возрастанию — меньше секунд = лучше).
// ysdk.leaderboards.setScore/getEntries — актуальный API (замена устаревшего
// ysdk.getLeaderboards().then(lb => lb.setLeaderboardScore(...)), см.
// https://yandex.ru/dev/games/doc/dg/sdk/sdk-leaderboard).
export async function submitLeaderboardScore(score) {
  const sdk = await initYandexSDK();
  if (!sdk?.leaderboards) return;
  try {
    const player = await sdk.getPlayer().catch(() => null);
    if (!player) return; // неавторизованный игрок — платформа не даёт отправлять счёт
    await sdk.leaderboards.setScore(LEADERBOARD_NAME, Math.round(score));
  } catch (err) {
    console.warn('[YandexSDK] submitLeaderboardScore failed (лидерборд не настроен в кабинете?):', err);
  }
}

// Возвращает массив [{rank, name, score}] реальных игроков или null, если
// лидерборд недоступен (нет SDK/не настроен/сеть/подвисший ответ вне
// песочницы Яндекс Игр) — вызывающий код (LeaderboardModal) в этом случае
// остаётся на локальной истории забегов. Таймаут — без него UI мог бы
// зависнуть на "Загрузка..." на много секунд в деградированном окружении
// (наблюдалось локально: SDK пытается достучаться до appId/родительского
// окна, которых вне их iframe просто нет, и не сразу отваливается).
export async function fetchLeaderboardEntries(limit = 10) {
  const sdk = await initYandexSDK();
  if (!sdk?.leaderboards) return null;
  const withTimeout = (promise, ms) => Promise.race([
    promise,
    new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), ms))
  ]);
  try {
    const data = await withTimeout(
      sdk.leaderboards.getEntries(LEADERBOARD_NAME, { quantityTop: limit, includeUser: true }),
      4000
    );
    return (data.entries ?? []).map((entry) => ({
      rank: entry.rank,
      name: entry.player?.publicName || entry.player?.uniqueID || '???',
      score: entry.score
    }));
  } catch (err) {
    console.warn('[YandexSDK] fetchLeaderboardEntries failed (лидерборд не настроен в кабинете?):', err);
    return null;
  }
}

// --- Облачные сохранения (player.setData/getData) ---
// Хранит те же три localStorage-ключа целиком одним объектом в данных
// игрока на сервере Яндекса — переживает переустановку/смену устройства,
// пока игрок авторизован. localStorage остаётся источником истины для
// синхронного чтения при старте (managers читают его в конструкторе), это
// облако лишь синхронизируется поверх — см. pullCloudSave()/pushCloudSave().
async function getPlayerSafe() {
  const sdk = await initYandexSDK();
  if (!sdk?.getPlayer) return null;
  try {
    // Та же защита, что и в initYandexSDK() — getPlayer() тоже способен
    // зависнуть без ответа вне реального Яндекс-окружения.
    return await Promise.race([
      sdk.getPlayer(),
      new Promise((resolve) => setTimeout(() => resolve(null), 5000))
    ]);
  } catch {
    return null; // неавторизован или SDK не поддерживает — тихо пропускаем
  }
}

// Вызывается один раз при старте игры (main.js) ДО импорта сцен/менеджеров —
// иначе было бы поздно: managers читают localStorage синхронно в конструкторе,
// а конструируются они при самом первом импорте. Поэтому pull делает две вещи:
// 1) если в облаке есть данные — мержит их в localStorage побайтово по
//    большему числовому прогрессу (см. mergeSaveValue), чтобы никогда не
//    затереть более свежий локальный прогресс явно устаревшим облачным;
// 2) возвращает true, если что-то реально обновилось — тогда main.js
//    перезагружает уже созданные singleton-менеджеры через их .load().
export async function pullCloudSave() {
  const player = await getPlayerSafe();
  if (!player) return false;

  let changed = false;
  for (const key of PLAYER_DATA_KEYS) {
    try {
      const remote = await player.getData([key]);
      const remoteValue = remote?.[key];
      if (remoteValue === undefined || remoteValue === null) continue;

      const localRaw = localStorage.getItem(key);
      const localValue = localRaw ? JSON.parse(localRaw) : null;
      const merged = mergeSaveValue(localValue, remoteValue);
      if (JSON.stringify(merged) !== localRaw) {
        localStorage.setItem(key, JSON.stringify(merged));
        changed = true;
      }
    } catch (err) {
      console.warn(`[YandexSDK] pullCloudSave(${key}) failed:`, err);
    }
  }
  return changed;
}

// Берёт максимум по каждому числовому полю верхнего уровня (cores, тиры
// улучшений и т.д.) — простое и безопасное правило "прогресс никогда не
// уменьшается при синхронизации", без полноценного слияния версий.
function mergeSaveValue(local, remote) {
  if (local === null || typeof local !== 'object') return remote;
  if (remote === null || typeof remote !== 'object') return local;
  if (Array.isArray(local) || Array.isArray(remote)) {
    // Массивы (achievements: ['first_blood', ...]) — объединяем без дублей.
    return Array.from(new Set([...(Array.isArray(local) ? local : []), ...(Array.isArray(remote) ? remote : [])]));
  }
  const result = { ...local };
  for (const k of Object.keys(remote)) {
    if (typeof remote[k] === 'number' && typeof local[k] === 'number') {
      result[k] = Math.max(local[k], remote[k]);
    } else if (typeof remote[k] === 'object' && remote[k] !== null) {
      result[k] = mergeSaveValue(local[k], remote[k]);
    } else if (local[k] === undefined) {
      result[k] = remote[k];
    }
  }
  return result;
}

// Каждый manager вызывает это в конце своего save() — фоново, без ожидания
// (компонент не должен зависеть от сети). Шлём только один изменившийся
// ключ, а не весь набор — дешевле и меньше шанс перезаписать несвязанные
// данные гонкой между вкладками.
export function pushCloudSave(key, value) {
  getPlayerSafe().then((player) => {
    if (!player) return;
    player.setData({ [key]: value }, true).catch((err) => {
      console.warn(`[YandexSDK] pushCloudSave(${key}) failed:`, err);
    });
  });
}
