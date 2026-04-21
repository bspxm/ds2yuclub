<template>
  <div class="knockout-bracket">
    <!-- 轮次标题 -->
    <div class="round-headers">
      <div v-for="round in rounds" :key="round.key" class="round-header">
        {{ round.label }}
      </div>
    </div>

    <!-- 对阵树容器 -->
    <div ref="bracketWrapper" class="bracket-wrapper">
      <div class="bracket-container" :style="containerStyle">
        <!-- SVG 连线层 -->
        <svg class="bracket-lines" :width="svgWidth" :height="svgHeight">
          <defs>
            <!-- 渐变定义 -->
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" class="line-gradient-start" />
              <stop offset="100%" class="line-gradient-end" />
            </linearGradient>
            <linearGradient id="activeLineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" class="active-line-gradient-start" />
              <stop offset="100%" class="active-line-gradient-end" />
            </linearGradient>
          </defs>
          <g v-for="line in lines" :key="line.id">
            <path :d="line.path" class="line" :class="{ active: line.isActive }" />
          </g>
        </svg>

        <!-- 比赛卡片层 -->
        <div
          v-for="match in layoutMatches"
          :key="match.id"
          class="match-card"
          :class="{
            completed: match.status === 'completed',
            bye: match.status === 'bye',
            'has-winner': match.winner_id,
            clickable: true,
          }"
          :style="getMatchStyle(match)"
          @click="handleMatchClick(match)"
          @mouseenter="hoveredMatch = match.id"
          @mouseleave="hoveredMatch = null"
        >
          <!-- 选手1 -->
          <div
            class="player-row"
            :class="{
              winner: match.player1?.is_winner,
              'is-bye': !match.player1 || match.player1.name === 'BYE',
            }"
          >
            <span v-if="match.player1?.seed" class="seed">{{ match.player1.seed }}</span>
            <span v-else class="seed empty"></span>
            <span v-if="match.player1?.country" class="flag">
              {{ getFlag(match.player1.country) }}
            </span>
            <span class="name" :class="{ 'empty-slot': !match.player1?.name }">
              {{ match.player1?.name || (match.round_number === 1 ? "轮空" : "等待对手") }}
            </span>
            <span class="scores-container">
              <span v-for="(score, idx) in getPlayerScores(match, 1)" :key="idx" class="score-item">
                {{ score }}
              </span>
            </span>
          </div>

          <!-- 选手2 -->
          <div
            class="player-row"
            :class="{
              winner: match.player2?.is_winner,
              'is-bye': !match.player2 || match.player2.name === 'BYE',
            }"
          >
            <span v-if="match.player2?.seed" class="seed">{{ match.player2.seed }}</span>
            <span v-else class="seed empty"></span>
            <span v-if="match.player2?.country" class="flag">
              {{ getFlag(match.player2.country) }}
            </span>
            <span class="name" :class="{ 'empty-slot': !match.player2?.name }">
              {{ match.player2?.name || (match.round_number === 1 ? "轮空" : "等待对手") }}
            </span>
            <span class="scores-container">
              <span v-for="(score, idx) in getPlayerScores(match, 2)" :key="idx" class="score-item">
                {{ score }}
              </span>
            </span>
          </div>

          <!-- 局分显示 -->
          <div v-if="match.status === 'COMPLETED' && getMatchResult(match)" class="match-result">
            <span class="result-score">{{ getMatchResult(match) }}</span>
          </div>

          <!-- 比赛状态指示器 -->
          <div v-if="match.status === 'completed'" class="match-status">
            <div class="status-dot completed"></div>
          </div>
          <div v-else-if="match.status === 'bye'" class="match-status">
            <div class="status-dot bye"></div>
          </div>
        </div>

        <!-- 冠军卡片 -->
        <div v-if="championMatch" class="champion-card" :style="getChampionStyle()">
          <div class="champion-header">
            <span class="trophy">🏆</span>
            <span class="champion-label">冠军</span>
          </div>
          <div class="champion-content">
            <span v-if="championMatch.championCountry" class="flag">
              {{ getFlag(championMatch.championCountry) }}
            </span>
            <span class="champion-name">{{ championMatch.championName }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图例说明 -->
    <div class="bracket-legend">
      <div class="legend-item">
        <div class="legend-dot completed"></div>
        <span>已完成</span>
      </div>
      <div class="legend-item">
        <div class="legend-dot pending"></div>
        <span>未开始</span>
      </div>
      <div class="legend-item">
        <div class="legend-dot bye"></div>
        <span>轮空</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";

interface KnockoutPlayer {
  id: number;
  name: string;
  seed?: number;
  country?: string;
  is_winner?: boolean;
  score?: number | string;
}

interface KnockoutMatch {
  id: number;
  round: string;
  round_number: number;
  match_number: number;
  player1: KnockoutPlayer | null;
  player2: KnockoutPlayer | null;
  scores?: string;
  winner_id?: number;
  status: "scheduled" | "completed" | "bye";
  prev_match1_id?: number;
  prev_match2_id?: number;
  next_match_id?: number;
}

const props = defineProps<{
  matches: KnockoutMatch[];
  totalRounds?: number;
}>();

const emit = defineEmits<{
  (e: "matchClick", match: KnockoutMatch): void;
}>();

// 布局参数 - 更紧凑的尺寸
const CARD_WIDTH = 240;
const CARD_HEIGHT = 64;
const ROUND_WIDTH = 380;
const VERTICAL_GAP = 16;

const bracketWrapper = ref<HTMLElement>();
const hoveredMatch = ref<number | null>(null);

// 计算总轮数
const totalRounds = computed(() => {
  if (props.totalRounds) return props.totalRounds;
  if (props.matches.length === 0) return 0;
  const maxRound = Math.max(...props.matches.map((m) => m.round_number), 1);
  return maxRound;
});

// 轮次标签映射 - 根据总轮数动态计算
const getRoundLabel = (roundNumber: number, total: number): string => {
  // 从最后一轮往前推
  const roundsFromEnd = total - roundNumber + 1;

  const labels: Record<number, string> = {
    1: "决赛",
    2: "半决赛",
    3: "1/4决赛",
    4: "1/8决赛",
    5: "1/16决赛",
    6: "1/32决赛",
    7: "1/64决赛",
  };

  return labels[roundsFromEnd] || `第${roundNumber}轮`;
};

// 轮次标题
const rounds = computed(() => {
  const result = [];
  for (let i = 1; i <= totalRounds.value; i++) {
    result.push({
      key: i,
      label: getRoundLabel(i, totalRounds.value),
    });
  }
  return result;
});

// 计算SVG和容器尺寸
const svgWidth = computed(() => {
  return totalRounds.value * ROUND_WIDTH + CARD_WIDTH + 60;
});

const svgHeight = computed(() => {
  const firstRoundMatches = props.matches.filter((m) => m.round_number === 1).length;
  if (firstRoundMatches === 0) return 400;
  // 计算所需高度
  const height = firstRoundMatches * (CARD_HEIGHT + VERTICAL_GAP) + 100;
  return Math.max(height, 300);
});

const containerStyle = computed(() => ({
  width: `${svgWidth.value}px`,
  minHeight: `${svgHeight.value}px`,
}));

// 改进的布局算法 - 递归计算位置
const layoutMatches = computed(() => {
  if (!props.matches.length) return [];

  const matches = [...props.matches];
  const matchesByRound: Record<number, KnockoutMatch[]> = {};

  // 按轮次分组并排序
  matches.forEach((m) => {
    if (!matchesByRound[m.round_number]) {
      matchesByRound[m.round_number] = [];
    }
    matchesByRound[m.round_number].push(m);
  });

  Object.keys(matchesByRound).forEach((round) => {
    matchesByRound[Number(round)].sort((a, b) => a.match_number - b.match_number);
  });

  // 存储布局结果
  const layoutMap = new Map<number, { x: number; y: number; match: KnockoutMatch }>();

  // 计算基础间距
  const getBaseGap = (round: number) => {
    // 随着轮次增加，间距增大
    return (CARD_HEIGHT + VERTICAL_GAP) * Math.pow(2, round - 1) - CARD_HEIGHT;
  };

  // 递归计算位置
  const calculatePosition = (match: KnockoutMatch): { x: number; y: number } => {
    if (layoutMap.has(match.id)) {
      return layoutMap.get(match.id)!;
    }

    const roundIndex = match.round_number - 1;
    const x = roundIndex * ROUND_WIDTH;

    let y: number;

    if (match.round_number === 1) {
      // 第一轮：均匀分布
      const firstRound = matchesByRound[1];
      const index = firstRound.findIndex((m) => m.id === match.id);
      const totalGap = CARD_HEIGHT + getBaseGap(1);
      y = index * totalGap + 40; // 顶部留白
    } else {
      // 后续轮次：基于上一轮两个上游比赛的位置
      const prevMatch1 = matches.find((m) => m.id === match.prev_match1_id);
      const prevMatch2 = matches.find((m) => m.id === match.prev_match2_id);

      if (prevMatch1 && prevMatch2) {
        const pos1 = calculatePosition(prevMatch1);
        const pos2 = calculatePosition(prevMatch2);
        // 取中间位置
        y = (pos1.y + pos2.y) / 2;
      } else {
        // 回退方案
        const roundMatches = matchesByRound[match.round_number];
        const index = roundMatches.findIndex((m) => m.id === match.id);
        const totalGap = CARD_HEIGHT + getBaseGap(match.round_number);
        y = index * totalGap + 40;
      }
    }

    layoutMap.set(match.id, { x, y, match });
    return { x, y };
  };

  // 计算所有比赛位置
  matches.forEach((match) => calculatePosition(match));

  // 转换为结果数组
  const result: (KnockoutMatch & { x: number; y: number })[] = [];
  layoutMap.forEach(({ x, y, match }) => {
    result.push({ ...match, x, y });
  });

  return result.sort((a, b) => a.round_number - b.round_number || a.match_number - b.match_number);
});

// 计算直角转弯连线
const lines = computed(() => {
  const result: {
    id: string;
    path: string;
    isActive: boolean;
  }[] = [];

  layoutMatches.value.forEach((match) => {
    const matchX = match.x;
    const matchY = match.y;

    // 上游比赛1的连线 (连接到上半部分)
    if (match.prev_match1_id) {
      const prevMatch = layoutMatches.value.find((m) => m.id === match.prev_match1_id);
      if (prevMatch) {
        const prevX = prevMatch.x + CARD_WIDTH;
        const prevY = prevMatch.y + CARD_HEIGHT / 2;
        const targetY = matchY + CARD_HEIGHT / 4;

        // 直角转弯连线
        const midX = (prevX + matchX) / 2;
        const path = `M ${prevX} ${prevY} L ${midX} ${prevY} L ${midX} ${targetY} L ${matchX} ${targetY}`;

        result.push({
          id: `${match.id}-1`,
          path,
          isActive: match.winner_id === match.player1?.id || hoveredMatch.value === match.id,
        });
      }
    }

    // 上游比赛2的连线 (连接到下半部分)
    if (match.prev_match2_id) {
      const prevMatch = layoutMatches.value.find((m) => m.id === match.prev_match2_id);
      if (prevMatch) {
        const prevX = prevMatch.x + CARD_WIDTH;
        const prevY = prevMatch.y + CARD_HEIGHT / 2;
        const targetY = matchY + (CARD_HEIGHT * 3) / 4;

        // 直角转弯连线
        const midX = (prevX + matchX) / 2;
        const path = `M ${prevX} ${prevY} L ${midX} ${prevY} L ${midX} ${targetY} L ${matchX} ${targetY}`;

        result.push({
          id: `${match.id}-2`,
          path,
          isActive: match.winner_id === match.player2?.id || hoveredMatch.value === match.id,
        });
      }
    }
  });

  return result;
});

// 获取比赛卡片样式
const getMatchStyle = (match: { x: number; y: number }) => ({
  left: `${match.x}px`,
  top: `${match.y}px`,
  width: `${CARD_WIDTH}px`,
});

// 获取冠军卡片样式
const getChampionStyle = () => {
  const finalRound = totalRounds.value;
  const finalMatches = layoutMatches.value.filter((m) => m.round_number === finalRound);
  if (finalMatches.length > 0) {
    const finalMatch = finalMatches[0];
    return {
      left: `${finalMatch.x + ROUND_WIDTH}px`,
      top: `${finalMatch.y}px`,
    };
  }
  return { left: "0px", top: "0px" };
};

// 冠军信息 - 只有决赛完成且有胜者和比分时才显示
const championMatch = computed(() => {
  // 找到决赛（最后一轮）
  const finalMatch = props.matches.find(
    (m) => m.round === "final" || m.round_number === totalRounds.value
  );

  // 检查决赛是否已完成、有胜者、有比分
  if (finalMatch?.winner_id && finalMatch.status === "COMPLETED" && finalMatch.scores) {
    let championName = "";
    let championCountry = "";

    if (finalMatch.player1?.id === finalMatch.winner_id) {
      championName = finalMatch.player1.name;
      championCountry = finalMatch.player1.country || "";
    } else if (finalMatch.player2?.id === finalMatch.winner_id) {
      championName = finalMatch.player2.name;
      championCountry = finalMatch.player2.country || "";
    }

    return {
      championName,
      championCountry,
      match: finalMatch,
    };
  }
  return null;
});

// 获取选手比分
const getPlayerScore = (match: KnockoutMatch, playerNum: 1 | 2) => {
  if (!match.scores || match.scores === "-") return "";

  // 解析比分字符串，如 "21-15, 18-21, 21-19"
  const sets = match.scores.split(",").map((s) => s.trim());
  const scores: string[] = [];

  sets.forEach((set) => {
    const parts = set.split("-").map((s) => s.trim());
    if (parts.length === 2) {
      const score1 = parts[0];
      const score2 = parts[1];
      if (playerNum === 1) {
        scores.push(score1);
      } else {
        scores.push(score2);
      }
    }
  });

  return scores.join(" ");
};

// 获取选手每局比分（返回数组）
const getPlayerScores = (match: KnockoutMatch, playerNum: 1 | 2): string[] => {
  if (!match.scores || match.scores === "-") return [];

  // 解析比分字符串，如 "21-15, 18-21, 21-19"
  const sets = match.scores.split(",").map((s) => s.trim());
  const scores: string[] = [];

  sets.forEach((set) => {
    const parts = set.split("-").map((s) => s.trim());
    if (parts.length === 2) {
      const score1 = parts[0];
      const score2 = parts[1];
      if (playerNum === 1) {
        scores.push(score1);
      } else {
        scores.push(score2);
      }
    }
  });

  return scores;
};

// 获取比赛局分（如 2:1）
const getMatchResult = (match: KnockoutMatch): string => {
  if (!match.scores || match.scores === "-") return "";

  const scores1 = getPlayerScores(match, 1);
  const scores2 = getPlayerScores(match, 2);

  if (scores1.length === 0 || scores2.length === 0) return "";

  let wins1 = 0;
  let wins2 = 0;

  for (let i = 0; i < scores1.length; i++) {
    const s1 = parseInt(scores1[i], 10);
    const s2 = parseInt(scores2[i], 10);
    if (s1 > s2) {
      wins1++;
    } else if (s2 > s1) {
      wins2++;
    }
  }

  return `${wins1}:${wins2}`;
};

// 国旗emoji映射
const countryFlags: Record<string, string> = {
  CN: "🇨🇳",
  JP: "🇯🇵",
  KR: "🇰🇷",
  DK: "🇩🇰",
  ID: "🇮🇩",
  MY: "🇲🇾",
  TH: "🇹🇭",
  IN: "🇮🇳",
  GB: "🇬🇧",
  US: "🇺🇸",
  DE: "🇩🇪",
  FR: "🇫🇷",
  TW: "🇹🇼",
  HK: "🇭🇰",
  SG: "🇸🇬",
  CA: "🇨🇦",
  AU: "🇦🇺",
  NZ: "🇳🇿",
  NL: "🇳🇱",
  ES: "🇪🇸",
  IT: "🇮🇹",
  CH: "🇨🇭",
  SE: "🇸🇪",
  NO: "🇳🇴",
  FI: "🇫🇮",
  RU: "🇷🇺",
  BR: "🇧🇷",
  MX: "🇲🇽",
  AR: "🇦🇷",
  CL: "🇨🇱",
  CO: "🇨🇴",
  PE: "🇵🇪",
  VE: "🇻🇪",
  EC: "🇪🇨",
  UY: "🇺🇾",
  PY: "🇵🇾",
  BO: "🇧🇴",
  CU: "🇨🇺",
  DO: "🇩🇴",
  PR: "🇵🇷",
  JM: "🇯🇲",
  TT: "🇹🇹",
  BB: "🇧🇧",
  BS: "🇧🇸",
  GY: "🇬🇾",
  SR: "🇸🇷",
  GF: "🇬🇫",
  CR: "🇨🇷",
  PA: "🇵🇦",
  GT: "🇬🇹",
  HN: "🇭🇳",
  SV: "🇸🇻",
  NI: "🇳🇮",
  BZ: "🇧🇿",
  HT: "🇭🇹",
  ZA: "🇿🇦",
  EG: "🇪🇬",
  NG: "🇳🇬",
  KE: "🇰🇪",
  GH: "🇬🇭",
  ET: "🇪🇹",
  UG: "🇺🇬",
  TZ: "🇹🇿",
  MW: "🇲🇼",
  ZM: "🇿🇲",
  ZW: "🇿🇼",
  BW: "🇧🇼",
  NA: "🇳🇦",
  MZ: "🇲🇿",
  MG: "🇲🇬",
  MU: "🇲🇺",
  SC: "🇸🇨",
  KM: "🇰🇲",
  CV: "🇨🇻",
  ST: "🇸🇹",
  GQ: "🇬🇶",
  GA: "🇬🇦",
  CG: "🇨🇬",
  CD: "🇨🇩",
  AO: "🇦🇴",
  CM: "🇨🇲",
  CF: "🇨🇫",
  TD: "🇹🇩",
  NE: "🇳🇪",
  ML: "🇲🇱",
  BF: "🇧🇫",
  SN: "🇸🇳",
  GM: "🇬🇲",
  GW: "🇬🇼",
  GN: "🇬🇳",
  SL: "🇸🇱",
  LR: "🇱🇷",
  CI: "🇨🇮",
  GH2: "🇬🇭",
  TG: "🇹🇬",
  BJ: "🇧🇯",
  NG2: "🇳🇬",
  NE2: "🇳🇪",
  DZ: "🇩🇿",
  TN: "🇹🇳",
  LY: "🇱🇾",
  MA: "🇲🇦",
  EH: "🇪🇭",
  MR: "🇲🇷",
  SN2: "🇸🇳",
  GM2: "🇬🇲",
  GW2: "🇬🇼",
  GN2: "🇬🇳",
  SL2: "🇸🇱",
  LR2: "🇱🇷",
  CI2: "🇨🇮",
  BF2: "🇧🇫",
  ML2: "🇲🇱",
  NE3: "🇳🇪",
  TG2: "🇹🇬",
  BJ2: "🇧🇯",
  NG3: "🇳🇬",
  TR: "🇹🇷",
  IR: "🇮🇷",
  IQ: "🇮🇶",
  IL: "🇮🇱",
  JO: "🇯🇴",
  LB: "🇱🇧",
  SY: "🇸🇾",
  YE: "🇾🇪",
  OM: "🇴🇲",
  AE: "🇦🇪",
  QA: "🇶🇦",
  BH: "🇧🇭",
  KW: "🇰🇼",
  SA: "🇸🇦",
  AF: "🇦🇫",
  PK: "🇵🇰",
  IN2: "🇮🇳",
  NP: "🇳🇵",
  BT: "🇧🇹",
  BD: "🇧🇩",
  LK: "🇱🇰",
  MV: "🇲🇻",
  MM: "🇲🇲",
  TH2: "🇹🇭",
  LA: "🇱🇦",
  KH: "🇰🇭",
  VN: "🇻🇳",
  MY2: "🇲🇾",
  SG2: "🇸🇬",
  ID2: "🇮🇩",
  BN: "🇧🇳",
  PH: "🇵🇭",
  TW2: "🇹🇼",
  CN2: "🇨🇳",
  MN: "🇲🇳",
  KP: "🇰🇵",
  KR2: "🇰🇷",
  JP2: "🇯🇵",
  KZ: "🇰🇿",
  KG: "🇰🇬",
  TJ: "🇹🇯",
  TM: "🇹🇲",
  UZ: "🇺🇿",
  AZ: "🇦🇿",
  GE: "🇬🇪",
  AM: "🇦🇲",
  UA: "🇺🇦",
  BY: "🇧🇾",
  MD: "🇲🇩",
  LT: "🇱🇹",
  LV: "🇱🇻",
  EE: "🇪🇪",
  FI2: "🇫🇮",
  SE2: "🇸🇪",
  NO2: "🇳🇴",
  DK2: "🇩🇰",
  IS: "🇮🇸",
  GB2: "🇬🇧",
  IE: "🇮🇪",
  PT: "🇵🇹",
  ES2: "🇪🇸",
  FR2: "🇫🇷",
  BE: "🇧🇪",
  NL2: "🇳🇱",
  LU: "🇱🇺",
  DE2: "🇩🇪",
  CH2: "🇨🇭",
  AT: "🇦🇹",
  IT2: "🇮🇹",
  MT: "🇲🇹",
  SM: "🇸🇲",
  VA: "🇻🇦",
  MC: "🇲🇨",
  AD: "🇦🇩",
  ES3: "🇪🇸",
  FR3: "🇫🇷",
  IT3: "🇮🇹",
  SI: "🇸🇮",
  HR: "🇭🇷",
  BA: "🇧🇦",
  RS: "🇷🇸",
  ME: "🇲🇪",
  AL: "🇦🇱",
  MK: "🇲🇰",
  BG: "🇧🇬",
  RO: "🇷🇴",
  MD2: "🇲🇩",
  UA2: "🇺🇦",
  RU2: "🇷🇺",
  BY2: "🇧🇾",
  PL: "🇵🇱",
  CZ: "🇨🇿",
  SK: "🇸🇰",
  HU: "🇭🇺",
  RO2: "🇷🇴",
  BG2: "🇧🇬",
  GR: "🇬🇷",
  CY: "🇨🇾",
  TR2: "🇹🇷",
  GE2: "🇬🇪",
  AM2: "🇦🇲",
  AZ2: "🇦🇿",
  KZ2: "🇰🇿",
  MN2: "🇲🇳",
  CN3: "🇨🇳",
  TW3: "🇹🇼",
  HK2: "🇭🇰",
  MO: "🇲🇴",
  KP2: "🇰🇵",
  KR3: "🇰🇷",
  JP3: "🇯🇵",
  VN2: "🇻🇳",
  LA2: "🇱🇦",
  KH2: "🇰🇭",
  TH3: "🇹🇭",
  MM2: "🇲🇲",
  MY3: "🇲🇾",
  SG3: "🇸🇬",
  ID3: "🇮🇩",
  BN2: "🇧🇳",
  PH2: "🇵🇭",
  TL: "🇹🇱",
  IN3: "🇮🇳",
  LK2: "🇱🇰",
  MV2: "🇲🇻",
  BD2: "🇧🇩",
  BT2: "🇧🇹",
  NP2: "🇳🇵",
  PK2: "🇵🇰",
  AF2: "🇦🇫",
  TJ2: "🇹🇯",
  KG2: "🇰🇬",
  UZ2: "🇺🇿",
  TM2: "🇹🇲",
  KZ3: "🇰🇿",
  MN3: "🇲🇳",
  RU3: "🇷🇺",
  UA3: "🇺🇦",
  BY3: "🇧🇾",
  MD3: "🇲🇩",
  PL2: "🇵🇱",
  SK2: "🇸🇰",
  CZ2: "🇨🇿",
  AT2: "🇦🇹",
  HU2: "🇭🇺",
  RO3: "🇷🇴",
  BG3: "🇧🇬",
  RS2: "🇷🇸",
  ME2: "🇲🇪",
  AL2: "🇦🇱",
  MK2: "🇲🇰",
  BA2: "🇧🇦",
  HR2: "🇭🇷",
  SI2: "🇸🇮",
  IT4: "🇮🇹",
  FR4: "🇫🇷",
  MC2: "🇲🇨",
  SM2: "🇸🇲",
  VA2: "🇻🇦",
  MT2: "🇲🇹",
  ES4: "🇪🇸",
  PT2: "🇵🇹",
  AD2: "🇦🇩",
  CH3: "🇨🇭",
  LI: "🇱🇮",
  DE3: "🇩🇪",
  BE2: "🇧🇪",
  NL3: "🇳🇱",
  LU2: "🇱🇺",
  GB3: "🇬🇧",
  IE2: "🇮🇪",
  IS2: "🇮🇸",
  NO3: "🇳🇴",
  SE3: "🇸🇪",
  FI3: "🇫🇮",
  DK3: "🇩🇰",
  EE2: "🇪🇪",
  LV2: "🇱🇻",
  LT2: "🇱🇹",
  BY4: "🇧🇾",
  RU4: "🇷🇺",
  UA4: "🇺🇦",
  MD4: "🇲🇩",
  RO4: "🇷🇴",
  BG4: "🇧🇬",
  GR2: "🇬🇷",
  CY2: "🇨🇾",
  TR3: "🇹🇷",
  GE3: "🇬🇪",
  AM3: "🇦🇲",
  AZ3: "🇦🇿",
  IR2: "🇮🇷",
  IQ2: "🇮🇶",
  IL2: "🇮🇱",
  JO2: "🇯🇴",
  LB2: "🇱🇧",
  SY2: "🇸🇾",
  YE2: "🇾🇪",
  SA2: "🇸🇦",
  KW2: "🇰🇼",
  BH2: "🇧🇭",
  QA2: "🇶🇦",
  AE2: "🇦🇪",
  OM2: "🇴🇲",
  YE3: "🇾🇪",
  SY3: "🇸🇾",
  LB3: "🇱🇧",
  JO3: "🇯🇴",
  IL3: "🇮🇱",
  IQ3: "🇮🇶",
  IR3: "🇮🇷",
  TR4: "🇹🇷",
  CY3: "🇨🇾",
  GR3: "🇬🇷",
  BG5: "🇧🇬",
  RO5: "🇷🇴",
  MD5: "🇲🇩",
  UA5: "🇺🇦",
  RU5: "🇷🇺",
  BY5: "🇧🇾",
  LT3: "🇱🇹",
  LV3: "🇱🇻",
  EE3: "🇪🇪",
  FI4: "🇫🇮",
  SE4: "🇸🇪",
  NO4: "🇳🇴",
  DK4: "🇩🇰",
  IS3: "🇮🇸",
  IE3: "🇮🇪",
  GB4: "🇬🇧",
  PT3: "🇵🇹",
  ES5: "🇪🇸",
  FR5: "🇫🇷",
  IT5: "🇮🇹",
  CH4: "🇨🇭",
  AT3: "🇦🇹",
  DE4: "🇩🇪",
  NL4: "🇳🇱",
  BE3: "🇧🇪",
  LU3: "🇱🇺",
  FR6: "🇫🇷",
  ES6: "🇪🇸",
  PT4: "🇵🇹",
  IT6: "🇮🇹",
  CH5: "🇨🇭",
  AT4: "🇦🇹",
  DE5: "🇩🇪",
  NL5: "🇳🇱",
  BE4: "🇧🇪",
  LU4: "🇱🇺",
  GB5: "🇬🇧",
  IE4: "🇮🇪",
  IS4: "🇮🇸",
  NO5: "🇳🇴",
  SE5: "🇸🇪",
  FI5: "🇫🇮",
  DK5: "🇩🇰",
  EE4: "🇪🇪",
  LV4: "🇱🇻",
  LT4: "🇱🇹",
  BY6: "🇧🇾",
  RU6: "🇷🇺",
  UA6: "🇺🇦",
  MD6: "🇲🇩",
  RO6: "🇷🇴",
  BG6: "🇧🇬",
  GR4: "🇬🇷",
  CY4: "🇨🇾",
  TR5: "🇹🇷",
  GE4: "🇬🇪",
  AM4: "🇦🇲",
  AZ4: "🇦🇿",
  IR4: "🇮🇷",
  IQ4: "🇮🇶",
  IL4: "🇮🇱",
  JO4: "🇯🇴",
  LB4: "🇱🇧",
  SY4: "🇸🇾",
  YE4: "🇾🇪",
  SA3: "🇸🇦",
  KW3: "🇰🇼",
  BH3: "🇧🇭",
  QA3: "🇶🇦",
  AE3: "🇦🇪",
  OM3: "🇴🇲",
  YE5: "🇾🇪",
  SY5: "🇸🇾",
  LB5: "🇱🇧",
  JO5: "🇯🇴",
  IL5: "🇮🇱",
  IQ5: "🇮🇶",
  IR5: "🇮🇷",
  TR6: "🇹🇷",
  CY5: "🇨🇾",
  GR5: "🇬🇷",
  BG7: "🇧🇬",
  RO7: "🇷🇴",
  MD7: "🇲🇩",
  UA7: "🇺🇦",
  RU7: "🇷🇺",
  BY7: "🇧🇾",
  LT5: "🇱🇹",
  LV5: "🇱🇻",
  EE5: "🇪🇪",
  FI6: "🇫🇮",
  SE6: "🇸🇪",
  NO6: "🇳🇴",
  DK6: "🇩🇰",
  IS5: "🇮🇸",
  IE5: "🇮🇪",
  GB6: "🇬🇧",
  PT5: "🇵🇹",
  ES7: "🇪🇸",
  FR7: "🇫🇷",
  IT7: "🇮🇹",
  CH6: "🇨🇭",
  AT5: "🇦🇹",
  DE6: "🇩🇪",
  NL6: "🇳🇱",
  BE5: "🇧🇪",
  LU5: "🇱🇺",
  FR8: "🇫🇷",
  ES8: "🇪🇸",
  PT6: "🇵🇹",
  IT8: "🇮🇹",
  CH7: "🇨🇭",
  AT6: "🇦🇹",
  DE7: "🇩🇪",
  NL7: "🇳🇱",
  BE6: "🇧🇪",
  LU6: "🇱🇺",
  GB7: "🇬🇧",
  IE6: "🇮🇪",
  IS6: "🇮🇸",
  NO7: "🇳🇴",
  SE7: "🇸🇪",
  FI7: "🇫🇮",
  DK7: "🇩🇰",
  EE6: "🇪🇪",
  LV6: "🇱🇻",
  LT6: "🇱🇹",
  BY8: "🇧🇾",
  RU8: "🇷🇺",
  UA8: "🇺🇦",
  MD8: "🇲🇩",
  RO8: "🇷🇴",
  BG8: "🇧🇬",
  GR6: "🇬🇷",
  CY6: "🇨🇾",
  TR7: "🇹🇷",
  GE5: "🇬🇪",
  AM5: "🇦🇲",
  AZ5: "🇦🇿",
  IR6: "🇮🇷",
  IQ6: "🇮🇶",
  IL6: "🇮🇱",
  JO6: "🇯🇴",
  LB6: "🇱🇧",
  SY6: "🇸🇾",
  YE6: "🇾🇪",
  SA4: "🇸🇦",
  KW4: "🇰🇼",
  BH4: "🇧🇭",
  QA4: "🇶🇦",
  AE4: "🇦🇪",
  OM4: "🇴🇲",
  YE7: "🇾🇪",
  SY7: "🇸🇾",
  LB7: "🇱🇧",
  JO7: "🇯🇴",
  IL7: "🇮🇱",
  IQ7: "🇮🇶",
  IR7: "🇮🇷",
  TR8: "🇹🇷",
  CY7: "🇨🇾",
  GR7: "🇬🇷",
  BG9: "🇧🇬",
  RO9: "🇷🇴",
  MD9: "🇲🇩",
  UA9: "🇺🇦",
  RU9: "🇷🇺",
  BY9: "🇧🇾",
  LT7: "🇱🇹",
  LV7: "🇱🇻",
  EE7: "🇪🇪",
  FI8: "🇫🇮",
  SE8: "🇸🇪",
  NO8: "🇳🇴",
  DK8: "🇩🇰",
  IS7: "🇮🇸",
  IE7: "🇮🇪",
  GB8: "🇬🇧",
  PT7: "🇵🇹",
  ES9: "🇪🇸",
  FR9: "🇫🇷",
  IT9: "🇮🇹",
  CH8: "🇨🇭",
  AT7: "🇦🇹",
  DE8: "🇩🇪",
  NL8: "🇳🇱",
  BE7: "🇧🇪",
  LU7: "🇱🇺",
  FR10: "🇫🇷",
  ES10: "🇪🇸",
  PT8: "🇵🇹",
  IT10: "🇮🇹",
  CH9: "🇨🇭",
  AT8: "🇦🇹",
  DE9: "🇩🇪",
  NL9: "🇳🇱",
  BE8: "🇧🇪",
  LU8: "🇱🇺",
  GB9: "🇬🇧",
  IE8: "🇮🇪",
  IS8: "🇮🇸",
  NO9: "🇳🇴",
  SE9: "🇸🇪",
  FI9: "🇫🇮",
  DK9: "🇩🇰",
  EE8: "🇪🇪",
  LV8: "🇱🇻",
  LT8: "🇱🇹",
  BY10: "🇧🇾",
  RU10: "🇷🇺",
  UA10: "🇺🇦",
  MD10: "🇲🇩",
  RO10: "🇷🇴",
  BG10: "🇧🇬",
  GR8: "🇬🇷",
  CY8: "🇨🇾",
  TR9: "🇹🇷",
  GE6: "🇬🇪",
  AM6: "🇦🇲",
  AZ6: "🇦🇿",
  IR8: "🇮🇷",
  IQ8: "🇮🇶",
  IL8: "🇮🇱",
  JO8: "🇯🇴",
  LB8: "🇱🇧",
  SY8: "🇸🇾",
  YE8: "🇾🇪",
  SA5: "🇸🇦",
  KW5: "🇰🇼",
  BH5: "🇧🇭",
  QA5: "🇶🇦",
  AE5: "🇦🇪",
  OM5: "🇴🇲",
  YE9: "🇾🇪",
  SY9: "🇸🇾",
  LB9: "🇱🇧",
  JO9: "🇯🇴",
  IL9: "🇮🇱",
  IQ9: "🇮🇶",
  IR9: "🇮🇷",
  TR10: "🇹🇷",
  CY9: "🇨🇾",
  GR9: "🇬🇷",
  BG11: "🇧🇬",
  RO11: "🇷🇴",
  MD11: "🇲🇩",
  UA11: "🇺🇦",
  RU11: "🇷🇺",
  BY11: "🇧🇾",
  LT9: "🇱🇹",
  LV9: "🇱🇻",
  EE9: "🇪🇪",
  FI10: "🇫🇮",
  SE10: "🇸🇪",
  NO10: "🇳🇴",
  DK10: "🇩🇰",
  IS9: "🇮🇸",
  IE9: "🇮🇪",
  GB10: "🇬🇧",
  PT9: "🇵🇹",
  ES11: "🇪🇸",
  FR11: "🇫🇷",
  IT11: "🇮🇹",
  CH10: "🇨🇭",
  AT9: "🇦🇹",
  DE10: "🇩🇪",
  NL10: "🇳🇱",
  BE9: "🇧🇪",
  LU9: "🇱🇺",
  FR12: "🇫🇷",
  ES12: "🇪🇸",
  PT10: "🇵🇹",
  IT12: "🇮🇹",
  CH11: "🇨🇭",
  AT10: "🇦🇹",
  DE11: "🇩🇪",
  NL11: "🇳🇱",
  BE10: "🇧🇪",
  LU10: "🇱🇺",
  GB11: "🇬🇧",
  IE10: "🇮🇪",
  IS10: "🇮🇸",
  NO11: "🇳🇴",
  SE11: "🇸🇪",
  FI11: "🇫🇮",
  DK11: "🇩🇰",
  EE10: "🇪🇪",
  LV10: "🇱🇻",
  LT10: "🇱🇹",
  BY12: "🇧🇾",
  RU12: "🇷🇺",
  UA12: "🇺🇦",
  MD12: "🇲🇩",
  RO12: "🇷🇴",
  BG12: "🇧🇬",
  GR10: "🇬🇷",
  CY10: "🇨🇾",
  TR11: "🇹🇷",
  GE7: "🇬🇪",
  AM7: "🇦🇲",
  AZ7: "🇦🇿",
  IR10: "🇮🇷",
  IQ10: "🇮🇶",
  IL10: "🇮🇱",
  JO10: "🇯🇴",
  LB10: "🇱🇧",
  SY10: "🇸🇾",
  YE10: "🇾🇪",
  SA6: "🇸🇦",
  KW6: "🇰🇼",
  BH6: "🇧🇭",
  QA6: "🇶🇦",
  AE6: "🇦🇪",
  OM6: "🇴🇲",
  YE11: "🇾🇪",
  SY11: "🇸🇾",
  LB11: "🇱🇧",
  JO11: "🇯🇴",
  IL11: "🇮🇱",
  IQ11: "🇮🇶",
  IR11: "🇮🇷",
  TR12: "🇹🇷",
  CY11: "🇨🇾",
  GR11: "🇬🇷",
  BG13: "🇧🇬",
  RO13: "🇷🇴",
  MD13: "🇲🇩",
  UA13: "🇺🇦",
  RU13: "🇷🇺",
  BY13: "🇧🇾",
  LT11: "🇱🇹",
  LV11: "🇱🇻",
  EE11: "🇪🇪",
  FI12: "🇫🇮",
  SE12: "🇸🇪",
  NO12: "🇳🇴",
  DK12: "🇩🇰",
  IS11: "🇮🇸",
  IE11: "🇮🇪",
  GB12: "🇬🇧",
  PT11: "🇵🇹",
  ES13: "🇪🇸",
  FR13: "🇫🇷",
  IT13: "🇮🇹",
  CH12: "🇨🇭",
  AT11: "🇦🇹",
  DE12: "🇩🇪",
  NL12: "🇳🇱",
  BE11: "🇧🇪",
  LU11: "🇱🇺",
  FR14: "🇫🇷",
  ES14: "🇪🇸",
  PT12: "🇵🇹",
  IT14: "🇮🇹",
  CH13: "🇨🇭",
  AT12: "🇦🇹",
  DE13: "🇩🇪",
  NL13: "🇳🇱",
  BE12: "🇧🇪",
  LU12: "🇱🇺",
  GB13: "🇬🇧",
  IE12: "🇮🇪",
  IS12: "🇮🇸",
  NO13: "🇳🇴",
  SE13: "🇸🇪",
  FI13: "🇫🇮",
  DK13: "🇩🇰",
  EE12: "🇪🇪",
  LV12: "🇱🇻",
  LT12: "🇱🇹",
  BY14: "🇧🇾",
  RU14: "🇷🇺",
  UA14: "🇺🇦",
  MD14: "🇲🇩",
  RO14: "🇷🇴",
  BG14: "🇧🇬",
  GR12: "🇬🇷",
  CY12: "🇨🇾",
  TR13: "🇹🇷",
  GE8: "🇬🇪",
  AM8: "🇦🇲",
  AZ8: "🇦🇿",
  IR12: "🇮🇷",
  IQ12: "🇮🇶",
  IL12: "🇮🇱",
  JO12: "🇯🇴",
  LB12: "🇱🇧",
  SY12: "🇸🇾",
  YE12: "🇾🇪",
  SA7: "🇸🇦",
  KW7: "🇰🇼",
  BH7: "🇧🇭",
  QA7: "🇶🇦",
  AE7: "🇦🇪",
  OM7: "🇴🇲",
  YE13: "🇾🇪",
  SY13: "🇸🇾",
  LB13: "🇱🇧",
  JO13: "🇯🇴",
  IL13: "🇮🇱",
  IQ13: "🇮🇶",
  IR13: "🇮🇷",
  TR14: "🇹🇷",
  CY13: "🇨🇾",
  GR13: "🇬🇷",
  BG15: "🇧🇬",
  RO15: "🇷🇴",
  MD15: "🇲🇩",
  UA15: "🇺🇦",
  RU15: "🇷🇺",
  BY15: "🇧🇾",
  LT13: "🇱🇹",
  LV13: "🇱🇻",
  EE13: "🇪🇪",
  FI14: "🇫🇮",
  SE14: "🇸🇪",
  NO14: "🇳🇴",
  DK14: "🇩🇰",
  IS13: "🇮🇸",
  IE13: "🇮🇪",
  GB14: "🇬🇧",
  PT13: "🇵🇹",
  ES15: "🇪🇸",
  FR15: "🇫🇷",
  IT15: "🇮🇹",
  CH14: "🇨🇭",
  AT13: "🇦🇹",
  DE14: "🇩🇪",
  NL14: "🇳🇱",
  BE13: "🇧🇪",
  LU13: "🇱🇺",
  FR16: "🇫🇷",
  ES16: "🇪🇸",
  PT14: "🇵🇹",
  IT16: "🇮🇹",
  CH15: "🇨🇭",
  AT14: "🇦🇹",
  DE15: "🇩🇪",
  NL15: "🇳🇱",
  BE14: "🇧🇪",
  LU14: "🇱🇺",
  GB15: "🇬🇧",
  IE14: "🇮🇪",
  IS14: "🇮🇸",
  NO15: "🇳🇴",
  SE15: "🇸🇪",
  FI15: "🇫🇮",
  DK15: "🇩🇰",
  EE14: "🇪🇪",
  LV14: "🇱🇻",
  LT14: "🇱🇹",
  BY16: "🇧🇾",
  RU16: "🇷🇺",
  UA16: "🇺🇦",
  MD16: "🇲🇩",
  RO16: "🇷🇴",
  BG16: "🇧🇬",
  GR14: "🇬🇷",
  CY14: "🇨🇾",
  TR15: "🇹🇷",
  GE9: "🇬🇪",
  AM9: "🇦🇲",
  AZ9: "🇦🇿",
  IR14: "🇮🇷",
  IQ14: "🇮🇶",
  IL14: "🇮🇱",
  JO14: "🇯🇴",
  LB14: "🇱🇧",
  SY14: "🇸🇾",
  YE14: "🇾🇪",
  SA8: "🇸🇦",
  KW8: "🇰🇼",
  BH8: "🇧🇭",
  QA8: "🇶🇦",
  AE8: "🇦🇪",
  OM8: "🇴🇲",
  YE15: "🇾🇪",
  SY15: "🇸🇾",
  LB15: "🇱🇧",
  JO15: "🇯🇴",
  IL15: "🇮🇱",
  IQ15: "🇮🇶",
  IR15: "🇮🇷",
  TR16: "🇹🇷",
  CY15: "🇨🇾",
  GR15: "🇬🇷",
  BG17: "🇧🇬",
  RO17: "🇷🇴",
  MD17: "🇲🇩",
  UA17: "🇺🇦",
  RU17: "🇷🇺",
  BY17: "🇧🇾",
  LT15: "🇱🇹",
  LV15: "🇱🇻",
  EE15: "🇪🇪",
  FI16: "🇫🇮",
  SE16: "🇸🇪",
  NO16: "🇳🇴",
  DK16: "🇩🇰",
  IS15: "🇮🇸",
  IE15: "🇮🇪",
  GB16: "🇬🇧",
  PT15: "🇵🇹",
  ES17: "🇪🇸",
  FR17: "🇫🇷",
  IT17: "🇮🇹",
  CH16: "🇨🇭",
  AT15: "🇦🇹",
  DE16: "🇩🇪",
  NL16: "🇳🇱",
  BE15: "🇧🇪",
  LU15: "🇱🇺",
  FR18: "🇫🇷",
  ES18: "🇪🇸",
  PT16: "🇵🇹",
  IT18: "🇮🇹",
  CH17: "🇨🇭",
  AT16: "🇦🇹",
  DE17: "🇩🇪",
  NL17: "🇳🇱",
  BE16: "🇧🇪",
  LU16: "🇱🇺",
  GB17: "🇬🇧",
  IE16: "🇮🇪",
  IS16: "🇮🇸",
  NO17: "🇳🇴",
  SE17: "🇸🇪",
  FI17: "🇫🇮",
  DK17: "🇩🇰",
  EE16: "🇪🇪",
  LV16: "🇱🇻",
  LT16: "🇱🇹",
  BY18: "🇧🇾",
  RU18: "🇷🇺",
  UA18: "🇺🇦",
  MD18: "🇲🇩",
  RO18: "🇷🇴",
  BG18: "🇧🇬",
  GR16: "🇬🇷",
  CY16: "🇨🇾",
  TR17: "🇹🇷",
  GE10: "🇬🇪",
  AM10: "🇦🇲",
  AZ10: "🇦🇿",
  IR16: "🇮🇷",
  IQ16: "🇮🇶",
  IL16: "🇮🇱",
  JO16: "🇯🇴",
  LB16: "🇱🇧",
  SY16: "🇸🇾",
  YE16: "🇾🇪",
  SA9: "🇸🇦",
  KW9: "🇰🇼",
  BH9: "🇧🇭",
  QA9: "🇶🇦",
  AE9: "🇦🇪",
  OM9: "🇴🇲",
  YE17: "🇾🇪",
  SY17: "🇸🇾",
  LB17: "🇱🇧",
  JO17: "🇯🇴",
  IL17: "🇮🇱",
  IQ17: "🇮🇶",
  IR17: "🇮🇷",
  TR18: "🇹🇷",
  CY17: "🇨🇾",
  GR17: "🇬🇷",
  BG19: "🇧🇬",
  RO19: "🇷🇴",
  MD19: "🇲🇩",
  UA19: "🇺🇦",
  RU19: "🇷🇺",
  BY19: "🇧🇾",
  LT17: "🇱🇹",
  LV17: "🇱🇻",
  EE17: "🇪🇪",
  FI18: "🇫🇮",
  SE18: "🇸🇪",
  NO18: "🇳🇴",
  DK18: "🇩🇰",
  IS17: "🇮🇸",
  IE17: "🇮🇪",
  GB18: "🇬🇧",
  PT17: "🇵🇹",
  ES19: "🇪🇸",
  FR19: "🇫🇷",
  IT19: "🇮🇹",
  CH18: "🇨🇭",
  AT17: "🇦🇹",
  DE18: "🇩🇪",
  NL18: "🇳🇱",
  BE17: "🇧🇪",
  LU17: "🇱🇺",
  FR20: "🇫🇷",
  ES20: "🇪🇸",
  PT18: "🇵🇹",
  IT20: "🇮🇹",
  CH19: "🇨🇭",
  AT18: "🇦🇹",
  DE19: "🇩🇪",
  NL19: "🇳🇱",
  BE18: "🇧🇪",
  LU18: "🇱🇺",
  GB19: "🇬🇧",
  IE18: "🇮🇪",
  IS18: "🇮🇸",
  NO19: "🇳🇴",
  SE19: "🇸🇪",
  FI19: "🇫🇮",
  DK19: "🇩🇰",
  EE18: "🇪🇪",
  LV18: "🇱🇻",
  LT18: "🇱🇹",
  BY20: "🇧🇾",
  RU20: "🇷🇺",
  UA20: "🇺🇦",
  MD20: "🇲🇩",
  RO20: "🇷🇴",
  BG20: "🇧🇬",
  GR18: "🇬🇷",
  CY18: "🇨🇾",
  TR19: "🇹🇷",
  GE11: "🇬🇪",
  AM11: "🇦🇲",
  AZ11: "🇦🇿",
  IR18: "🇮🇷",
  IQ18: "🇮🇶",
  IL18: "🇮🇱",
  JO18: "🇯🇴",
  LB18: "🇱🇧",
  SY18: "🇸🇾",
  YE18: "🇾🇪",
  SA10: "🇸🇦",
  KW10: "🇰🇼",
  BH10: "🇧🇭",
  QA10: "🇶🇦",
  AE10: "🇦🇪",
  OM10: "🇴🇲",
  YE19: "🇾🇪",
  SY19: "🇸🇾",
  LB19: "🇱🇧",
  JO19: "🇯🇴",
  IL19: "🇮🇱",
  IQ19: "🇮🇶",
  IR19: "🇮🇷",
  TR20: "🇹🇷",
  CY19: "🇨🇾",
  GR19: "🇬🇷",
  BG21: "🇧🇬",
  RO21: "🇷🇴",
  MD21: "🇲🇩",
  UA21: "🇺🇦",
  RU21: "🇷🇺",
  BY21: "🇧🇾",
  LT19: "🇱🇹",
  LV19: "🇱🇻",
  EE19: "🇪🇪",
  FI20: "🇫🇮",
  SE20: "🇸🇪",
  NO20: "🇳🇴",
  DK20: "🇩🇰",
  IS19: "🇮🇸",
  IE19: "🇮🇪",
  GB20: "🇬🇧",
  PT19: "🇵🇹",
  ES21: "🇪🇸",
  FR21: "🇫🇷",
  IT21: "🇮🇹",
  CH20: "🇨🇭",
  AT19: "🇦🇹",
  DE20: "🇩🇪",
  NL20: "🇳🇱",
  BE19: "🇧🇪",
  LU19: "🇱🇺",
  FR22: "🇫🇷",
  ES22: "🇪🇸",
  PT20: "🇵🇹",
  IT22: "🇮🇹",
  CH21: "🇨🇭",
  AT20: "🇦🇹",
  DE21: "🇩🇪",
  NL21: "🇳🇱",
  BE20: "🇧🇪",
  LU20: "🇱🇺",
  GB21: "🇬🇧",
  IE20: "🇮🇪",
  IS20: "🇮🇸",
  NO21: "🇳🇴",
  SE21: "🇸🇪",
  FI21: "🇫🇮",
  DK21: "🇩🇰",
  EE20: "🇪🇪",
  LV20: "🇱🇻",
  LT20: "🇱🇹",
  BY22: "🇧🇾",
  RU22: "🇷🇺",
  UA22: "🇺🇦",
  MD22: "🇲🇩",
  RO22: "🇷🇴",
  BG22: "🇧🇬",
  GR20: "🇬🇷",
  CY20: "🇨🇾",
  TR21: "🇹🇷",
  GE12: "🇬🇪",
  AM12: "🇦🇲",
  AZ12: "🇦🇿",
  IR20: "🇮🇷",
  IQ20: "🇮🇶",
  IL20: "🇮🇱",
  JO20: "🇯🇴",
  LB20: "🇱🇧",
  SY20: "🇸🇾",
  YE20: "🇾🇪",
  SA11: "🇸🇦",
  KW11: "🇰🇼",
  BH11: "🇧🇭",
  QA11: "🇶🇦",
  AE11: "🇦🇪",
  OM11: "🇴🇲",
  YE21: "🇾🇪",
  SY21: "🇸🇾",
  LB21: "🇱🇧",
  JO21: "🇯🇴",
  IL21: "🇮🇱",
  IQ21: "🇮🇶",
  IR21: "🇮🇷",
  TR22: "🇹🇷",
  CY21: "🇨🇾",
  GR21: "🇬🇷",
  BG23: "🇧🇬",
  RO23: "🇷🇴",
  MD23: "🇲🇩",
  UA23: "🇺🇦",
  RU23: "🇷🇺",
  BY23: "🇧🇾",
  LT21: "🇱🇹",
  LV21: "🇱🇻",
  EE21: "🇪🇪",
  FI22: "🇫🇮",
  SE22: "🇸🇪",
  NO22: "🇳🇴",
  DK22: "🇩🇰",
  IS21: "🇮🇸",
  IE21: "🇮🇪",
  GB22: "🇬🇧",
  PT21: "🇵🇹",
  ES23: "🇪🇸",
  FR23: "🇫🇷",
  IT23: "🇮🇹",
  CH22: "🇨🇭",
  AT21: "🇦🇹",
  DE22: "🇩🇪",
  NL22: "🇳🇱",
  BE21: "🇧🇪",
  LU21: "🇱🇺",
  FR24: "🇫🇷",
  ES24: "🇪🇸",
  PT22: "🇵🇹",
  IT24: "🇮🇹",
  CH23: "🇨🇭",
  AT22: "🇦🇹",
  DE23: "🇩🇪",
  NL23: "🇳🇱",
  BE22: "🇧🇪",
  LU22: "🇱🇺",
  GB23: "🇬🇧",
  IE22: "🇮🇪",
  IS22: "🇮🇸",
  NO23: "🇳🇴",
  SE23: "🇸🇪",
  FI23: "🇫🇮",
  DK23: "🇩🇰",
  EE22: "🇪🇪",
  LV22: "🇱🇻",
  LT22: "🇱🇹",
  BY24: "🇧🇾",
  RU24: "🇷🇺",
  UA24: "🇺🇦",
  MD24: "🇲🇩",
  RO24: "🇷🇴",
  BG24: "🇧🇬",
  GR22: "🇬🇷",
  CY22: "🇨🇾",
  TR23: "🇹🇷",
  GE13: "🇬🇪",
  AM13: "🇦🇲",
  AZ13: "🇦🇿",
  IR22: "🇮🇷",
  IQ22: "🇮🇶",
  IL22: "🇮🇱",
  JO22: "🇯🇴",
  LB22: "🇱🇧",
  SY22: "🇸🇾",
  YE22: "🇾🇪",
  SA12: "🇸🇦",
  KW12: "🇰🇼",
  BH12: "🇧🇭",
  QA12: "🇶🇦",
  AE12: "🇦🇪",
  OM12: "🇴🇲",
  YE23: "🇾🇪",
  SY23: "🇸🇾",
  LB23: "🇱🇧",
  JO23: "🇯🇴",
  IL23: "🇮🇱",
  IQ23: "🇮🇶",
  IR23: "🇮🇷",
  TR24: "🇹🇷",
  CY23: "🇨🇾",
  GR23: "🇬🇷",
  BG25: "🇧🇬",
  RO25: "🇷🇴",
  MD25: "🇲🇩",
  UA25: "🇺🇦",
  RU25: "🇷🇺",
  BY25: "🇧🇾",
  LT23: "🇱🇹",
  LV23: "🇱🇻",
  EE23: "🇪🇪",
  FI24: "🇫🇮",
  SE24: "🇸🇪",
  NO24: "🇳🇴",
  DK24: "🇩🇰",
  IS23: "🇮🇸",
  IE23: "🇮🇪",
  GB24: "🇬🇧",
  PT23: "🇵🇹",
  ES25: "🇪🇸",
  FR25: "🇫🇷",
  IT25: "🇮🇹",
  CH24: "🇨🇭",
  AT23: "🇦🇹",
  DE24: "🇩🇪",
  NL24: "🇳🇱",
  BE23: "🇧🇪",
  LU23: "🇱🇺",
  FR26: "🇫🇷",
  ES26: "🇪🇸",
  PT24: "🇵🇹",
  IT26: "🇮🇹",
  CH25: "🇨🇭",
  AT24: "🇦🇹",
  DE25: "🇩🇪",
  NL25: "🇳🇱",
  BE24: "🇧🇪",
  LU24: "🇱🇺",
  GB25: "🇬🇧",
  IE24: "🇮🇪",
  IS24: "🇮🇸",
  NO25: "🇳🇴",
  SE25: "🇸🇪",
  FI25: "🇫🇮",
  DK25: "🇩🇰",
  EE24: "🇪🇪",
  LV24: "🇱🇻",
  LT24: "🇱🇹",
  BY26: "🇧🇾",
  RU26: "🇷🇺",
  UA26: "🇺🇦",
  MD26: "🇲🇩",
  RO26: "🇷🇴",
  BG26: "🇧🇬",
  GR24: "🇬🇷",
  CY24: "🇨🇾",
  TR25: "🇹🇷",
  GE14: "🇬🇪",
  AM14: "🇦🇲",
  AZ14: "🇦🇿",
  IR24: "🇮🇷",
  IQ24: "🇮🇶",
  IL24: "🇮🇱",
  JO24: "🇯🇴",
  LB24: "🇱🇧",
  SY24: "🇸🇾",
  YE24: "🇾🇪",
  SA13: "🇸🇦",
  KW13: "🇰🇼",
  BH13: "🇧🇭",
  QA13: "🇶🇦",
  AE13: "🇦🇪",
  OM13: "🇴🇲",
  YE25: "🇾🇪",
  SY25: "🇸🇾",
  LB25: "🇱🇧",
  JO25: "🇯🇴",
  IL25: "🇮🇱",
  IQ25: "🇮🇶",
  IR25: "🇮🇷",
  TR26: "🇹🇷",
  CY25: "🇨🇾",
  GR25: "🇬🇷",
};

function getFlag(country: string): string {
  return countryFlags[country.toUpperCase()] || "🏳️";
}

function handleMatchClick(match: KnockoutMatch) {
  emit("matchClick", match);
}
</script>

<style scoped>
.knockout-bracket {
  padding: 24px;
  background: var(--el-bg-color-page);
  border-radius: 12px;
  min-height: 500px;
  border: 1px solid var(--el-border-color-light);
}

/* 轮次标题 */
.round-headers {
  display: flex;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--el-border-color);
}

