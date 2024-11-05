<template>
  <div>
    <Header />
    <section class="breadcrumb-area with-overlay"></section>
    <h1 data-aos="fade-right" data-aos-delay="100" style="color: #000; font-weight: 700; font-size: 3rem; font-family: Inter;" class="pt-5 pb-3 text-center">
        Knowledge <span style="color: green; font-weight: 700;">Resources</span>
    </h1>
    <div v-for="item in data.message" :key="item.name" class="text-content">
      <p v-if="item.kr_content">
        {{ item.kr_content }}
      </p>
    </div>
    <knowledgeResource  :data="data" />
    <Footer :data="data" />
  </div>
</template>

<script setup>
import Footer from '@/components/Footer.vue'
import Header from '@/components/Header.vue'
import knowledgeResource from '@/components/KnowledgeResource.vue'

import { ref, onMounted } from 'vue';
import axios from 'axios';
// $.ajax({
//    success:function(){
//   }
// }) 
const data = ref([]);

const fetchData = async () => {
  try {
    const response = await axios.get('/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all');

    if (response.status === 200) {
      console.log("Response ==== ",response.data);
      data.value = response.data;
    } else {
      throw Error('Network response was not ok');
    }
  } catch (error) {
    console.error('Error:', error);
  }
  $.ajax({
   success:function(){
    $('.breadcrumb-area').attr('style', `display:block !important; background:url(${data.value.message.parent_data.breadcrumb_image});`)
   }
  })
};

onMounted(() => {
  fetchData();
});
</script>

<style>
.text-content{
    width: 100%;
    justify-content: center;
    display: flex;
}

.text-content p{
    width: 84%;
    text-align: justify;
    padding: 20px 0;
}
</style>