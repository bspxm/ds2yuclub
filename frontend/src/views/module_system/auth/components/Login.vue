<template>
  <div>
    <h3 text-center m-0 mb-20px>{{ t("login.login") }}</h3>
    <el-form
      ref="loginFormRef"
      :model="loginForm"
      :rules="loginRules"
      size="large"
      :validate-on-rule-change="false"
    >
      <!-- 用户名 -->
      <el-form-item prop="username">
        <el-input v-model.trim="loginForm.username" :placeholder="t('login.username')" clearable>
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>

      <!-- 密码 -->
      <el-tooltip :visible="isCapsLock" :content="t('login.capsLock')" placement="right">
        <el-form-item prop="password">
          <el-input
            v-model.trim="loginForm.password"
            :placeholder="t('login.password')"
            type="password"
            show-password
            clearable
            @keyup="checkCapsLock"
            @keyup.enter="handleLoginSubmit"
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-tooltip>

      <!-- 验证码 -->
      <el-form-item v-if="captchaState.enable" prop="captcha">
        <div flex items-center gap-10px class="flex-1">
          <el-input
            v-model.trim="loginForm.captcha"
            :placeholder="t('login.captchaCode')"
            clearable
            class="flex-1"
            @keyup.enter="handleLoginSubmit"
          >
            <template #prefix>
              <div class="i-svg:captcha" />
            </template>
          </el-input>
          <div cursor-pointer flex-center h-40px w-100px>
            <el-icon v-if="codeLoading" class="is-loading" size="20">
              <Loading />
            </el-icon>
            <el-image
              v-else-if="captchaState.img_base"
              border-rd-4px
              object-cover
              shadow="[0_0_0_1px_var(--el-border-color)_inset]"
              :src="captchaState.img_base"
              class="w-full h-full"
              @click="getCaptcha"
            />
            <el-text v-else type="info" size="small">点击获取验证码</el-text>
          </div>
        </div>
      </el-form-item>

      <div class="flex-x-between w-full">
        <el-checkbox v-model="loginForm.remember">{{ t("login.rememberMe") }}</el-checkbox>
        <el-link type="primary" underline="never" @click="toOtherForm('resetPwd')">
          {{ t("login.forgetPassword") }}
        </el-link>
      </div>

      <!-- 登录按钮 -->
      <el-form-item>
        <el-button :loading="loading" type="primary" class="w-full" @click="handleLoginSubmit">
          {{ t("login.login") }}
        </el-button>
      </el-form-item>
    </el-form>

    <div flex-center gap-10px>
      <el-text size="default">{{ t("login.noAccount") }}</el-text>
      <el-link type="primary" underline="never" @click="toOtherForm('register')">
        {{ t("login.reg") }}
      </el-link>
    </div>

    <!-- 第三方登录 -->
    <div class="third-party-login">
      <div class="divider-container">
        <div class="divider-line"></div>
        <span class="divider-text">{{ t("login.otherLoginMethods") }}</span>
        <div class="divider-line"></div>
      </div>
      <div class="flex-center gap-x-5 w-full text-[var(--el-text-color-secondary)]">
        <CommonWrapper>
          <div text-20px cursor-pointer class="i-svg:wechat" @click="handleWechatLogin" />
        </CommonWrapper>
        <CommonWrapper>
          <div text-20px cursor-pointer class="i-svg:qq" />
        </CommonWrapper>
        <CommonWrapper>
          <div text-20px cursor-pointer class="i-svg:github" />
        </CommonWrapper>
        <CommonWrapper>
          <div text-20px cursor-pointer class="i-svg:gitee" />
        </CommonWrapper>
      </div>
    </div>

    <!-- 微信扫码登录弹窗 -->
    <el-dialog
      v-model="wechatDialogVisible"
      title="微信扫码登录"
      width="400px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      class="wechat-login-dialog"
    >
      <div class="wechat-qrcode-container">
        <div v-if="wechatLoading" class="loading-container">
          <el-icon class="is-loading" :size="40"><Loading /></el-icon>
          <p class="loading-text">正在生成二维码...</p>
        </div>
        <div v-else-if="wechatError" class="error-container">
          <el-icon :size="40" color="var(--el-color-danger)"><CircleClose /></el-icon>
          <p class="error-text">{{ wechatError }}</p>
          <el-button type="primary" @click="handleWechatLogin">重新生成</el-button>
        </div>
        <div v-else-if="wechatSuccess" class="success-container">
          <el-icon :size="40" color="var(--el-color-success)"><CircleCheck /></el-icon>
          <p class="success-text">扫码成功，正在登录...</p>
        </div>
        <div v-else class="qrcode-container">
          <el-image
            :src="wechatQrCodeUrl"
            fit="contain"
            class="qrcode-image"
          />
          <p class="qrcode-tip">请使用微信扫描二维码登录</p>
          <p class="qrcode-expire">二维码有效期: 120秒</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="closeWechatDialog">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import type { FormInstance } from "element-plus";
