<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import axios from 'axios'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { useReveal } from '@/composables/useReveal'

/**
 * About page — pulls the same MrvFrontend payload Home.vue uses, but only
 * surfaces the long-form `description_1` body (and any sibling description
 * fields rendered in the original page) for the about-the-tool narrative.
 *
 * Endpoint: mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all
 *   message: {
 *     message: [ { description_1, description_2?, about_heading_1?, ... } ],
 *     parent_data: { ...contact data consumed by <Footer :data="data" /> }
 *   }
 *
 * The legacy template only rendered description_1 (heading_1/heading_2 and
 * description_2 were commented out), so we preserve that contract.
 */
const data = ref({})
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
    console.error('Error fetching About content:', error)
  }
}

const aboutItems = computed(() => {
  const message = data.value?.message?.message
  if (Array.isArray(message)) return message
  if (message && typeof message === 'object') return [message]
  return []
})

const decodeHtml = (raw) => {
  if (!raw || typeof raw !== 'string') return ''
  return raw
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
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
      <span class="eyebrow" data-reveal>(Index 00) About the Platform</span>
      <div class="intro-head">
        <h1 class="display" data-reveal>
          About<br />
          <em>iMRV</em>
        </h1>
        <p class="intro-lede" data-reveal data-reveal-delay="2">
          An open accountability platform for climate action across the Solomon
          Islands. iMRV traces every project, every figure, and every flow of
          finance from the field to the registry — so the country can measure
          what it means to protect.
        </p>
      </div>
    </section>

    <!-- ========== NARRATIVE (Olive) ========== -->
    <section class="narrative">
      <span class="eyebrow" data-reveal>(Index 01) The Tool</span>
      <h2 class="section-title" data-reveal>What iMRV Does</h2>

      <div class="narrative-grid">
        <div
          v-for="(item, i) in aboutItems"
          :key="item.name || i"
          class="narrative-block"
          data-reveal
          :data-reveal-delay="i + 1"
        >
          <span class="block-num">0{{ i + 1 }}</span>
          <div
            v-if="item.description_1"
            class="prose"
            v-html="decodeHtml(item.description_1)"
          ></div>
          <div
            v-else-if="item.description_2"
            class="prose"
            v-html="decodeHtml(item.description_2)"
          ></div>
        </div>

        <!-- Static fallback when the Frappe payload is empty so the page
             still reads as an editorial document instead of a blank slab. -->
        <div v-if="!aboutItems.length" class="narrative-block" data-reveal>
          <span class="block-num">01</span>
          <div class="prose">
            <p>
              The Measurement, Reporting and Verification system underpins the
              Solomon Islands' climate commitments — bringing adaptation,
              mitigation, the GHG inventory, and climate finance flows under a
              single transparent ledger.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- ========== PILLARS (Sage) ========== -->
    <section class="pillars">
      <span class="eyebrow" data-reveal>(Index 02) Pillars</span>
      <h2 class="section-title" data-reveal>Four Workstreams</h2>

      <div class="pillars-grid">
        <article class="pillar" data-reveal data-reveal-delay="1">
          <span class="pillar-num">01</span>
          <h3 class="pillar-title">Adaptation</h3>
          <p class="pillar-body">
            Site-level resilience programs across coastal, agricultural and
            community sectors — tracked from proposal through verified outcome.
          </p>
        </article>
        <article class="pillar" data-reveal data-reveal-delay="2">
          <span class="pillar-num">02</span>
          <h3 class="pillar-title">Mitigation</h3>
          <p class="pillar-body">
            Forest, energy and waste sector projects measured against the
            country's NDC pathway, with traceable emission reductions.
          </p>
        </article>
        <article class="pillar" data-reveal data-reveal-delay="3">
          <span class="pillar-num">03</span>
          <h3 class="pillar-title">GHG Inventory</h3>
          <p class="pillar-body">
            A national greenhouse gas inventory built sector by sector, province
            by province — versioned, sourced, and open to review.
          </p>
        </article>
        <article class="pillar" data-reveal data-reveal-delay="4">
          <span class="pillar-num">04</span>
          <h3 class="pillar-title">Climate Finance</h3>
          <p class="pillar-body">
            A live ledger of incoming finance and disbursements — every
            commitment matched to the workstream it funds.
          </p>
        </article>
      </div>
    </section>

    <!-- ========== DIVISION (Forest) ========== -->
    <section class="division">
      <span class="eyebrow eyebrow-light" data-reveal
        >(Index 03) The Office</span
      >
      <h2 class="division-title" data-reveal>
        Climate Change<br /><em>Division.</em>
      </h2>
      <div class="division-body">
        <p data-reveal data-reveal-delay="1">
          iMRV is operated by the Climate Change Division of the Ministry of
          Environment, Climate Change, Disaster Management and Meteorology
          (MECDM), Government of Solomon Islands. The Division leads
          coordination on UNFCCC reporting, NDC implementation, and the
          country's adaptation and mitigation portfolio.
        </p>
        <router-link
          to="/climate-change-division"
          class="division-cta"
          data-reveal
          data-reveal-delay="2"
        >
          <span>Visit<br />the<br />Division →</span>
        </router-link>
      </div>
    </section>

    <Footer :data="data" :flush="false" />
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

/* ---------- shared eyebrow / section title ---------- */
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

/* ---------- narrative (olive) ---------- */
.narrative {
  position: relative;
  background: var(--olive);
  padding: 7rem 2rem 8rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 5;
}
.narrative-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 3rem;
  max-width: 1100px;
}
.narrative-block {
  display: grid;
  grid-template-columns: 6rem 1fr;
  gap: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(1, 71, 46, 0.18);
}
.block-num {
  font-family: var(--display);
  font-size: 2.5rem;
  line-height: 1;
  letter-spacing: -0.02em;
  color: var(--forest);
  opacity: 0.55;
}
.prose {
  font-family: var(--body);
  font-size: 16px;
  line-height: 1.6;
  max-width: 60ch;
  color: var(--forest);
}
.prose :deep(p) {
  margin: 0 0 1rem;
}
.prose :deep(p:last-child) {
  margin-bottom: 0;
}
.prose :deep(strong),
.prose :deep(b) {
  font-weight: 700;
  color: var(--forest);
}
.prose :deep(a) {
  color: var(--forest);
  text-decoration: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 3px;
  transition: color 0.3s var(--ease);
}
.prose :deep(a:hover) {
  color: var(--moss);
}
.prose :deep(ul),
.prose :deep(ol) {
  margin: 0 0 1rem;
  padding-left: 1.25rem;
}
.prose :deep(li) {
  margin-bottom: 0.35rem;
}

