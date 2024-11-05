<template>
    <div style="
    display: flex;
    position: sticky;
    top: 0;
    z-index: 99999;
    background-color: #fff;">
    <div class="site-logo ml-auto mr-4 ">
        <router-link to='/home'><img style="color: white"  src="../assets/images/sig-coa.png" alt="Logo" loading="lazy" class="img-fluid p-2" /></router-link>
      </div>
    <h2 style="color: #000; font-weight: 700; font-size: 3rem; font-family: Inter;" class="p-5 text-center"> About<span style="color: green; font-weight: 700;"> MRV Tools</span></h2>

  </div>

  <header class="header">
    <nav class="navbar cus-navbar navbar-expand-lg navbar-fixed-top bg navbar-light p-0">
      <button
      style="margin-right: 10px; border: none !important;"

        class="navbar-toggler text-white"
        type="button"
        data-toggle="collapse"
        data-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
      <span><i class="bi bi-list" style="color: white !important;"></i></span>
      </button>
      <div class="site-logo ml-auto mr-4 "> <!-- Display only on lg and smaller screens -->
        <router-link to='/home'><img style="color: white"  src="../assets/images/sig-coa.png" alt="Logo" loading="lazy" class="img-fluid p-2" /></router-link>
      </div>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav w-100 mr-2">
          <li class="nav-item mr-2">
            <router-link to='/home' class="custom-link text-lg  active" style="transition:.3s; margin-right:20px;">Home</router-link>
          </li>
          <li class="nav-item mr-2">
            <router-link to='/about' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/about' }" style="transition:.3s; margin-right:20px;">About MRV Tool</router-link>
          </li>
          <li class="nav-item mr-2">
            <router-link to='/project' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/project' }" style="transition:.3s; margin-right:20px;">Project</router-link>
          </li>
          <li>
            <router-link to='/climate-change-division' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/climate-change-division' }" style="margin-right:20px;">Climate Change Division</router-link>
          </li>
          <li>
            <router-link to='/reports' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/reports' }" style="transition:.3s; margin-right:20px;">Reports</router-link>
          </li>
          <li>
            <router-link to='/support' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/support' }" style="margin-right:20px;">Support</router-link>
          </li>
          <li class="nav-item mr-2">
            <router-link to='/knowledgeresource' class="custom-link text-lg " :class="{ 'active-link': $route.path === '/knowledgeresource' }" style="transition:.3s; margin-right:20px;">Knowledge Resource</router-link>
          </li>
        </ul>
      </div>
      <div>
        <a href="/login#login">
        <button class="btn custom-btn btn-md">Login</button>
        </a>
      </div>
    </nav>


    
<router-view />
  
    </header>



  </template>
  
  <script scoped>



  export default {
    data() {
      return {
        aboutRefreshKey: 0,
      };
    },
  };
  
  $(function () {
    $(document).scroll(function () {
      var $nav = $(".navbar-fixed-top");
      $nav.toggleClass('scrolled', $(this).scrollTop() > $nav.height());
    });
    $(document).scroll(function () {
      var $nav = $(".custom-link");
      $nav.toggleClass('scrolled', $(this).scrollTop() > $nav.height());
    });
  });
  </script>
  
  <style scoped>
.active {
  color: rgb(0, 174, 0) !important;
  text-decoration: none;
  font-size: 17px !important;
  font-weight: 700 !important;

}


.bg {
  background-image: linear-gradient(rgba(255, 255, 255, 0.538), rgba(255, 255, 255, 0.118));
  border: none;
}
.bg.scrolled {
  background-image: linear-gradient(#fff, #fff);
  border: none;
}

.navbar-fixed-top.scrolled {
  /* transition: 10s; */
  background-color: #ffffff !important;
  transition: background-color 200ms linear;
}

.custom-link.scrolled {
  /* transition: 10s; */
  color: black;
}

/* Reduce the logo size */
.site-logo img {
  margin-left: 10px;
  height: 91px;
  margin-right: 36px;
  padding: 12px !important;
}

li {
  font-size: 18px;
  font-weight: 500;
  color: rgb(255, 255, 255);
}


.mr-4 {
  margin-left: 20px;
}

.custom-link {
  color: rgb(255, 255, 255);
  margin-left: 10px;
  font-size: 15px;
  border: none !important;
  font-weight: 500;
  font-family: 'Inter';
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
  background-color: rgb(0, 174, 0);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
  display: block;
  content: '';
}

.custom-link:hover::after {
  transform: scaleX(1);
  height: 2px; 
  font-weight: 500;
}


.custom-btn {
  background-color: rgba(255, 0, 0, 0.678);
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.097);
    color: #fff;
    text-decoration: none;
    border: none;
    margin-right: 15px;
    width: 84px;
    border-radius: 4px;
    position: absolute;
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
  border-radius: 0 !important;
  display: flex;
  /* position: sticky; */
  top: 93px;
  z-index: 1101;
  background-color: #6c6c6c;
}


/* toggle nav area */

/* .navbar-toggler-icon {
    display: inline-block;
    width: 2.5em;
    height: 2.5em;
    vertical-align: middle;
    background-image: var(--bs-navbar-toggler-icon-bg);
    background-repeat: no-repeat;
    background-position: center;
    background-size: 93%;
    color: #fff;
} */



@media (max-width: 576px) {
    /* .carousel {x
      margin-top: 80px;
    } */

    .bi-list {
  
  font-size: 28px;
  }
  .custom-link.scrolled {
  color: rgb(255, 255, 255);
  }


    .img-fluid{
    padding: 20px !important;
  }
    .navbar-toggler:focus {
      text-decoration: none;
      outline: 0;
      box-shadow:none !important;
    }
    /* .mr-4 {
    margin-left: -10px;
    } */
    .ml-auto {
        margin-right: 203px;
        margin-top: 4px;
      }
    
      .site-logo img {
    height: 49px !important;
    margin-left: 0px !important;
    padding: 1px !important;
    margin-right: 101px;
}
.custom-btn{
    top:0 !important;
  }

}
.bi-chevron-left{
    font-weight: bold !important;
    font-size: 3rem !important;
}
.bi-chevron-right{
    font-weight: bold !important;
    font-size: 3rem !important;
}


.bg {
  background-image: linear-gradient(rgba(58, 58, 58, 0.701), rgba(79, 79, 79, 0.289));
  border: none;
}

</style>
