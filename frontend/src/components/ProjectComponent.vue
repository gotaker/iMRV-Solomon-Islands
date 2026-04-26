<template>
  <!-- <section class="breadcrumb-area with-overlay"></section> -->
  <div>
    <div
      class="tab-area fix area-padding bg-color wow fadeInUp"
      data-aos="fade-right "
      data-aos-delay="100"
      data-wow-delay="0.3s"
      id="projects"
    >
      <div class="container-fluid">
        <div class="section-headline text-center">
          <h2
            style="
              color: #000;
              font-weight: 700;
              font-size: 3rem;
              font-family: Inter;
            "
            class="p-5 text-center"
          >
            Our <span style="color: #01472e; font-weight: 700">Projects</span>
          </h2>
        </div>
        <ul
          v-for="item in data.message"
          :key="item.name"
          class="pr-blw-img-list"
          style="list-style: none; display: flex"
        >
          <li v-if="item.project_image1" class="list_image">
            <img :src="item.project_image1" class="pro_image" />
            <div class="overlay">
              <h5>{{ item.project_image1_title }}</h5>
            </div>
          </li>
          <li v-if="item.project_image2" class="list_image">
            <img :src="item.project_image2" class="pro_image" />
            <div class="overlay">
              <h5></h5>
              {{ item.project_image2_title }}
            </div>
          </li>
          <li v-if="item.project_image3" class="list_image">
            <img :src="item.project_image3" class="pro_image" />
            <div class="overlay">
              <h5>{{ item.project_image3_title }}</h5>
            </div>
          </li>
        </ul>
        <br />
        <br />

        <div class="row">
          <div class="tab-menu mx-5 mb-4">
            <!-- Start Nav tabs -->

            <ul
              style="margin-right: 35px"
              data-aos="fade-right "
              data-aos-delay="100"
              class="nav nav-pills flex-wrap tab_parent"
              id="pills-tab"
              role="tablist"
            >
              <li class="nav-item active tab_child">
                <a
                  class="nav-link style-class"
                  id="pills-home-tab"
                  href="#p-view-2"
                  role="tab"
                  data-toggle="tab"
                  aria-controls="pills-home"
                  aria-selected="true"
                  >Adaptation
                </a>
              </li>
              <li class="nav-item tab_child">
                <a
                  class="nav-link style-class"
                  id="pills-profile-tab"
                  href="#p-view-5"
                  role="tab"
                  data-toggle="tab"
                  aria-controls="pills-profile"
                  aria-selected="false"
                  >Mitigation
                </a>
              </li>
              <li class="nav-item tab_child">
                <a
                  class="nav-link style-class"
                  id="pills-contact-tab"
                  href="#p-view-6"
                  role="tab"
                  data-toggle="tab"
                  aria-controls="pills-contact"
                  aria-selected="false"
                  >Cross cutting</a
                >
              </li>
              <li class="nav-item tab_child">
                <a
                  class="nav-link style-class"
                  id="pills-contact-tab"
                  href="#p-view-7"
                  role="tab"
                  data-toggle="tab"
                  aria-controls="pills-contact"
                  aria-selected="false"
                  >Enablers</a
                >
              </li>
              <li class="nav-item tab_child">
                <a
                  class="nav-link style-class"
                  id="pills-contact-tab"
                  href="#p-view-8"
                  role="tab"
                  data-toggle="tab"
                  aria-controls="pills-contact"
                  aria-selected="false"
                  >Transparency</a
                >
              </li>
              <li class="nav-item tab_child">
                <a
                  class="nav-link style-class"
                  id="pills-contact-tab"
                  href="#p-view-9"
                  role="tab"
                  data-toggle="tab"
                  aria-controls="pills-contact"
                  aria-selected="false"
                  >Support</a
                >
              </li>
            </ul>
          </div>
          <!-- </div> -->

          <div style="display: flex; justify-content: center; width: 100%">
            <div style="border-top: 0.1px solid #0000006c; width: 94%"></div>
          </div>
          <div class="container-fluid">
            <div
              class="col-md-12 col-sm-12 col-xs-12 wow fadeInUp"
              data-wow-delay="0.7s"
            >
              <div class="tab-content p-4">
                <!-- Start Tab Content -->
                <v-data-table
                  :items="sortedData1"
                  class="datatable"
                ></v-data-table>
                <div class="tab-pane active" id="p-view-2">
                  <div class="tab-inner">
                    <div
                      class="table-responsive"
                      data-aos=""
                      style="max-height: 50rem; overflow: auto"
                      data-aos-delay="100"
                    >
                      <table
                        class="table table-striped table-bordered table-hover"
                        id="tab-view-2"
                      >
                        <thead
                          style="
                            background-color: #01472e;
                            color: white;
                            padding: 20px;
                          "
                        >
                          <tr>
                            <th scope="col">S.No</th>
                            <th scope="col" @click="sortList1('intervention')">
                              Intervention
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList1('sector')">
                              Sector <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList1('subsector')">
                              Subsector
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList1('project_title')">
                              Project Title
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList1('implementing_agency')"
                            >
                              Implementing Agency
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList1('area_name')">
                              Area Name
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList1('project_costusd')"
                            >
                              Project Cost (USD)
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList1('source_of_funding')"
                            >
                              Sources of Funding
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList1('start_date')">
                              Start Date
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList1('end_date')">
                              End Date <span style="float: right">&#8597;</span>
                            </th>
                          </tr>
                          <tr style="background-color: #fefae0">
                            <th></th>
                            <th>
                              <input
                                type="text"
                                id="myInput-1"
                                placeholder="Search"
                                v-on:keyup="filterRows1"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th>
                              <input
                                type="text"
                                id="myInput-2"
                                placeholder="Search"
                                v-on:keyup="filterRows1"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th>
                              <input
                                type="text"
                                id="myInput-3"
                                placeholder="Search"
                                v-on:keyup="filterRows1"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th>
                              <input
                                type="text"
                                id="myInput-4"
                                placeholder="Search"
                                v-on:keyup="filterRows1"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th>
                              <input
                                type="text"
                                id="myInput-5"
                                placeholder="Search"
                                v-on:keyup="filterRows1"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th>
                              <input
                                type="text"
                                id="myInput-6"
                                placeholder="Search"
                                v-on:keyup="filterRows1"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th>
                              <input
                                type="text"
                                id="myInput-7"
                                placeholder="Search"
                                v-on:keyup="filterRows1"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th>
                              <input
                                type="text"
                                id="myInput-8"
                                placeholder="Search"
                                v-on:keyup="filterRows1"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th>
                              <input
                                type="text"
                                id="myInput-9"
                                placeholder="Search"
                                v-on:keyup="filterRows1"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th>
                              <input
                                type="text"
                                id="myInput-10"
                                placeholder="Search"
                                v-on:keyup="filterRows1"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                          </tr>
                        </thead>
                        <tbody
                          class="table-group-divider table-divider-color"
                          style="overflow: auto"
                        >
                          <tr
                            v-for="table_item in sortedData1"
                            :key="table_item.name"
                          >
                            <th style="padding: 10px" scope="row">
                              {{ table_item.idx }}
                            </th>

                            <td v-if="table_item.intervention">
                              {{ table_item.intervention }}
                            </td>
                            <td
                              v-else="table_item.intervention"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.sector">
                              {{ table_item.sector }}
                            </td>
                            <td v-else="table_item.sector" class="none-table">
                              -
                            </td>
                            <td v-if="table_item.subsector">
                              {{ table_item.subsector }}
                            </td>
                            <td
                              v-else="table_item.subsector"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.project_title">
                              {{ table_item.project_title }}
                            </td>
                            <td
                              v-else="table_item.project_title"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.implementing_agency">
                              {{ table_item.implementing_agency }}
                            </td>
                            <td
                              v-else="table_item.implementing_agency"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.area_name">
                              {{ table_item.area_name }}
                            </td>
                            <td
                              v-else="table_item.area_name"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.project_costusd">
                              {{ table_item.project_costusd }}
                            </td>
                            <td
                              v-else="table_item.project_costusd"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.source_of_funding">
                              {{ table_item.source_of_funding }}
                            </td>
                            <td
                              v-else="table_item.source_of_funding"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.start_date">
                              {{ table_item.start_date }}
                            </td>
                            <td
                              v-else="table_item.start_date"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.end_date">
                              {{ table_item.end_date }}
                            </td>
                            <td v-else="table_item.end_date" class="none-table">
                              -
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div class="tab-pane" id="p-view-5">
                  <div class="tab-inner">
                    <div
                      class="table-responsive"
                      style="max-height: 50rem; overflow: auto"
                    >
                      <table
                        class="table table-striped table-bordered table-hover"
                        id="tab-view-5"
                      >
                        <thead
                          style="
                            background-color: #01472e;
                            color: white;
                            padding: 20px;
                          "
                        >
                          <tr>
                            <th style="padding: 20px" scope="col">S.No</th>
                            <th scope="col" @click="sortList2('intervention')">
                              Intervention
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList2('sector')">
                              Sector <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList2('subsector')">
                              Subsector
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList2('project_title')">
                              Project Title
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList2('implementing_agency')"
                            >
                              Implementing Agency
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList2('area_name')">
                              Area Name
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList2('project_costusd')"
                            >
                              Project Cost (USD)
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList2('source_of_funding')"
                            >
                              Sources of Funding
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList2('start_date')">
                              Start Date
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList2('end_date')">
                              End Date <span style="float: right">&#8597;</span>
                            </th>
                          </tr>
                          <tr style="background-color: #fefae0">
                            <th scope="col"></th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-11"
                                placeholder="Search"
                                v-on:keyup="filterRows2"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-12"
                                placeholder="Search"
                                v-on:keyup="filterRows2"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-13"
                                placeholder="Search"
                                v-on:keyup="filterRows2"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-14"
                                placeholder="Search"
                                v-on:keyup="filterRows2"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-15"
                                placeholder="Search"
                                v-on:keyup="filterRows2"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-16"
                                placeholder="Search"
                                v-on:keyup="filterRows2"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-17"
                                placeholder="Search"
                                v-on:keyup="filterRows2"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-18"
                                placeholder="Search"
                                v-on:keyup="filterRows2"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-19"
                                placeholder="Search"
                                v-on:keyup="filterRows2"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-20"
                                placeholder="Search"
                                v-on:keyup="filterRows2"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                          </tr>
                        </thead>
                        <tbody class="table-group-divider table-divider-color">
                          <tr
                            v-for="table_item in sortedData2"
                            :key="table_item.name"
                          >
                            <th style="padding: 10px" scope="row">
                              {{ table_item.idx }}
                            </th>
                            <td v-if="table_item.intervention">
                              {{ table_item.intervention }}
                            </td>
                            <td
                              v-else="table_item.intervention"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.sector">
                              {{ table_item.sector }}
                            </td>
                            <td v-else="table_item.sector" class="none-table">
                              -
                            </td>
                            <td v-if="table_item.subsector">
                              {{ table_item.subsector }}
                            </td>
                            <td
                              v-else="table_item.subsector"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.project_title">
                              {{ table_item.project_title }}
                            </td>
                            <td
                              v-else="table_item.project_title"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.implementing_agency">
                              {{ table_item.implementing_agency }}
                            </td>
                            <td
                              v-else="table_item.implementing_agency"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.area_name">
                              {{ table_item.area_name }}
                            </td>
                            <td
                              v-else="table_item.area_name"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.project_costusd">
                              {{ table_item.project_costusd }}
                            </td>
                            <td
                              v-else="table_item.project_costusd"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.source_of_funding">
                              {{ table_item.source_of_funding }}
                            </td>
                            <td
                              v-else="table_item.source_of_funding"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.start_date">
                              {{ table_item.start_date }}
                            </td>
                            <td
                              v-else="table_item.start_date"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.end_date">
                              {{ table_item.end_date }}
                            </td>
                            <td v-else="table_item.end_date" class="none-table">
                              -
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div class="tab-pane" id="p-view-6">
                  <div class="tab-inner">
                    <div
                      class="table-responsive"
                      style="max-height: 50rem; overflow: auto"
                    >
                      <table
                        class="table table-striped table-bordered table-hover"
                        id="tab-view-6"
                      >
                        <thead
                          style="
                            background-color: #01472e;
                            color: white;
                            padding: 20px;
                          "
                        >
                          <tr>
                            <th style="padding: 20px" scope="col">S.No</th>
                            <th scope="col" @click="sortList3('intervention')">
                              Intervention
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList3('sector')">
                              Sector <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList3('subsector')">
                              Subsector
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList3('project_title')">
                              Project Title
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList3('implementing_agency')"
                            >
                              Implementing Agency
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList3('area_name')">
                              Area Name
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList3('project_costusd')"
                            >
                              Project Cost (USD)
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList3('source_of_funding')"
                            >
                              Sources of Funding
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList3('start_date')">
                              Start Date
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList3('end_date')">
                              End Date <span style="float: right">&#8597;</span>
                            </th>
                          </tr>
                          <tr style="background-color: #fefae0">
                            <th scope="col"></th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-21"
                                placeholder="Search"
                                v-on:keyup="filterRows3"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-22"
                                placeholder="Search"
                                v-on:keyup="filterRows3"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-23"
                                placeholder="Search"
                                v-on:keyup="filterRows3"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-24"
                                placeholder="Search"
                                v-on:keyup="filterRows3"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-25"
                                placeholder="Search"
                                v-on:keyup="filterRows3"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-26"
                                placeholder="Search"
                                v-on:keyup="filterRows3"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-27"
                                placeholder="Search"
                                v-on:keyup="filterRows3"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-28"
                                placeholder="Search"
                                v-on:keyup="filterRows3"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-29"
                                placeholder="Search"
                                v-on:keyup="filterRows3"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-30"
                                placeholder="Search"
                                v-on:keyup="filterRows3"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                          </tr>
                        </thead>
                        <tbody class="table-group-divider table-divider-color">
                          <tr
                            v-for="table_item in sortedData3"
                            :key="table_item.name"
                          >
                            <th style="padding: 10px" scope="row">
                              {{ table_item.idx }}
                            </th>
                            <td v-if="table_item.intervention">
                              {{ table_item.intervention }}
                            </td>
                            <td
                              v-else="table_item.intervention"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.sector">
                              {{ table_item.sector }}
                            </td>
                            <td v-else="table_item.sector" class="none-table">
                              -
                            </td>
                            <td v-if="table_item.subsector">
                              {{ table_item.subsector }}
                            </td>
                            <td
                              v-else="table_item.subsector"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.project_title">
                              {{ table_item.project_title }}
                            </td>
                            <td
                              v-else="table_item.project_title"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.implementing_agency">
                              {{ table_item.implementing_agency }}
                            </td>
                            <td
                              v-else="table_item.implementing_agency"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.area_name">
                              {{ table_item.area_name }}
                            </td>
                            <td
                              v-else="table_item.area_name"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.project_costusd">
                              {{ table_item.project_costusd }}
                            </td>
                            <td
                              v-else="table_item.project_costusd"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.source_of_funding">
                              {{ table_item.source_of_funding }}
                            </td>
                            <td
                              v-else="table_item.source_of_funding"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.start_date">
                              {{ table_item.start_date }}
                            </td>
                            <td
                              v-else="table_item.start_date"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.end_date">
                              {{ table_item.end_date }}
                            </td>
                            <td v-else="table_item.end_date" class="none-table">
                              -
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div class="tab-pane" id="p-view-7">
                  <div class="tab-inner">
                    <div
                      class="table-responsive"
                      style="max-height: 50rem; overflow: auto"
                    >
                      <table
                        class="table table-striped table-bordered table-hover"
                        id="tab-view-7"
                      >
                        <thead
                          style="
                            background-color: #01472e;
                            color: white;
                            padding: 20px;
                          "
                        >
                          <tr>
                            <th style="padding: 20px" scope="col">S.No</th>
                            <th scope="col" @click="sortList4('intervention')">
                              Intervention
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList4('sector')">
                              Sector <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList4('subsector')">
                              Subsector
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList4('project_title')">
                              Project Title
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList4('implementing_agency')"
                            >
                              Implementing Agency
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList4('area_name')">
                              Area Name
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList4('project_costusd')"
                            >
                              Project Cost (USD)
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList4('source_of_funding')"
                            >
                              Sources of Funding
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList4('start_date')">
                              Start Date
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList4('end_date')">
                              End Date <span style="float: right">&#8597;</span>
                            </th>
                          </tr>
                          <tr style="background-color: #fefae0">
                            <th scope="col"></th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-31"
                                placeholder="Search"
                                v-on:keyup="filterRows4"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-32"
                                placeholder="Search"
                                v-on:keyup="filterRows4"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-33"
                                placeholder="Search"
                                v-on:keyup="filterRows4"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-34"
                                placeholder="Search"
                                v-on:keyup="filterRows4"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-35"
                                placeholder="Search"
                                v-on:keyup="filterRows4"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-36"
                                placeholder="Search"
                                v-on:keyup="filterRows4"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-37"
                                placeholder="Search"
                                v-on:keyup="filterRows4"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-38"
                                placeholder="Search"
                                v-on:keyup="filterRows4"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-39"
                                placeholder="Search"
                                v-on:keyup="filterRows4"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-40"
                                placeholder="Search"
                                v-on:keyup="filterRows4"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                          </tr>
                        </thead>
                        <tbody class="table-group-divider table-divider-color">
                          <tr
                            v-for="table_item in sortedData4"
                            :key="table_item.name"
                          >
                            <th style="padding: 10px" scope="row">
                              {{ table_item.idx }}
                            </th>
                            <td v-if="table_item.intervention">
                              {{ table_item.intervention }}
                            </td>
                            <td
                              v-else="table_item.intervention"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.sector">
                              {{ table_item.sector }}
                            </td>
                            <td v-else="table_item.sector" class="none-table">
                              -
                            </td>
                            <td v-if="table_item.subsector">
                              {{ table_item.subsector }}
                            </td>
                            <td
                              v-else="table_item.subsector"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.project_title">
                              {{ table_item.project_title }}
                            </td>
                            <td
                              v-else="table_item.project_title"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.implementing_agency">
                              {{ table_item.implementing_agency }}
                            </td>
                            <td
                              v-else="table_item.implementing_agency"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.area_name">
                              {{ table_item.area_name }}
                            </td>
                            <td
                              v-else="table_item.area_name"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.project_costusd">
                              {{ table_item.project_costusd }}
                            </td>
                            <td
                              v-else="table_item.project_costusd"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.source_of_funding">
                              {{ table_item.source_of_funding }}
                            </td>
                            <td
                              v-else="table_item.source_of_funding"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.start_date">
                              {{ table_item.start_date }}
                            </td>
                            <td
                              v-else="table_item.start_date"
                              class="none-table"
                            >
                              -
                            </td>
                            <td v-if="table_item.end_date">
                              {{ table_item.end_date }}
                            </td>
                            <td v-else="table_item.end_date" class="none-table">
                              -
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div class="tab-pane" id="p-view-8">
                  <div class="tab-inner">
                    <div
                      class="table-responsive"
                      style="max-height: 50rem; overflow: auto"
                    >
                      <table
                        class="table table-striped table-bordered table-hover"
                        id="tab-view-8"
                      >
                        <thead
                          style="
                            background-color: #01472e;
                            color: white;
                            padding: 20px;
                          "
                        >
                          <tr>
                            <th style="padding: 20px" scope="col">S.No</th>
                            <th scope="col" @click="sortList5('intervention')">
                              Intervention
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList5('sector')">
                              Sector <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList5('subsector')">
                              Subsector
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList5('project_title')">
                              Project Title
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList5('implementing_agency')"
                            >
                              Implementing Agency
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList5('area_name')">
                              Area Name
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList5('project_costusd')"
                            >
                              Project Cost (USD)
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList5('source_of_funding')"
                            >
                              Sources of Funding
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList5('start_date')">
                              Start Date
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList5('end_date')">
                              End Date <span style="float: right">&#8597;</span>
                            </th>
                          </tr>
                          <tr style="background-color: #fefae0">
                            <th scope="col"></th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-41"
                                placeholder="Search"
                                v-on:keyup="filterRows5"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-42"
                                placeholder="Search"
                                v-on:keyup="filterRows5"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-43"
                                placeholder="Search"
                                v-on:keyup="filterRows5"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-44"
                                placeholder="Search"
                                v-on:keyup="filterRows5"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-45"
                                placeholder="Search"
                                v-on:keyup="filterRows5"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-46"
                                placeholder="Search"
                                v-on:keyup="filterRows5"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-47"
                                placeholder="Search"
                                v-on:keyup="filterRows5"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-48"
                                placeholder="Search"
                                v-on:keyup="filterRows5"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-49"
                                placeholder="Search"
                                v-on:keyup="filterRows5"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-50"
                                placeholder="Search"
                                v-on:keyup="filterRows5"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                          </tr>
                        </thead>
                        <tbody class="table-group-divider table-divider-color">
                          <tr
                            v-for="trans_item in sortedData5"
                            :key="trans_item.name"
                          >
                            <th style="padding: 10px" scope="row">
                              {{ trans_item.idx }}
                            </th>
                            <td v-if="trans_item.intervention">
                              {{ trans_item.intervention }}
                            </td>
                            <td
                              v-else="table_item.intervention"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="trans_item.sector">
                              {{ trans_item.sector }}
                            </td>
                            <td v-else="table_item.sector" class="none-table">
                              -
                            </td>

                            <td v-if="trans_item.subsector">
                              {{ trans_item.subsector }}
                            </td>
                            <td
                              v-else="table_item.subsector"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="trans_item.project_title">
                              {{ trans_item.project_title }}
                            </td>
                            <td
                              v-else="table_item.project_title"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="trans_item.implementing_agency">
                              {{ trans_item.implementing_agency }}
                            </td>
                            <td
                              v-else="table_item.implementing_agency"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="trans_item.area_name">
                              {{ trans_item.area_name }}
                            </td>
                            <td
                              v-else="table_item.area_name"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="trans_item.project_costusd">
                              {{ trans_item.project_costusd }}
                            </td>
                            <td
                              v-else="table_item.project_costusd"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="trans_item.source_of_funding">
                              {{ trans_item.source_of_funding }}
                            </td>
                            <td
                              v-else="table_item.source_of_funding"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="trans_item.start_date">
                              {{ trans_item.start_date }}
                            </td>
                            <td
                              v-else="table_item.start_date"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="trans_item.end_date">
                              {{ trans_item.end_date }}
                            </td>
                            <td v-else="table_item.end_date" class="none-table">
                              -
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
                <div class="tab-pane" id="p-view-9">
                  <div class="tab-inner">
                    <div
                      class="table-responsive"
                      style="max-height: 50rem; overflow: auto"
                    >
                      <table
                        class="table table-striped table-bordered table-hover"
                        id="tab-view-9"
                      >
                        <thead
                          style="
                            background-color: #01472e;
                            color: white;
                            padding: 20px;
                          "
                        >
                          <tr>
                            <th style="padding: 20px" scope="col">S.No</th>
                            <th scope="col" @click="sortList6('intervention')">
                              Intervention
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList6('sector')">
                              Sector <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList6('subsector')">
                              Subsector
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList6('project_title')">
                              Project Title
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList6('implementing_agency')"
                            >
                              Implementing Agency
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList6('area_name')">
                              Area Name
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList6('project_costusd')"
                            >
                              Project Cost (USD)
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th
                              scope="col"
                              @click="sortList6('source_of_funding')"
                            >
                              Sources of Funding
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList6('start_date')">
                              Start Date
                              <span style="float: right">&#8597;</span>
                            </th>
                            <th scope="col" @click="sortList6('end_date')">
                              End Date <span style="float: right">&#8597;</span>
                            </th>
                          </tr>
                          <tr style="background-color: #fefae0">
                            <th scope="col"></th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-51"
                                placeholder="Search"
                                v-on:keyup="filterRows6"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-52"
                                placeholder="Search"
                                v-on:keyup="filterRows6"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-53"
                                placeholder="Search"
                                v-on:keyup="filterRows6"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-54"
                                placeholder="Search"
                                v-on:keyup="filterRows6"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-55"
                                placeholder="Search"
                                v-on:keyup="filterRows6"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-56"
                                placeholder="Search"
                                v-on:keyup="filterRows6"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-57"
                                placeholder="Search"
                                v-on:keyup="filterRows6"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-58"
                                placeholder="Search"
                                v-on:keyup="filterRows6"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-59"
                                placeholder="Search"
                                v-on:keyup="filterRows6"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                            <th scope="col">
                              <input
                                type="text"
                                id="myInput-60"
                                placeholder="Search"
                                v-on:keyup="filterRows6"
                                style="
                                  border-radius: 4px;
                                  background: #fefae0;
                                  color: #022e1d;
                                  padding: 0px 0px 0px 4px;
                                  font-size: 12px;
                                  font-weight: 200;
                                  width: 100%;
                                  border: none;
                                  height: 22px;
                                "
                              />
                            </th>
                          </tr>
                        </thead>
                        <tbody class="table-group-divider table-divider-color">
                          <tr
                            v-for="support_item in sortedData6"
                            :key="support_item.name"
                          >
                            <th style="padding: 10px" scope="row">
                              {{ support_item.idx }}
                            </th>
                            <td v-if="support_item.intervention">
                              {{ support_item.intervention }}
                            </td>
                            <td
                              v-else="table_item.intervention"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="support_item.sector">
                              {{ support_item.sector }}
                            </td>
                            <td v-else="table_item.sector" class="none-table">
                              -
                            </td>

                            <td v-if="support_item.subsector">
                              {{ support_item.subsector }}
                            </td>
                            <td
                              v-else="table_item.subsector"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="support_item.project_title">
                              {{ support_item.project_title }}
                            </td>
                            <td
                              v-else="table_item.project_title"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="support_item.implementing_agency">
                              {{ support_item.implementing_agency }}
                            </td>
                            <td
                              v-else="table_item.implementing_agency"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="support_item.area_name">
                              {{ support_item.area_name }}
                            </td>
                            <td
                              v-else="table_item.area_name"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="support_item.project_costusd">
                              {{ support_item.project_costusd }}
                            </td>
                            <td
                              v-else="table_item.project_costusd"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="support_item.source_of_funding">
                              {{ support_item.source_of_funding }}
                            </td>
                            <td
                              v-else="table_item.source_of_funding"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="support_item.start_date">
                              {{ support_item.start_date }}
                            </td>
                            <td
                              v-else="table_item.start_date"
                              class="none-table"
                            >
                              -
                            </td>

                            <td v-if="support_item.end_date">
                              {{ support_item.end_date }}
                            </td>
                            <td v-else="table_item.end_date" class="none-table">
                              -
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- end Row -->
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    data: {
      type: Object,
      required: true,
    },
  },

  data() {
    return {
      sortedData: [],
      sortedData1: [],
      sortedData2: [],
      sortedData3: [],
      sortedData4: [],
      sortedData5: [],
      sortedData6: [],
      sortedbyASC1: true,
      sortedbyASC2: true,
      sortedbyASC3: true,
      sortedbyASC4: true,
      sortedbyASC5: true,
      sortedbyASC6: true,
    }
  },
  watch: {
    data: {
      deep: true,
      immediate: true,
      handler(val) {
        const pd = val?.message?.parent_data
        if (!pd) return
        this.sortedData1 = pd.adaptation_table || []
        this.sortedData2 = pd.mitigation_table || []
        this.sortedData3 = pd.cross_cutting_table || []
        this.sortedData4 = pd.enablers_table || []
        this.sortedData5 = pd.transparency_table || []
        this.sortedData6 = pd.support_table || []
      },
    },
  },
  methods: {
    sortList1(sortBy) {
      if (this.sortedbyASC1) {
        // Sort in ascending order
        if (sortBy == 'project_costusd') {
          this.sortedData1.sort((a, b) =>
            (a[sortBy] ? a[sortBy] : 0).localeCompare(
              b[sortBy] ? b[sortBy] : 0,
              undefined,
              { numeric: true },
            ),
          )
        } else {
          this.sortedData1.sort((a, b) =>
            (a[sortBy] ? a[sortBy] : '').localeCompare(
              b[sortBy] ? b[sortBy] : '',
            ),
          )
        }
      } else {
        // Sort in descending order
        if (sortBy == 'project_costusd') {
          this.sortedData1.sort((a, b) =>
            (b[sortBy] ? b[sortBy] : '').localeCompare(
              a[sortBy] ? a[sortBy] : '',
              undefined,
              { numeric: true },
            ),
          )
        } else {
          this.sortedData1.sort((a, b) =>
            (b[sortBy] ? b[sortBy] : '').localeCompare(
              a[sortBy] ? a[sortBy] : '',
            ),
          )
        }
      }
      // Toggle the flag for next click
      this.sortedbyASC1 = !this.sortedbyASC1
    },

    filterRows1(event) {
      var inputField, parent, table, tr, td, i, txtValue, idx
      let search1 = $('#myInput-1').val().toUpperCase()
      let search2 = $('#myInput-2').val().toUpperCase()
      let search3 = $('#myInput-3').val().toUpperCase()
      let search4 = $('#myInput-4').val().toUpperCase()
      let search5 = $('#myInput-5').val().toUpperCase()
      let search6 = $('#myInput-6').val().toUpperCase()
      let search7 = $('#myInput-7').val().toUpperCase()
      let search8 = $('#myInput-8').val().toUpperCase()
      let search9 = $('#myInput-9').val().toUpperCase()
      let search10 = $('#myInput-10').val().toUpperCase()

      inputField = $(`#${event.target.id}`)
      parent = inputField.closest('table').attr('id')

      table = document.getElementById(parent)
      tr = table.getElementsByTagName('tr')
      idx = parseInt(event.target.id.replace(/\D/g, ''))
      if (idx >= 1 && idx <= 10) {
        idx = idx - 1
      }
      for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName('td')[idx]
        if (td) {
          txtValue = td.textContent || td.innerText
          if (
            tr[i]
              .getElementsByTagName('td')[0]
              .textContent.toUpperCase()
              .includes(search1) &&
            tr[i]
              .getElementsByTagName('td')[1]
              .textContent.toUpperCase()
              .includes(search2) &&
            tr[i]
              .getElementsByTagName('td')[2]
              .textContent.toUpperCase()
              .includes(search3) &&
            tr[i]
              .getElementsByTagName('td')[3]
              .textContent.toUpperCase()
              .includes(search4) &&
            tr[i]
              .getElementsByTagName('td')[4]
              .textContent.toUpperCase()
              .includes(search5) &&
            tr[i]
              .getElementsByTagName('td')[5]
              .textContent.toUpperCase()
              .includes(search6) &&
            tr[i]
              .getElementsByTagName('td')[6]
              .textContent.toUpperCase()
              .includes(search7) &&
            tr[i]
              .getElementsByTagName('td')[7]
              .textContent.toUpperCase()
              .includes(search8) &&
            tr[i]
              .getElementsByTagName('td')[8]
              .textContent.toUpperCase()
              .includes(search9) &&
            tr[i]
              .getElementsByTagName('td')[9]
              .textContent.toUpperCase()
              .includes(search10)
          ) {
            tr[i].style.display = ''
          } else {
            tr[i].style.display = 'none'
          }
        }
      }
    },
    sortList2(sortBy) {
      if (this.sortedbyASC2) {
        // Sort in ascending order
        this.sortedData2.sort((a, b) =>
          (a[sortBy] ? a[sortBy] : '').localeCompare(
            b[sortBy] ? b[sortBy] : '',
          ),
        )
      } else {
        // Sort in descending order
        this.sortedData2.sort((a, b) =>
          (b[sortBy] ? b[sortBy] : '').localeCompare(
            a[sortBy] ? a[sortBy] : '',
          ),
        )
      }
      // Toggle the flag for next click
      this.sortedbyASC2 = !this.sortedbyASC2
    },
    filterRows2(event) {
      var inputField, parent, table, tr, td, i, txtValue, idx
      let search1 = $('#myInput-11').val().toUpperCase()
      let search2 = $('#myInput-12').val().toUpperCase()
      let search3 = $('#myInput-13').val().toUpperCase()
      let search4 = $('#myInput-14').val().toUpperCase()
      let search5 = $('#myInput-15').val().toUpperCase()
      let search6 = $('#myInput-16').val().toUpperCase()
      let search7 = $('#myInput-17').val().toUpperCase()
      let search8 = $('#myInput-18').val().toUpperCase()
      let search9 = $('#myInput-19').val().toUpperCase()
      let search10 = $('#myInput-20').val().toUpperCase()

      inputField = $(`#${event.target.id}`)
      parent = inputField.closest('table').attr('id')

      table = document.getElementById(parent)
      tr = table.getElementsByTagName('tr')
      idx = parseInt(event.target.id.replace(/\D/g, ''))
      if (idx >= 11 && idx <= 20) {
        idx = idx - 11
      }
      for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName('td')[idx]
        if (td) {
          txtValue = td.textContent || td.innerText
          if (
            tr[i]
              .getElementsByTagName('td')[0]
              .textContent.toUpperCase()
              .includes(search1) &&
            tr[i]
              .getElementsByTagName('td')[1]
              .textContent.toUpperCase()
              .includes(search2) &&
            tr[i]
              .getElementsByTagName('td')[2]
              .textContent.toUpperCase()
              .includes(search3) &&
            tr[i]
              .getElementsByTagName('td')[3]
              .textContent.toUpperCase()
              .includes(search4) &&
            tr[i]
              .getElementsByTagName('td')[4]
              .textContent.toUpperCase()
              .includes(search5) &&
            tr[i]
              .getElementsByTagName('td')[5]
              .textContent.toUpperCase()
              .includes(search6) &&
            tr[i]
              .getElementsByTagName('td')[6]
              .textContent.toUpperCase()
              .includes(search7) &&
            tr[i]
              .getElementsByTagName('td')[7]
              .textContent.toUpperCase()
              .includes(search8) &&
            tr[i]
              .getElementsByTagName('td')[8]
              .textContent.toUpperCase()
              .includes(search9) &&
            tr[i]
              .getElementsByTagName('td')[9]
              .textContent.toUpperCase()
              .includes(search10)
          ) {
            tr[i].style.display = ''
          } else {
            tr[i].style.display = 'none'
          }
        }
      }
    },
    sortList3(sortBy) {
      if (this.sortedbyASC3) {
        // Sort in ascending order
        this.sortedData3.sort((a, b) =>
          (a[sortBy] ? a[sortBy] : '').localeCompare(
            b[sortBy] ? b[sortBy] : '',
          ),
        )
      } else {
        // Sort in descending order
        this.sortedData3.sort((a, b) =>
          (b[sortBy] ? b[sortBy] : '').localeCompare(
            a[sortBy] ? a[sortBy] : '',
          ),
        )
      }
      // Toggle the flag for next click
      this.sortedbyASC3 = !this.sortedbyASC3
    },
    filterRows3(event) {
      var inputField, parent, table, tr, td, i, txtValue, idx
      let search1 = $('#myInput-21').val().toUpperCase()
      let search2 = $('#myInput-22').val().toUpperCase()
      let search3 = $('#myInput-23').val().toUpperCase()
      let search4 = $('#myInput-24').val().toUpperCase()
      let search5 = $('#myInput-25').val().toUpperCase()
      let search6 = $('#myInput-26').val().toUpperCase()
      let search7 = $('#myInput-27').val().toUpperCase()
      let search8 = $('#myInput-28').val().toUpperCase()
      let search9 = $('#myInput-29').val().toUpperCase()
      let search10 = $('#myInput-30').val().toUpperCase()

      inputField = $(`#${event.target.id}`)
      parent = inputField.closest('table').attr('id')

      table = document.getElementById(parent)
      tr = table.getElementsByTagName('tr')
      idx = parseInt(event.target.id.replace(/\D/g, ''))
      if (idx >= 21 && idx <= 30) {
        idx = idx - 21
      }
      for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName('td')[idx]
        if (td) {
          txtValue = td.textContent || td.innerText
          if (
            tr[i]
              .getElementsByTagName('td')[0]
              .textContent.toUpperCase()
              .includes(search1) &&
            tr[i]
              .getElementsByTagName('td')[1]
              .textContent.toUpperCase()
              .includes(search2) &&
            tr[i]
              .getElementsByTagName('td')[2]
              .textContent.toUpperCase()
              .includes(search3) &&
            tr[i]
              .getElementsByTagName('td')[3]
              .textContent.toUpperCase()
              .includes(search4) &&
            tr[i]
              .getElementsByTagName('td')[4]
              .textContent.toUpperCase()
              .includes(search5) &&
            tr[i]
              .getElementsByTagName('td')[5]
              .textContent.toUpperCase()
              .includes(search6) &&
            tr[i]
              .getElementsByTagName('td')[6]
              .textContent.toUpperCase()
              .includes(search7) &&
            tr[i]
              .getElementsByTagName('td')[7]
              .textContent.toUpperCase()
              .includes(search8) &&
            tr[i]
              .getElementsByTagName('td')[8]
              .textContent.toUpperCase()
              .includes(search9) &&
            tr[i]
              .getElementsByTagName('td')[9]
              .textContent.toUpperCase()
              .includes(search10)
          ) {
            tr[i].style.display = ''
          } else {
            tr[i].style.display = 'none'
          }
        }
      }
    },
    sortList4(sortBy) {
      if (this.sortedbyASC4) {
        // Sort in ascending order
        this.sortedData4.sort((a, b) =>
          (a[sortBy] ? a[sortBy] : '').localeCompare(
            b[sortBy] ? b[sortBy] : '',
          ),
        )
      } else {
        // Sort in descending order
        this.sortedData4.sort((a, b) =>
          (b[sortBy] ? b[sortBy] : '').localeCompare(
            a[sortBy] ? a[sortBy] : '',
          ),
        )
      }
      // Toggle the flag for next click
      this.sortedbyASC4 = !this.sortedbyASC4
    },
    filterRows4(event) {
      var inputField, parent, table, tr, td, i, txtValue, idx
      let search1 = $('#myInput-31').val().toUpperCase()
      let search2 = $('#myInput-32').val().toUpperCase()
      let search3 = $('#myInput-33').val().toUpperCase()
      let search4 = $('#myInput-34').val().toUpperCase()
      let search5 = $('#myInput-35').val().toUpperCase()
      let search6 = $('#myInput-36').val().toUpperCase()
      let search7 = $('#myInput-37').val().toUpperCase()
      let search8 = $('#myInput-38').val().toUpperCase()
      let search9 = $('#myInput-39').val().toUpperCase()
      let search10 = $('#myInput-40').val().toUpperCase()

      inputField = $(`#${event.target.id}`)
      parent = inputField.closest('table').attr('id')

      table = document.getElementById(parent)
      tr = table.getElementsByTagName('tr')
      idx = parseInt(event.target.id.replace(/\D/g, ''))
      if (idx >= 31 && idx <= 40) {
        idx = idx - 31
      }
      for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName('td')[idx]
        if (td) {
          txtValue = td.textContent || td.innerText
          if (
            tr[i]
              .getElementsByTagName('td')[0]
              .textContent.toUpperCase()
              .includes(search1) &&
            tr[i]
              .getElementsByTagName('td')[1]
              .textContent.toUpperCase()
              .includes(search2) &&
            tr[i]
              .getElementsByTagName('td')[2]
              .textContent.toUpperCase()
              .includes(search3) &&
            tr[i]
              .getElementsByTagName('td')[3]
              .textContent.toUpperCase()
              .includes(search4) &&
            tr[i]
              .getElementsByTagName('td')[4]
              .textContent.toUpperCase()
              .includes(search5) &&
            tr[i]
              .getElementsByTagName('td')[5]
              .textContent.toUpperCase()
              .includes(search6) &&
            tr[i]
              .getElementsByTagName('td')[6]
              .textContent.toUpperCase()
              .includes(search7) &&
            tr[i]
              .getElementsByTagName('td')[7]
              .textContent.toUpperCase()
              .includes(search8) &&
            tr[i]
              .getElementsByTagName('td')[8]
              .textContent.toUpperCase()
              .includes(search9) &&
            tr[i]
              .getElementsByTagName('td')[9]
              .textContent.toUpperCase()
              .includes(search10)
          ) {
            tr[i].style.display = ''
          } else {
            tr[i].style.display = 'none'
          }
        }
      }
    },
    sortList5(sortBy) {
      if (this.sortedbyASC5) {
        // Sort in ascending order
        this.sortedData5.sort((a, b) =>
          (a[sortBy] ? a[sortBy] : '').localeCompare(
            b[sortBy] ? b[sortBy] : '',
          ),
        )
      } else {
        // Sort in descending order
        this.sortedData5.sort((a, b) =>
          (b[sortBy] ? b[sortBy] : '').localeCompare(
            a[sortBy] ? a[sortBy] : '',
          ),
        )
      }
      // Toggle the flag for next click
      this.sortedbyASC5 = !this.sortedbyASC5
    },
    filterRows5(event) {
      var inputField, parent, table, tr, td, i, txtValue, idx
      let search1 = $('#myInput-41').val().toUpperCase()
      let search2 = $('#myInput-42').val().toUpperCase()
      let search3 = $('#myInput-43').val().toUpperCase()
      let search4 = $('#myInput-44').val().toUpperCase()
      let search5 = $('#myInput-45').val().toUpperCase()
      let search6 = $('#myInput-46').val().toUpperCase()
      let search7 = $('#myInput-47').val().toUpperCase()
      let search8 = $('#myInput-48').val().toUpperCase()
      let search9 = $('#myInput-49').val().toUpperCase()
      let search10 = $('#myInput-50').val().toUpperCase()

      inputField = $(`#${event.target.id}`)
      parent = inputField.closest('table').attr('id')

      table = document.getElementById(parent)
      tr = table.getElementsByTagName('tr')
      idx = parseInt(event.target.id.replace(/\D/g, ''))
      if (idx >= 41 && idx <= 50) {
        idx = idx - 41
      }
      for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName('td')[idx]
        if (td) {
          txtValue = td.textContent || td.innerText
          if (
            tr[i]
              .getElementsByTagName('td')[0]
              .textContent.toUpperCase()
              .includes(search1) &&
            tr[i]
              .getElementsByTagName('td')[1]
              .textContent.toUpperCase()
              .includes(search2) &&
            tr[i]
              .getElementsByTagName('td')[2]
              .textContent.toUpperCase()
              .includes(search3) &&
            tr[i]
              .getElementsByTagName('td')[3]
              .textContent.toUpperCase()
              .includes(search4) &&
            tr[i]
              .getElementsByTagName('td')[4]
              .textContent.toUpperCase()
              .includes(search5) &&
            tr[i]
              .getElementsByTagName('td')[5]
              .textContent.toUpperCase()
              .includes(search6) &&
            tr[i]
              .getElementsByTagName('td')[6]
              .textContent.toUpperCase()
              .includes(search7) &&
            tr[i]
              .getElementsByTagName('td')[7]
              .textContent.toUpperCase()
              .includes(search8) &&
            tr[i]
              .getElementsByTagName('td')[8]
              .textContent.toUpperCase()
              .includes(search9) &&
            tr[i]
              .getElementsByTagName('td')[9]
              .textContent.toUpperCase()
              .includes(search10)
          ) {
            tr[i].style.display = ''
          } else {
            tr[i].style.display = 'none'
          }
        }
      }
    },
    sortList6(sortBy) {
      if (this.sortedbyASC6) {
        // Sort in ascending order
        this.sortedData6.sort((a, b) =>
          (a[sortBy] ? a[sortBy] : '').localeCompare(
            b[sortBy] ? b[sortBy] : '',
          ),
        )
      } else {
        // Sort in descending order
        this.sortedData6.sort((a, b) =>
          (b[sortBy] ? b[sortBy] : '').localeCompare(
            a[sortBy] ? a[sortBy] : '',
          ),
        )
      }
      // Toggle the flag for next click
      this.sortedbyASC6 = !this.sortedbyASC6
    },
    filterRows6(event) {
      var inputField, parent, table, tr, td, i, txtValue, idx
      let search1 = $('#myInput-51').val().toUpperCase()
      let search2 = $('#myInput-52').val().toUpperCase()
      let search3 = $('#myInput-53').val().toUpperCase()
      let search4 = $('#myInput-54').val().toUpperCase()
      let search5 = $('#myInput-55').val().toUpperCase()
      let search6 = $('#myInput-56').val().toUpperCase()
      let search7 = $('#myInput-57').val().toUpperCase()
      let search8 = $('#myInput-58').val().toUpperCase()
      let search9 = $('#myInput-59').val().toUpperCase()
      let search10 = $('#myInput-60').val().toUpperCase()

      inputField = $(`#${event.target.id}`)
      parent = inputField.closest('table').attr('id')

      table = document.getElementById(parent)
      tr = table.getElementsByTagName('tr')
      idx = parseInt(event.target.id.replace(/\D/g, ''))
      if (idx >= 51 && idx <= 60) {
        idx = idx - 51
      }
      for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName('td')[idx]
        if (td) {
          txtValue = td.textContent || td.innerText
          if (
            tr[i]
              .getElementsByTagName('td')[0]
              .textContent.toUpperCase()
              .includes(search1) &&
            tr[i]
              .getElementsByTagName('td')[1]
              .textContent.toUpperCase()
              .includes(search2) &&
            tr[i]
              .getElementsByTagName('td')[2]
              .textContent.toUpperCase()
              .includes(search3) &&
            tr[i]
              .getElementsByTagName('td')[3]
              .textContent.toUpperCase()
              .includes(search4) &&
            tr[i]
              .getElementsByTagName('td')[4]
              .textContent.toUpperCase()
              .includes(search5) &&
            tr[i]
              .getElementsByTagName('td')[5]
              .textContent.toUpperCase()
              .includes(search6) &&
            tr[i]
              .getElementsByTagName('td')[6]
              .textContent.toUpperCase()
              .includes(search7) &&
            tr[i]
              .getElementsByTagName('td')[7]
              .textContent.toUpperCase()
              .includes(search8) &&
            tr[i]
              .getElementsByTagName('td')[8]
              .textContent.toUpperCase()
              .includes(search9) &&
            tr[i]
              .getElementsByTagName('td')[9]
              .textContent.toUpperCase()
              .includes(search10)
          ) {
            tr[i].style.display = ''
          } else {
            tr[i].style.display = 'none'
          }
        }
      }
    },
  },
}
</script>

