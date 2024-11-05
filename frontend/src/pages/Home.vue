<template >
  <Header />
  <div id="carouselExampleIndicators" class="carousel slide" data-bs-ride="carousel">
    <div class="carousel-inner">
      <div v-for="(item, index) in data.message.parent_data.carousel_image" :key="index" class="carousel-item" :class="{ active: index == 0 }">
        <div class="card mx-0 image-overlay cus-card" style="height: 50rem;">
          <img v-if="item.image" :src="item.image" class="d-block w-100 h-100 carousel_image" alt="...">
        </div>
      </div>
    </div>
    <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="prev">
      <i style="font-size: 35px;" class="bi bi-chevron-left bi-2x"></i>
      <span class="visually-hidden">Previous</span>
    </button>
    <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="next">
      <i style="font-size: 35px;" class="bi bi-chevron-right bi-2x"></i>
      <span class="visually-hidden">Next</span>
    </button>

  </div>
  
  <div>
     <ProjectComponent :data="data" />
     <!-- <hr style="border-color: #8f8f8f;"> -->

     <div>
     <div
        data-aos="fade-right"
        data-aos-delay="50"
        class="about-area report-section about-2 fix wow fadeInUp"
        data-wow-delay="0.3s"
        id="reports"
        >
        <div class="container-fluid report-top-ground" style="border-bottom: 1px solid #f0f0f0;">
          <div class="pattern-background">
              <img src="../assets/images/pattern.png" style="height: 100%; width: 100%;">
          </div>


          <h1 style="color: #000; font-weight: 700; font-size: 3rem; font-family: Inter;" class="p-5 text-center">
             National <span style="color: green; font-weight: 700;">GHG</span> Inventory
          </h1>

          <div class="container-fluid" style="padding-bottom: 25px;">
            <div class="parent_pops">
              <a class="pop" @click="openModal(data.message.parent_data.report_image)">
                <img :src="data.message.parent_data.report_image" id="myImg" class="rep_image">
                <div class="overlay"></div>

              </a>
              <a class="pop" @click="openModal(data.message.parent_data.report_image1)">
                <img :src="data.message.parent_data.report_image1" id="myImg" class="rep_image">
                <div class="overlay"></div>

              </a>
              <a class="pop" @click="openModal(data.message.parent_data.report_image2)">
                <img :src="data.message.parent_data.report_image2" id="myImg" class="rep_image">
                <div class="overlay"></div>

              </a>
            </div>

          </div>
        </div>

        </div>
     </div>

     <!-- Knowledge Resource Carousel -->
     <div>
      <hr style="border-color: 1px #8f8f8f;">   
      <h1 data-aos="fade-right" data-aos-delay="100" style="color: #000; font-weight: 700; font-size: 3rem; font-family: Inter;" class="pt-5 pb-3 text-center">
            Knowledge <span style="color: green; font-weight: 700;">Resources</span>
         </h1>
        <knowledgeResource  :data="data" />
        <br>
     </div>
  </div>
  <div id="myModal" :class="{ 'full-page-modal': isModalOpen }" @click="closeModal">
    <span class="close">&times;</span>
    <img class="modal-content" id="img01">
  </div>
  <Footer  :data="data" />
</template>
<script setup>
  import Footer from '@/components/Footer.vue'
  import Header from '@/components/Header.vue'
  import Report from '@/components/Report.vue'
  import knowledgeResource from '@/components/KnowledgeResource.vue'
  import ProjectComponent from '@/components/ProjectComponent.vue'
  import { ref, onMounted } from 'vue';
  import axios from 'axios';
  
  const data = ref([]);
const isModalOpen = ref(false);
  
  const fetchData = async () => {
    try {
      const response = await axios.get('/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all');
  
      if (response.status === 200) {
        data.value = response.data;
        console.log("Dta = ",data)
      } else {
        throw new Error('Network response was not ok');
      }
    } catch (error) {
      console.error('Error:', error);
    }
    var values = data._rawValue.message.parent_data
    var field = values.heading
    var childField = data._rawValue.message.child_table_data
    for (var item of childField){
      if (item.image){
        console.log("item",item.image);
      }
      else{
        console.log("no item found");
      }
    }
  };

  const openModal = (src) => {
    const modal = document.getElementById("myModal");
  const modalImg = document.getElementById("img01");
  modal.style.display = "block";
  $('.modal-content').attr("style","display:block;");
  modalImg.src = src;
  isModalOpen.value = true;
};

const closeModal = () => {
  const modal = document.getElementById("myModal");
  modal.style.display = "none";
  isModalOpen.value = false;
};

onMounted(() => {
  fetchData();
});  
$.ajax({success: ()=> {
  setTimeout(() => {
    $('.carousel').carousel({
      interval: 5000
    })
  }, 1000);
 $('.breadcrumb-area').attr('style', "display:none !important;")
}})
</script>
<style>
.pop{
  cursor: pointer;
}
 .breadcrumb-area{
   display: none !important;
  }
  .card-link:hover .card {
  transition: .2s;
  box-shadow: 4px 8px 14px 4px rgba(0, 0, 0, 0.098); 
  }
  .carousel_image{
   border-radius:0 !important;
   object-fit: cover;
  }

  
  .cus-card{
  transition: .2s;
  box-shadow: 0px 0px 10px #0000002e;
  border-radius: 10px;
  border: none !important;
  }
  .cus-card:hover{
  transition: .2s;
  box-shadow: 0 0 10px #00000056;
  }     
  .img {
  position: relative;
  background-color: #00220012;
  height: auto;
  }

  @media (max-width: 768px) {
  .img{
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
  .cus-card {
  text-overflow: hidden;
  width: 100%;
  margin-right: 10px;
  }
  .text-center{
  font: inline;
  }
  .custom-col{
  padding: 10px !important;
  display: table !important;
  }
  .container{
  width: 90%;
  }
  }
  @media only screen and (max-width: 600px) {
  .custom-col {
  flex: 0 0 calc(50% - 20px); 
  margin: 10px;
  }
  }
</style>