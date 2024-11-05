<template>
  <br>
  <footer data-aos="" data-aos-delay="50" class="footer p-0 bg" style=" color: aliceblue; background-color: #001000 !important;">
   <div class="container-fluid px-5 text-start">
    <div class="row column-both">
        <div class="inner-row">
            <div class="column-one">
                <div class="col-lg-3 col-md-3 col-sm-6 column">
                    <div class="site-logo" style="padding: 12px;">
                      <router-link to='/home'>
                        <img src="../assets/images/Flag_of_the_Solomon_Islands.png" alt="Logo" loading="lazy" class="img-fluid" />
                      </router-link>
                    </div>
                    <p class="text-left text-start"></p>
                </div>
            </div>
            <div class="column-two">
            <div class="col-lg-3 col-md-3 col-sm-6" style="width: auto; column">
              <h3 class="" >Contact Information</h3>
              <!-- <div  v-for="item in data.message" :key="item.name" style="padding: 1rem 2rem;"> -->
                  <div class="media" style="max-width:256px;">
                     <p  v-if="data.message.parent_data.address"> <i class="mr-3 bi bi-geo-alt  b text-start" ></i>{{ data.message.parent_data.address }}</p>
                  </div>
                  <div class="media">
                     <p v-if="data.message.parent_data.email"><i class="mr-3 bi bi-envelope" ></i>{{ data.message.parent_data.email }}</p>
                  </div>
                  <div class="media" v-if="data.message.parent_data.contact_number1 ||  data.message.parent_data.contact_number2 || data.message.parent_data.contact_number3">
                     <p><i class="mr-3 bi bi-telephone "></i>{{ data.message.parent_data.contact_number1 }}, {{ data.message.parent_data.contact_number2 }},</p>
                     <p style="margin-left: 22px;">{{ data.message.parent_data.contact_number3 }}</p>
                  </div>
               <!-- </div> -->
            </div>
                <div class="col-lg-3 col-md-3 col-sm-6 column">
                    <h3 class="">Present Pages</h3>
                    <ul class="list-unstyled mx-4">
                      <li v-for="(routeKey, displayText) in {
                          'Home': 'home',
                          'About Climate Change Division': 'climate-change-division' ,
                          'About MRV Tool': 'about',
                          'Project': 'project',
                          'GHG Summary': 'reports',
                          'Support': 'support',
                          'Knowledge Resource': 'knowledgeresource',
                          'What\'s New?': 'new'
                        }" :key="routeKey">
                          <router-link :to="'/' + routeKey" class="custom-link text-start">
                              <i class="mr-3 bi bi-chevron-right  " style="font-weight: 900 !important;"></i> {{ displayText }}
                          </router-link>
                      </li>
                    </ul>
                </div>
                <div class="col-lg-3 col-md-3 col-sm-6">
                    <h3 class="">Our Partners</h3>
                    <div class="row m-0">
                        <div v-for="(item, index) in data.message" :key="index" class="partners">
                            <div class="col-6 col-sm-5 mb-4 partner-img" v-if="item.partner1">
                                <img :src="item.partner1" alt="" class="img-fluid partner-logo">
                            </div>
                            <div class="col-6 col-sm-5 mb-4 partner-img" v-if="item.partner2">
                                <img :src="item.partner2" alt="" class="bg-white img-fluid partner-logo">
                            </div>
                            <div class="col-6 col-sm-5 mb-4 partner-img" v-if="item.partner3">
                                <img :src="item.partner3" alt="" class="img-fluid partner-logo">
                            </div>
                            <div class="col-6 col-sm-5 mb-4 partner-img" v-if="item.partner4">
                                <img :src="item.partner4" alt="" class="bg-white img-fluid partner-logo">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
<br>
     <hr>
     <div class="copyright text-center pt-4">
        <!-- Copyright © 2024 <a href="#" class="text-light"><strong>mrvtools.com</strong></a> All Rights Reserved -->
        Copyright © 2024 <strong>Solomon Islands Government</strong> - All Rights Reserved
     </div>
     <br>
  </footer>
</template>
<script>
  export default {
    props: {
      data: {
        type: Array,
        required: true,
      },
    },
  };
</script>
<style scoped>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300&display=swap');
  .custom-link {
  color: aliceblue;
  margin-right: 4px;
  line-height: 40px;
  font-size: 14px !important;
  transition: .2s;
  }
  .partner-img{
   width: 50% !important;
  }
  .partner-logo{
   max-width: 100%;
    height: auto;
    aspect-ratio: 4 / 4.5;
    object-fit: contain;
    background-color: #fff;
  }
  .custom-link:hover {
  color: red !important;
  text-decoration: none;
  transition: .2s;
  font-size: 14px !important;
  font-weight: 600;
  }
  .inner-row {
      display: flex;
    justify-content: space-between;
    gap: 70px;
    width: 100%;
    height: auto;
    height: aotu !important;
  }
  
  .column-two {
    display: flex;
    justify-content: space-around;
  }
  @media (min-width: 700px){
    .column{
      width: 33% !important;
    }
  }
  @media (max-width: 400px){
    .column{
      width: 100% !important;
    }
  }
  p,
  li {
  line-height: 1.6;
  color: rgba(240, 248, 255, 0.884);
  font-size: 14px;
  text-align: left;
  font-family: 'Poppins', sans-serif;
  font-weight: lighter;
  }
  h3 {
  font-weight: 600;
  font-size: 18px;
  color: aliceblue;
  }
  img {
  border-radius: 5px;
  }
  .site-logo{
  width: 121px !important;
  /* background-color: #fff; */
  }
  .bg{
  background-image: url('../assets/images/footer.png');
  padding: 0 !important;
  }
  img{
  background-color: none !important;
  }

  @media (max-width: 576px) {
   .inner-row {
      display: flex;
      gap: 7px;
      width: 100%;
      height: auto !important;
      flex-direction: column;
   }  
   .column-one {
    display: flex;
    flex-direction: column;

   }
   .partners{
      display: contents;
   }
  .column-two {
    display: flex;
    flex-direction: column;

   }
  }
</style>