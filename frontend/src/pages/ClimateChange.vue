<template>
   <div>
     <Header />
     <section class="breadcrumb-area with-overlay"></section>

     <div class="counter-area fix area-padding" id="about">
      <div class="container-fluid" style="padding:0 15px;">
           <div class="section-headline text-center">
            <h2 style="color: #000; font-weight: 700; font-size: 3rem; font-family: Inter;" class="p-5 text-center">About <span style="color: green; font-weight: 700;">Climate Change Division</span></h2>
           </div>
            <ul class="pr-blw-img-list image-list" style="list-style: none; display:flex">
            <div class="par_image">
              <li class="CCDImages" v-if="data.message.parent_data.climate_image1">
                 <img :src="data.message.parent_data.climate_image1" style="width: 100%; height: auto;">
              </li>
            </div>
            <div class="par_image">
              <li class="CCDImages" v-if="data.message.parent_data.climate_image2">
                 <img :src="data.message.parent_data.climate_image2" style="width: 100%; height: auto;">
              </li>
            </div>
            <div class="par_image">
              <li class="CCDImages" v-if="data.message.parent_data.climate_image3">
                 <img :src="data.message.parent_data.climate_image3" style="width: 100%; height: auto;">
              </li>
            </div>
            </ul>
              <h3 v-if="data.message.parent_data.climate_change_title" style="color:#000 !important">
                  {{ data.message.parent_data.climate_change_title }}
              </h3>

                <p class="CCDContent" v-if="data.message.parent_data.climate_change_division_content1">
                  {{ data.message.parent_data.climate_change_division_content1 }}
                </p>  

              <div class="clearfix">
                <li class="side-image" v-if="data.message.parent_data.content_image" style="list-style: none; display: contents; position: relative;">
                  <img :src="data.message.parent_data.content_image" class="col-md-5 float-md-end mb-3 ms-md-3 inner-side-image" alt="..." 
                  style="border-radius: 7px; width: 29%; height: 28rem; padding: 0px !important; object-fit: cover; margin: 0px 0px 37px 22px !important; box-shadow: rgba(0, 0, 0, 0.41) 0px 0px 6px;">
                </li>
                <p class="CCDContent content2" v-if="data.message.parent_data.climate_change_division_content2">
                  {{ data.message.parent_data.climate_change_division_content2 }}
                </p>  
              </div>
              <hr style="height: 30px; color: #000; border-top: 1px solid #000;">
            <div class="climate_image">
              <ul v-for="ccd_image in data.message.parent_data.climate_change_division_images" :key="ccd_image.image" class="climate-image-list" style="list-style: none; display:flex">
                <li v-if="ccd_image.image" style="position: relative; height: 25rem;" class="ccd_list">
                  <img :src="ccd_image.image" style="width: 100%; height: auto;" class="ccd_image">
                  <!-- <div class="overlay"><h5 style="margin-top: 30%;">{{item.ccd_image_title}}</h5></div> -->
                </li>
              </ul>
            </div>
            <br>

            <p class="CCDContent content3" v-if="data.message.parent_data.climate_change_division_content3">
                  {{ data.message.parent_data.climate_change_division_content3 }}
                </p>  
          </div>
     </div>
 
     <router-view />
 
     <Footer :data="data" />
   </div>
 </template>
 <script setup>
   import Footer from '@/components/Footer.vue'
   import Header from '@/components/Header.vue'
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
   setTimeout(()=>{
			var description_1 = $('.content2');
			var description_2 = $('.content3');
      if (description_2.length) {
				var descriptionHTML = description_2.html();
				if (descriptionHTML) {
					var extractedValue = descriptionHTML.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, '');
					description_2.html(extractedValue);
				} else {
					console.error('No HTML content found in #desctiption-1 element.');
				}
			}

			if (description_1.length) {
				var descriptionHTML = description_1.html();
				if (descriptionHTML) {
					var extractedValue = descriptionHTML.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, '');
					description_1.html(extractedValue);
				} else {
					console.error('No HTML content found in #desctiption-1 element.');
				}
			}
			
		}, 100)
  var childField = data._rawValue.message.CCDImages
  for (var item of childField){
    if (item.image){
      console.log("item.image",item.image);
    }
    else{
      console.log("no item found");
    }
  }
 
 };
 
 onMounted(() => {
   fetchData();
 }); 
//  $.ajax({
//    success:function(){
//       $('.breadcrumb-area').attr('style', "display:block !important;")
//    }
//   }) 

  setTimeout(() =>{
    $('.breadcrumb-area').attr('style', `display:block !important; background:url(${data.value.message.parent_data.breadcrumb_image});`)
  }, 1000)
 </script> 
 
 
 <style scoped>

 
 p{
 margin-left: 20px;
 line-height: 1.8;
 }

 .CCDContent{
    margin-left: 20px;
    line-height: 1.8;
    text-align: justify;
    padding: 10px;
}
 
 .climate_image{
    padding: 0px;
    display: flex;
    height: auto;
    width: 100%;
    flex-wrap: wrap;
    gap: 0px 0px;
    justify-content: space-between;
}
.image-list{
    display: flex;
    justify-content: space-evenly;
    margin-bottom: 4px;
}
 .climate-image-list{
    width: 30%;
    height: 100%;
    align-items: center;
    margin: 0px 9px 0px 21px;
    flex-direction: row;
    padding-bottom: 45px;

}
.par_image{
    margin-right: 10px;
    margin-left: 10px;

}
.CCDImages{
    position: relative;
    margin-right: 10px;
    display: flex;
    margin-left: 10px;
    box-shadow: 0 0 6px #00000069;
    border-radius: 7px;
    height: 25rem;
  }
  li.ccd_list {
    height: 24rem;
    display: flex;
    width: 100%;
  }
  img.ccd_image {
    object-fit: cover;
  }

@media (max-width: 576px) {
  .image-list{
    position: relative;
    flex-direction: column;
      margin-right: 10px;
      margin-left: 10px;
      padding: 20px 0px   
  }
  .par_image{
    padding: 20px 0px;
  }
  .side-image{
    margin-right: 10px;
    height: 100%;
    margin-left: 32px;
    display: inline-flex;
    width: 1000px;
  }
  .inner-side-image{
      width: auto !important;
  }
}
</style>