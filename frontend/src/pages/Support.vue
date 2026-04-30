<template>
  <div class="editorial">
    <Header />

    <!-- Section 1: Cream intro -->
    <section class="section-cream">
      <div class="container">
        <span class="eyebrow" data-reveal>(Index 00) Help Center</span>
        <h1 class="display-heading" data-reveal data-reveal-delay="1">
          Support<br /><em>Centre.</em>
        </h1>
        <p class="lede" data-reveal data-reveal-delay="2">
          Documentation, guides, and contacts for using the iMRV platform.
        </p>
      </div>
    </section>

    <!-- Section 2: Olive — main content -->
    <section class="section-olive">
      <div class="container">
        <span class="eyebrow" data-reveal>(Index 01) Guidance</span>
        <h2 class="section-title" data-reveal data-reveal-delay="1">
          Using iMRV
        </h2>

        <div v-if="supportItems.length">
          <div v-for="item in supportItems" :key="item.name">
            <h3
              v-if="item.support_main_heading"
              class="support-heading"
              data-reveal
            >
              {{ item.support_main_heading }}
            </h3>
            <p v-if="item.main_paragraph" class="support-body" data-reveal>
              {{ item.main_paragraph }}
            </p>

            <!-- Bulletin block 1 -->
            <template v-if="item.bulletin_heading1">
              <h4 class="bulletin-heading" data-reveal>
                {{ item.bulletin_heading1 }}
              </h4>
              <ul
                v-if="item.bulletin_content1?.length"
                class="bulletin-list"
                data-reveal
              >
                <li v-for="b in item.bulletin_content1" :key="b.name">
                  {{ b.content }}
                </li>
              </ul>
            </template>
            <img
              v-if="item.support_image1"
              :src="item.support_image1"
              class="support-img"
              alt=""
              data-reveal
            />

            <!-- Bulletin block 2 -->
            <template v-if="item.bulletin_heading2">
              <h4 class="bulletin-heading" data-reveal>
                {{ item.bulletin_heading2 }}
              </h4>
              <ul
                v-if="item.bulletin_content2?.length"
                class="bulletin-list"
                data-reveal
              >
                <li v-for="b in item.bulletin_content2" :key="b.name">
                  {{ b.content }}
                </li>
              </ul>
            </template>
            <img
              v-if="item.support_image2"
              :src="item.support_image2"
              class="support-img"
              alt=""
              data-reveal
            />

            <!-- Bulletin block 3 -->
            <template v-if="item.bulletin_heading3">
              <h4 class="bulletin-heading" data-reveal>
                {{ item.bulletin_heading3 }}
              </h4>
              <ul
                v-if="item.bulletin_content3?.length"
                class="bulletin-list"
                data-reveal
              >
                <li v-for="b in item.bulletin_content3" :key="b.name">
                  {{ b.content }}
                </li>
              </ul>
            </template>
            <img
              v-if="item.support_image3"
              :src="item.support_image3"
              class="support-img"
              alt=""
              data-reveal
            />

            <!-- Bulletin block 4 -->
            <template v-if="item.bulletin_heading4">
              <h4 class="bulletin-heading" data-reveal>
                {{ item.bulletin_heading4 }}
              </h4>
              <ul
                v-if="item.bulletin_content4?.length"
                class="bulletin-list"
                data-reveal
              >
                <li v-for="b in item.bulletin_content4" :key="b.name">
                  {{ b.content }}
                </li>
              </ul>
            </template>
            <img
              v-if="item.support_image4"
              :src="item.support_image4"
              class="support-img"
              alt=""
              data-reveal
            />
          </div>
        </div>

        <div v-else class="support-fallback" data-reveal>
          <p class="support-body">
            For questions about using the iMRV platform, contact the Climate
            Change Division at the Ministry of Environment, Climate Change,
            Disaster Management and Meteorology (MECDM).
          </p>
        </div>
      </div>
    </section>

    <!-- Section 3: Sage — quick links -->
    <section class="section-sage">
      <div class="container">
        <span class="eyebrow" data-reveal>(Index 02) Quick Links</span>
        <h2 class="section-title" data-reveal data-reveal-delay="1">
          Get Help
        </h2>

        <div class="cards-grid cards-grid--single">
          <router-link
            to="/climate-change-division"
            class="help-card"
            data-reveal
            data-reveal-delay="1"
          >
            <span class="card-title">Contact Division</span>
            <span class="card-desc"
              >Reach the Climate Change Division team directly</span
            >
            <span class="card-arrow" aria-hidden="true">→</span>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Section 4: Forest CTA -->
    <section class="section-forest">
      <div class="container">
        <span class="eyebrow eyebrow-light" data-reveal
          >(Index 03) Platform</span
        >
        <h2
          class="display-heading display-heading-light"
          data-reveal
          data-reveal-delay="1"
        >
          Back to<br /><em>Home.</em>
        </h2>
        <router-link to="/" class="cta-pill" data-reveal data-reveal-delay="2">
          Go to Home
        </router-link>
      </div>
    </section>

    <Footer :data="data" />
  </div>
</template>

