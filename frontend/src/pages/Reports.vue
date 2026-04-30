<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import axios from 'axios'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { useReveal } from '@/composables/useReveal'

const data = ref({})
const modalSrc = ref(null)
const modalLabel = ref('')
const { observeAll } = useReveal()

const fetchData = async () => {
  try {
    const response = await axios.get(
      '/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all',
    )
    if (response.status === 200) {
      data.value = response.data
      await nextTick()
      observeAll()
    } else {
      throw new Error('Network response was not ok')
    }
  } catch (error) {
    console.error('Error fetching Reports content:', error)
  }
}

const parentData = computed(() => data.value?.message?.parent_data ?? {})

// The Frappe single-doc carries up to 3 report image fields, but only an
// image URL — no inherent title or year. Differentiate the cards in the UI
// so visitors don't see three identical "GHG Inventory Report" buttons.
// Cycle through the country's three reporting milestones in the order they
// were authored (2019/2020 archive, 2023 update, 2026 latest).
const REPORT_META = [
  {
    year: '2019/2020',
    label: 'GHG Inventory · Archive',
    scope: 'Initial National Communication',
  },
  {
    year: '2023',
    label: 'GHG Inventory · Update',
    scope: 'Biennial Update Report',
  },
  {
    year: '2026',
    label: 'GHG Inventory · Latest',
    scope: 'NDC Implementation Report',
  },
]

const reportCards = computed(() => {
  const pd = parentData.value
  const sources = [pd.report_image, pd.report_image1, pd.report_image2]
  return sources
    .map((src, i) => (src ? { src, ...REPORT_META[i] } : null))
    .filter(Boolean)
})

