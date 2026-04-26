<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { createResource } from 'frappe-ui'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import hero1 from '@/assets/images/editorial/hero-1.jpg'
import hero2 from '@/assets/images/editorial/hero-2.jpg'
import hero3 from '@/assets/images/editorial/hero-3.jpg'
import imgCoastal from '@/assets/images/editorial/program-coastal.jpg'
import imgForest from '@/assets/images/editorial/program-forest.jpg'
import imgReef from '@/assets/images/editorial/program-reef.jpg'

/* ----- staggered hero text ----- */
const heroLetters = [...'iMRV']

/* ----- fallback demo content (used when Frappe data is empty/unavailable) ----- */
const fallbackPrograms = [
  {
    num: '01',
    title: ['Coastal', 'Adaptation'],
    metaTop: '14 Sites',
    metaBottom: 'SBD 12.4M',
    img: imgCoastal,
    alt: 'Coastal mangroves',
  },
  {
    num: '02',
    title: ['Forest', 'Mitigation'],
    metaTop: '9 Provinces',
    metaBottom: '−18.2 ktCO₂e',
    img: imgForest,
    alt: 'Forest canopy',
  },
  {
    num: '03',
    title: ['Reef', 'Inventory'],
    metaTop: '228 Reports',
    metaBottom: 'Q1 — 2026',
    img: imgReef,
    alt: 'Coral reef',
  },
]

const fallbackStats = [
  { num: '42', sup: '+', label: 'Verified Projects' },
  { num: '9', sup: '/9', label: 'Provinces Reporting' },
  {
    num: 'SBD',
    sup: '',
    sub: '84.6',
    subSup: 'M',
    label: 'Climate Finance Tracked',
  },
  { num: '−12', sup: '%', label: 'Sectoral Emissions YoY' },
]

/**
 * Editorial home content fetched from the MrvFrontend Single doctype.
 *
 * Endpoint: mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all
 * Response shape (relevant slices):
 *   {
 *     message: {
 *       parent_data: {
 *         editorial_programs: [
 *           { num, title, metaTop, metaBottom, img, alt }, ...
 *         ],
 *         editorial_stats: [
 *           { num, sup, label, sub?, subSup? }, ...
 *         ],
 *       }
 *     }
 *   }
 *
 * Field names on the Frappe child rows MUST match the keys above —
 * the template iterates `programs`/`stats` and reads these keys directly.
 * If either child table is missing or empty, the page falls back to the
 * static demo arrays defined above so the editorial layout never blanks.
 */
const homeResource = createResource({
  url: 'mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all',
  cache: 'editorial-home',
  auto: true,
})

const programs = computed(() =>
  homeResource.data?.message?.parent_data?.editorial_programs?.length
    ? homeResource.data.message.parent_data.editorial_programs
    : fallbackPrograms,
)
const stats = computed(() =>
  homeResource.data?.message?.parent_data?.editorial_stats?.length
    ? homeResource.data.message.parent_data.editorial_stats
    : fallbackStats,
)

/* ----- intersection-observer reveals + parallax floats ----- */
let io = null
const baseTransforms = new WeakMap()
let ticking = false

const onScrollParallax = () => {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  if (ticking) return
  ticking = true
  requestAnimationFrame(() => {
    const y = window.scrollY
    document.querySelectorAll('[data-parallax]').forEach((el) => {
      const speed = parseFloat(el.dataset.parallax) || 0.05
      const base = baseTransforms.get(el) || ''
      el.style.transform = `${base} translate3d(0, ${-y * speed}px, 0)`
    })
    ticking = false
  })
}

onMounted(() => {
  document.querySelectorAll('[data-parallax]').forEach((el) => {
    const cs = getComputedStyle(el)
    baseTransforms.set(el, cs.transform === 'none' ? '' : cs.transform)
  })

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
  document.querySelectorAll('[data-reveal]').forEach((el) => io.observe(el))

  window.addEventListener('scroll', onScrollParallax, { passive: true })
})

onUnmounted(() => {
  if (io) io.disconnect()
  window.removeEventListener('scroll', onScrollParallax)
})
</script>

