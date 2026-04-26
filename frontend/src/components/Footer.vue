<script setup>
// `data` accepted to keep parity with legacy `<Footer :data="..." />` callers.
// `flush` lets legacy pages opt out of the editorial overlap (negative margin + radius).
defineProps({
  data: { type: [Object, Array], default: () => ({}) },
  flush: { type: Boolean, default: false },
})

const onSubscribe = (e) => {
  const input = e.target.querySelector('input')
  input.value = ''
  input.placeholder = 'Subscribed →'
}
</script>

<template>
  <footer class="ed-footer" :class="{ 'is-flush': flush }">
    <div class="ed-footer-grid">
      <div class="ed-news">
        <span class="ed-eyebrow">Field Dispatch</span>
        <h3>Slow news. From the islands.</h3>
        <form class="ed-signup" @submit.prevent="onSubscribe">
          <label class="ed-sr-only" for="ed-news-email">Email address</label>
          <input
            id="ed-news-email"
            type="email"
            aria-label="Email address"
            placeholder="Your email address"
            required
          />
          <button type="submit" aria-label="Subscribe">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="square"
            >
              <path d="M5 12h14M13 5l7 7-7 7" />
            </svg>
          </button>
        </form>
      </div>

      <div
        v-if="
          data?.message?.parent_data?.address ||
          data?.message?.parent_data?.email ||
          data?.message?.parent_data?.contact_number1 ||
          data?.message?.parent_data?.contact_number2 ||
          data?.message?.parent_data?.contact_number3
        "
        class="ed-contact"
      >
        <span class="ed-eyebrow">Contact</span>
        <h4 class="ed-contact-heading">Honiara</h4>
        <p v-if="data?.message?.parent_data?.address" class="ed-contact-line">
          {{ data.message.parent_data.address }}
        </p>
        <p v-if="data?.message?.parent_data?.email" class="ed-contact-line">
          <span class="ed-contact-label">Email</span>
          <a :href="`mailto:${data.message.parent_data.email}`">{{
            data.message.parent_data.email
          }}</a>
        </p>
        <p
          v-if="data?.message?.parent_data?.contact_number1"
          class="ed-contact-line"
        >
          <span class="ed-contact-label">Tel</span>
          <a :href="`tel:${data.message.parent_data.contact_number1}`">{{
            data.message.parent_data.contact_number1
          }}</a>
        </p>
        <p
          v-if="data?.message?.parent_data?.contact_number2"
          class="ed-contact-line"
        >
          <span class="ed-contact-label">Tel</span>
          <a :href="`tel:${data.message.parent_data.contact_number2}`">{{
            data.message.parent_data.contact_number2
          }}</a>
        </p>
        <p
          v-if="data?.message?.parent_data?.contact_number3"
          class="ed-contact-line"
        >
          <span class="ed-contact-label">Tel</span>
          <a :href="`tel:${data.message.parent_data.contact_number3}`">{{
            data.message.parent_data.contact_number3
          }}</a>
        </p>
      </div>

      <div class="ed-links">
        <h4>Index</h4>
        <router-link to="/project">Programs</router-link>
        <router-link to="/reports">Inventory</router-link>
        <router-link to="/reports">Finance Ledger</router-link>
        <router-link to="/new">Field Notes</router-link>
        <router-link to="/knowledgeresource">Issue Archive</router-link>
      </div>

      <div class="ed-links">
        <h4>The Office</h4>
        <router-link to="/climate-change-division"
          >Climate Division</router-link
        >
        <router-link to="/about">MECDM Honiara</router-link>
        <router-link to="/support">Press &amp; Inquiries</router-link>
        <a href="#">Open Data API</a>
        <a href="#">Methodology</a>
      </div>
    </div>

    <div class="ed-mega" aria-hidden="true">iMRV</div>

    <div class="ed-mark">
      <span>© 2026 Government of Solomon Islands · MECDM</span>
      <div class="ed-legal">
        <a href="#">Privacy</a>
        <a href="#">Accessibility</a>
        <a href="#">Source</a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.ed-footer {
  position: relative;
  background: #01472e;
  color: #ccd5ae;
  padding: 7rem 2rem 2rem;
  margin-top: -5rem;
  border-radius: 5rem 5rem 0 0;
  overflow: hidden;
  font-family: 'Inter', system-ui, sans-serif;
}
.ed-footer.is-flush {
  margin-top: 0;
  border-radius: 0;
}
.ed-footer::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse at 80% 0%,
    rgba(204, 213, 174, 0.08),
    transparent 50%
  );
  pointer-events: none;
}

