<template>
  <div>
     <Header />
     <section class="breadcrumb-area with-overlay"></section>
     <div
        data-aos="fade-right"
        data-aos-delay="50"
        class="about-area report-section about-2 fix wow fadeInUp"
        data-wow-delay="0.3s"
        id="reports"
        >
        <div class="container-fluid report-top-ground">
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

            <!-- <div id="myModal" :class="{ 'full-page-modal': isModalOpen }" @click="closeModal">
              <span class="close">&times;</span>
              <img class="modal-content" id="img01">
            </div> -->
          </div>
        </div>

        </div>
     </div>
     <div id="myModal" :class="{ 'full-page-modal': isModalOpen }" @click="closeModal">
      <span class="close">&times;</span>
      <img class="modal-content" id="img01">
    </div>
     <Footer :data="data" />
</template>
<script setup>
  import Footer from '@/components/Footer.vue'
  import Header from '@/components/Header.vue'
  import { ref, onMounted } from 'vue';
  import axios from 'axios';
  // $.ajax({
  //  success:function(){
  //     $('.breadcrumb-area').attr('style', "display:block !important;")
  //  }
  // })
 
const data = ref([]);
const isModalOpen = ref(false);

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
  $.ajax({
			success:function(){
				$('.breadcrumb-area').attr('style', `display:block !important; background:url(${data.value.message.parent_data.breadcrumb_image});`)
			}
		})
};

const openModal = (src) => {
  const modal = document.getElementById("myModal");
  const modalImg = document.getElementById("img01");
  modal.style.display = "block";
  $('.modal-content').attr("style","display:block;");
  console.log("kishore")
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
</script>
<style scoped>


</style>