import { LocationQuery, RouteLocationRaw, useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { onActivated, onMounted, onBeforeUnmount, watch } from "vue";
import AuthAPI, { type LoginFormData, type CaptchaInfo } from "@/api/module_system/auth";
import { useAppStore, useUserStore, useSettingsStore } from "@/store";
import CommonWrapper from "@/components/CommonWrapper/index.vue";

const { t } = useI18n();
const userStore = useUserStore();
const appStore = useAppStore();
const settingsStore = useSettingsStore();

// 来自父容器的预填用户名和密码
const props = defineProps<{ presetUsername?: string; presetPassword?: string }>();

const route = useRoute();
const router = useRouter();

// 组件挂载时获取验证码
onMounted(() => getCaptcha());

// 组件激活时获取验证码（适用于KeepAlive缓存的情况）
onActivated(() => {
  getCaptcha();
  // 重置登录表单
  loginForm.captcha = "";
});

// 监听路由变化，确保每次进入登录页面都有最新验证码
watch(
  () => route.fullPath,
  () => {
    getCaptcha();
    loginForm.captcha = "";
  }
);

const loginFormRef = ref<FormInstance>();
const loading = ref(false);
// 是否大写锁定
const isCapsLock = ref(false);

const loginForm = reactive<LoginFormData>({
  username: "",
  password: "",
  captcha: "",
  captcha_key: "",
  remember: true,
  login_type: "PC端",
});

// 监听父组件传入的预填信息，立即填充到登录表单
watch(
  () => [props.presetUsername, props.presetPassword],
  ([presetUsername, presetPassword]) => {
    if (typeof presetUsername === "string") {
      loginForm.username = presetUsername;
    }
    if (typeof presetPassword === "string") {
      loginForm.password = presetPassword;
    }
  },
  { immediate: true }
);

const captchaState = reactive<CaptchaInfo>({
  enable: true,
  key: "",
  img_base: "",
});

const loginRules = computed(() => {
  const rules: any = {
    username: [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.username.required"),
      },
    ],
    password: [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.password.required"),
      },
      {
        min: 6,
        message: t("login.message.password.min"),
        trigger: "blur",
      },
    ],
  };

  // 只有在验证码开启时才添加验证码验证规则
  if (captchaState.enable) {
    rules.captcha = [
      {
        required: true,
        trigger: "blur",
        message: t("login.message.captchaCode.required"),
      },
    ];
  }

  return rules;
});

// 获取验证码
const codeLoading = ref(false);
async function getCaptcha() {
  try {
    codeLoading.value = true;
    const response = await AuthAPI.getCaptcha();
    loginForm.captcha_key = response.data.data.key;
    captchaState.img_base = response.data.data.img_base;
    captchaState.enable = response.data.data.enable;
  } catch (error: any) {
    // 验证码获取失败时，默认关闭验证码功能
    console.error("获取验证码失败:", error);
    captchaState.enable = false;
    // 清空验证码相关字段，避免影响登录
    loginForm.captcha = "";
    loginForm.captcha_key = "";
  } finally {
    codeLoading.value = false;
  }
}

/**
 * 登录提交
 */
async function handleLoginSubmit() {
  try {
    // 1. 表单验证
    const valid = await loginFormRef.value?.validate();
    if (!valid) return;

    loading.value = true;

    // 2. 执行登录
    await userStore.login(loginForm);

    // 4. 登录成功，让路由守卫处理跳转逻辑
    // 解析目标地址，但不直接跳转
    const redirect = resolveRedirectTarget(route.query);

    // 通过替换当前路由触发路由守卫，让守卫处理后续的路由生成和跳转
    await router.replace(redirect);

    // 5. 记住我功能已实现，根据用户选择决定token的存储方式:
    // - 选中"记住我": token存储在localStorage中，浏览器关闭后仍然有效
    // - 未选中"记住我": token存储在sessionStorage中，浏览器关闭后失效

    // 登录成功后自动开启项目引导
    if (settingsStore.showGuide) {
      appStore.showGuide(true);
    }
  } catch (error: any) {
    if (error) {
      getCaptcha(); // 刷新验证码
    }
  } finally {
    loading.value = false;
  }
}

/**
 * 解析重定向目标
 *
 * @param query 路由查询参数
 * @returns 标准化后的路由地址
 */
function resolveRedirectTarget(query: LocationQuery): RouteLocationRaw {
  // 默认跳转路径
  const defaultPath = "/";

  // 获取原始重定向路径
  const rawRedirect = (query.redirect as string) || defaultPath;

  try {
    // 6. 使用Vue Router解析路径
    const resolved = router.resolve(rawRedirect);
    return {
      path: resolved.path,
      query: resolved.query,
    };
  } catch {
    // 7. 异常处理：返回安全路径
    return { path: defaultPath };
  }
}

