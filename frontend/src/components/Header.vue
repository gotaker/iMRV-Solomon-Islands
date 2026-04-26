<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

defineProps({
  // When true, the nav floats over the page content (Home hero handles its own clearance).
  // Default: render a spacer so legacy pages don't slip under the fixed nav.
  overlap: { type: Boolean, default: false },
})

const route = useRoute()
const navScrolled = ref(false)
const mobileOpen = ref(false)

const onScroll = () => {
  navScrolled.value = window.scrollY > 40
}

const toggleMobile = () => {
  mobileOpen.value = !mobileOpen.value
}
const closeMobile = () => {
  mobileOpen.value = false
}

// Close the panel on route change so navigation feels natural.
watch(
  () => route.path,
  () => {
    mobileOpen.value = false
  },
)

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})

const isActive = (path) => route.path === path
</script>

<template>
  <header class="ed-nav" :class="{ scrolled: navScrolled }">
    <router-link to="/home" class="ed-logo">iMRV / SOLOMONS</router-link>
    <nav class="ed-pill" aria-label="Primary">
      <router-link to="/home" :class="{ active: isActive('/home') }"
        >Index</router-link
      >
      <router-link to="/project" :class="{ active: isActive('/project') }"
        >Programs</router-link
      >
      <router-link to="/reports" :class="{ active: isActive('/reports') }"
        >Ledger</router-link
      >
      <router-link
        to="/climate-change-division"
        :class="{ active: isActive('/climate-change-division') }"
        >Division</router-link
      >
      <router-link to="/new" :class="{ active: isActive('/new') }"
        >Field Notes</router-link
      >
    </nav>
    <a href="/login" class="ed-cart">
      <span>Login</span>
      <span class="ed-cart-count">→</span>
    </a>
    <button
      type="button"
      class="ed-burger"
      :aria-expanded="mobileOpen"
      aria-controls="ed-mobile-panel"
      aria-label="Open menu"
      @click="toggleMobile"
    >
      <span></span>
      <span></span>
      <span></span>
    </button>
  </header>

  <transition name="ed-mobile">
    <aside
      v-if="mobileOpen"
      id="ed-mobile-panel"
      class="ed-mobile-panel"
      role="dialog"
      aria-modal="true"
      aria-label="Site navigation"
    >
      <button
        type="button"
        class="ed-mobile-close"
        aria-label="Close menu"
        @click="closeMobile"
      >
        <span aria-hidden="true">×</span>
      </button>
      <nav class="ed-mobile-nav" aria-label="Mobile primary">
        <router-link to="/home" @click="closeMobile">Index</router-link>
        <router-link to="/project" @click="closeMobile">Programs</router-link>
        <router-link to="/reports" @click="closeMobile">Ledger</router-link>
        <router-link to="/climate-change-division" @click="closeMobile"
          >Division</router-link
        >
        <router-link to="/new" @click="closeMobile">Field Notes</router-link>
        <a href="/login" class="ed-mobile-login" @click="closeMobile"
          >Login →</a
        >
      </nav>
    </aside>
  </transition>

  <div v-if="!overlap" class="ed-nav-spacer" aria-hidden="true"></div>
</template>

<style scoped>
.ed-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem 2rem;
  font-family: 'Inter', system-ui, sans-serif;
  transition: padding 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.ed-nav.scrolled {
  padding: 1rem 2rem;
}
.ed-nav-spacer {
  height: 5.5rem;
}

.ed-logo {
  font-weight: 700;
  font-size: 13px;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: #01472e;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}
.ed-logo::before {
  content: '—';
  font-family: 'Anton', 'Helvetica Neue', sans-serif;
  font-size: 18px;
  line-height: 1;
  transform: translateY(-1px);
}

.ed-pill {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px) saturate(140%);
  -webkit-backdrop-filter: blur(20px) saturate(140%);
  border: 1px solid rgba(1, 71, 46, 0.08);
  border-radius: 999px;
}
.ed-pill a {
  padding: 0.65rem 1.15rem;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: #01472e;
  text-decoration: none;
  border-radius: 999px;
  transition:
    background 0.4s cubic-bezier(0.16, 1, 0.3, 1),
    color 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.ed-pill a:hover {
  background: #01472e;
  color: #fefae0;
}
.ed-pill a.active {
  background: #01472e;
  color: #fefae0;
}
.ed-pill a:focus-visible {
  outline: 2px solid #01472e;
  outline-offset: 4px;
}

.ed-cart {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px) saturate(140%);
  -webkit-backdrop-filter: blur(20px) saturate(140%);
  border: 1px solid rgba(1, 71, 46, 0.08);
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: #01472e;
  text-decoration: none;
  transition: background 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.ed-cart:hover {
  background: rgba(255, 255, 255, 0.9);
}
.ed-cart:focus-visible {
  outline: 2px solid #01472e;
  outline-offset: 4px;
}
.ed-cart-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  background: white;
  color: #01472e;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0;
}

/* Hamburger — desktop hidden, shown ≤900px */
.ed-burger {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  width: 44px;
  height: 44px;
  padding: 10px 8px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px) saturate(140%);
  -webkit-backdrop-filter: blur(20px) saturate(140%);
  border: 1px solid rgba(1, 71, 46, 0.08);
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.ed-burger span {
  display: block;
  width: 100%;
  height: 2px;
  background: #01472e;
  border-radius: 2px;
}
.ed-burger:focus-visible {
  outline: 2px solid #01472e;
  outline-offset: 4px;
}

/* Full-viewport mobile panel */
.ed-mobile-panel {
  position: fixed;
  inset: 0;
  z-index: 250;
  background: #01472e;
  color: #fefae0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 2rem 1.5rem;
  transition:
    opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
.ed-mobile-close {
  position: absolute;
  top: 1.25rem;
  right: 1.25rem;
  width: 44px;
  height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(254, 250, 224, 0.3);
  border-radius: 999px;
  color: #fefae0;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
}
.ed-mobile-close:focus-visible {
  outline: 2px solid #fefae0;
  outline-offset: 4px;
}
.ed-mobile-nav {
  margin-top: 5rem;
  display: flex;
  flex-direction: column;
}
.ed-mobile-nav a {
  display: block;
  width: 100%;
  padding: 1.5rem 0.5rem;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: #fefae0;
  text-decoration: none;
  border-bottom: 1px solid rgba(254, 250, 224, 0.15);
}
.ed-mobile-nav a:focus-visible {
  outline: 2px solid #fefae0;
  outline-offset: 4px;
}
.ed-mobile-login {
  margin-top: 1.5rem;
  border-bottom: none !important;
  color: #ccd5ae !important;
}

/* Slide/fade transition for the mobile panel */
.ed-mobile-enter-from,
.ed-mobile-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}
.ed-mobile-enter-active,
.ed-mobile-leave-active {
  transition:
    opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@media (max-width: 900px) {
  .ed-pill {
    display: none;
  }
  .ed-nav {
    padding: 1rem 1.25rem;
  }
  .ed-nav-spacer {
    height: 4.5rem;
  }
  .ed-burger {
    display: flex;
  }
  .ed-cart {
    padding: 0.95rem 1.25rem;
    min-height: 44px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .ed-nav,
  .ed-pill a,
  .ed-cart,
  .ed-mobile-panel,
  .ed-burger {
    transition: none !important;
    animation: none !important;
  }
}
</style>
