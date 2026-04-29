<template>
  <Header />

  <!-- Section 1: Cream intro -->
  <div class="editorial section-cream">
    <div class="container">
      <div class="eyebrow" data-reveal>(Index 00) Updates</div>
      <h1 class="display-heading" data-reveal data-reveal-delay="1">
        What's<br /><em>New.</em>
      </h1>
      <p class="lede" data-reveal data-reveal-delay="2">
        The latest announcements, publications, and milestones from the Solomon
        Islands climate programme.
      </p>
    </div>
  </div>

  <!-- Section 2: Olive — news feed -->
  <div class="editorial section-olive">
    <div class="container">
      <div class="eyebrow" data-reveal>(Index 01) Latest</div>
      <h2 class="section-title" data-reveal data-reveal-delay="1">News</h2>

      <div class="news-feed" v-if="newsItems.length > 0">
        <article
          v-for="(item, i) in newsItems"
          :key="item.title || i"
          class="news-article"
          data-reveal
          :data-reveal-delay="(i % 4) + 1"
        >
          <div class="news-image-wrap" v-if="item.add_image">
            <img :src="item.add_image" :alt="item.title" class="news-img" />
          </div>
          <div
            class="news-image-wrap news-no-image"
            v-else
            aria-hidden="true"
          ></div>
          <div class="news-body">
            <time class="news-date">{{ item.creation }}</time>
            <h3 class="news-title">{{ item.title }}</h3>
            <p class="news-desc">{{ item.content }}</p>
            <a
              v-if="item.add_url"
              :href="item.add_url"
              target="_blank"
              rel="noopener noreferrer"
              class="news-link"
              >Read More →</a
            >
          </div>
        </article>
      </div>
      <p class="news-empty" v-else data-reveal>
        No updates yet — check back soon.
      </p>
    </div>
  </div>

  <!-- Section 3: Sage — topics -->
  <div class="editorial section-sage">
    <div class="container">
      <div class="eyebrow" data-reveal>(Index 02) Categories</div>
      <h2 class="section-title" data-reveal data-reveal-delay="1">Topics</h2>
      <div class="topics-row" data-reveal data-reveal-delay="2">
        <span class="topic-chip">Adaptation</span>
        <span class="topic-chip">Mitigation</span>
        <span class="topic-chip">GHG Inventory</span>
        <span class="topic-chip">Climate Finance</span>
      </div>
    </div>
  </div>

  <!-- Section 4: Forest CTA -->
  <div class="editorial section-forest">
    <div class="container">
      <div class="eyebrow eyebrow-light" data-reveal>(Index 03) Navigate</div>
      <h2
        class="section-title section-title-light"
        data-reveal
        data-reveal-delay="1"
      >
        The<br /><em>Platform.</em>
      </h2>
      <div data-reveal data-reveal-delay="2">
        <router-link to="/about" class="cta-pill"
          >Explore the Platform</router-link
        >
      </div>
    </div>
  </div>

  <Footer :data="data" />
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import axios from 'axios'
import Footer from '@/components/Footer.vue'
import Header from '@/components/Header.vue'
import { useReveal } from '@/composables/useReveal'

const data = ref({})
const { observeAll } = useReveal()

const newsItems = computed(() => data.value?.message?.add_new_content ?? [])