.round-header {
  width: v-bind('ROUND_WIDTH + "px"');
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.round-header:last-child {
  width: 200px;
}

/* 容器 */
.bracket-wrapper {
  overflow-x: auto;
  overflow-y: hidden;
  padding: 16px 0;
}

.bracket-wrapper::-webkit-scrollbar {
  height: 8px;
}

.bracket-wrapper::-webkit-scrollbar-track {
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.bracket-wrapper::-webkit-scrollbar-thumb {
  background: var(--el-text-color-disabled);
  border-radius: 4px;
}

.bracket-wrapper::-webkit-scrollbar-thumb:hover {
  background: var(--el-text-color-secondary);
}

.bracket-container {
  position: relative;
  min-height: 400px;
}

/* SVG 连线渐变 - 使用 CSS 变量 */
:deep(.line-gradient-start) {
  stop-color: var(--el-border-color);
  stop-opacity: 1;
}

:deep(.line-gradient-end) {
  stop-color: var(--el-border-color-dark);
  stop-opacity: 1;
}

:deep(.active-line-gradient-start) {
  stop-color: var(--el-color-success);
  stop-opacity: 0.6;
}

:deep(.active-line-gradient-end) {
  stop-color: var(--el-color-success);
  stop-opacity: 1;
}

/* SVG 连线 */
.bracket-lines {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 1;
}

.line {
  fill: none;
  stroke: url(#lineGradient);
  stroke-width: 2;
  transition: all 0.3s ease;
}

.line.active {
  stroke: url(#activeLineGradient);
  stroke-width: 2.5;
  filter: drop-shadow(0 0 3px rgba(103, 194, 58, 0.4));
}

/* 比赛卡片 */
.match-card {
  position: absolute;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.match-card:hover {
  transform: translateY(-2px);
  border-color: var(--el-color-primary);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
}

.dark .match-card:hover {
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.3);
}

.match-card.completed {
  background: var(--el-color-success-light-9);
  border-color: var(--el-color-success-light-5);
}

.match-card.bye {
  opacity: 0.75;
  background: var(--el-fill-color-light);
}

.match-card.has-winner {
  border-left: 3px solid var(--el-color-success);
}

/* 选手行 */
.player-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
  font-size: 13px;
  line-height: 20px;
  height: 28px;
  color: var(--el-text-color-primary);
  border-bottom: 1px solid var(--el-border-color-lighter);
  box-sizing: border-box;
}

.player-row:last-child {
  border-bottom: none;
}

.player-row.winner {
  font-weight: 600;
  color: var(--el-color-success-dark);
}

.dark .player-row.winner {
  color: var(--el-color-success-light-3);
}

.player-row.is-bye {
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

/* 种子号 */
.seed {
  font-size: 11px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  min-width: 18px;
  text-align: center;
  background: var(--el-fill-color);
  border-radius: 3px;
  padding: 1px 4px;
}

.seed.empty {
  background: transparent;
}

/* 国旗 */
.flag {
  font-size: 14px;
  line-height: 1;
}

/* 选手名 */
.name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 60px;
  max-width: 120px;
}

.name.empty-slot {
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

/* 比分容器 */
.scores-container {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  min-width: 80px;
}

/* 单个比分 */
.score-item {
  font-weight: 600;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  width: 22px;
  text-align: center;
  font-variant-numeric: tabular-nums;
  font-family: "Courier New", monospace;
}

.player-row.winner .score {
  color: var(--el-color-success-dark);
}

.dark .player-row.winner .score {
  color: var(--el-color-success-light-3);
}

/* 局分显示 */
.match-result {
  position: absolute;
  right: -45px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--el-color-primary);
  color: white;
  font-weight: 700;
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 4px;
  box-shadow: 0 2px 6px rgba(59, 130, 246, 0.3);
  white-space: nowrap;
}

.dark .match-result {
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.4);
}

.result-score {
  font-variant-numeric: tabular-nums;
  font-family: "Courier New", monospace;
}

/* 比赛状态指示器 */
.match-status {
  position: absolute;
  right: -6px;
  top: 50%;
  transform: translateY(-50%);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  border: 2px solid var(--el-bg-color);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.status-dot.completed {
  background: var(--el-color-success);
}

.status-dot.bye {
  background: var(--el-text-color-disabled);
}

/* 冠军卡片 */
.champion-card {
  position: absolute;
  width: 180px;
  background: linear-gradient(
    135deg,
    var(--el-color-warning-light-9) 0%,
    var(--el-color-warning-light-8) 50%,
    var(--el-color-warning-light-7) 100%
  );
  border: 2px solid var(--el-color-warning);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 10px 40px rgba(230, 162, 60, 0.3);
  z-index: 20;
  text-align: center;
}

.dark .champion-card {
  background: linear-gradient(
    135deg,
    rgba(230, 162, 60, 0.2) 0%,
    rgba(230, 162, 60, 0.3) 50%,
    rgba(230, 162, 60, 0.4) 100%
  );
  box-shadow: 0 10px 40px rgba(230, 162, 60, 0.4);
}

.champion-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(230, 162, 60, 0.3);
}

.trophy {
  font-size: 24px;
}

.champion-label {
  font-size: 14px;
  font-weight: 700;
  color: var(--el-color-warning-dark);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.dark .champion-label {
  color: var(--el-color-warning-light-3);
}

.champion-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.champion-content .flag {
  font-size: 18px;
}

.champion-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--el-color-warning-dark);
}

.dark .champion-name {
  color: var(--el-color-warning-light-3);
}

/* 图例 */
.bracket-legend {
  display: flex;
  gap: 24px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color);
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.completed {
  background: var(--el-color-success);
}

.legend-dot.pending {
  background: var(--el-fill-color);
  border: 1px solid var(--el-border-color);
}

.legend-dot.bye {
  background: var(--el-text-color-disabled);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .knockout-bracket {
    padding: 12px;
  }

  .round-header {
    font-size: 11px;
    width: 160px;
  }

  .match-card {
    padding: 6px 8px;
  }

  .player-row {
    font-size: 11px;
    padding: 3px 0;
  }

  .name {
    max-width: 80px;
  }

  .champion-card {
    width: 140px;
    padding: 12px;
  }

  .champion-name {
    font-size: 13px;
  }
}
</style>