<style scoped>
.nav-pills > li.active > a,
.nav-pills > li.active > a:focus,
.nav-pills > li.active > a:hover {
  color: #fff !important;
  background-color: #01472e;
  border: none !important;
  box-shadow: #014b053e 0 0 10px;
}

.tab-area .nav-pills .nav-link:not(.active):hover {
  color: #ffffff !important;
  background-color: #01472e !important;
}

.style-class:hover {
  color: red !important;
  font-weight: 600;
}
.pro_image {
  width: 100%;
  height: auto;
  object-fit: cover;
}
.list_image {
  position: relative;
  margin-right: 10px;
  display: flex;
  margin-left: 10px;
  box-shadow: 0 0 4px #000;
  border-radius: 8px;
}
[type='text']:focus {
  --tw-ring-color: #c7c7c7 !important;
}
.style-class {
  color: rgb(0, 0, 0) !important;
  background-color: none !important;
  border: 0.1px solid #0000006c !important;
  font-size: 15px !important;
  font-weight: 500;
  border-radius: 4px !important ;
  margin-left: 10px;
  margin-top: 10px !important;
}

.tab-menu {
  size: 20% !important;
  width: 90%;
}
.tab-menu ul {
  box-shadow: none !important;
}
@media only screen and (max-width: 600px) {
  .list_image {
    display: flex;
    height: 200px !important;
  }
  .pr-blw-img-list {
    flex-direction: column;
    gap: 24px;
  }

  .tab_parent {
    display: flex !important;
    gap: 5px !important;
    margin: 0 !important;
    justify-content: space-between;
    flex-wrap: nowrap !important;
    overflow: auto !important;
  }
  .tab_child {
    flex: 0 0 auto;
  }
  .nav-item a {
    margin: 0 !important;
    font-size: 11px !important;
    padding: 5px 10px !important;
    border: 1px solid #ddd !important;
  }
  .tab-menu {
    margin: auto;
    margin: 0 !important;
    width: 100% !important;
    padding-inline: 13px !important;
  }
  .tab-content {
    padding: 0 !important;
    margin-top: 25px !important;
  }
}
</style>
