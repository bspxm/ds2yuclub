<template>
  <div class="auth-view" :style="{ '--login-background-url': `url(${loginBackgroundUrl})` }">
    <div class="auth-view__toolbar">
      <el-tooltip :content="t('login.themeToggle')" placement="bottom">
        <CommonWrapper>
          <ThemeSwitch />
        </CommonWrapper>
      </el-tooltip>
      <el-tooltip :content="t('login.languageToggle')" placement="bottom">
        <CommonWrapper>
          <LangSelect size="text-20px" />
        </CommonWrapper>
      </el-tooltip>
    </div>

    <div class="mobile-header">
      <div class="mobile-header__shuttle">
        <svg viewBox="0 0 64 80" fill="none">
          <path
            d="M20 60 L32 8 L44 60"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
            opacity="0.7"
          />
          <line
            x1="32"
            y1="8"
            x2="32"
            y2="65"
            stroke="currentColor"
            stroke-width="1.5"
            opacity="0.55"
          />
          <line
            x1="24"
            y1="30"
            x2="28"
            y2="60"
            stroke="currentColor"
            stroke-width="0.8"
            opacity="0.35"
          />
          <line
            x1="40"
            y1="30"
            x2="36"
            y2="60"
            stroke="currentColor"
            stroke-width="0.8"
            opacity="0.35"
          />
          <path
            d="M22 42 Q32 47, 42 42"
            stroke="currentColor"
            stroke-width="0.8"
            fill="none"
            opacity="0.3"
          />
          <path
            d="M21 52 Q32 57, 43 52"
            stroke="currentColor"
            stroke-width="0.8"
            fill="none"
            opacity="0.3"
          />
          <ellipse cx="32" cy="68" rx="8" ry="5.5" fill="currentColor" opacity="0.7" />
          <path d="M25.5 65 Q25.5 76, 32 76 Q38.5 76, 38.5 65" fill="currentColor" opacity="0.55" />
        </svg>
      </div>
      <h1 class="mobile-header__title">DS2YU Club</h1>
      <p class="mobile-header__tagline">挥拍之间，掌控全场</p>
    </div>

    <div class="auth-view__wrapper">
      <section class="auth-feature">
        <div class="auth-feature__shuttle">
          <svg viewBox="0 0 120 160" fill="none">
            <path
              d="M38 116 L60 16 L82 116"
              stroke="currentColor"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
              opacity="0.6"
            />
            <line
              x1="60"
              y1="16"
              x2="60"
              y2="125"
              stroke="currentColor"
              stroke-width="2"
              opacity="0.45"
            />
            <line
              x1="44"
              y1="55"
              x2="52"
              y2="116"
              stroke="currentColor"
              stroke-width="1"
              opacity="0.3"
            />
            <line
              x1="76"
              y1="55"
              x2="68"
              y2="116"
              stroke="currentColor"
              stroke-width="1"
              opacity="0.3"
            />
            <line
              x1="34"
              y1="70"
              x2="44"
              y2="116"
              stroke="currentColor"
              stroke-width="0.8"
              opacity="0.25"
            />
            <line
              x1="86"
              y1="70"
              x2="76"
              y2="116"
              stroke="currentColor"
              stroke-width="0.8"
              opacity="0.25"
            />
            <path
              d="M22 50 Q60 30, 98 50"
              stroke="currentColor"
              stroke-width="1.2"
              fill="none"
              opacity="0.2"
            />
            <path
              d="M24 72 Q60 80, 96 72"
              stroke="currentColor"
              stroke-width="1"
              fill="none"
              opacity="0.25"
            />
            <path
              d="M28 94 Q60 102, 92 94"
              stroke="currentColor"
              stroke-width="1"
              fill="none"
              opacity="0.25"
            />
            <ellipse cx="60" cy="134" rx="16" ry="10" fill="currentColor" opacity="0.65" />
            <path d="M47 126 Q47 148, 60 148 Q73 148, 73 126" fill="currentColor" opacity="0.5" />
          </svg>
        </div>

        <div class="auth-feature__lines" aria-hidden="true">
          <div class="court-line court-line--h1" />
          <div class="court-line court-line--h2" />
          <div class="court-line court-line--h3" />
          <div class="court-line court-line--v" />
        </div>

        <svg class="auth-feature__arc" viewBox="0 0 400 200" fill="none" preserveAspectRatio="none">
          <path
            d="M0 180 Q200 0, 400 180"
            stroke="currentColor"
            stroke-width="1"
            opacity="0.12"
            stroke-linecap="round"
          />
        </svg>

        <div class="auth-feature__text">
          <h2 class="auth-feature__tagline">挥拍之间，掌控全场</h2>
          <p class="auth-feature__brand">DS2YU Club</p>
        </div>
      </section>

      <section class="auth-panel">
        <div class="auth-panel__brand">
          <div class="auth-panel__logo-wrap">
            <el-image
              :src="configStore.configData?.sys_web_logo?.config_value || ''"
              class="auth-panel__logo"
            />
          </div>
          <div class="auth-panel__meta">
            <div class="auth-panel__title-row">
              <span class="auth-panel__title">
                {{ configStore.configData?.sys_web_title?.config_value || "" }}
              </span>
              <el-tooltip
                :content="configStore.configData?.sys_web_description?.config_value || ''"
                placement="bottom"
              >
                <el-icon class="cursor-help"><QuestionFilled /></el-icon>
              </el-tooltip>
            </div>
            <div class="auth-panel__version-row">
              <span class="auth-panel__version-label">Version</span>
              <span class="auth-panel__version-pill">
                v{{ configStore.configData?.sys_web_version?.config_value || "" }}
              </span>
            </div>
          </div>
        </div>

        <transition name="fade-slide" mode="out-in">
          <component
            :is="formComponents[component]"
            v-model="component"
            v-model:preset-username="loginPreset.username"
            v-model:preset-password="loginPreset.password"
            class="auth-panel__form"
          />
        </transition>

        <footer class="auth-panel__footer">
          <el-text size="small">
            <a :href="configStore.configData?.sys_git_code?.config_value || ''" target="_blank">
              {{ configStore.configData?.sys_web_copyright?.config_value || "" }}
            </a>
            |
            <a :href="configStore.configData?.sys_help_doc?.config_value || ''" target="_blank">
              帮助
            </a>
            |
            <a :href="configStore.configData?.sys_web_privacy?.config_value || ''" target="_blank">
              隐私
            </a>
            |
            <a :href="configStore.configData?.sys_web_clause?.config_value || ''" target="_blank">
              条款
            </a>
            {{ configStore.configData?.sys_keep_record?.config_value || "" }}
          </el-text>
        </footer>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import CommonWrapper from "@/components/CommonWrapper/index.vue";
