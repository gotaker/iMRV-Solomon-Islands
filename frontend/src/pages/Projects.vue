<template >
   <Header />
   <section class="breadcrumb-area with-overlay"></section>

   <ProjectComponent :data="data" />
   <Footer :data="data" />
</template>
<script setup>
import Footer from '@/components/Footer.vue'
import Header from '@/components/Header.vue'
import ProjectComponent from '@/components/ProjectComponent.vue'

import { ref, onMounted } from 'vue';
import axios from 'axios';
const data = ref([]);

const fetchData = async () => {
  try {
    const response = await axios.get('/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all');

    if (response.status === 200) {
      data.value = response.data;
    } else {
      throw new Error('Network response was not ok');
    }
  } catch (error) {
    console.error('Error:', error);
  }
  var values = data
  var childField = data._rawValue.message.child_table_data
  for (var item of childField){
    if (item.image){
      console.log("item",item.image);
    }
    else{
      console.log("no item found");
    }
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
