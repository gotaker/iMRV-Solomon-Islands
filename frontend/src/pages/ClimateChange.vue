<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import axios from 'axios'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

const data = ref({})

const fetchData = async () => {
  try {
    const response = await axios.get(
      '/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all',
    )
    if (response.status === 200) {
      data.value = response.data
    } else {
      throw new Error('Network response was not ok')
    }
  } catch (error) {
    console.error('Error fetching Climate Change Division content:', error)
  }
}

const parentData = computed(() => data.value?.message?.parent_data ?? {})

const decodeHtml = (raw) => {
  if (!raw || typeof raw !== 'string') return ''
  return raw
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
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
      <span class="eyebrow" data-reveal
        >(Index 00) Climate Change Division</span
      >
      <div class="intro-head">
        <h1 class="display" data-reveal>
          Climate<br />
          <em>Change</em>
        </h1>
        <p class="intro-lede" data-reveal data-reveal-delay="2">
          The Climate Change Division leads Solomon Islands' national response
          to a changing climate — coordinating adaptation programmes, mitigation
          projects, and the country's greenhouse gas inventory under a single
          accountable mandate.
        </p>
      </div>
      <h2
        v-if="parentData.climate_change_title"
        class="intro-sub"
        data-reveal
        data-reveal-delay="3"
      >
        {{ parentData.climate_change_title }}
      </h2>
    </section>

    <!-- ========== NARRATIVE (Olive) ========== -->
    <section class="narrative">
      <span class="eyebrow" data-reveal>(Index 01) About the Division</span>
      <h2 class="section-title" data-reveal>The Division</h2>

      <div class="narrative-layout">
        <div class="narrative-content">
          <div
            v-if="parentData.climate_change_division_content1"
            class="narrative-block"
            data-reveal
          >
            <span class="block-num">01</span>
            <div
              class="prose"
              v-html="decodeHtml(parentData.climate_change_division_content1)"
            ></div>
          </div>
          <div
            v-if="!parentData.climate_change_division_content1"
            class="narrative-block"
            data-reveal
          >
            <span class="block-num">01</span>
            <div class="prose">
              <p>
                The Climate Change Division of the Ministry of Environment,
                Climate Change, Disaster Management and Meteorology (MECDM)
                leads the Solomon Islands' engagement on the United Nations
                Framework Convention on Climate Change and oversees
                implementation of the country's Nationally Determined
                Contributions.
              </p>
            </div>
          </div>
        </div>

        <figure
          v-if="parentData.content_image"
          class="narrative-float"
          data-reveal
          data-reveal-delay="2"
        >
          <img
            :src="parentData.content_image"
            alt="Climate Change Division"
            class="float-image"
          />
        </figure>
      </div>
    </section>

    <!-- ========== GALLERY (Sage) ========== -->
    <section class="gallery">
      <span class="eyebrow" data-reveal>(Index 02) Gallery</span>
      <h2 class="section-title" data-reveal>Images</h2>

      <!-- 3-column photo grid -->
      <div
        v-if="
          parentData.climate_image1 ||
          parentData.climate_image2 ||
          parentData.climate_image3
        "
        class="photo-grid"
        data-reveal
      >
        <div v-if="parentData.climate_image1" class="photo-cell">
          <img :src="parentData.climate_image1" alt="" class="photo-img" />
        </div>
        <div v-if="parentData.climate_image2" class="photo-cell">
          <img :src="parentData.climate_image2" alt="" class="photo-img" />
        </div>
        <div v-if="parentData.climate_image3" class="photo-cell">
          <img :src="parentData.climate_image3" alt="" class="photo-img" />
        </div>
      </div>

      <!-- Masonry-style gallery row from child table -->
      <div
        v-if="parentData.climate_change_division_images?.length"
        class="masonry-row"
        data-reveal
        data-reveal-delay="1"
      >
        <div
          v-for="(item, i) in parentData.climate_change_division_images"
          :key="i"
          class="masonry-cell"
        >
          <img v-if="item.image" :src="item.image" alt="" class="masonry-img" />
        </div>
      </div>

      <!-- Prose below gallery -->
      <div class="gallery-prose">
        <div
          v-if="parentData.climate_change_division_content2"
          class="prose"
          data-reveal
          data-reveal-delay="2"
          v-html="decodeHtml(parentData.climate_change_division_content2)"
        ></div>
        <div
          v-if="parentData.climate_change_division_content3"
          class="prose"
          data-reveal
          data-reveal-delay="3"
          v-html="decodeHtml(parentData.climate_change_division_content3)"
        ></div>
      </div>
    </section>

    <!-- ========== CTA (Forest) ========== -->
    <section class="division">
      <span class="eyebrow eyebrow-light" data-reveal
        >(Index 03) Learn More</span
      >
      <h2 class="division-title" data-reveal>The<br /><em>Division.</em></h2>
      <div class="division-body">
        <p data-reveal data-reveal-delay="1">
          Learn more about iMRV's platform and the broader climate
          accountability work that underpins Solomon Islands' national reporting
          — from the GHG inventory to adaptation and mitigation project
          tracking.
        </p>
        <router-link
          to="/about"
          class="division-cta"
          data-reveal
          data-reveal-delay="2"
        >
          <span>About<br />the<br />Platform →</span>
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
.intro-sub {
  margin-top: 3rem;
  font-family: var(--display);
  font-size: clamp(1.5rem, 3vw, 2.5rem);
  line-height: 1;
  letter-spacing: -0.02em;
  color: var(--forest);
  text-transform: uppercase;
  font-weight: 400;
  opacity: 0.7;
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
.narrative-layout {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 4rem;
  align-items: start;
  max-width: 1100px;
}
.narrative-content {
  display: grid;
  gap: 3rem;
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
.narrative-float {
  margin: 0;
  flex-shrink: 0;
}
.float-image {
  width: 280px;
  height: 360px;
  object-fit: cover;
  border-radius: 2rem;
  box-shadow: 0 30px 70px -20px var(--forest-shadow);
  display: block;
}

/* ---------- gallery (sage) ---------- */
.gallery {
  position: relative;
  background: var(--sage);
  padding: 7rem 2rem 8rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  z-index: 6;
}
.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
  margin-bottom: 3rem;
}
.photo-cell {
  border-radius: 1.5rem;
  overflow: hidden;
  height: 22rem;
  box-shadow: 0 20px 50px -15px var(--forest-shadow);
}
.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.8s var(--ease);
}
.photo-cell:hover .photo-img {
  transform: scale(1.04);
}
.masonry-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  margin-bottom: 3rem;
}
.masonry-cell {
  flex: 1 1 calc(33% - 1rem);
  min-width: 200px;
  border-radius: 1.5rem;
  overflow: hidden;
  box-shadow: 0 20px 50px -15px var(--forest-shadow);
}
.masonry-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  min-height: 18rem;
  transition: transform 0.8s var(--ease);
}
.masonry-cell:hover .masonry-img {
  transform: scale(1.04);
}
.gallery-prose {
  display: grid;
  gap: 2rem;
  max-width: 1100px;
}

/* ---------- cta (forest) ---------- */
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
  .narrative-layout {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  .narrative-block {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  .narrative-float {
    order: -1;
  }
  .float-image {
    width: 100%;
    height: 260px;
  }
  .photo-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  .photo-cell {
    height: 16rem;
  }
  .masonry-cell {
    flex: 1 1 100%;
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
