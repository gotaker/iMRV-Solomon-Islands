<template>
    <div>
      <h1 data-aos="fade-right" data-aos-delay="100" style="color: #000; font-weight: 700; font-size: 3rem; font-family: Inter;" class="pt-5 pb-3 text-center">
        Knowledge <span style="color: green; font-weight: 700;">Resources</span>
      </h1>
      <div data-aos="fade-right" data-aos-delay="100" id="carouselExampleControls" class="carousel carousel-dark slide" data-bs-ride="carousel">
        <div class="carousel-inner">
          <div class="carousel-item pt-4 pb-3 active">
            <div class="container">
              <div class="row" style="width: 98%; margin-left: 5px;">
                <div v-for="item in data.message.child_table_data" :key="item.name" class="col col-md-3 col-sm-3 col-xs-12 custom-col">
                  <div v-if="item.image" class="card mx-0 image-overlay cus-card" style="border-radius: none;">
                    <a :href="item.document" class="cus-text mobile-hidden" style="text-decoration: none; color: #000; font-weight: 900;">
                      <img :src="item.image" class="card-img-top" style=" border-radius: 6px;" alt="..." />
                      <div v-if="item.link_name" class="overlay">
                        <h5 style="justify-content: center;    place-items: center; font-family: serif; padding: inherit; margin: revert;">{{ item.link_name }}</h5>
                      </div>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="carousel-item pt-4 pb-3">
            <div class="container">
              <div class="row" style="width: 98%; margin-left: 5px;">
                <div v-for="item in data.message.child_table_data2" :key="item.name" class="col col-md-3 col-sm-3 col-xs-12 custom-col">
                  <div v-if="item.image" class="card mx-0 image-overlay cus-card" style="border-radius: none;">
                    <a :href="item.document" class="cus-text mobile-hidden" style="text-decoration: none; color: #000; font-weight: 900;">
                      <img :src="item.image" class="card-img-top" style="position:relative; border-radius: 6px;" alt="..." />
                      <div v-if="item.link_name" class="overlay">
                        <h5 style="justify-content: center;    place-items: center; font-family: serif; padding: inherit; margin: revert;">{{ item.link_name }}</h5>
                      </div>
                    </a>
                  </div>
                </div>
              </div>
            </div>  
          </div>
          <!-- <div class="carousel-item pt-4 pb-3">
            <div class="container">
              <div class="row" style="width: 98%; margin-left: 5px;">
                <div v-for="item in data.message.child_table_data2" :key="item.name" class="col col-md-3 col-sm-3 col-xs-12 custom-col">
                  <div v-if="item.image" class="card mx-0 image-overlay cus-card" style="border-radius: none;">
                    <a :href="item.document" class="cus-text mobile-hidden" style="text-decoration: none; color: #000; font-weight: 900;">
                      <img :src="item.image" class="card-img-top" style="position:relative; border-radius: 6px;" alt="..." />
                      <div v-if="item.link_name" class="overlay">
                        <h5 style="justify-content: center;    place-items: center; font-family: serif; padding: inherit; margin: revert;">{{ item.link_name }}</h5>
                      </div>
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div> -->
        </div>
        <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleControls" data-bs-slide="prev">
          <span class="carousel-control-prev-icon" aria-hidden="true" style="margin-right: 70px!important;"></span>
          <span class="visually-hidden">Previous</span>
        </button>
        <button class=" carousel-control-next" type="button" data-bs-target="#carouselExampleControls" data-bs-slide="next">
          <span class="carousel-control-next-icon" aria-hidden="true" style="margin-left: 70px!important;"></span>
          <span class="visually-hidden">Next</span>
        </button>
      </div>
    </div>
    <br>

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
.carousel-control-next, .carousel-control-prev {
    position: absolute;
    top: 0;
    bottom: 0;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 90px;
    padding: 0;
    margin: 37px;
    color: #fff;
    text-align: center;
    background: 0 0;
    border: 0;
    opacity: .5;
    transition: opacity .15s ease;
}


@media (max-width: 768px) {
  .cus-card{
   border-radius: 6px;
}
.custom-col {
    flex: 0 0 calc(50% - 24px); /* Adjust width as needed */
    margin: 8px;
    width: 100%;
    margin-left: 25px !important;
    margin-right: -26px !important;
    margin-bottom: 20px !important;
  }
  .carousel-control-next, .carousel-control-prev {
    position: absolute;
    top: 0;
    bottom: 0;
    z-index: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 90px;
    margin: 6px;
    padding: 0;
    color: #fff;
    text-align: center;
    background: 0 0;
    border: 0;
    opacity: .5;
    transition: opacity .15s ease;
}
}
</style>
