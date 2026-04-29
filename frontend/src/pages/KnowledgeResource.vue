<script setup>
import { nextTick, onMounted, ref } from 'vue'
import axios from 'axios'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import knowledgeResource from '@/components/KnowledgeResource.vue'
import { useReveal } from '@/composables/useReveal'

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
    console.error('Error fetching Knowledge Resource content:', error)
  }
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
      <span class="eyebrow" data-reveal>(Index 00) Resources</span>
      <div class="intro-head">
        <h1 class="display" data-reveal>
          Knowledge<br />
          <em>Resources.</em>
        </h1>
        <p class="intro-lede" data-reveal data-reveal-delay="2">
          A curated library of climate reports, policy documents, and technical
          references for the Solomon Islands.
        </p>
      </div>
    </section>

    <!-- ========== OVERVIEW (Olive) ========== -->
    <section class="overview">
      <span class="eyebrow" data-reveal>(Index 01) Overview</span>

      <template v-if="data?.message?.length">
        <div
          v-for="(item, i) in data.message"
          :key="item.name || i"
          class="overview-block"
          data-reveal
          :data-reveal-delay="(i % 4) + 1"
        >
          <p v-if="item.kr_content" class="overview-prose">
            {{ item.kr_content }}
          </p>
        </div>
      </template>

      <div v-else class="overview-block" data-reveal>
        <p class="overview-prose">
          The Knowledge Resource library brings together the reports, datasets,
          and policy instruments that underpin the Solomon Islands' climate
          commitments — accessible in one place for practitioners, researchers,
          and the public alike.
        </p>
      </div>
    </section>

    <!-- ========== LIBRARY (Sage) ========== -->
    <section class="library">
      <span class="eyebrow" data-reveal>(Index 02) Library</span>
      <h2 class="section-title" data-reveal>Browse</h2>

      <div data-reveal data-reveal-delay="1">
        <knowledgeResource :data="data" />
      </div>
    </section>

    <!-- ========== CTA (Forest) ========== -->
    <section class="cta-section">
      <span class="eyebrow eyebrow-light" data-reveal>(Index 03) Navigate</span>
      <h2 class="cta-title" data-reveal>Learn<br /><em>More.</em></h2>
      <div class="cta-body">
        <p data-reveal data-reveal-delay="1">
          Explore the platform's adaptation and mitigation programs, or access
          the GHG inventory.
        </p>
        <router-link
          to="/about"
          class="division-cta"
          data-reveal
          data-reveal-delay="2"
        >
          <span>Explore<br />the<br />Platform →</span>
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

/* ---------- overview (olive) ---------- */
.overview {
  position: relative;
  background: var(--olive);
  padding: 7rem 2rem 8rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 5;
}
.overview-block {
  padding-top: 2rem;
  border-top: 1px solid rgba(1, 71, 46, 0.18);
  max-width: 1100px;
}
.overview-block + .overview-block {
  margin-top: 2rem;
}
.overview-prose {
  font-family: var(--body);
  font-size: 16px;
  line-height: 1.6;
  max-width: 60ch;
  color: var(--forest);
}

/* ---------- library (sage) ---------- */
.library {
  position: relative;
  background: var(--sage);
  padding: 5rem 2rem 8rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 6;
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
  .cta-body {
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
