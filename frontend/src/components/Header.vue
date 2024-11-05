<template>
  <div style="display: flex;position: sticky;top: 0px;height: 88px;justify-content: space-between;
              z-index: 99999;gap: 6;background-color: rgb(255, 255, 255); padding: 0 10px;">

    <div style="display: flex; gap: 8px;">
      <div class="site-logo">
        <router-link to='/home'><img style="color: white"  src="../assets/images/Flag_of_the_Solomon_Islands.png" alt="Logo" loading="lazy" class="img-fluid p-2" /></router-link>
      </div>
        <h2 style="
          color: rgb(0, 0, 0);
          font-weight: 700;
          font-size: 20px;
          font-family: Inter;
          display: flex;
          line-height: 1.5;
          align-items: center;
          justify-content: center;
          margin-left: 12px;
          /* flex-direction: column; */"
          class="heading"> SOLOMON ISLANDS iMRV TOOL <span style="color: green; margin:0 0 0 7px;" >FOR CLIMATE ACTIONS</span></h2>
      </div>

      <div class="mob-parent-nav">
        <nav class="navbar cus-navbar desk-nav navbar-expand-lg bg navbar-light p-0">
      <button
      style="border: none !important;"
        class="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
      <span><i class="bi bi-list toggle-btn" style="color: rgb(39, 39, 39) !important;"></i></span>
      </button>
      

    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav w-100 mr-2">
        <li class="nav-item dropdown">
          <a style="text-decoration: none;" class="nav-link dropdown-toggle text-lg" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            <i class="bi bi-list" style="font-size: 20px; display: flex;"><p style="font-size: 16px;text-transform: uppercase;font-style: normal;margin: 0px 5px;">Menu
          </p><i class="bi bi-caret-down-fill" style="font-size: 13px; margin-top: 2px;"></i></i>
          </a>
          <ul class="dropdown-menu" aria-labelledby="navbarDropdown">
            <li>
            <router-link to='/home' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/home' }">Home</router-link>
          </li>
          <li>
            <router-link to='/climate-change-division' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/climate-change-division' }">About Climate Change Division</router-link>
          </li>
          <li>
            <router-link to='/about' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/about' }">About MRV Tool</router-link>
          </li>
          <li>
            <router-link to='/project' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/project' }">Project</router-link>
          </li>
          <li>
            <router-link to='/reports' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/reports' }">GHG Summary</router-link>
          </li>
          <li>
            <router-link to='/support' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/support' }">Support</router-link>
          </li>
          <li>
            <router-link to='/knowledgeresource' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/knowledgeresource' }">Knowledge Resource</router-link>
          </li>
          <li>
            <router-link to='/new' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/new' }">What's New?</router-link>
          </li>
          </ul>
        </li>
      </ul>
    </div>

     
    </nav>
        <nav class="navbar cus-navbar mobile-nav navbar-expand-lg bg navbar-light p-0">
      <button
      style="border: none !important;"
        class="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#mobileNav"
        aria-controls="mobileNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
      <span><i class="bi bi-list toggle-btn" style="color: rgb(39, 39, 39) !important;"></i></span>
      </button>
      

      <div class="collapse navbar-collapse" id="mobileNav">
        <ul class="navbar-nav w-100">
          <li class="nav-item">
            <router-link to='/home' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/home' }">Home</router-link>
          </li>
          <li class="nav-item">
            <router-link to='/climate-change-division' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/climate-change-division' }">About Climate Change Division</router-link>
          </li>
          <li class="nav-item">
            <router-link to='/about' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/about' }">About MRV Tool</router-link>
          </li>
          <li class="nav-item">
            <router-link to='/project' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/project' }">Project</router-link>
          </li>
          <li class="nav-item">
            <router-link to='/reports' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/reports' }">GHG Summary</router-link>
          </li>
          <li class="nav-item">
            <router-link to='/support' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/support' }">Support</router-link>
          </li>
          <li class="nav-item">
            <router-link to='/knowledgeresource' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/knowledgeresource' }">Knowledge Resource</router-link>
          </li>
          <li class="nav-item">
            <router-link to='/new' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/new' }">What's New?</router-link>
          </li>
        </ul>
      </div>
    </nav>
      <div style="display: flex; align-items: center;">
        <a href="/login#login">
        <button class="btn custom-btn btn-md">Login</button>
        </a>
      </div>
      </div>


      

  </div>
  <header class="header">
    <!-- <section class="">
      <div v-for="item in data.message" :key="item.name">
        <div v-if="item.breadcrumb_image">
          <img :src="item.breadcrumb_image">
        </div>
      </div>
    </section> -->


    <!-- <div><img src="/files/Screenshot 2024-03-13 185349.png" class="report-image"></div> -->
    
    <router-view />
  </header>
</template>

<script scoped>
import { ref, onMounted, onUnmounted } from 'vue';
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

  console.log("response", values);
  console.log("response", field);
};

onMounted(() => {
  fetchData();
});


// Function to handle the click event and add "active" class
function handleRouterLinkClick(event) {
  const current = document.querySelector('.custom-link.active');
  if (current) {
    current.classList.remove('active');
  }
  event.target.classList.add('active');
}

onMounted(() => {
  // Attach click event listener to the router-links
  const routerLinks = document.querySelectorAll('.custom-link');
  routerLinks.forEach((link) => {
    link.addEventListener('click', handleRouterLinkClick);
  });
});