const openReport = (card) => {
  modalSrc.value = card.src
  modalLabel.value = `${card.label} — ${card.year}`
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="editorial">
    <Header />

    <!-- ========== INTRO (Cream) ========== -->
    <section class="intro">
      <span class="eyebrow" data-reveal>(Index 00) Reports</span>
      <div class="intro-head">
        <h1 class="display" data-reveal>
          National<br /><em>GHG</em><br />Inventory.
        </h1>
        <p class="intro-lede" data-reveal data-reveal-delay="2">
          Three decades of greenhouse gas data — measured, verified, and open to
          the world.
        </p>
      </div>
    </section>

    <!-- ========== REPORT GALLERY (Olive) ========== -->
    <section class="gallery">
      <span class="eyebrow" data-reveal>(Index 01) Documents</span>
      <h2 class="section-title" data-reveal>Reports</h2>

      <div class="report-grid">
        <button
          v-for="(card, i) in reportCards"
          :key="card.src"
          class="report-card"
          @click="openReport(card)"
          data-reveal
          :data-reveal-delay="i + 1"
        >
          <img :src="card.src" :alt="`${card.label} — ${card.year}`" />
          <span class="card-year">{{ card.year }}</span>
          <span class="card-title">{{ card.label }}</span>
          <span class="card-scope">{{ card.scope }}</span>
          <span class="card-label">View Report →</span>
        </button>
      </div>
    </section>

    <!-- ========== SCOPE (Sage) ========== -->
    <section class="scope">
      <span class="eyebrow" data-reveal>(Index 02) About the Inventory</span>
      <h2 class="section-title" data-reveal>Scope</h2>

      <div class="pillars-grid">
        <article class="pillar" data-reveal data-reveal-delay="1">
          <span class="pillar-num">01</span>
          <h3 class="pillar-title">Energy</h3>
          <p class="pillar-body">
            Emissions from fuel combustion and fugitive sources across all
            sectors
          </p>
        </article>
        <article class="pillar" data-reveal data-reveal-delay="2">
          <span class="pillar-num">02</span>
          <h3 class="pillar-title">Land Use</h3>
          <p class="pillar-body">
            Forest carbon stocks, deforestation rates, and land-use change
            accounting
          </p>
        </article>
        <article class="pillar" data-reveal data-reveal-delay="3">
          <span class="pillar-num">03</span>
          <h3 class="pillar-title">Waste</h3>
          <p class="pillar-body">
            Solid waste disposal, wastewater treatment and biological treatment
          </p>
        </article>
      </div>
    </section>

    <!-- ========== CTA (Forest) ========== -->
    <section class="cta-section">
      <span class="eyebrow eyebrow-light" data-reveal>(Index 03) Navigate</span>
      <h2 class="cta-title" data-reveal>The<br /><em>Platform.</em></h2>
      <div class="cta-body">
        <router-link
          to="/about"
          class="cta-pill"
          data-reveal
          data-reveal-delay="1"
        >
          <span>Explore<br />the<br />Platform →</span>
        </router-link>
      </div>
    </section>

    <Footer :data="data" />

    <!-- ========== LIGHTBOX ========== -->
    <Teleport to="#modals">
      <div
        v-if="modalSrc"
        class="modal-overlay"
        role="dialog"
        aria-modal="true"
        :aria-label="modalLabel || 'Report full view'"
        @click="modalSrc = null"
        @keydown.escape="modalSrc = null"
      >
        <figure class="modal-figure" @click.stop>
          <img
            :src="modalSrc"
            class="modal-img"
            :alt="modalLabel || 'Report full view'"
          />
          <figcaption v-if="modalLabel" class="modal-caption">
            {{ modalLabel }}
          </figcaption>
        </figure>
        <button
          class="modal-close"
          @click.stop="modalSrc = null"
          aria-label="Close"
        >
          ×
        </button>
      </div>
    </Teleport>
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

/* ---------- eyebrow ---------- */
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

/* ---------- gallery (olive) ---------- */
.gallery {
  position: relative;
  background: var(--olive);
  padding: 7rem 2rem 8rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 5;
}
.report-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}
.report-card {
  border-radius: 2.5rem;
  overflow: hidden;
  cursor: pointer;
  background: var(--cream);
  border: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 60px -25px var(--forest-shadow);
  transition:
    transform 0.5s var(--ease),
    box-shadow 0.5s var(--ease);
}
.report-card:hover {
  transform: scale(1.03);
  box-shadow: 0 35px 80px -30px var(--forest-shadow);
}
.report-card img {
  width: 100%;
  aspect-ratio: 3 / 4;
  object-fit: cover;
  display: block;
}
.card-year {
  display: block;
  padding: 1.25rem 1.5rem 0.25rem;
  font-family: 'Anton', 'Helvetica Neue', sans-serif;
  font-size: 1.5rem;
  line-height: 1;
  letter-spacing: -0.02em;
  text-transform: uppercase;
  color: var(--forest);
  opacity: 0.55;
  text-align: left;
}
.card-title {
  display: block;
  padding: 0 1.5rem;
  font-family: 'Anton', 'Helvetica Neue', sans-serif;
  font-size: 1.25rem;
  line-height: 1.05;
  letter-spacing: -0.01em;
  text-transform: uppercase;
  color: var(--forest);
  text-align: left;
}
.card-scope {
  display: block;
  padding: 0.4rem 1.5rem 0.5rem;
  font-size: 12px;
  line-height: 1.4;
  color: var(--forest);
  opacity: 0.7;
  text-align: left;
}
.card-label {
  display: block;
  padding: 0.75rem 1.5rem 1rem;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--forest);
  text-align: left;
}

/* ---------- scope (sage) ---------- */
.scope {
  position: relative;
  background: var(--sage);
  padding: 7rem 2rem 8rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 6;
}
.pillars-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}
.pillar {
  background: var(--cream);
  border-radius: 2.5rem;
  padding: 2.5rem;
  box-shadow: 0 25px 60px -25px var(--forest-shadow);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.pillar-num {
  font-family: var(--display);
  font-size: 2.5rem;
  line-height: 1;
  letter-spacing: -0.02em;
  color: var(--forest);
  opacity: 0.55;
}
.pillar-title {
  font-family: var(--display);
  font-size: clamp(2rem, 3.2vw, 2.8rem);
  line-height: 0.95;
  letter-spacing: -0.02em;
  color: var(--forest);
  text-transform: uppercase;
  font-weight: 400;
}
.pillar-body {
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
  display: flex;
  align-items: center;
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

/* ---------- modal ---------- */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}
.modal-figure {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  max-width: 92vw;
}
.modal-img {
  max-width: 90vw;
  max-height: 80vh;
  border-radius: 1rem;
  object-fit: contain;
  display: block;
}
.modal-caption {
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--cream);
  opacity: 0.85;
}
.modal-close {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  font-size: 2rem;
  color: white;
  background: none;
  border: none;
  cursor: pointer;
}

/* ---------- mobile ---------- */
@media (max-width: 900px) {
  .intro-head {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  .report-grid {
    grid-template-columns: 1fr;
  }
  .pillars-grid {
    grid-template-columns: 1fr;
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
