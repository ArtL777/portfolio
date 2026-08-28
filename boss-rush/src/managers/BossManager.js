import { SlimeBoss } from '../bosses/SlimeBoss.js';
import { GolemBoss } from '../bosses/GolemBoss.js';
import { DragonBoss } from '../bosses/DragonBoss.js';
import { RobotBoss } from '../bosses/RobotBoss.js';
import { SpaceWormBoss } from '../bosses/SpaceWormBoss.js';

const BOSS_CLASSES = [SlimeBoss, GolemBoss, DragonBoss, RobotBoss, SpaceWormBoss];
export const TOTAL_BOSSES = BOSS_CLASSES.length;

// Игрок копит улучшения с каждой победой (П.39), поэтому одних только
// собственных стат-различий между боссами недостаточно — иначе более поздние
// боссы ощущаются слабее прокачанного игрока. Компаундим сложность по индексу
// (П.41: "должен становиться сложнее"), не трогая индивидуальные паттерны атак.
const DIFFICULTY_STEP = 0.18;

// New Game+ (roguelite-цикл): после полного прохождения игрок может начать
// цикл заново с той же прокачкой персонажа, но с боссами, усиленными ещё
// сильнее — иначе повторное прохождение ощущалось бы идентично первому.
const NG_PLUS_STEP = 0.35;

// Каждый цикл NG+ боссы не только живучее/больнее (scale выше), но и бьют
// чаще — иначе после нескольких циклов бой ощущается как "тот же босс, просто
// с большим числом HP", а не реально усложняется (ТЗ: "живучее и повышали
// скорость атак"). Та же идея, что и внутрибоевые фазы (Boss.phaseSpeedup),
// но накапливается МЕЖДУ забегами, а не внутри одного боя, и не имеет
// нижней границы через min — вместо этого капается на NG_PLUS_MAX_SPEEDUP,
// чтобы паузы между атаками не улетели в ноль на высоких циклах.
const NG_PLUS_ATTACK_SPEEDUP_STEP = 0.08;
const NG_PLUS_MAX_ATTACK_SPEEDUP = 0.5;

export class BossManager {
  createBoss(scene, index, x, y, ngPlusCycle = 0) {
    const BossClass = BOSS_CLASSES[index] ?? SlimeBoss;
    const boss = new BossClass(scene, x, y);

    const scale = (1 + index * DIFFICULTY_STEP) * (1 + ngPlusCycle * NG_PLUS_STEP);
    boss.maxHp = Math.round(boss.maxHp * scale);
    boss.hp = boss.maxHp;
    boss.damage = Math.round(boss.damage * scale);

    if (ngPlusCycle > 0) {
      const speedupFactor = 1 - Math.min(ngPlusCycle * NG_PLUS_ATTACK_SPEEDUP_STEP, NG_PLUS_MAX_ATTACK_SPEEDUP);
      boss.pauseMs = Math.round(boss.pauseMs * speedupFactor);
    }

    return boss;
  }
}