onUnmounted(() => {
  // Remove event listeners to prevent memory leaks
  const routerLinks = document.querySelectorAll('.custom-link');
  routerLinks.forEach((link) => {
    link.removeEventListener('click', handleRouterLinkClick);
  });
});



  $(function () {
    $(document).scroll(function () {
      var $nav = $(".navbar-fixed-top");
      // var $banner = $(".breadcrumb-area");
      $nav.toggleClass('scrolled', $(this).scrollTop() > $nav.height());
    });
    $(document).scroll(function () {
      var $nav = $(".custom-link");
      // var $banner = $(".breadcrumb-area");
      $nav.toggleClass('scrolled', $(this).scrollTop() > $nav.height());
    });
  });

</script>

<style scoped>

.dropdown-menu{
  left: -68px;
    padding: 0px;
    border: none;
    box-shadow: 0 0px 3px -2px #000;
    border-radius: 4px;
} 
.dropdown-menu li a{
  padding: 8px 20px;
}

.breadcrumb-area {
  position: relative;
  display: block !important;
}

.with-overlay::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.312), rgba(0, 0, 0, 0.082));
  z-index: 1;
}
/* NAvbar */
.active-link {
  color: green !important;
  text-decoration: none;
  font-size: 15px !important;
  font-weight: 700 !important;

}
.dropdown-toggle::after{
display: none !important;
}

.bg {
  background-image: none;
  border: none;
}
.bg.scrolled {
  background-image: linear-gradient(#fff, #fff);
  border: none;
}
.navbar-fixed-top.scrolled {
  transition: 1s;
  background-color: #fff !important;
  /* background-image: linear-gradient(#ffffffe7, #f3f3f33e) !important;  border: none; */
  transition: background-color 200ms linear;
}

.custom-link.scrolled {
  /* transition: 1s; */
  color: rgb(0, 0, 0);
}
.site-logo {
  display: flex;
}
.site-logo a {
  align-items: center;
  display: flex;
}

.mobile-nav{
  display: none;
}
/* Reduce the logo size */
.site-logo img {
  height: 70px;
}li {
  font-size: 18px;
  font-weight: 500;
  color: rgb(0, 0, 0);
}


.mr-4 {
  margin-left: 20px;
}


/* Router-link */

.custom-link {
  color: #000;
    font-size: 14px;
    border: none !important;
    font-weight: 500;
    width: auto;
    font-family: Inter;
    text-decoration: none;
    position: relative;
  }

.custom-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 1px;
  background-color: green;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
  display: block;
  content: '';
}

/* .custom-link:hover::after {
  transform: scaleX(1);
  height: 2px; 
  font-weight: 500;
} */

/* Router-link end */

.custom-btn {
    background-color: rgba(255, 0, 0, 0.678);
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.075);
    color: #fff;
    text-decoration: none;
    border: none;
    margin-right: 34px;
    width: 70px;
    height: 30px;
    border-radius: 4px;
    top: 19px !important;
    right: 0;
    margin: 10px;
  }
  
  .custom-btn:hover {
    box-shadow: 0 0 10px rgba(255, 191, 191, 0.109);
    color: #fff;
  }

.cus-navbar {
  margin-bottom: 0 !important;
  /* border-radius: 0 !important;
  display: flex;
  top: 70px;
  background: linear-gradient(to bottom, rgb(0 0 0 / 35%), rgb(0 0 0 / 4%));
  z-index: 1101; */
}



/* toggle area */
.bi-list {
  
  font-size: 32px;
  border: none;
    background-size: 93%;
}
.navbar-collapse {
    padding-right: 0px;
    padding-left: 0px;
}
/* .bi-list:hover {
    text-decoration: none;
    height: 30px;
    width: 45px;
} */
.mob-parent-nav{
    display: flex;
  }
.navbar-nav{
    gap: 12px;
    background-color: #fff;
    padding: 15px;  }

@media (max-width: 576px) {
  .mob-parent-nav{
    display: flex;
    /* gap: 15px; */
    align-items: flex-start;
    margin-top: 5%;
  }
  .mobile-nav{
      display: flex !important;
    }
    .desk-nav{
      display: none !important;
    }
  .navbar-collapse{
    width: 100%;
    height: auto;
    top: 0;
    /* display: flex; */
  }
  .navbar-nav{
    /* background-color: #0006; */
    margin: 0px !important;
  }
  .custom-btn{
    top:0 !important;
  }
  .img-fluid{
    padding: 10px;
    height: 50%;
  }
    .navbar-toggler:focus {
      text-decoration: none;
      outline: 0;
      box-shadow:none !important;
  }
  .navbar{
    background-color: #fff;
  }

.ml-auto {
    margin-right: 200px;
    margin-top: 4px;

}
.site-logo img {
    height: 49px !important;
    margin-left: 0px !important;
    margin-right: 34px !important;
    padding: 1px !important;
    color: #ffffff41;
}

h2.heading{
  display: none !important;
}
.custom-link.scrolled {
  /* transition: 10s; */
  color: rgb(0, 0, 0);
}

.breadcrumb-area {
    background: url("../assets/images/carousel/Untitled-3.jpg");
    background-size: cover;
    height: 202px;
}
}
</style>
