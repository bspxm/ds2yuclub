import { ThemeMode } from "@/enums";

const STORAGE_KEY = "theme";

function resolveDark(mode: ThemeMode): boolean {
  if (mode === ThemeMode.DARK) return true;
  if (mode === ThemeMode.LIGHT) return false;
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

export function useMobileTheme() {
  const mode = useStorage<ThemeMode>(STORAGE_KEY, ThemeMode.AUTO);
  const isSystemDark = useMediaQuery("(prefers-color-scheme: dark)");

  const isDark = computed(() => {
    if (mode.value === ThemeMode.LIGHT) return false;
    if (mode.value === ThemeMode.DARK) return true;
    return isSystemDark.value;
  });

  const isAuto = computed(() => mode.value === ThemeMode.AUTO);

  function applyHtmlClass() {
    if (isDark.value) {
      document.documentElement.classList.add(ThemeMode.DARK);
    } else {
      document.documentElement.classList.remove(ThemeMode.DARK);
    }
  }

  watch(isDark, applyHtmlClass, { immediate: true });

  function setMode(newMode: ThemeMode) {
    mode.value = newMode;
  }

  function toggle() {
    if (mode.value === ThemeMode.AUTO) {
      mode.value = ThemeMode.LIGHT;
    } else if (mode.value === ThemeMode.LIGHT) {
      mode.value = ThemeMode.DARK;
    } else {
      mode.value = ThemeMode.AUTO;
    }
  }

  return {
    mode: readonly(mode),
    isDark: readonly(isDark),
    isAuto: readonly(isAuto),
    setMode,
    toggle,
  };
}
