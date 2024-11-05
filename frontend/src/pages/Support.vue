<template>
  <div>
    <Header />
    <section class="breadcrumb-area with-overlay"></section>
    <div class="counter-area fix area-padding" id="about">
      <div class="container-fluid" data-aos="fade-right" data-aos-delay="100">
        <div class="row" data-aos="fade-right" style="padding: 0 10px;" data-aos-delay="100">
          <h2 style="color: #000; font-weight: 700; font-size: 3rem; font-family: Inter;" class="p-5 text-center"> Support</h2>

          <div class="col-md-12 col-sm-12 col-xs-12 wow fadeInLeft" data-wow-delay="0.3s">
            <div v-for="item in data.message" :key="item.name">
              <div v-if="item.support_main_heading">
                <h3 style="color: #000 !important;" class="bulletin_heading">{{ item.support_main_heading }}</h3>
              </div>
              <p v-if="item.main_paragraph" class="listItem">
                {{ item.main_paragraph }}
              </p>
              

              <div v-if="item.bulletin_heading1">
                <h3 class="bulletin_heading">{{ item.bulletin_heading1 }}</h3>
              </div>
              <div v-if="data.message.parent_data.bulletin_content1">
                <div v-for="bulletinItem in item.bulletin_content1" :key="item.name">
                  <li v-if="bulletinItem.content" style="position: relative" class="listItem">
                    {{ bulletinItem.content }}
                  </li>
                </div>
              </div>
              
              <li v-if="item.support_image1" class="support_image" >
                <img :src="item.support_image1" style="width: 70%; height: auto;" class="supp_image">
              </li>
              

              <div v-if="item.bulletin_heading2">
                <h3 class="bulletin_heading">{{ item.bulletin_heading2 }}</h3>
              </div>
              <div v-if="data.message.parent_data.bulletin_content2">
                <div v-for="bulletinItem in item.bulletin_content2" :key="item.name">
                  <li v-if="bulletinItem.content" style="position: relative" class="listItem">
                    {{ bulletinItem.content }}
                  </li>
                </div>
              </div>
              <li v-if="item.support_image2" class="support_image" >
                <img :src="item.support_image2" style="width: 70%; height: auto;" class="supp_image">
              </li>
              

              <div v-if="item.bulletin_heading3">
                <h3 class="bulletin_heading">{{ item.bulletin_heading3 }}</h3>
              </div>
              <div v-if="data.message.parent_data.bulletin_content3">
                <div v-for="bulletinItem in item.bulletin_content3" :key="item.name">
                  <li v-if="bulletinItem.content" style="position: relative" class="listItem">
                    {{ bulletinItem.content }}
                  </li>
                </div>
              </div>
              <li v-if="item.support_image3" class="support_image" >
                <img :src="item.support_image3" style="width: 70%; height: auto;" class="supp_image">
              </li>
              

              <div v-if="item.bulletin_heading4">
                <h3 class="bulletin_heading">{{ item.bulletin_heading4 }}</h3>
              </div>
              <div v-if="data.message.parent_data.bulletin_content4">
                <div v-for="bulletinItem in item.bulletin_content4" :key="item.name">
                  <li v-if="bulletinItem.content" style="position: relative" class="listItem">
                    {{ bulletinItem.content }}
                  </li>
                </div>
              </div>
              <li v-if="item.support_image4" class="support_image" >
                <img :src="item.support_image3" style="width: 70%; height: auto;" class="supp_image">
              </li>
              

            </div>
          </div>
        </div>
      </div>
    </div>

    <router-view />

    <Footer :data="data" />
  </div>
 </template>
 <script setup>
   import Footer from '@/components/Footer.vue'
   import Header from '@/components/Header.vue'
 // import { createListResource } from 'frappe-ui';
 import { ref, onMounted } from 'vue';
 import axios from 'axios';
 const data = ref([]);
 
 const fetchData = async () => {
   try {
     const response = await axios.get('/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all');
     console.log("response", response) 
     console.log("response.data",response.data.message.parent_data)
     if (response.status === 200) {
       data.value = response.data;
     } else {
       throw new Error('Network response was not ok');
     }
   } catch (error) {
     console.error('Error:', error);
   }
  //  var values = data
  var childField = data._rawValue.message.CCDImages
  for (var item of childField){
    if (item.ccd_image){
      console.log("item.ccd_image",item.ccd_image);
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
 
 
 <style scoped>
 .supp_image{
    width: 70%;
    height: auto !important;
    overflow: hidden;
    object-fit: cover;
    box-shadow: 0 0 6px #00000069;
 }
 .support_image{
    position: relative;
    margin-right: 10px;
    margin-left: 10px;
    padding: 30px 0px;
    justify-content: center;
    display: flex;
    height: auto;
    width: 100%;
  }

 .bulletin_heading{
  color: #000; font-weight: 700;
 }
.listItem{
    line-height: 1.5;
    padding: 5px 53px;
    text-align: justify;
  }
 .content{
  color: #000; 
  font-weight: 500;
  font-size: 14px;
  line-height: 1.5;

 }


 
 p{
 /* margin-left: 20px; */
 line-height: 1.8;
 }
 
 .climate_image{
    padding: 15px;
    display: flex;
    height: auto;
    width: 100%;
    flex-wrap: wrap;
    gap: 0px 11px;
    justify-content: flex-start;
}
 .climate-image-list{
    width: 30%;
    height: 100%;
    align-items: center;
    margin: 0px 9px 0px 21px;
    flex-direction: row;
    padding-bottom: 45px;
}
@media (max-width: 576px) {
  .support_image{
    position: relative;
    padding: 30px 0;
    justify-content: center;
    display: flex;
    height: auto;
    width: 100%;
  }
  .listItem{
    line-height: 1.5;
    padding: 5px 22px;
    text-align: justify;
  }
  .col-md-12{
    padding: 0 !important;
  }
}
</style>