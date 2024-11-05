<template>
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

          <div class="container-fluid">
            <div class="parent_pops">
              <a class="pop" @click="openModal(data.message.parent_data.report_image)">
                <img :src="data.message.parent_data.report_image" id="myImg" class="pro_image">
                <div class="overlay"></div>

              </a>
              <a class="pop" @click="openModal(data.message.parent_data.report_image1)">
                <img :src="data.message.parent_data.report_image1" id="myImg" class="pro_image">
                <div class="overlay"></div>

              </a>
              <a class="pop" @click="openModal(data.message.parent_data.report_image2)">
                <img :src="data.message.parent_data.report_image2" id="myImg" class="pro_image">
                <div class="overlay"></div>

              </a>
            </div>

            <div id="myModal" class="modal" @click="closeModal">
              <span class="close">&times;</span>
              <img class="modal-content" id="img01">
              <div id="caption"></div>
            </div>
          </div>
        </div>

        </div>
</template>
<script>
    import { ref, onMounted } from 'vue';
      import axios from 'axios';
export default {
  props: {
    data: {
      type: Array,
      required: true,
    },
  },
};

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
  };

  const openModal = (src, alt) => {
    const modal = document.getElementById("myModal");
    const modalImg = document.getElementById("img01");
    const captionText = document.getElementById("caption");
    $('.column-two')[0].style.display='none';
    $('.column-one')[0].style.display='none';
    $('.report-top-ground')[0].style.height='100vh';

    modal.style.display = "block";
    modalImg.src = src;
    captionText.innerHTML = alt;
  };

  const closeModal = () => {
    const modal = document.getElementById("myModal");
    modal.style.display = "none";
    $('.column-two')[0].style.display='block';
    $('.column-one')[0].style.display='block';
    $('.report-top-ground')[0].style.height='';
  };

  onMounted(() => {
    fetchData();
  });
</script>
