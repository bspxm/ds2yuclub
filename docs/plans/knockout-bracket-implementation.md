# 单败制淘汰赛实施计划

## 目标
根据 `docs/小组单败制淘汰.png` 创建单败制淘汰赛可视化，与现有小组赛分离为独立模块。

## 图片分析
从图片可以看出：
1. **树形结构** - 从1/32赛 → 1/16赛 → 1/8赛 → 1/4赛 → 半决赛 → 决赛 → 冠军
2. **连线方式** - 胜者进入右侧下一轮，败者淘汰
3. **每场比赛** - 显示选手名、国籍国旗、种子排名、详细比分
4. **轮次递进** - 每轮比赛数减半，直到决赛

## 数据结构

### 淘汰赛对阵树
```typescript
interface KnockoutMatch {
  id: number;
  round: string;           // "1/32", "1/16", "1/8", "1/4", "semi", "final", "champion"
  round_number: number;    // 1, 2, 3, 4, 5, 6, 7
  match_number: number;    // 在当前轮次中的序号
  position: number;        // 在树中的位置（用于连线）
  
  player1: {
    id: number;
    name: string;
    seed?: number;
    country?: string;
    is_winner: boolean;
  } | null;
  
  player2: {
    id: number;
    name: string;
    seed?: number;
    country?: string;
    is_winner: boolean;
  } | null;
  
  scores?: string;         // "21-15, 25-23"
  winner_id?: number;
  status: "scheduled" | "completed" | "bye";
  
  // 树形关系
  prev_match1_id?: number; // 左上游比赛
  prev_match2_id?: number; // 右上游比赛
  next_match_id?: number;   // 下游比赛（胜者进入）
}
```

### API 响应
```typescript
interface KnockoutData {
  tournament_id: number;
  total_rounds: number;      // 总轮数（根据参赛人数决定）
  matches: KnockoutMatch[]; // 所有比赛
  current_round: string;    // 当前进行到的轮次
  is_completed: boolean;
}
```

## 实施步骤

### 步骤1：后端API (30分钟)
- [ ] 创建 `GET /tournament/{id}/knockout` API
- [ ] 返回淘汰赛对阵树数据
- [ ] 实现从小组赛晋级的逻辑

### 步骤2：前端组件 (60分钟)
- [ ] 创建 `KnockoutBracketView.vue`
- [ ] 实现树形布局（CSS Grid或绝对定位）
- [ ] 实现比赛卡片组件
- [ ] 实现轮次标题和连线

### 步骤3：视图切换 (20分钟)
- [ ] 修改赛事管理页面
- [ ] 根据 `tournament_type` 显示不同视图：
  - `ROUND_ROBIN` / `PURE_GROUP` → 小组赛视图
  - `SINGLE_ELIMINATION` → 单败淘汰赛视图

### 步骤4：晋级逻辑 (30分钟)
- [ ] 录入比分后自动更新下一轮对阵
- [ ] 胜者自动进入右侧比赛
- [ ] 处理轮空（bye）情况

## 组件设计

### KnockoutBracketView.vue
```vue
<template>
  <div class="knockout-bracket">
    <!-- 轮次标题 -->
    <div class="round-headers">
      <div v-for="round in rounds" :key="round" class="round-header">
        {{ getRoundLabel(round) }}
      </div>
    </div>
    
    <!-- 对阵树 -->
    <div class="bracket-container">
      <div 
        v-for="match in matches" 
        :key="match.id"
        class="match-card"
        :style="getMatchPosition(match)"
        @click="handleMatchClick(match)"
      >
        <!-- 选手1 -->
        <div class="player" :class="{ winner: match.player1?.is_winner }">
          <span class="seed">{{ match.player1?.seed }}</span>
          <span class="name">{{ match.player1?.name }}</span>
          <span v-if="match.player1?.is_winner" class="winner-mark">✓</span>
        </div>
        
        <!-- 比分 -->
        <div class="scores" v-if="match.scores">
          {{ match.scores }}
        </div>
        
        <!-- 选手2 -->
        <div class="player" :class="{ winner: match.player2?.is_winner }">
          <span class="seed">{{ match.player2?.seed }}</span>
          <span class="name">{{ match.player2?.name }}</span>
          <span v-if="match.player2?.is_winner" class="winner-mark">✓</span>
        </div>
      </div>
      
      <!-- SVG 连线 -->
      <svg class="bracket-lines">
        <path v-for="line in lines" :key="line.id" :d="line.path" />
      </svg>
    </div>
  </div>
</template>
```

### CSS 布局策略
使用 CSS Grid 的灵活布局：
```css
.bracket-container {
  display: grid;
  grid-template-columns: repeat(7, 200px); /* 7轮比赛 */
  grid-template-rows: repeat(32, 60px);   /* 最多32场比赛 */
  gap: 20px;
}

.match-card {
  /* 根据 round 和 position 设置 grid-area */
}
```

## 后端API设计

### GET /tournament/{id}/knockout
返回单败淘汰赛数据

### POST /tournament/{id}/knockout/generate
生成单败淘汰赛对阵表

### PUT /tournament/{id}/knockout/matches/{match_id}/score
录入单败淘汰赛比分

## 数据库变更
可能需要添加：
- `knockout_matches` 表 或扩展现有 `tournament_match`
- `next_match_id` 字段用于建立树形关系
- `round_type` 区分小组赛和淘汰赛

## 依赖
- 无新增依赖
- 复用现有比分录入组件
- 复用现有服务层逻辑

## 测试
- [ ] 4人单败淘汰赛
- [ ] 8人单败淘汰赛  
- [ ] 16人单败淘汰赛
- [ ] 从小组赛晋级到单败淘汰赛
- [ ] 比分录入后自动晋级

---

**预计总时间：2-3小时**
**优先级：高**