.ed-footer-grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 3rem;
}
.ed-news {
  grid-column: span 5;
}
.ed-contact {
  grid-column: span 3;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.ed-eyebrow {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  color: #c1cba4;
  margin-bottom: 1.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
}
.ed-eyebrow::before {
  content: '';
  width: 28px;
  height: 1px;
  background: #c1cba4;
}
.ed-news h3 {
  font-family: 'Anton', 'Helvetica Neue', sans-serif;
  font-size: clamp(2.5rem, 5vw, 5rem);
  line-height: 0.95;
  letter-spacing: -0.02em;
  color: #fefae0;
  text-transform: uppercase;
  max-width: 11ch;
  margin: 0 0 2rem;
  font-weight: 400;
}

.ed-contact-heading {
  font-family: 'Anton', 'Helvetica Neue', sans-serif;
  font-size: clamp(1.75rem, 2.4vw, 2.4rem);
  line-height: 0.95;
  letter-spacing: -0.01em;
  color: #fefae0;
  text-transform: uppercase;
  margin: 0 0 1.25rem;
  font-weight: 400;
}
.ed-contact-line {
  font-size: 12px;
  line-height: 1.55;
  color: #fefae0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.ed-contact-line a {
  color: #fefae0;
  text-decoration: none;
  transition: color 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.ed-contact-line a:hover {
  color: #c1cba4;
}
.ed-contact-label {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  color: #c1cba4;
}

.ed-signup {
  display: flex;
  align-items: flex-end;
  gap: 1.5rem;
  max-width: 540px;
}
.ed-signup input {
  flex: 1;
  background: transparent;
  border: 0;
  border-bottom: 1px solid rgba(204, 213, 174, 0.4);
  padding: 0.85rem 0;
  font-family: inherit;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: #fefae0;
  outline: none;
  transition: border-color 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.ed-signup input::placeholder {
  color: rgba(204, 213, 174, 0.6);
  letter-spacing: 0.3em;
}
.ed-signup input:focus {
  border-color: #fefae0;
}
.ed-signup input:focus-visible {
  border-bottom-color: #fefae0;
}
.ed-signup button {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: 999px;
  background: #fefae0;
  color: #01472e;
  border: 0;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition:
    transform 0.5s cubic-bezier(0.16, 1, 0.3, 1),
    background 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.ed-signup button:hover {
  transform: rotate(-45deg);
  background: white;
}
.ed-signup button:focus-visible,
.ed-links a:focus-visible {
  outline: 2px solid #fefae0;
  outline-offset: 4px;
}
.ed-signup button svg {
  width: 20px;
  height: 20px;
}

.ed-links {
  grid-column: span 2;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.ed-links h4 {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  color: #c1cba4;
  margin: 0 0 1rem;
}
.ed-links a {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: #fefae0;
  text-decoration: none;
  transition:
    color 0.3s cubic-bezier(0.16, 1, 0.3, 1),
    padding-left 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  width: fit-content;
}
.ed-links a:hover {
  padding-left: 1rem;
  color: #c1cba4;
}
.ed-links a:hover::before {
  content: '\2192';
  position: absolute;
  left: 0;
  transform: translateX(-4px);
}

.ed-mega {
  position: relative;
  font-family: 'Anton', 'Helvetica Neue', sans-serif;
  font-size: 33vw;
  line-height: 0.75;
  letter-spacing: -0.05em;
  color: #fefae0;
  text-transform: uppercase;
  text-align: center;
  margin: 4rem 0 -1rem;
  opacity: 0.95;
  pointer-events: none;
  user-select: none;
}

.ed-mark {
  position: relative;
  margin-top: 6rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(204, 213, 174, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: rgba(204, 213, 174, 0.6);
}
.ed-mark a {
  color: inherit;
  text-decoration: none;
}
.ed-mark a:hover {
  color: #fefae0;
}
.ed-legal {
  display: flex;
  gap: 2rem;
}

.ed-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 900px) {
  .ed-news,
  .ed-links,
  .ed-contact {
    grid-column: span 12;
  }
  .ed-mark {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  .ed-mega {
    font-size: 45vw;
  }
}

@media (prefers-reduced-motion: reduce) {
  .ed-footer,
  .ed-signup input,
  .ed-signup button,
  .ed-links a {
    transition: none !important;
    animation: none !important;
  }
}
</style>
