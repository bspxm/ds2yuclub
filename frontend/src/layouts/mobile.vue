<template>
  <div class="mobile-layout">
    <van-nav-bar :title="title" left-arrow fixed placeholder @click-left="onBack" />
    <div class="mobile-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const title = computed(() => (route.meta?.title as string) || "");

function onBack() {
  router.back();
}
</script>

<style scoped>
.mobile-layout {
  min-height: 100vh;
  background: #f5f5f5;
}

.mobile-content {
  padding: 12px 16px;
  padding-bottom: calc(12px + env(safe-area-inset-bottom));
}
</style>
