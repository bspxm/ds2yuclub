# 羽毛球主题登录页重构实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `frontend/src/views/module_system/auth/index.vue` 登录页重构为羽毛球竞技运动风格，桌面/移动自适应。

**Architecture:** 单文件重构，不改动登录表单子组件（Login/Register/ResetPwd.vue）。桌面端左右布局（左侧羽毛球装饰区 + 右侧表单卡片），移动端上下布局（顶部绿色装饰区 + 底部表单卡片）。使用 CSS @import 加载 Google Fonts，内联 SVG 羽球装饰。

**Tech Stack:** Vue 3 + Composition API + `<script setup lang="ts">` + SCSS + Element Plus

**Files:**
- Modify: `frontend/src/views/module_system/auth/index.vue` (全部重写，保持 script 逻辑不变)

---

### Task 1: 重写 index.vue

**File:** Modify: `frontend/src/views/module_system/auth/index.vue`

- [ ] **Step 1: 重写 template**

保留：
- toolbar 区域（ThemeSwitch + LangSelect）
- 动态表单组件 `<component :is="formComponents[component]" />`
- footer 版权区域
- script 中所有逻辑（configStore, component switching, notification 等）

重写布局：
- 桌面端：左侧 `auth-feature` 显示羽球 SVG + 球场线条 + 标语，右侧 `auth-panel` 显示表单
- 移动端：顶部深绿渐变区显示羽球图标 + 品牌名 + 标语，下方白色卡片显示表单

- [ ] **Step 2: 添加字体加载**

在 style 区域顶部添加 Google Fonts @import：
```scss
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700&family=Barlow:wght@300;400;500;600;700&display=swap');
```

- [ ] **Step 3: 重写全部样式**

删除原有样式，替换为新的羽毛球主题样式：
- 球场深绿 `#1B5E20` 主色调
- 金色 `#F5A623` 强调色
- 白色毛玻璃卡片
- 羽球浮动动画、线条脉冲光效
- 响应式：768px 断点切换布局
- 暗色模式兼容

- [ ] **Step 4: 运行 lint 检查**

```bash
pnpm run lint
```

确认无 lint 错误。

- [ ] **Step 5: 运行 ts:check**

```bash
pnpm run ts:check
```

确认无类型错误。

- [ ] **Step 6: 运行 build**

```bash
pnpm build
```

确认构建成功。