<template>
  <div class="editorial">
    <!-- nav floats over the sage hero — overlap=true skips the flow spacer -->
    <Header :overlap="true" />

    <!-- ========== HERO ========== -->
    <section class="hero">
      <div class="hero-meta">
        <span><i class="dot"></i>Live · Verified Ledger 2026</span>
        <span>Honiara · 9°S 159°E</span>
      </div>

      <div class="hero-display">
        <h1 class="hero-text" aria-label="iMRV">
          <span
            v-for="(ch, i) in heroLetters"
            :key="i"
            aria-hidden="true"
            :style="{ animationDelay: 0.15 + i * 0.05 + 's' }"
            >{{ ch }}</span
          >
        </h1>
      </div>

      <figure class="float float-1" data-parallax="0.06" aria-hidden="true">
        <div class="float-inner">
          <img :src="hero1" alt="" fetchpriority="high" />
        </div>
      </figure>
      <figure class="float float-2" data-parallax="0.09" aria-hidden="true">
        <div class="float-inner">
          <img :src="hero2" alt="" />
        </div>
      </figure>
      <figure class="float float-3" data-parallax="0.04" aria-hidden="true">
        <div class="float-inner">
          <img :src="hero3" alt="" />
        </div>
      </figure>

      <div class="hero-bottom">
        <div class="hero-blurb" data-reveal>
          <p>
            An open accountability platform for climate action across the
            Solomon Islands — tracking adaptation programs, mitigation projects
            and finance flows from the field to the registry.
          </p>
          <p>Every commitment, traceable. Every figure, sourced.</p>
        </div>
        <div class="hero-scroll" data-reveal data-reveal-delay="2">Scroll</div>
        <div class="hero-origin" data-reveal data-reveal-delay="3">
          Issue Nº 04 — Wet Season<br />
          <span class="accent">Climate Change Division</span><br />
          MECDM · Government of SI<br />
          © 2026
        </div>
      </div>
    </section>

    <!-- ========== PROGRAMS ========== -->
    <section class="programs" id="programs">
      <span class="programs-tag" data-reveal
        >(Index 01) Active Initiatives</span
      >
      <div class="programs-head">
        <h2 class="programs-title" data-reveal>Programs</h2>
        <router-link
          to="/project"
          class="programs-cta"
          data-reveal
          data-reveal-delay="2"
        >
          <span>View<br />the<br />full ledger →</span>
        </router-link>
      </div>

      <div class="grid">
        <article
          v-for="(p, i) in programs"
          :key="p.num"
          class="card"
          data-reveal
          :data-reveal-delay="i + 1"
        >
          <a href="#" class="card-link">
            <div class="card-img">
              <span class="card-num">{{ p.num }}</span>
              <img :src="p.img" :alt="p.alt" loading="lazy" />
              <div class="card-overlay">
                <span class="quick-add" aria-hidden="true">Open Brief →</span>
              </div>
            </div>
            <div class="card-info">
              <h3 class="card-title">
                <template v-for="(line, idx) in p.title" :key="idx">
                  {{ line }}<br v-if="idx < p.title.length - 1" />
                </template>
              </h3>
              <div class="card-meta">
                {{ p.metaTop }}<br />
                <b>{{ p.metaBottom }}</b>
              </div>
            </div>
          </a>
        </article>
      </div>
    </section>

    <!-- ========== LEDGER ========== -->
    <section class="ledger" id="ledger">
      <div class="ledger-inner">
        <h2 class="ledger-quote" data-reveal>
          We measure what we mean to <em>protect.</em>
        </h2>
        <div class="stats">
          <div
            v-for="(s, i) in stats"
            :key="i"
            class="stat"
            data-reveal
            :data-reveal-delay="i + 1"
          >
            <div class="num">
              <template v-if="s.sub">
                {{ s.num }}<br />{{ s.sub }}<small>{{ s.subSup }}</small>
              </template>
              <template v-else>
                {{ s.num }}<small>{{ s.sup }}</small>
              </template>
            </div>
            <div class="label">{{ s.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <Footer :data="homeResource.data" mega-text="Climate Change Division" />
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

.editorial img {
  display: block;
  max-width: 100%;
}
.editorial button {
  font: inherit;
  color: inherit;
  background: none;
  border: 0;
  cursor: pointer;
  padding: 0;
}
.editorial h1,
.editorial h2,
.editorial h3,
.editorial p {
  margin: 0;
  padding: 0;
}

/* ---------- hero ---------- */
.hero {
  position: relative;
  min-height: 100vh;
  background: var(--sage);
  padding: 9rem 2rem 8rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse at 30% 20%,
    rgba(254, 250, 224, 0.4),
    transparent 60%
  );
  pointer-events: none;
}
.hero-meta {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  color: var(--forest);
  z-index: 3;
}
.hero-meta .dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  background: var(--forest);
  border-radius: 999px;
  margin-right: 0.7rem;
  transform: translateY(-1px);
  animation: pulse 2.4s var(--ease) infinite;
}
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
    transform: translateY(-1px) scale(1);
  }
  50% {
    opacity: 0.4;
    transform: translateY(-1px) scale(0.85);
  }
}
.hero-display {
  position: relative;
  text-align: center;
  z-index: 2;
  pointer-events: none;
}
.hero-text {
  font-family: var(--display);
  font-size: 23vw;
  line-height: 0.75;
  letter-spacing: -0.05em;
  color: var(--forest);
  text-transform: uppercase;
  display: block;
}
.hero-text span {
  display: inline-block;
  opacity: 0;
  transform: translateY(100px);
  will-change: transform, opacity;
  animation: letterReveal 1.2s var(--ease) forwards;
}
@keyframes letterReveal {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* floating images */
.float {
  position: absolute;
  border-radius: 3rem;
  overflow: hidden;
  box-shadow: 0 30px 80px -20px var(--forest-shadow);
  z-index: 3;
  will-change: transform;
}
.float .float-inner {
  width: 100%;
  height: 100%;
  animation: floatY 7s ease-in-out infinite;
  will-change: transform;
}
.float img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
@keyframes floatY {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(5deg);
  }
}
.float-1 {
  top: 22%;
  left: 4%;
  width: 14vw;
  height: 18vw;
  min-width: 140px;
  min-height: 180px;
  transform: rotate(-8deg);
}
.float-1 .float-inner {
  animation-duration: 8s;
  animation-delay: -2s;
}
.float-2 {
  top: 28%;
  right: 5%;
  width: 13vw;
  height: 17vw;
  min-width: 130px;
  min-height: 170px;
  transform: rotate(11deg);
}
.float-2 .float-inner {
  animation-duration: 6.5s;
  animation-delay: -4s;
}
.float-3 {
  bottom: 18%;
  left: 38%;
  width: 11vw;
  height: 14vw;
  min-width: 110px;
  min-height: 145px;
  transform: rotate(-4deg);
  z-index: 1;
}
.float-3 .float-inner {
  animation-duration: 9s;
  animation-delay: -1s;
}

