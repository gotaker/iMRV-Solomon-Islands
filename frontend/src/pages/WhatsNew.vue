<template>
  <Header />
  <div class="content">
    <h1 data-aos="fade-right" data-aos-delay="100" style="color: #000; font-weight: 700; font-size: 3rem; font-family: Inter;" class="pt-5 pb-3 text-center">
      What's <span style="color: green; font-weight: 700;">New?</span>
    </h1>
    <div v-if="data.add_new_content.length != 0" class="whats-new-section">
      <div v-for="item in data.add_new_content" :key="item.title" class="news-item">
        <div class = "news-header">

          <img v-if="item.add_image" :src="item.add_image" alt="News Image" class="news-image">
          <img v-else src="../assets/images/no_image.png" alt="News Image" class="news-image">
          <div class="news-content">
            <h3 class="news-title">{{ item.title }}</h3>
            <p class="news-description">{{ item.content }}</p>
          </div>
        </div>
        <div class="news-footer">
          <p class="posting-date" style= "color:#a8a8a8;">{{ item.creation }}  </p>
          <a v-if="item.add_url" :href="item.add_url" class="read-more" Target="_blank">  Read More</a>
        </div>
      </div>
  
      <!-- Modal -->
      <div id="myModal" class="modal" v-if="isModalOpen">
        <span class="close" @click="closeModal">&times;</span>
        <img class="modal-content" :src="modalImage" id="img01">
      </div>
    </div>
    <div v-else>No data Found</div>
  </div>
  <Footer  :data="footer_data" />
  </template>
  <script setup>
  import { ref, onMounted } from 'vue';
  import axios from 'axios';
  import Footer from '@/components/Footer.vue'
  import Header from '@/components/Header.vue'
  
  const data = ref([]);
  const footer_data = ref([]);
  const isModalOpen = ref(false);
  
  const fetchData = async () => {
    try {
      const response = await axios.get('/api/method/mrvtools.mrvtools.doctype.mrvfrontend.mrvfrontend.get_all');
      if (response.status === 200) {
        footer_data.value = response.data
        data.value = response.data.message;
        console.log("Dta == ",data.value.add_new_content);
        let formatter = new Intl.DateTimeFormat('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
        for (let i = 0; i < data.value.add_new_content.length; i++) {
            let creation = data.value.add_new_content[i].date;
            let date = new Date(creation);

            // Use frappe.datetime to format the date
            let formattedDate = formatter.format(date);

            // Update the creation date in the  array
            data.value.add_new_content[i].creation = formattedDate;
        }
        console.log("Dta222 == ",data.value.add_new_content);
      } else {
        throw new Error('Network response was not ok');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };
  
  const openModal = (src) => {

    isModalOpen.value = true;
  };
  
  const closeModal = () => {
    isModalOpen.value = false;
  };
  
  onMounted(() => {
    fetchData();
  });
  </script>
  <style>
  /* Your existing styles */
  body {
    font-family: Arial, sans-serif;
    background-color: #f4f4f4;
    margin: 0;
    padding: 0;
  }
  .content{
    /* box-shadow: 0 2px 4px #0000001a;  */
    display: flex;
    gap: 30px;
      flex-direction: column;
    width: 100%;
    align-items: center;
  }
  .whats-new-section {
    width: 90%;
    flex-direction: column;
    background-color: #fff;
    padding: inherit;
    border-radius: 8px;
    box-shadow: 0 2px 4px #0000001a;
    align-content: center;
}
  
  .whats-new-section h2 {
    position: relative;
    top: 20px;
    margin-bottom: 40px;
    text-align: center;
    color: #333;
  }
  
  .news-item {
    display: flex;
    align-items: flex-start;
    border-bottom: 1px solid #ddd;
    padding: 30px 30px;
    flex-direction: column;
  }
  .news-header{
    display: flex;
    flex-direction: row;
  }
  
  .news-item:last-child {
    border-bottom: none;
  }
  
  .news-image {
    width: 335px;
    height: 250px;
    -o-object-fit: cover;
    object-fit: cover;
    margin-right: 20px;
    border-radius: 8px;
  }
  
  .news-content {
    flex: 1;
  }
  .news-footer{
    gap:10px;
    display: flex;
    min-width: 100%;
    justify-content: flex-end
  }
  
  .news-title {
    font-size: 1.4em;
    margin: 0;
    color: #188a18;
    padding: 18px 0px !important;
    text-align: justify;
  }
 
  
  .news-date {
    font-size: 0.9em;
    color: #666;
    margin: 5px 0;
  }
  
  .news-description {
    font-size: 1em;
    color: #333;
    margin: 10px 0;
    text-wrap: wrap;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 6;
    -webkit-box-orient: vertical;
    text-align: justify;
  }
  
  .read-more {
    text-decoration: none;
    color: #5b975b;
    font-weight: bold;
  }
  
  .read-more:hover {
    text-decoration: underline;
    color: #008000 !important;
  }
  .read-more:focus {
    color: #008000 !important;
  }
  
  /* Modal styles */
  .modal {
    display: flex;
    align-items: center;
    justify-content: center;
    position: fixed;
    z-index: 1;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
    background-color: rgba(0, 0, 0, 0.9);
  }
  
  .modal-content {
    margin: auto;
    display: block;
    width: 80%;
    max-width: 700px;
  }
  
  .close {
    position: absolute;
    top: 15px;
    right: 35px;
    color: #fff;
    font-size: 40px;
    font-weight: bold;
    transition: 0.3s;
  }
  
  .close:hover,
  .close:focus {
    color: #bbb;
    text-decoration: none;
    cursor: pointer;
  }
  @media (max-width: 600px) {
    .news-header {
      flex-direction: column;
    }
    @media only screen and (max-width: 600px) {
   .list_image{
      display:flex;
      height: 200px !important;
   }
   .pr-blw-img-list{
      flex-direction: column;
      gap: 24px;
   }

   .tab_parent{
       display: flex!important;
       gap: 5px!important;
       margin: 0!important;
       justify-content: space-between;
       flex-wrap: nowrap!important;
       overflow: auto!important;
   }
   .tab_child{
      flex: 0 0 auto;
   }
   /* .nav-item a{
    margin: 0!important;
    font-size: 13px!important;
    padding: 5px 10px !important;
    border: 1px solid #ddd!important;
   } */
   .tab-menu{
      margin: auto;
      margin: 0!important;
      width: 100%!important;
      padding-inline: 13px!important;
   }
   .tab-content{
      padding: 0!important;
      margin-top: 25px!important;
   }
}
}

  </style>
  
  
  