/* ---------- pillars (sage) ---------- */
.pillars {
  position: relative;
  background: var(--sage);
  padding: 7rem 2rem 8rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 6;
}
.pillars-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 3rem 2.5rem;
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

/* ---------- division (forest) ---------- */
.division {
  position: relative;
  background: var(--forest);
  color: var(--cream);
  padding: 7rem 2rem 9rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 7;
  overflow: hidden;
}
.division::before {
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
.division-title {
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
.division-title em {
  font-style: normal;
  color: var(--sage);
}
.division-body {
  position: relative;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 4rem;
  align-items: end;
}
.division-body p {
  max-width: 60ch;
  font-size: 16px;
  line-height: 1.6;
  color: var(--cream);
}
.division-cta {
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
.division-cta:hover {
  transform: rotate(-12deg) scale(1.05);
  background: white;
}
.division-cta span {
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
  .narrative-block {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  .pillars-grid {
    grid-template-columns: 1fr;
  }
  .division-body {
    grid-template-columns: 1fr;
    gap: 2.5rem;
    align-items: start;
  }
  .division-cta {
    width: 8rem;
    height: 8rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  [data-reveal],
  .division-cta {
    animation: none !important;
    transition: none !important;
    opacity: 1 !important;
    transform: none !important;
  }
}
</style>