.hero-bottom {
  position: relative;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 4rem;
  align-items: end;
  z-index: 4;
}
.hero-blurb {
  max-width: 30ch;
  font-size: 13px;
  line-height: 1.5;
  color: var(--forest);
}
.hero-blurb p + p {
  margin-top: 0.75rem;
}
.hero-origin {
  text-align: right;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  color: var(--forest);
  line-height: 1.9;
  max-width: 30ch;
  margin-left: auto;
}
.hero-origin .accent {
  opacity: 0.5;
}
.hero-scroll {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  margin: 0 auto;
  padding-bottom: 0.5rem;
  opacity: 0.7;
}
.hero-scroll::after {
  content: '';
  display: block;
  width: 1px;
  height: 40px;
  background: var(--forest);
  margin: 0.75rem auto 0;
  transform-origin: top;
  animation: scrollLine 2.4s var(--ease) infinite;
}
@keyframes scrollLine {
  0% {
    transform: scaleY(0);
  }
  50% {
    transform: scaleY(1);
  }
  100% {
    transform: scaleY(0);
    transform-origin: bottom;
  }
}

/* ---------- programs ---------- */
.programs {
  position: relative;
  background: var(--olive);
  padding: 7rem 2rem 8rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 5;
}
.programs-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 3rem;
  margin-bottom: 5rem;
}
.programs-title {
  font-family: var(--display);
  font-size: 15vw;
  line-height: 0.8;
  letter-spacing: -0.04em;
  color: var(--forest);
  text-transform: uppercase;
  flex: 1;
}
.programs-cta {
  flex: 0 0 auto;
  width: 11rem;
  height: 11rem;
  border-radius: 999px;
  background: var(--forest);
  color: var(--cream);
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
  box-shadow: 0 20px 50px -15px var(--forest-shadow);
  transition:
    transform 0.6s var(--ease),
    background 0.4s var(--ease);
}
.programs-cta:hover {
  transform: rotate(-12deg) scale(1.05);
  background: #022e1d;
}
.programs-cta span {
  padding: 0 1.2rem;
}
.programs-tag {
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
.programs-tag::before {
  content: '';
  width: 28px;
  height: 1px;
  background: var(--forest);
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}
.card {
  display: block;
}
.card-link {
  display: block;
  color: inherit;
  text-decoration: none;
}
.card-link:focus {
  outline: none;
}
.card-link:focus-visible {
  outline: 2px solid var(--forest);
  outline-offset: 4px;
  border-radius: 2.5rem;
}
.card-img {
  position: relative;
  overflow: hidden;
  aspect-ratio: 4/5;
  border-radius: 2.5rem;
  background: var(--moss);
  box-shadow: 0 25px 60px -25px var(--forest-shadow);
}
.card-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 1s var(--ease);
}
.card:hover .card-img img,
.card:focus-within .card-img img {
  transform: scale(1.1);
}
.card-num {
  position: absolute;
  top: 1.5rem;
  left: 1.75rem;
  z-index: 3;
  font-family: var(--display);
  font-size: 28px;
  line-height: 1;
  color: var(--cream);
  mix-blend-mode: difference;
  letter-spacing: -0.02em;
}
.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(1, 71, 46, 0.3);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  opacity: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 2rem;
  transition: opacity 0.7s var(--ease);
  z-index: 2;
}
.card:hover .card-overlay,
.card:focus-within .card-overlay {
  opacity: 1;
}
.quick-add {
  background: var(--cream);
  color: var(--forest);
  padding: 1.1rem 2.2rem;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.35em;
  text-transform: uppercase;
  transform: translateY(32px);
  transition:
    transform 0.7s var(--ease),
    background 0.4s var(--ease);
  box-shadow: 0 12px 30px -10px rgba(0, 0, 0, 0.25);
}
.card:hover .quick-add,
.card:focus-within .quick-add {
  transform: translateY(0);
}
.quick-add {
  display: inline-block;
  text-decoration: none;
}
.quick-add:hover {
  background: white;
}
.card-info {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1.5rem 0.5rem 0;
}
.card-title {
  font-family: var(--display);
  font-size: clamp(1.5rem, 2.5vw, 2.4rem);
  line-height: 0.95;
  letter-spacing: -0.02em;
  color: var(--forest);
  text-transform: uppercase;
}
.card-meta {
  text-align: right;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--forest);
  opacity: 0.7;
  line-height: 1.7;
  flex-shrink: 0;
}
.card-meta b {
  display: block;
  opacity: 1;
  font-family: var(--display);
  font-size: 18px;
  letter-spacing: 0;
  margin-top: 4px;
}