// 检查输入大小写
function checkCapsLock(event: KeyboardEvent) {
  // 防止浏览器密码自动填充时报错
  if (event instanceof KeyboardEvent) {
    isCapsLock.value = event.getModifierState("CapsLock");
  }
}

const emit = defineEmits(["update:modelValue"]);
function toOtherForm(type: "register" | "resetPwd") {
  emit("update:modelValue", type);
}

// ========== 微信扫码登录相关 ==========
const wechatDialogVisible = ref(false);
const wechatLoading = ref(false);
const wechatError = ref("");
const wechatSuccess = ref(false);
const wechatQrCodeUrl = ref("");
const wechatState = ref("");
let wechatPollingTimer: number | null = null;

// 生成随机state
function generateState(): string {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

// 处理微信登录
async function handleWechatLogin() {
  try {
    wechatDialogVisible.value = true;
    wechatLoading.value = true;
    wechatError.value = "";
    wechatSuccess.value = false;
    wechatQrCodeUrl.value = "";
    wechatState.value = generateState();

    // 调用后端API生成二维码
    const response = await AuthAPI.getWechatQRCode({ state: wechatState.value });
    if (response.data && response.data.data) {
      wechatQrCodeUrl.value = response.data.data.qr_code_url;
      wechatLoading.value = false;

      // 开始轮询检查扫码状态
      startWechatPolling();
    } else {
      throw new Error("获取二维码失败");
    }
  } catch (error: any) {
    console.error("微信登录失败:", error);
    wechatLoading.value = false;
    wechatError.value = error.message || "获取二维码失败，请稍后重试";
  }
}

// 开始轮询检查扫码状态
function startWechatPolling() {
  // 清除之前的定时器
  if (wechatPollingTimer) {
    clearInterval(wechatPollingTimer);
  }

  // 每2秒检查一次扫码状态
  wechatPollingTimer = window.setInterval(async () => {
    try {
      // 这里需要后端提供检查扫码状态的API
      // 暂时使用localStorage来模拟扫码状态检查
      const scanResult = localStorage.getItem(`wechat_scan_${wechatState.value}`);
      if (scanResult) {
        // 扫码成功，执行登录
        const scanData = JSON.parse(scanResult);
        await handleWechatCallback(scanData);
      }
    } catch (error: any) {
      console.error("轮询检查扫码状态失败:", error);
    }
  }, 2000);

  // 120秒后停止轮询
  setTimeout(() => {
    if (wechatPollingTimer) {
      clearInterval(wechatPollingTimer);
      wechatPollingTimer = null;
      if (!wechatSuccess.value && !wechatError.value) {
        wechatError.value = "二维码已过期，请重新扫描";
        wechatQrCodeUrl.value = "";
      }
    }
  }, 120000);
}

// 处理微信回调
async function handleWechatCallback(scanData: any) {
  try {
    wechatSuccess.value = true;

    // 停止轮询
    if (wechatPollingTimer) {
      clearInterval(wechatPollingTimer);
      wechatPollingTimer = null;
    }

    // 执行微信登录
    await userStore.wechatLogin({
      openid: scanData.openid,
      unionid: scanData.unionid,
      nickname: scanData.nickname,
      headimgurl: scanData.headimgurl,
      login_type: "微信登录"
    });

    // 关闭弹窗
    closeWechatDialog();

    // 登录成功，跳转到首页
    await router.replace("/");

    // 显示成功提示
    ElMessage.success("微信登录成功");

    // 登录成功后自动开启项目引导
    if (settingsStore.showGuide) {
      appStore.showGuide(true);
    }
  } catch (error: any) {
    console.error("微信登录回调处理失败:", error);
    wechatSuccess.value = false;
    wechatError.value = error.message || "微信登录失败，请稍后重试";
  }
}

// 关闭微信登录弹窗
function closeWechatDialog() {
  wechatDialogVisible.value = false;
  wechatLoading.value = false;
  wechatError.value = "";
  wechatSuccess.value = false;
  wechatQrCodeUrl.value = "";

  // 停止轮询
  if (wechatPollingTimer) {
    clearInterval(wechatPollingTimer);
    wechatPollingTimer = null;
  }

  // 清除localStorage中的扫码状态
  if (wechatState.value) {
    localStorage.removeItem(`wechat_scan_${wechatState.value}`);
  }
}

// 组件卸载时清理定时器
onBeforeUnmount(() => {
  if (wechatPollingTimer) {
    clearInterval(wechatPollingTimer);
    wechatPollingTimer = null;
  }
});
</script>

<style lang="scss" scoped>
.third-party-login {
  .divider-container {
    display: flex;
    align-items: center;
    margin: 20px 0;

    .divider-line {
      flex: 1;
      height: 1px;
      background: linear-gradient(to right, transparent, var(--el-border-color-light), transparent);
    }

    .divider-text {
      padding: 0 16px;
      font-size: 12px;
      color: var(--el-text-color-regular);
      white-space: nowrap;
    }
  }
}
</style>