const fetchData = async () => {
  try {
    const response = await axios.get(
      '/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all',
    )
    if (response.status === 200) {
      data.value = response.data
      let formatter = new Intl.DateTimeFormat('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
      })
      for (let i = 0; i < data.value.message.add_new_content.length; i++) {
        let date = new Date(data.value.message.add_new_content[i].date)
        data.value.message.add_new_content[i].creation = formatter.format(date)
      }
      await nextTick()
      observeAll()
    } else {
      throw new Error('Network response was not ok')
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
/* ── Design tokens ─────────────────────────────────────────── */
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
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

/* ── Sections ──────────────────────────────────────────────── */
.section-cream {
  background: var(--cream);
  padding: 4rem 2rem 7rem;
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
  color: var(--cream);
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 7;
  position: relative;
  padding: 5rem 2rem 6rem;
}

.container {
  max-width: 72rem;
  margin: 0 auto;
}

/* ── Reveal animation ──────────────────────────────────────── */
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

/* ── Eyebrow ───────────────────────────────────────────────── */
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

/* ── Typography ────────────────────────────────────────────── */
.display-heading {
  font-family: var(--display);
  font-size: clamp(4rem, 10vw, 8rem);
  line-height: 0.9;
  letter-spacing: -0.03em;
  text-transform: uppercase;
  font-weight: 400;
  margin: 0 0 2rem;
  color: var(--forest);
}

.display-heading em {
  font-style: italic;
}

.lede {
  font-size: clamp(1rem, 2vw, 1.2rem);
  line-height: 1.6;
  max-width: 52ch;
  color: var(--forest);
  opacity: 0.8;
  margin: 0;
}

.section-title {
  font-family: var(--display);
  font-size: clamp(3rem, 7vw, 6rem);
  line-height: 0.9;
  letter-spacing: -0.03em;
  text-transform: uppercase;
  font-weight: 400;
  margin: 0 0 3rem;
  color: var(--forest);
}

.section-title em {
  font-style: italic;
}

.section-title-light {
  color: var(--cream);
}

/* ── News feed ─────────────────────────────────────────────── */
.news-feed {
  display: flex;
  flex-direction: column;
}

.news-article {
  display: grid;
  grid-template-columns: 14rem 1fr;
  gap: 2.5rem;
  padding: 3rem 0;
  border-top: 1px solid rgba(1, 71, 46, 0.18);
}

.news-img {
  width: 100%;
  height: 10rem;
  object-fit: cover;
  border-radius: 1.5rem;
}

.news-no-image {
  width: 100%;
  height: 10rem;
  border-radius: 1.5rem;
  background: var(--cream);
  opacity: 0.5;
}

.news-body {
  display: flex;
  flex-direction: column;
}

.news-date {
  display: block;
  font-size: 11px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--forest);
  opacity: 0.6;
  margin-bottom: 0.5rem;
}

.news-title {
  font-family: var(--display);
  font-size: clamp(1.4rem, 2.5vw, 2rem);
  line-height: 0.95;
  letter-spacing: -0.02em;
  text-transform: uppercase;
  margin: 0 0 0.75rem;
  font-weight: 400;
  color: var(--forest);
}

.news-desc {
  font-size: 14px;
  line-height: 1.65;
  max-width: 60ch;
  margin: 0 0 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  color: var(--forest);
}

.news-link {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--forest);
  border-bottom: 1px solid var(--forest);
  padding-bottom: 2px;
  align-self: flex-start;
}

.news-link:hover {
  color: var(--moss);
  border-color: var(--moss);
}

.news-empty {
  font-size: 1rem;
  opacity: 0.6;
  padding: 3rem 0;
  border-top: 1px solid rgba(1, 71, 46, 0.18);
}

@media (max-width: 900px) {
  .news-article {
    grid-template-columns: 1fr;
  }

  .news-image-wrap {
    height: 14rem;
  }
}

/* ── Topics ────────────────────────────────────────────────── */
.topics-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.topic-chip {
  display: inline-flex;
  align-items: center;
  padding: 1rem 2rem;
  border-radius: 999px;
  border: 2px solid var(--forest);
  font-family: var(--display);
  font-size: 1.4rem;
  letter-spacing: -0.02em;
  text-transform: uppercase;
  color: var(--forest);
}

/* ── CTA pill ──────────────────────────────────────────────── */
.cta-pill {
  display: inline-flex;
  align-items: center;
  padding: 1.1rem 2.5rem;
  border-radius: 999px;
  border: 2px solid var(--cream);
  font-family: var(--display);
  font-size: 1.1rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--cream);
  transition:
    background 0.3s var(--ease),
    color 0.3s var(--ease);
}

.cta-pill:hover {
  background: var(--cream);
  color: var(--forest);
}
</style>
