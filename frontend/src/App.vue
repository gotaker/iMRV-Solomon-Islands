<template>
  <div class="templa">
    <div class="ed-noise" aria-hidden="true"></div>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const data = ref([])
// const partnerLogos = ref([]);

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
    console.log('Check response', response)
    var values = data._rawValue.message.parent_data
    var childField = data._rawValue.message.child_table_data

    for (var item of childField) {
      if (item.image) {
        console.log('item', item.image)
      } else {
        console.log('no item found')
      }
    }

    console.log('responseee', values)
  } catch (error) {
    console.error('Error:', error)
  }
}

// const fetchPartnerLogos = async () => {
//   try {
//     const response = await axios.get('http://your-api-url-for-partner-logos');
//     if (response.status === 200) {
//       partnerLogos.value = response.data; // Assuming your API returns an array of partner logos
//     } else {
//       throw new Error('Network response was not ok');
//     }
//   } catch (error) {
//     console.error('Error:', error);
//   }
// };

onMounted(() => {
  fetchData()
  // fetchPartnerLogos();
})
</script>
<style>
/* global editorial noise overlay — fixed across every route */
.ed-noise {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  opacity: 0.06;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.6 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
}

@media (prefers-reduced-motion: reduce) {
  .ed-noise {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

.overlay {
  position: absolute;
  bottom: 0;
  color: #f1f1f1;
  width: 100%;
  transition: 0.2s ease;
  opacity: 0;
  color: #fff;
  font-size: 20px;
  border-radius: 4px;
  padding: 20px;
  text-align: center;
  height: 100%;
  background: linear-gradient(rgb(0 0 0 / 28%), rgba(0, 0, 0, 0.431));
}

.overlay:hover {
  opacity: 1;
}

a,
p,
h4,
h5,
h6 {
  font-family: 'Inter', sans-serif;
}

.all-banner img {
  display: none; /* Hide the image tag, as it's not needed for the background */
}

@media (max-width: 768px) {
  .img {
    /* Your styles for .img at max-width: 576px */
    position: relative;
    background-color: #00220012;
    height: 19rem;
  }
  .report-image {
    width: 94%;
    height: 120% !important;
    margin: auto;
    position: unset;
  }
}
</style>
