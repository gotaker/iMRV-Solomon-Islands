<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import axios from 'axios'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import ProjectComponent from '@/components/ProjectComponent.vue'

const data = ref({})

const fetchData = async () => {
  try {
    const response = await axios.get(
      '/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all',
    )
    if (response.status === 200) {
      data.value = response.data
      // v-if elements gated on data are inserted now — observe them
      // so the reveal animation actually fires.
      await nextTick()
      if (io) {
        document.querySelectorAll('[data-reveal]').forEach((el) => io.observe(el))
      }
    } else {
      throw new Error('Network response was not ok')
    }
  } catch (error) {
    console.error('Error fetching Projects content:', error)
  }
}

/* ----- intersection-observer reveals ----- */
let io = null

onMounted(() => {
  fetchData()

  io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('is-revealed')
          io.unobserve(e.target)
        }
      })
    },
    { threshold: 0.12, rootMargin: '0px 0px -60px 0px' },
  )
  requestAnimationFrame(() => {
    document.querySelectorAll('[data-reveal]').forEach((el) => io.observe(el))
  })
})

onUnmounted(() => {
  if (io) io.disconnect()
})
</script>

<template>
  <div class="editorial">
    <Header />

    <!-- ========== INTRO (Cream) ========== -->
    <section class="intro">
      <span class="eyebrow" data-reveal>(Index 00) Portfolio</span>
      <div class="intro-head">
        <h1 class="display" data-reveal>
          Climate<br />
          <em>Projects.</em>
        </h1>
        <p class="intro-lede" data-reveal data-reveal-delay="2">
          Every adaptation, mitigation, and resilience project tracked from
          proposal through verified outcome.
        </p>
      </div>
    </section>

    <!-- ========== ALL PROJECTS (Olive) ========== -->
    <section class="projects-section">
      <span class="eyebrow" data-reveal>(Index 01) All Projects</span>
      <ProjectComponent :data="data" />
    </section>

    <!-- ========== STATS (Sage) ========== -->
    <section class="stats-section">
      <span class="eyebrow" data-reveal>(Index 02) Overview</span>
      <h2 class="section-title" data-reveal>
        By the<br />
        Numbers
      </h2>

      <div class="stats-grid">
        <article class="stat-card" data-reveal data-reveal-delay="1">
          <span class="stat-num">01</span>
          <h3 class="stat-label">Adaptation</h3>
          <p class="stat-body">
            Site-level resilience programs across coastal and agricultural
            sectors
          </p>
        </article>
        <article class="stat-card" data-reveal data-reveal-delay="2">
          <span class="stat-num">02</span>
          <h3 class="stat-label">Mitigation</h3>
          <p class="stat-body">
            Forest, energy and waste sector emission reduction projects
          </p>
        </article>
        <article class="stat-card" data-reveal data-reveal-delay="3">
          <span class="stat-num">03</span>
          <h3 class="stat-label">Finance</h3>
          <p class="stat-body">
            Climate finance flows tracked from commitment to disbursement
          </p>
        </article>
      </div>
    </section>

    <!-- ========== CTA (Forest) ========== -->
    <section class="cta-section">
      <span class="eyebrow eyebrow-light" data-reveal>(Index 03) Explore</span>
      <h2 class="cta-title" data-reveal>
        The<br />
        <em>Platform.</em>
      </h2>
      <div class="cta-body">
        <p data-reveal data-reveal-delay="1">
          iMRV brings every climate commitment made by the Solomon Islands into
          a single transparent ledger — from field-level adaptation work to
          national greenhouse gas reporting. Every figure is sourced. Every
          project, traceable.
        </p>
        <router-link
          to="/about"
          class="cta-pill"
          data-reveal
          data-reveal-delay="2"
        >
          <span>Learn<br />about<br />the platform →</span>
        </router-link>
      </div>
    </section>

    <Footer :data="data" />
  </div>
</template>

<style scoped>
.editorial {
  --forest: #01472e;
  --sage: #ccd5ae;
  --olive: #e9edc9;
  --cream: #fefae0;
  --moss: #a3b18a;
  --forest-shadow: rgba(1, 71, 46, 0.2);
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
  --display: 'Anton', 'Helvetica Neue', sans-serif;
  --body: 'Inter', system-ui, sans-serif;

  font-family: var(--body);
  color: var(--forest);
  background: var(--cream);
  min-height: 100vh;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

.editorial h1,
.editorial h2,
.editorial h3,
.editorial p {
  margin: 0;
  padding: 0;
}

/* ---------- shared eyebrow ---------- */
.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1.25rem;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  color: var(--forest);
}
.eyebrow::before {
  content: '';
  width: 28px;
  height: 1px;
  background: var(--forest);
}
.eyebrow-light {
  color: var(--cream);
}
.eyebrow-light::before {
  background: var(--cream);
}