import ThemeSwitch from "@/components/ThemeSwitch/index.vue";
import { useConfigStore } from "@/store";

const configStore = useConfigStore();

const loginBackgroundUrl = computed(() => {
  return (
    configStore.configData?.sys_login_background?.config_value ||
    new URL("@/assets/images/login-bg.svg", import.meta.url).href
  );
});

type LayoutMap = "login" | "register" | "resetPwd";

const t = useI18n().t;

const component = ref<LayoutMap>("login");
const formComponents = {
  login: defineAsyncComponent(() => import("./components/Login.vue")),
  register: defineAsyncComponent(() => import("./components/Register.vue")),
  resetPwd: defineAsyncComponent(() => import("./components/ResetPwd.vue")),
};

const loginPreset = reactive<{ username: string; password: string }>({
  username: "admin",
  password: "123456",
});

configStore.getConfig();
</script>

<style lang="scss">
@import url("https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;600;700&family=Barlow:wght@300;400;500;600;700&display=swap");
</style>

<style lang="scss" scoped>
.auth-view {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #f0f7f0 0%, #e8f5e9 40%, #c8e6c9 100%);

  &::before {
    position: fixed;
    inset: 0;
    z-index: -1;
    content: "";
    opacity: 0.4;
    background: var(--login-background-url) center/cover no-repeat;
  }

  @media (prefers-color-scheme: dark) {
    background: linear-gradient(135deg, #0a1f0a 0%, #0d2b0d 40%, #143814 100%);
  }
}

html.dark .auth-view {
  background: linear-gradient(135deg, #0a1f0a 0%, #0d2b0d 40%, #143814 100%);
}

/* ===================== Toolbar ===================== */

.auth-view__toolbar {
  position: fixed;
  top: 16px;
  right: 20px;
  z-index: 20;
  display: inline-flex;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(27, 94, 32, 0.15);
  border-radius: 999px;
  box-shadow: 0 6px 20px rgba(27, 94, 32, 0.12);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;

  &:hover {
    box-shadow: 0 10px 30px rgba(27, 94, 32, 0.18);
    transform: translateY(-2px);
  }

  @media (prefers-color-scheme: dark) {
    background: rgba(15, 30, 15, 0.9);
    border-color: rgba(76, 175, 80, 0.3);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
  }
}

html.dark .auth-view__toolbar {
  background: rgba(15, 30, 15, 0.9);
  border-color: rgba(76, 175, 80, 0.3);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
}

/* ===================== Mobile Header ===================== */

.mobile-header {
  display: none;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px 32px;
  margin-top: 40px;
  text-align: center;
}

.mobile-header__shuttle {
  width: 56px;
  height: 70px;
  margin-bottom: 12px;
  color: rgba(255, 255, 255, 0.9);
  animation: shuttleFloat 3s ease-in-out infinite;
  filter: drop-shadow(0 4px 12px rgba(27, 94, 32, 0.3));
}

.mobile-header__title {
  margin: 0;
  font-family: "Barlow Condensed", sans-serif;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.1;
  color: rgba(255, 255, 255, 0.95);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.mobile-header__tagline {
  margin: 6px 0 0;
  font-family: "Barlow Condensed", sans-serif;
  font-size: 15px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
  letter-spacing: 0.1em;
}

/* ===================== Wrapper ===================== */

.auth-view__wrapper {
  display: grid;
  flex: 1;
  grid-template-columns: 1fr minmax(360px, 520px);
  gap: 0;
  align-items: center;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* ===================== Desktop Feature ===================== */

.auth-feature {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
  overflow: hidden;
}

.auth-feature__shuttle {
  width: 180px;
  height: 240px;
  margin-bottom: 24px;
  color: rgba(27, 94, 32, 0.25);
  animation: shuttleFloat 3.5s ease-in-out infinite;
  filter: drop-shadow(0 8px 24px rgba(27, 94, 32, 0.15));

  @media (prefers-color-scheme: dark) {
    color: rgba(76, 175, 80, 0.2);
  }
}

html.dark .auth-feature__shuttle {
  color: rgba(76, 175, 80, 0.2);
}

.auth-feature__lines {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.court-line {
  position: absolute;
  background: rgba(27, 94, 32, 0.1);
  animation: courtPulse 4s ease-in-out infinite;

  @media (prefers-color-scheme: dark) {
    background: rgba(76, 175, 80, 0.08);
  }
}

html.dark .court-line {
  background: rgba(76, 175, 80, 0.08);
}

.court-line--h1 {
  top: 22%;
  left: 10%;
  width: 80%;
  height: 2px;
  border-radius: 1px;
  animation-delay: 0s;
}

.court-line--h2 {
  top: 45%;
  left: 10%;
  width: 80%;
  height: 1.5px;
  border-radius: 1px;
  animation-delay: 1s;
}

.court-line--h3 {
  top: 68%;
  left: 10%;
  width: 80%;
  height: 2px;
  border-radius: 1px;
  animation-delay: 2s;
}

.court-line--v {
  top: 15%;
  left: 50%;
  width: 1.5px;
  height: 70%;
  border-radius: 1px;
  animation-delay: 0.5s;
  transform: translateX(-50%);
}

.auth-feature__arc {
  position: absolute;
  bottom: 30%;
  left: 5%;
  width: 90%;
  height: 120px;
  color: rgba(27, 94, 32, 0.15);

  @media (prefers-color-scheme: dark) {
    color: rgba(76, 175, 80, 0.1);
  }
}

html.dark .auth-feature__arc {
  color: rgba(76, 175, 80, 0.1);
}

.auth-feature__text {
  position: relative;
  z-index: 1;
  text-align: center;
}

.auth-feature__tagline {
  margin: 0;
  font-family: "Barlow Condensed", sans-serif;
  font-size: clamp(28px, 4vw, 42px);
  font-weight: 700;
  line-height: 1.1;
  color: #1b5e20;
  text-transform: uppercase;
  letter-spacing: 0.08em;

  @media (prefers-color-scheme: dark) {
    color: #a5d6a7;
  }
}

html.dark .auth-feature__tagline {
  color: #a5d6a7;
}

.auth-feature__brand {
  margin: 8px 0 0;
  font-family: "Barlow", sans-serif;
  font-size: 15px;
  font-weight: 400;
  color: rgba(27, 94, 32, 0.55);
  letter-spacing: 0.15em;

  @media (prefers-color-scheme: dark) {
    color: rgba(165, 214, 167, 0.5);
  }
}

html.dark .auth-feature__brand {
  color: rgba(165, 214, 167, 0.5);
}

/* ===================== Auth Panel ===================== */

.auth-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  justify-content: flex-start;
  width: 100%;
  max-width: 480px;
  padding: clamp(1.5rem, 2.5vw, 2.5rem);
  margin: 24px 0;
  margin-left: auto;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(27, 94, 32, 0.1);
  border-radius: 20px;
  box-shadow:
    0 12px 40px rgba(27, 94, 32, 0.1),
    0 2px 8px rgba(27, 94, 32, 0.06),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset;
  backdrop-filter: blur(16px);
  animation: panelLift 0.7s ease;

  @media (prefers-color-scheme: dark) {
    background: rgba(15, 30, 15, 0.9);
    border-color: rgba(76, 175, 80, 0.2);
    box-shadow:
      0 16px 48px rgba(0, 0, 0, 0.5),
      0 0 0 1px rgba(76, 175, 80, 0.1) inset;
  }
}

html.dark .auth-panel {
  background: rgba(15, 30, 15, 0.9);
  border-color: rgba(76, 175, 80, 0.2);
  box-shadow:
    0 16px 48px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(76, 175, 80, 0.1) inset;
}

.auth-panel__brand {
  display: flex;
  gap: 0.85rem;
  align-items: center;
  padding-bottom: 0.75rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid rgba(27, 94, 32, 0.08);

  @media (prefers-color-scheme: dark) {
    border-color: rgba(76, 175, 80, 0.12);
  }
}

html.dark .auth-panel__brand {
  border-color: rgba(76, 175, 80, 0.12);
}

.auth-panel__logo-wrap {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: radial-gradient(circle at 30% 20%, #e8f5e9, #c8e6c9);
  border-radius: 14px;
  box-shadow:
    0 4px 12px rgba(27, 94, 32, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.8) inset;

  @media (prefers-color-scheme: dark) {
    background: radial-gradient(circle at 30% 20%, #1b3d1b, #0f2a0f);
    box-shadow:
      0 4px 12px rgba(0, 0, 0, 0.5),
      0 0 0 1px rgba(76, 175, 80, 0.25) inset;
  }
}

html.dark .auth-panel__logo-wrap {
  background: radial-gradient(circle at 30% 20%, #1b3d1b, #0f2a0f);
  box-shadow:
    0 4px 12px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(76, 175, 80, 0.25) inset;
}

.auth-panel__logo {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
}

.auth-panel__meta {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 0.3rem;
  min-width: 0;
}

.auth-panel__title-row {
  display: flex;
  gap: 0.4rem;
  align-items: baseline;
}

.auth-panel__title {
  overflow: hidden;
  font-size: 1.1rem;
  font-weight: 650;
  line-height: 1.3;
  color: #1b5e20;
  text-overflow: ellipsis;
  white-space: nowrap;

  @media (prefers-color-scheme: dark) {
    color: #a5d6a7;
  }
}

html.dark .auth-panel__title {
  color: #a5d6a7;
}

.auth-panel__version-row {
  display: inline-flex;
  gap: 0.4rem;
  align-items: center;
  font-size: 0.75rem;
}

.auth-panel__version-label {
  color: var(--el-text-color-placeholder);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.auth-panel__version-pill {
  padding: 0.08rem 0.5rem;
  font-weight: 500;
  color: #1b5e20;
  background: linear-gradient(135deg, rgba(27, 94, 32, 0.1), rgba(76, 175, 80, 0.15));
  border: 1px solid rgba(27, 94, 32, 0.15);
  border-radius: 999px;

  @media (prefers-color-scheme: dark) {
    color: #81c784;
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.15), rgba(129, 199, 132, 0.1));
    border-color: rgba(76, 175, 80, 0.25);
  }
}

html.dark .auth-panel__version-pill {
  color: #81c784;
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.15), rgba(129, 199, 132, 0.1));
  border-color: rgba(76, 175, 80, 0.25);
}

.auth-panel__form {
  width: 100%;
  max-width: 100%;
  margin-inline: auto;

  :deep(.el-form-item) {
    margin-bottom: 1.1rem;
  }

  :deep(.el-input__wrapper) {
    box-shadow: 0 0 0 1px var(--el-border-color) inset;
    transition: all 0.25s ease;

    &:hover {
      box-shadow: 0 0 0 1px var(--el-border-color-hover) inset;
    }

    &.is-focus {
      box-shadow: 0 0 0 1.5px #1b5e20 inset;
    }
  }

  :deep(.el-button--primary) {
    background: linear-gradient(135deg, #1b5e20, #2e7d32);
    border: none;

    &:hover {
      background: linear-gradient(135deg, #2e7d32, #388e3c);
    }
  }

  :deep(.el-card) {
    background: transparent;
    box-shadow: none;
  }
}

.auth-panel__footer {
  padding-top: 0.75rem;
  margin-top: 0.25rem;
  font-size: 0.85rem;
  text-align: center;
  border-top: 1px solid rgba(27, 94, 32, 0.06);

  a {
    margin-left: 0.1rem;
    color: var(--el-text-color-regular);
    text-decoration: none;
    transition: color 0.2s ease;

    &:hover {
      color: #1b5e20;
    }
  }

  @media (prefers-color-scheme: dark) {
    border-color: rgba(76, 175, 80, 0.1);

    a {
      color: rgba(165, 214, 167, 0.7);

      &:hover {
        color: rgba(165, 214, 167, 1);
      }
    }
  }
}

html.dark .auth-panel__footer {
  border-color: rgba(76, 175, 80, 0.1);

  a {
    color: rgba(165, 214, 167, 0.7);

    &:hover {
      color: rgba(165, 214, 167, 1);
    }
  }
}

/* ===================== Responsive ===================== */

@media (max-width: 768px) {
  .auth-view {
    background: linear-gradient(180deg, #1b5e20 0%, #2e7d32 40%, #f0f7f0 40%, #f0f7f0 100%);

    @media (prefers-color-scheme: dark) {
      background: linear-gradient(180deg, #0a1f0a 0%, #0d2b0d 40%, #0d2b0d 40%, #0d2b0d 100%);
    }
  }

  html.dark .auth-view {
    background: linear-gradient(180deg, #0a1f0a 0%, #0d2b0d 40%, #0d2b0d 40%, #0d2b0d 100%);
  }

  .auth-view__toolbar {
    top: 10px;
    right: 12px;
    padding: 0.35rem 0.6rem;
  }

  .mobile-header {
    display: flex;
  }

  .auth-view__wrapper {
    display: block;
    padding: 0 12px 24px;
  }

  .auth-feature {
    display: none;
  }

  .auth-panel {
    max-width: 100%;
    padding: 1.25rem 1rem;
    margin: 0;
    border-radius: 16px;
    box-shadow:
      0 8px 24px rgba(27, 94, 32, 0.18),
      0 0 0 1px rgba(255, 255, 255, 0.5) inset;

    @media (prefers-color-scheme: dark) {
      box-shadow:
        0 8px 24px rgba(0, 0, 0, 0.5),
        0 0 0 1px rgba(76, 175, 80, 0.1) inset;
    }
  }

  html.dark .auth-panel {
    box-shadow:
      0 8px 24px rgba(0, 0, 0, 0.5),
      0 0 0 1px rgba(76, 175, 80, 0.1) inset;
  }
}

/* ===================== Animations ===================== */

@keyframes shuttleFloat {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes courtPulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.35;
  }
}

@keyframes panelLift {
  from {
    opacity: 0;
    transform: translateY(24px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(-40px) scale(0.95);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(40px) scale(0.95);
}

.fade-slide-enter-to,
.fade-slide-leave-from {
  opacity: 1;
  transform: translateX(0) scale(1);
}
</style>
