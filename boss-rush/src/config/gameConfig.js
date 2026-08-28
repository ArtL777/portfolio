import Phaser from 'phaser';
import { MenuScene } from '../scenes/MenuScene.js';
import { GameScene } from '../scenes/GameScene.js';
import { ResultScene } from '../scenes/ResultScene.js';
import { MetaScene } from '../scenes/MetaScene.js';
import { GAME_WIDTH, GAME_HEIGHT } from './constants.js';

export { GAME_WIDTH, GAME_HEIGHT };

export const gameConfig = {
  type: Phaser.AUTO,
  parent: 'game-container',
  width: GAME_WIDTH,
  height: GAME_HEIGHT,
  backgroundColor: '#0d0d14',
  pixelArt: true,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH
  },
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { x: 0, y: 0 },
      debug: false
    }
  },
  scene: [MenuScene, GameScene, ResultScene, MetaScene]
};
