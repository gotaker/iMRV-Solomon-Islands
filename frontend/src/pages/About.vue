<template>
  <div>
    <Header />
    <section class="breadcrumb-area with-overlay"></section>
    <div class="counter-area fix area-padding" id="about">
      <div class="container-fluid" data-aos="fade-right" data-aos-delay="100">
        <div class="row" data-aos="fade-right" data-aos-delay="100">
          <h2 style="color: #000; font-weight: 700; font-size: 3rem; font-family: Inter;" class="p-5 text-center"> About<span style="color: green; font-weight: 700;"> MRV Tools</span></h2>

          <div class="col-md-12 col-sm-12 col-xs-12 wow fadeInLeft" data-wow-delay="0.3s">
            <div v-for="item in data.message" :key="item.name">
              <!-- <div v-if="item.about_heading_1">
                <h3 style="color: #000; font-weight: 700;" class="text-start">{{ item.about_heading_1 }}</h3>
              </div> -->
              <div v-if="item.description_1" class = "about-desctiption" style="padding: 0px 25px;">
                {{ item.description_1 }}
			  </div>
              <!-- <br>

              <div v-if="item.about_heading_2">
                <h3 style="color: #000; font-weight: 700;" class="text-start">{{ item.about_heading_2 }}</h3>
              </div>
              <div v-if="item.description_2" class = "about-desctiption">
                {{ item.description_2 }}
			  </div>
              <br> -->
            </div>
          </div>
        </div>
      </div>
    </div>
    <br>
    <br>

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

		if (response.status === 200) {
		data.value = response.data;
		} else {
		throw new Error('Network response was not ok');
		}
		setTimeout(()=>{
			var description_1 = $('.about-desctiption');
			if (description_1.length) {
				var descriptionHTML = description_1.html();
				if (descriptionHTML) {
					var extractedValue = descriptionHTML.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&nbsp;/g, '');
					description_1.html(extractedValue);
				} else {
					console.error('No HTML content found in #desctiption-1 element.');
				}
			} else {
				console.error('Element with ID #desctiption-1 not found.');
			}
			
		}, 100)
		$.ajax({
			success:function(){
				$('.breadcrumb-area').attr('style', `display:block !important; background:url(${data.value.message.parent_data.breadcrumb_image});`)
			}
		})
		console.log("extractedValue ------- ",extractedValue);
	} catch (error) {
		console.error('Error:', error);
	}
	var childField = data._rawValue.message.child_table_data2
	for (var item of childField){
		if (item.image){
		console.log("item",item.image);
		}
		else{
		console.log("no item found");
		}
	}


	var contact = data._rawValue.message.parent_data
	for (var item of contact){
		if (item.contact_number){
		console.log("item",item.contact_number);
		}
		else{
		console.log("no item found");
		}
	}


	console.log("response", contact);
	console.log("response", childField);

	// console.log("response", values);
	// console.log("response", field);
	};

	onMounted(() => {
	fetchData();
	});



	// const actions = createListResource({
	//   doctype: 'FrontendList',
	//   fields: ["name"],
	//   limit: 100
	// });
	// const action_data = actions.reload();
	// console.log("data", action_data);

	// actions.reload()


</script> 


<style scoped>




</style>