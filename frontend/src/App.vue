<template>

  <div class="templa">
    <router-view />
  </div>
</template>

<script>
 import AOS from 'aos';
 
 import { ref, onMounted } from 'vue';
import axios from 'axios';

const data = ref([]);
// const partnerLogos = ref([]);

const fetchData = async () => {
  try {
    const response = await axios.get('/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all');

    if (response.status === 200) {
      data.value = response.data;
    } else {
      throw new Error('Network response was not ok');
    }
    console.log("Check response", response);

  } catch (error) {
    console.error('Error:', error);
  }
  var values = data._rawValue.message.parent_data
  var childField = data._rawValue.message.child_table_data

  for (var item of childField){
    if (item.image){
      console.log("item",item.image);
    }
    else{
      console.log("no item found");
    }
  }

  console.log("responseee", values);
};

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
  fetchData();
  // fetchPartnerLogos();
});

 

 AOS.init({
   duration: 300,
   offset: 100,
   once: true,
 });
</script>
<!-- 
.breadcrumb-area {
  position: relative;
  background: url('http://environment.g oappssolutions.com/wp-content/uploads/2021/11/all.jpg') no-repeat center center fixed;
  background-size:cover;
  background-attachment: fixed;
  height: 300px; /* Set the desired fixed height */

}
 -->
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300&family=Poppins:wght@300&display=swap');
.overlay {
  position: absolute;
  bottom: 0;
  color: #f1f1f1;
  width: 100%;
  transition: .2s ease;
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

a, p, h4, h5, h6{
  font-family: 'Inter', sans-serif;
  font-family: 'Poppins', sans-serif;
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