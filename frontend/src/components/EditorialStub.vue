<script setup>
/**
 * EditorialStub — minimal placeholder page for legal / governance pages
 * (Privacy, Accessibility, Source, Open Data API, Methodology) that the SPA
 * advertises in its footer but has no full editorial copy for yet. Matches
 * the typography of /frontend/about so it doesn't read as a 404.
 *
 * Pages still link to admin@imrv.netzerolabs.io via a single mailto button
 * at the foot of the body — we just don't put the mailto link in the global
 * footer where it wears the visual cost on every page.
 */
import { onMounted, ref } from 'vue'
import axios from 'axios'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { useReveal } from '@/composables/useReveal'

defineProps({
  eyebrow: { type: String, required: true }, // "(Index 00) Privacy"
  titleA: { type: String, required: true }, // "Privacy"
  titleB: { type: String, default: '' }, // "Statement."
  lede: { type: String, required: true },
  bodyParagraphs: { type: Array, required: true }, // string[]
  contactSubject: { type: String, default: 'iMRV inquiry' },
})

const data = ref({})
const { observeAll } = useReveal()

const fetchData = async () => {
  try {
    const response = await axios.get(
      '/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all',
    )
    if (response.status === 200) {
      data.value = response.data
      observeAll()
    }
  } catch (error) {
    /* footer is decorative on a stub page */
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
      <span class="eyebrow" data-reveal>{{ eyebrow }}</span>
      <div class="intro-head">
        <h1 class="display" data-reveal>
          {{ titleA }}<br v-if="titleB" />
          <em v-if="titleB">{{ titleB }}</em>
        </h1>
        <p class="intro-lede" data-reveal data-reveal-delay="2">
          {{ lede }}
        </p>
      </div>
    </section>

    <!-- ========== BODY (Olive) ========== -->
    <section class="body">
      <span class="eyebrow" data-reveal>(Index 01) Statement</span>
      <div class="body-grid">
        <p
          v-for="(para, i) in bodyParagraphs"
          :key="i"
          class="body-para"
          data-reveal
          :data-reveal-delay="(i % 4) + 1"
        >
          {{ para }}
        </p>
        <p class="body-para body-contact" data-reveal>
          For corrections, requests or questions, write to
          <a
            :href="`mailto:admin@imrv.netzerolabs.io?subject=${encodeURIComponent(contactSubject)}`"
            >admin@imrv.netzerolabs.io</a
          >.
        </p>
      </div>
    </section>

    <!-- ========== CTA (Forest) ========== -->
    <section class="cta-section">
      <span class="eyebrow eyebrow-light" data-reveal>(Index 02) Navigate</span>
      <h2 class="cta-title" data-reveal>The<br /><em>Platform.</em></h2>
      <div class="cta-body">
        <p data-reveal data-reveal-delay="1">
          Continue exploring the iMRV ledger or return to the home page.
        </p>
        <router-link to="/" class="cta-pill" data-reveal data-reveal-delay="2">
          <span>Back<br />to<br />Home →</span>
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
  font-size: clamp(3.5rem, 10vw, 9rem);
  line-height: 0.9;
  letter-spacing: -0.04em;
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

.body {
  position: relative;
  background: var(--olive);
  padding: 7rem 2rem 8rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 5;
}
.body-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 64ch;
}
.body-para {
  font-family: var(--body);
  font-size: 16px;
  line-height: 1.7;
  color: var(--forest);
}
.body-contact a {
  color: var(--forest);
  text-decoration: underline;
  text-underline-offset: 3px;
}
.body-contact a:hover {
  color: var(--moss);
}

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