.section-title {
  font-family: var(--display);
  font-size: clamp(4rem, 12vw, 12rem);
  line-height: 0.85;
  letter-spacing: -0.04em;
  color: var(--forest);
  text-transform: uppercase;
  margin-bottom: 4rem;
  font-weight: 400;
}

/* ---------- intro (cream) ---------- */
.intro {
  position: relative;
  background: var(--cream);
  padding: 4rem 2rem 7rem;
}
.intro-head {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 4rem;
  align-items: end;
}
.display {
  font-family: var(--display);
  font-size: clamp(4rem, 12vw, 12rem);
  line-height: 0.85;
  letter-spacing: -0.05em;
  color: var(--forest);
  text-transform: uppercase;
  font-weight: 400;
}
.display em {
  font-style: normal;
  color: var(--moss);
}
.intro-lede {
  font-size: 16px;
  line-height: 1.6;
  max-width: 60ch;
  color: var(--forest);
  padding-bottom: 1.5rem;
}

/* ---------- projects (olive) ---------- */
.projects-section {
  position: relative;
  background: var(--olive);
  padding: 7rem 0 8rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 5;
}
/* Eyebrow inside this section needs horizontal padding to align with the page */
.projects-section > .eyebrow {
  margin-left: 2rem;
}

/* ---------- stats (sage) ---------- */
.stats-section {
  position: relative;
  background: var(--sage);
  padding: 7rem 2rem 8rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 6;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem 2.5rem;
}
.stat-card {
  background: var(--cream);
  border-radius: 2.5rem;
  padding: 2.5rem;
  box-shadow: 0 25px 60px -25px var(--forest-shadow);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.stat-num {
  font-family: var(--display);
  font-size: 2.5rem;
  line-height: 1;
  letter-spacing: -0.02em;
  color: var(--forest);
  opacity: 0.55;
}
.stat-label {
  font-family: var(--display);
  font-size: clamp(2rem, 3.2vw, 2.8rem);
  line-height: 0.95;
  letter-spacing: -0.02em;
  color: var(--forest);
  text-transform: uppercase;
  font-weight: 400;
}
.stat-body {
  font-size: 14px;
  line-height: 1.6;
  max-width: 50ch;
  color: var(--forest);
}

/* ---------- cta (forest) ---------- */
.cta-section {
  position: relative;
  background: var(--forest);
  color: var(--cream);
  padding: 7rem 2rem 9rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 7;
  overflow: hidden;
}
.cta-section::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse at 80% 0%,
    rgba(204, 213, 174, 0.1),
    transparent 55%
  );
  pointer-events: none;
}
.cta-title {
  position: relative;
  font-family: var(--display);
  font-size: clamp(4rem, 12vw, 12rem);
  line-height: 0.85;
  letter-spacing: -0.05em;
  color: var(--cream);
  text-transform: uppercase;
  font-weight: 400;
  margin-bottom: 3.5rem;
}
.cta-title em {
  font-style: normal;
  color: var(--sage);
}
.cta-body {
  position: relative;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 4rem;
  align-items: end;
}
.cta-body p {
  max-width: 60ch;
  font-size: 16px;
  line-height: 1.6;
  color: var(--cream);
}
.cta-pill {
  flex: 0 0 auto;
  width: 11rem;
  height: 11rem;
  border-radius: 999px;
  background: var(--cream);
  color: var(--forest);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-decoration: none;
  text-transform: uppercase;
  line-height: 1.4;
  box-shadow: 0 20px 50px -15px rgba(0, 0, 0, 0.35);
  transition:
    transform 0.6s var(--ease),
    background 0.4s var(--ease);
}
.cta-pill:hover {
  transform: rotate(-12deg) scale(1.05);
  background: white;
}
.cta-pill span {
  padding: 0 1.2rem;
}

/* ---------- reveal ---------- */
[data-reveal] {
  opacity: 0;
  transform: translateY(100px);
  transition:
    opacity 1.2s var(--ease),
    transform 1.2s var(--ease);
}
[data-reveal].is-revealed {
  opacity: 1;
  transform: translateY(0);
}
[data-reveal-delay='1'] {
  transition-delay: 0.1s;
}
[data-reveal-delay='2'] {
  transition-delay: 0.2s;
}
[data-reveal-delay='3'] {
  transition-delay: 0.3s;
}
[data-reveal-delay='4'] {
  transition-delay: 0.4s;
}

@media (max-width: 900px) {
  .intro-head {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .cta-body {
    grid-template-columns: 1fr;
    gap: 2.5rem;
    align-items: start;
  }
  .cta-pill {
    width: 8rem;
    height: 8rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  [data-reveal],
  .cta-pill {
    animation: none !important;
    transition: none !important;
    opacity: 1 !important;
    transform: none !important;
  }
}
</style>
