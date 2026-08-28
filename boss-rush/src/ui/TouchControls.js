import Phaser from 'phaser';
import { GAME_WIDTH, GAME_HEIGHT, COLORS, TEXT, FONT } from '../config/constants.js';

// Увеличено и отодвинуто от края экрана — на маленьких телефонах элементы
// у самой кромки canvas визуально/тактильно проваливались за видимую область.
const JOYSTICK_RADIUS = 85;
const JOYSTICK_HIT_RADIUS = 130;
const STICK_RADIUS = 40;
const JOYSTICK_ORIGIN = { x: 150, y: GAME_HEIGHT - 210 };

const ATTACK_BUTTON = { x: GAME_WIDTH - 150, y: GAME_HEIGHT - 210, radius: 75 };
const DASH_BUTTON = { x: GAME_WIDTH - 150, y: GAME_HEIGHT - 210 - 160, radius: 55 };
const DEAD_ZONE = 0.15;

// Виртуальный джойстик + кнопка атаки (+ опционально кнопка рывка). Не вешает
// собственные слушатели ввода — только хранит визуал и состояние; маршрутизацию
// pointer-событий делает GameScene (единая точка входа для input, П.31).
export class TouchControls {
  constructor(scene, { dashEnabled = false } = {}) {
    this.scene = scene;
    this.vector = { x: 0, y: 0 };
    this.activePointerId = null;
    this.dashEnabled = dashEnabled;

    this.base = scene.add.circle(JOYSTICK_ORIGIN.x, JOYSTICK_ORIGIN.y, JOYSTICK_RADIUS, COLORS.panelFill, 0.55)
      .setStrokeStyle(3, COLORS.panelBorder, 0.9);
    this.stick = scene.add.circle(JOYSTICK_ORIGIN.x, JOYSTICK_ORIGIN.y, STICK_RADIUS, COLORS.player, 0.9);

    this.attackCircle = scene.add.circle(ATTACK_BUTTON.x, ATTACK_BUTTON.y, ATTACK_BUTTON.radius, COLORS.dangerMid, 0.45)
      .setStrokeStyle(3, COLORS.dangerHigh, 0.9);
    scene.add.text(ATTACK_BUTTON.x, ATTACK_BUTTON.y, 'АТАКА', {
      fontFamily: FONT.display, resolution: 3,
      fontSize: '20px',
      color: TEXT.primary,
      fontStyle: 'bold'
    }).setOrigin(0.5);

    if (dashEnabled) {
      scene.add.circle(DASH_BUTTON.x, DASH_BUTTON.y, DASH_BUTTON.radius, COLORS.accent, 0.35)
        .setStrokeStyle(3, COLORS.accent, 0.9);
      scene.add.text(DASH_BUTTON.x, DASH_BUTTON.y, 'РЫВОК', {
        fontFamily: FONT.display, resolution: 3,
        fontSize: '15px',
        color: TEXT.primary,
        fontStyle: 'bold'
      }).setOrigin(0.5);
    }
  }

  isInJoystickZone(pointer) {
    return Phaser.Math.Distance.Between(pointer.x, pointer.y, JOYSTICK_ORIGIN.x, JOYSTICK_ORIGIN.y) <= JOYSTICK_HIT_RADIUS;
  }

  isInDashZone(pointer) {
    if (!this.dashEnabled) return false;
    return Phaser.Math.Distance.Between(pointer.x, pointer.y, DASH_BUTTON.x, DASH_BUTTON.y) <= DASH_BUTTON.radius * 1.2;
  }

  beginJoystick(pointer) {
    this.activePointerId = pointer.id;
    this.updateJoystick(pointer);
  }

  updateJoystick(pointer) {
    if (pointer.id !== this.activePointerId) return;

    const dx = pointer.x - JOYSTICK_ORIGIN.x;
    const dy = pointer.y - JOYSTICK_ORIGIN.y;
    const distance = Math.min(Math.hypot(dx, dy), JOYSTICK_RADIUS);
    const angle = Math.atan2(dy, dx);

    this.stick.setPosition(
      JOYSTICK_ORIGIN.x + Math.cos(angle) * distance,
      JOYSTICK_ORIGIN.y + Math.sin(angle) * distance
    );

    const normalized = distance / JOYSTICK_RADIUS;
    this.vector = normalized > DEAD_ZONE
      ? { x: Math.cos(angle) * normalized, y: Math.sin(angle) * normalized }
      : { x: 0, y: 0 };
  }

  endJoystick(pointer) {
    if (pointer.id !== this.activePointerId) return;
    this.activePointerId = null;
    this.vector = { x: 0, y: 0 };
    this.stick.setPosition(JOYSTICK_ORIGIN.x, JOYSTICK_ORIGIN.y);
  }

  getVector() {
    return this.vector;
  }
}