<script setup>
import Footer from '@/components/Footer.vue'
import Header from '@/components/Header.vue'
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useReveal } from '@/composables/useReveal'

const data = ref({})
const { observeAll } = useReveal()

const supportItems = computed(() => {
  const m = data.value?.message
  if (Array.isArray(m)) return m
  if (m && typeof m === 'object') return [m]
  return []
})

const fetchData = async () => {
  try {
    const response = await axios.get(
      '/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all',
    )
    if (response.status === 200) {
      data.value = response.data
    }
  } catch (error) {
    // silently handle fetch errors
  }
}

onMounted(async () => {
  await fetchData()
  observeAll()
})
</script>

<style scoped>
/* ── Design tokens ─────────────────────────────────────── */
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

/* ── Reveal animation ──────────────────────────────────── */
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
@media (prefers-reduced-motion: reduce) {
  [data-reveal] {
    animation: none !important;
    transition: none !important;
    opacity: 1 !important;
    transform: none !important;
  }
}

/* ── Eyebrow ───────────────────────────────────────────── */
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

/* ── Container ─────────────────────────────────────────── */
.container {
  max-width: 1140px;
  margin: 0 auto;
  padding: 0 2rem;
}

/* ── Section shells ────────────────────────────────────── */
.section-cream {
  padding: 4rem 2rem 7rem;
  background: var(--cream);
}

.section-olive {
  background: var(--olive);
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 5;
  position: relative;
  padding: 5rem 2rem 7rem;
}

.section-sage {
  background: var(--sage);
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 6;
  position: relative;
  padding: 5rem 2rem 7rem;
}

.section-forest {
  background: var(--forest);
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 7;
  position: relative;
  padding: 5rem 2rem 7rem;
  color: var(--cream);
}

/* ── Typography ────────────────────────────────────────── */
.display-heading {
  font-family: var(--display);
  font-size: clamp(3.5rem, 8vw, 7rem);
  font-weight: 400;
  line-height: 1;
  letter-spacing: -0.03em;
  text-transform: uppercase;
  margin: 0 0 1.5rem;
}
.display-heading em {
  font-style: italic;
}
.display-heading-light {
  color: var(--cream);
}

.section-title {
  font-family: var(--display);
  font-size: clamp(2rem, 4vw, 3.5rem);
  font-weight: 400;
  letter-spacing: -0.02em;
  text-transform: uppercase;
  margin: 0 0 2.5rem;
}

.lede {
  font-size: clamp(1rem, 1.5vw, 1.25rem);
  max-width: 55ch;
  line-height: 1.6;
  margin: 0;
  opacity: 0.8;
}

/* ── Support content ───────────────────────────────────── */
.support-heading {
  font-family: var(--display);
  font-size: clamp(1.8rem, 3vw, 2.5rem);
  margin: 2.5rem 0 0.75rem;
  text-transform: uppercase;
  letter-spacing: -0.02em;
}

.bulletin-heading {
  font-family: var(--body);
  font-size: 1rem;
  font-weight: 700;
  margin: 1.5rem 0 0.5rem;
}

.bulletin-list {
  margin: 0;
  padding-left: 1.25rem;
}
.bulletin-list li {
  margin-bottom: 0.4rem;
  font-size: 15px;
  line-height: 1.6;
}

.support-body {
  font-size: 16px;
  line-height: 1.6;
  max-width: 70ch;
}

.support-img {
  width: 100%;
  max-width: 600px;
  border-radius: 2rem;
  object-fit: cover;
  margin: 2rem 0;
  box-shadow: 0 25px 60px -25px var(--forest-shadow);
  display: block;
}

/* ── Quick-link cards ──────────────────────────────────── */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
.cards-grid--single {
  grid-template-columns: minmax(0, 22rem);
  justify-content: start;
}

.help-card {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  padding: 2rem;
  background: var(--cream);
  border-radius: 1.5rem;
  text-decoration: none;
  color: var(--forest);
  transition:
    transform 0.3s var(--ease),
    box-shadow 0.3s var(--ease);
}
.help-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 50px -15px var(--forest-shadow);
}

.card-title {
  font-family: var(--display);
  font-size: 1.25rem;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: -0.01em;
}

.card-desc {
  font-size: 14px;
  line-height: 1.5;
  opacity: 0.75;
  flex: 1;
}

.card-arrow {
  font-size: 1.25rem;
  margin-top: 0.5rem;
}

/* ── CTA pill ──────────────────────────────────────────── */
.cta-pill {
  display: inline-flex;
  align-items: center;
  padding: 1rem 2.5rem;
  border-radius: 999px;
  border: 2px solid var(--cream);
  color: var(--cream);
  text-decoration: none;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  transition:
    background 0.3s var(--ease),
    color 0.3s var(--ease);
}
.cta-pill:hover {
  background: var(--cream);
  color: var(--forest);
}

/* ── Mobile ────────────────────────────────────────────── */
@media (max-width: 900px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }

  .section-olive,
  .section-sage,
  .section-forest {
    border-radius: 2.5rem 2.5rem 0 0;
    padding: 4rem 1.5rem 6rem;
  }

  .section-cream {
    padding: 3rem 1.5rem 6rem;
  }
}
</style>
