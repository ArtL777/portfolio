// Звуки синтезируются через Web Audio API (без файлов-ассетов, П.43 пока
// нечего класть в public/assets/sounds) — набор событий строго по П.44:
// hit, player_damage, boss_attack, boss_defeated, button_click, victory, defeat.
// AudioContext один на вкладку: браузер блокирует звук до первого жеста
// пользователя, поэтому resume() вызывается перед каждым проигрыванием.
import { settingsManager } from './SettingsManager.js';

let sharedContext = null;
let visibilityHandlerAttached = false;

// AudioContext — отдельная звуковая шина, НЕ завязанная на requestAnimationFrame
// (в отличие от игрового цикла Phaser, который сам останавливается в фоновой
// вкладке) — уже запущенный звук иначе продолжал бы играть после сворачивания/
// смены вкладки (§1.3 требований платформы). Слушатель вешается один раз на
// документ, а не на конкретный контекст — контекст пересоздаётся редко, но
// документ всегда один и тот же.
function attachVisibilityHandler() {
  if (visibilityHandlerAttached || typeof document === 'undefined') return;
  visibilityHandlerAttached = true;
  document.addEventListener('visibilitychange', () => {
    if (!sharedContext) return;
    if (document.hidden) sharedContext.suspend().catch(() => {});
    else sharedContext.resume().catch(() => {});
  });
}

// Явная пауза/возобновление извне (см. YandexSDK.js showInterstitialAd —
// §4.7 требований: "звук игры паузится во время показа рекламного ролика").
export function suspendAudio() {
  sharedContext?.suspend().catch(() => {});
}

export function resumeAudio() {
  if (!document.hidden) sharedContext?.resume().catch(() => {});
}

function getContext() {
  if (!sharedContext) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    sharedContext = new AudioContextClass();
    attachVisibilityHandler();
  }
  return sharedContext;
}

export class SoundManager {
  constructor() {
    this.context = getContext();
  }

  resume() {
    if (this.context.state === 'suspended') {
      this.context.resume();
    }
  }

  playTone({ frequency = 440, duration = 0.15, type = 'sine', volume = 0.2, slideTo = null, delay = 0 }) {
    // Настройки (ТЗ "Окно 3: AUDIO") — Master Mute и Sound FX слайдер
    // масштабируют громкость каждого события здесь же, в одной точке.
    const effectiveVolume = volume * settingsManager.effectiveSfxVolume();
    if (effectiveVolume <= 0) return;
    this.resume();
    const ctx = this.context;
    const startAt = ctx.currentTime + delay;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(frequency, startAt);
    if (slideTo !== null) {
      osc.frequency.exponentialRampToValueAtTime(Math.max(slideTo, 1), startAt + duration);
    }

    gain.gain.setValueAtTime(effectiveVolume, startAt);
    gain.gain.exponentialRampToValueAtTime(0.001, startAt + duration);

    osc.connect(gain).connect(ctx.destination);
    osc.start(startAt);
    osc.stop(startAt + duration);
  }

  playNoise({ duration = 0.08, volume = 0.2 }) {
    const effectiveVolume = volume * settingsManager.effectiveSfxVolume();
    if (effectiveVolume <= 0) return;
    this.resume();
    const ctx = this.context;
    const bufferSize = Math.max(1, Math.floor(ctx.sampleRate * duration));
    const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i += 1) {
      data[i] = (Math.random() * 2 - 1) * (1 - i / bufferSize);
    }

    const source = ctx.createBufferSource();
    source.buffer = buffer;
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(effectiveVolume, ctx.currentTime);
    source.connect(gain).connect(ctx.destination);
    source.start();
  }

  hit() {
    this.playNoise({ duration: 0.06, volume: 0.18 });
  }

  playerDamage() {
    this.playTone({ frequency: 220, duration: 0.18, type: 'sawtooth', volume: 0.18, slideTo: 100 });
  }

  bossAttack() {
    this.playTone({ frequency: 500, duration: 0.12, type: 'triangle', volume: 0.12, slideTo: 700 });
  }

  bossDefeated() {
    this.playTone({ frequency: 300, duration: 0.5, type: 'sawtooth', volume: 0.2, slideTo: 900 });
  }

  buttonClick() {
    this.playTone({ frequency: 600, duration: 0.05, type: 'square', volume: 0.12 });
  }

  victory() {
    [440, 660, 880].forEach((frequency, i) => {
      this.playTone({ frequency, duration: 0.2, type: 'triangle', volume: 0.2, delay: i * 0.12 });
    });
  }

  defeat() {
    [400, 300, 200].forEach((frequency, i) => {
      this.playTone({ frequency, duration: 0.25, type: 'sawtooth', volume: 0.2, delay: i * 0.15 });
    });
  }
}
