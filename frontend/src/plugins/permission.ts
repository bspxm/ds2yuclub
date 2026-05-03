import type { NavigationGuardNext, RouteLocationNormalized, RouteRecordRaw } from "vue-router";
import NProgress from "@/utils/nprogress";
import { Auth } from "@/utils/auth";
import router from "@/router";
import { usePermissionStore, useUserStore } from "@/store";

export function setupPermission() {
  const whiteList = ["/login"];

  router.beforeEach(async (to, from, next) => {
    NProgress.start();

    try {
      const isLoggedIn = Auth.isLoggedIn();

      if (isLoggedIn) {
        if (to.path === "/login") {
          next({ path: "/" });
          return;
        }
        await handleAuthenticatedUser(to, from, next);
      } else {
        if (whiteList.includes(to.path)) {
          next();
        } else {
          next(`/login?redirect=${encodeURIComponent(to.fullPath)}`);
          NProgress.done();
        }
      }
    } catch (error) {
      console.error("Route guard error:", error);
      await useUserStore().resetAllState();
      next("/login");
      NProgress.done();
    }
  });

  router.afterEach(() => {
    NProgress.done();
  });
}

async function handleAuthenticatedUser(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) {
  const permissionStore = usePermissionStore();
  const userStore = useUserStore();

  try {
    if (!permissionStore.isRouteGenerated) {
      if (!userStore.basicInfo?.roles?.length) {
        await userStore.getUserInfo();
      }

      const dynamicRoutes = await permissionStore.generateRoutes();
      dynamicRoutes.forEach((route: RouteRecordRaw) => {
        if (!route.path?.startsWith("/m/")) {
          router.addRoute(route);
        }
      });

      next({ ...to, replace: true });
      return;
    }

    if (to.matched.length === 0) {
      next("/404");
      return;
    }

    const isSuper = !!userStore.basicInfo?.is_superuser;
    const roles = userStore.basicInfo?.roles || [];
    const roleCodes = roles.map((r: any) => r.code);
    const isParent = roleCodes.includes("PARENTS");

    if (to.path === "/" || to.path === "/home") {
      if (isSuper) {
        next();
        return;
      }
      const target = isParent ? "/m/badminton/parent/student" : "/m/badminton/coach/home";
      next(target);
      return;
    }

    if (to.path.startsWith("/m/")) {
      if (isSuper) {
        next("/home");
        return;
      }
      if (to.path.startsWith("/m/badminton/parent/") && !isParent) {
        next("/m/badminton/coach/home");
        return;
      }
    }

    const title = (to.params.title as string) || (to.query.title as string);
    if (title) {
      to.meta.title = title;
    }

    next();
  } catch (error) {
    console.error("❌ Route guard error:", error);
    await useUserStore().resetAllState();
    next("/login");
    NProgress.done();
  }
  router.afterEach(() => {
    NProgress.done();
  });
}
