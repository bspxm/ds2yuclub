<template>
  <van-config-provider :theme="isDark ? 'dark' : 'light'">
    <div class="mobile-layout">
      <van-nav-bar :title="title" :left-arrow="!isHome" fixed placeholder @click-left="onBack">
        <template #right>
          <van-icon
            :name="themeIcon"
            size="20"
            class="theme-toggle"
            @click="showThemePopover = !showThemePopover"
          />
        </template>
      </van-nav-bar>

      <van-popover
        v-model:show="showThemePopover"
        :actions="themeActions"
        placement="bottom-end"
        teleport="body"
        @select="onThemeSelect"
      >
        <template #reference>
          <div />
        </template>
      </van-popover>

      <div class="mobile-content">
        <router-view />
      </div>
    </div>
  </van-config-provider>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ThemeMode } from "@/enums";
import { useMobileTheme } from "@/composables/useMobileTheme";
import "@/styles/mobile-theme.css";

const route = useRoute();
const router = useRouter();

const { isDark, mode, setMode } = useMobileTheme();
const showThemePopover = ref(false);

const title = computed(() => (route.meta?.title as string) || "");
const isHome = computed(() => route.path === "/m/badminton/coach/home");

const themeIcon = computed(() => {
  if (mode.value === ThemeMode.AUTO) return "replay";
  if (isDark.value) return "circle";
  return "circle";
});

const themeActions = computed(() => [
  { text: "跟随系统", icon: "replay", mode: ThemeMode.AUTO },
  { text: "深色模式", icon: "circle", mode: ThemeMode.DARK },
  { text: "浅色模式", icon: "circle", mode: ThemeMode.LIGHT },
]);

function onThemeSelect(action: { mode: ThemeMode }) {
  setMode(action.mode);
  showThemePopover.value = false;
}

function onBack() {
  router.back();
}
</script>

<style scoped>
.mobile-layout {
  min-height: 100vh;
  background: var(--mobile-bg);
  transition: background 0.3s;
}

.mobile-content {
  padding: 12px 16px;
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
}

.theme-toggle {
  cursor: pointer;
}
</style>