/* ---------- ledger ---------- */
.ledger {
  position: relative;
  background: var(--cream);
  padding: 8rem 2rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 6;
}
.ledger-inner {
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 5rem;
  align-items: center;
}
.ledger-quote {
  font-family: var(--display);
  font-size: clamp(2.5rem, 5vw, 5rem);
  line-height: 0.95;
  letter-spacing: -0.03em;
  color: var(--forest);
  text-transform: uppercase;
}
.ledger-quote em {
  font-style: normal;
  color: var(--moss);
}
.stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem 2rem;
}
.stat {
  border-top: 1px solid rgba(1, 71, 46, 0.2);
  padding-top: 1.25rem;
}
.stat .num {
  font-family: var(--display);
  font-size: 4.5rem;
  line-height: 0.9;
  letter-spacing: -0.04em;
  color: var(--forest);
}
.stat .num small {
  font-size: 1.5rem;
  vertical-align: top;
  margin-left: 4px;
  letter-spacing: 0;
}
.stat .label {
  margin-top: 0.5rem;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.35em;
  text-transform: uppercase;
  color: var(--forest);
  opacity: 0.7;
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
  .hero {
    padding-top: 7rem;
  }
  .hero-bottom {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  .hero-origin {
    text-align: left;
    margin-left: 0;
  }
  .hero-scroll {
    display: none;
  }
  .float-1,
  .float-2,
  .float-3 {
    display: none;
  }
  .programs-head {
    flex-direction: column;
    align-items: flex-start;
  }
  .programs-cta {
    width: 8rem;
    height: 8rem;
  }
  .grid {
    grid-template-columns: 1fr;
  }
  .ledger-inner {
    grid-template-columns: 1fr;
    gap: 3rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-text span,
  .float .float-inner,
  .hero-meta .dot,
  .hero-scroll::after,
  [data-reveal] {
    animation: none !important;
    transition: none !important;
    opacity: 1 !important;
    transform: none !important;
  }
}
</style>
