$(document).ready(function() {
    $('[class="app-logo"]').css({
        "display": "block"
    });

    let pageLength
    let doctype = '';
    let currentPage = null;
    let isFetching = false;
    let records = []; 
    let start = 0; 

    frappe.call({
        method: "frappe_side_menu.frappe_side_menu.api.get_menulist",
        args: {},
        async: false,
        callback: function(r) {
            let roles = '';
            if ($.inArray('System Manager', frappe.user_roles) != -1)
                roles = 'Admin';
            else if ($.inArray('Super Admin', frappe.user_roles) != -1)
                roles = 'Admin';
            else if ($.inArray('Vendor', frappe.user_roles) != -1)
                roles = 'Vendor';
            else if ($.inArray('Admin', frappe.user_roles) != -1)
                roles = 'Admin';
            else
                roles = '';
            $('body').prepend(r.message.template_html);
        }
    });

    const sidebarMenuItems = document.querySelectorAll('.treeview');
    const searchInput = document.querySelector('.search-input');
    // SetHeight
    // window.addEventListener('resize', setRecordListContainerStyles);


    // _______________________________________x_____________X____________x____________________________________________
    
    function getQueryParam(param) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }
    
    function applyFilterAndFetchRecords() {
        const field = getQueryParam('field');
        const value = getQueryParam('value');
    
        if (field && value) {
        const filteredRecords = fetchRecordsBasedOnFilter(field, value);
            displayRecordsInSideMenu(filteredRecords);
        }
    }
    applyFilterAndFetchRecords();
  
    const currentForm = cur_list || {};
    handleFormRefresh(currentForm);


    function clearRecords() {
        records = [];
        start = 0;
    }

    function hidemainMenu() {
        sidebarMenuItems.forEach(item => {
            item.style.display = 'none';
        });
    }
    function showmainMenu() {
        sidebarMenuItems.forEach(item => {
            item.style.display = 'flex';
        });
    }

    let firstAttempt = true;

    function filterEvent() {
        if (cur_list && cur_list.filters && cur_list.filters.length > 0) {
            const nameFilter = cur_list.filters.find(filter => filter[1] === "name");

            if (nameFilter) {
                const nameFilterValue = nameFilter[3];
                const cleanedFilterValue = nameFilterValue.replace(/%/g, '');
                // console.log(cleanedFilterValue);
                const searchInput = document.querySelector('.search-input');
                if (searchInput) {
                    searchInput.value = cleanedFilterValue;
                    $('.search-input').focus()
                    searchInput.dispatchEvent(new Event('input'));
                    if($('.search-input').focus()){
                        // console.log("Focused");
                    }
                    firstAttempt = true;
                }
            }
        }
    }


    // function updateSelectedStylesAndScroll() {
    //     const recordList = document.getElementById('recordList');
    //     const listItems = recordList.getElementsByClassName('listItem');
    //     const {
    //         offsetHeight
    //     } = listItems[0];

    //     const containerHeight = document.getElementById('recordListContainer').offsetHeight;
    //     const scrollOffset = (selectedIndex - Math.floor(containerHeight / offsetHeight / 2)) * offsetHeight;

    //     [...listItems].forEach((item, i) => item.classList.toggle('selected', i === selectedIndex));
    //     recordList.scrollTop = scrollOffset;

    //     listItems[selectedIndex]?.scrollIntoView({
    //         behavior: 'smooth',
    //         block: 'center',
    //         inline: 'start'
    //     });
    // }

    function updateActiveRecord(lastName) {
        const recordList = document.getElementById('recordList');
    
        if (recordList || !recordList) {
            const listItems = recordList.getElementsByClassName('listItem');
    
            for (const listItem of listItems) {
                const link = listItem.querySelector('.recordLink');
                const href = link ? link.getAttribute('href') : null;
    
                if (href && href.endsWith(lastName)) {
                    listItem.classList.add('active');
                } else {
                    listItem.classList.remove('active');
                }
            }
        }
    }

    if ('features' in document) {
        document.features.allowedFeatures().then(features => {
            if (features.autoplay) {
                const videoElement = document.getElementById('yourVideoElementId');
                if (videoElement) {
                    videoElement.play();
                }
            }
        });
    }

    function loadMoreRecords() {
        if (!isFetching) {
            isFetching = true;

            pageLength = cur_list ? cur_list.page_length : 20;
            // console.log("Doc", doctype);
                // console.log("Logged");
                frappe.call({
                    method: "frappe.client.get_list",
                    args: {
                        doctype: doctype,
                        fields: ["name"],
                        limit_start: start,
                        limit_page_length: pageLength,
                    },
                        callback: function(response) {
                            try {
                                // console.log('Response:', response);
                                const newRecords = response.message || [];
        
                                if (newRecords.length > 0) {
                                    if (start === 0) {
                                        clearRecords();
                                    }
                                    records = records.concat(newRecords);
                                    start += newRecords.length;
        
                                    updateRecordList(records);
                                } else {
                                    // console.log('No more records to fetch.');
                                }
        
                                isFetching = false;
                            } catch (error) {
                                // console.error('Error processing response:', error);
                                isFetching = false;
                            }
                        },
                            error: function(error) {
                            // console.error('Error:', error);
                            isFetching = false;
                        }
                    });
    
        }
    }


    // const observer = new IntersectionObserver(entries => {
    //     entries.forEach(entry => {
    //         if (entry.isIntersecting) {
    //             entry.target.classList.add('new');
    //             observer.unobserve(entry.target);
    //         }
    //     });
    // }, { threshold: 0.5 });
            
    function updateRecordList(records) {
        const recordList = document.getElementById('recordList');
        recordList.innerHTML = '';
    
        records.forEach(function(record) {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            const infoContainer = document.createElement('div');
            const status = document.createElement('p');
            const icon = document.createElement('i');
            const lowercaseDoctype = doctype.toLowerCase().replace(/\s+/g, '-');
            const start_date = document.createElement('p');
    
            start_date.textContent = record.start_date || '';
            link.href = `/app/${lowercaseDoctype}/${record.name}`;
            link.textContent = `${record.name}`;
            status.textContent = record.status || '';
            status.className = 'status';
            start_date.className = "start_date";
            link.className = 'recordLink';
            listItem.className = 'listItem';
            infoContainer.className = 'infoContainer';
            icon.className = 'fa fa-angle-right documentIcon';
    
            infoContainer.appendChild(link);
            infoContainer.appendChild(status);
            infoContainer.appendChild(start_date);
            listItem.appendChild(infoContainer);
            listItem.appendChild(icon);
            recordList.appendChild(listItem);

            $('[class="search"]').css("display", "block");
                hidemainMenu();
    
            // console.log(hidemainMenu());
        });

        // observer.observe(recordList);
    
    }


    function handleFormRefresh(frm) {
        // console.log('handleFormRefresh called:', frm);
            try {
            const recordListContainer = document.getElementById('recordList');
    
            if (frm && frm.doc && frm.doc.doctype !== undefined && frm.doc.doctype !== "" && cur_frm.meta.issingle ==0 ) {
                // console.log('Form refreshed for doctype:', frm.doc.doctype);
                
                clearRecords();
                if(cur_frm.meta.issingle ==0){
                    
                $('[class="app-logo"]').css({
                    "display": "block"
                });
                $('[id="recordList"]').css({
                    "display": "contents"
                });
                $('[id="recordListContainer"]').css({
                    "display": "block"
                });
                $('[class="search"]').css("display", "block");
                }
                if(cur_frm.meta.issingle ==1){
                    $('[id="menuTab"]').click()
                }
                const newDoctype = frm.doc.doctype;
                // console.log(newDoctype);
    
                if (newDoctype !== doctype || !currentPage) {
                    doctype = newDoctype;
                    currentPage = null;
                    loadMoreRecords(doctype, recordListContainer);
                }
    
                if (searchInput) {
                    searchInput.value = '';
                }
    
                const currentRoute = frappe.router.current_sub_path;
                const parts = currentRoute.split('/');
                const lastName = parts[parts.length - 1];
    
                updateActiveRecord(lastName);
    
            }
        } catch (error) {
            // console.error('Error handling form refresh:', error);
        }
    }
        
 // _______________________________________x_____________X____________x____________________________________________

    $('#recordListContainer').scroll(function() {
        const container = $(this);
        const currentScrollPosition = container.scrollTop();

        if (currentScrollPosition + container.height() >= container.get(0).scrollHeight && !isFetching) {
            // console.log('Fetching next set of documents:', start + 1, 'to', start + pageLength);

            loadMoreRecords();
        }
    });


    $('[class="search"]').css("display", "none");
    $('[id="recordListContainer"]').css("display", "none");



    $(document).on("form-refresh", function(e, frm) {
        
        // $('[id="filterTab"]').click()
        if(frm.meta.issingle != 1){
            frappe.call({
                method: "frappe_side_menu.frappe_side_menu.api.get_doctype",
                callback: function(response) {
                    msg = response.message
                    if(msg == "Side Menu With Tab"){
                        hidemainMenu();
                    }
                }
            });
            sideMenu_route = frappe.get_route()
            handleFormRefresh(frm);
            filterEvent();
    
        }else if (frm.meta.issingle === 1) {
            console.log("Inside else if block for issingle === 1");
            $('[id="treeview"]').css("display", "contents");
            $('[id="recordListContainer"]').css("display", "none");
            $('[class="search"]').css("display", "none");
            $('[id="menuTab"]').click()
        }
    });

    document.addEventListener('click', function (event) {
        const target = event.target;
        if (target && target.classList && target.classList.contains('infoContainer')) {
            const link = target.querySelector('.recordLink');
            const href = link ? link.getAttribute('href') : null;
    
            if (href) {
                frappe.set_route(href);
            }
        }
    });
    



    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.trim().toLowerCase();
        const recordList = document.getElementById('recordList');
        const listItems = recordList.getElementsByClassName('listItem');
        let counter = 0;

        for (const listItem of listItems) {
            const linkText = listItem.textContent.toLowerCase();
            const shouldShow = linkText.includes(searchTerm);

            if (shouldShow) {
                counter++;
            }

            listItem.style.display = shouldShow ? 'flex' : 'none';
        }

        // if (searchInput.value === "") {
        //     countElement.textContent = ''; 
        // } else {
        //     countElement.textContent = `Filtered Records: ${counter}`;
        // }

        searchInput.dataset.lastSearchTerm = searchTerm;
    });

    // KeyNavigator
    // document.getElementById('recordList').addEventListener('click', ({
    //     target
    // }) => {
    //     const listItem = target.closest('.listItem');
    //     if (listItem) {
    //         selectedIndex = [...listItem.parentNode.children].indexOf(listItem);
    //         updateSelectedStylesAndScroll();
    //     }
    // });

    // let selectedIndex = -1;

    // document.addEventListener('keydown', ({
    //     key
    // }) => {
    //     const listItems = document.getElementById('recordList').getElementsByClassName('listItem');

    //     if (key === 'ArrowUp' || key === 'ArrowDown') {
    //         selectedIndex = Math.max(0, Math.min(listItems.length - 1, selectedIndex + (key === 'ArrowUp' ? -1 : 1)));
    //         updateSelectedStylesAndScroll();
    //     }

    //     if (key === 'Enter') {
    //         const link = listItems[selectedIndex]?.querySelector('.recordLink');
    //         const href = link?.getAttribute('href');

    //         if (href) {
    //             frappe.set_route(href);
    //         }
    //     }
    // });
    
});



$('[class="search"]').css("display", "none");
$('[id="recordListContainer"]').css("display", "none");


function toggleSubMenu(element) {
    const parentListItem = element.parentNode;
    const submenu = parentListItem.querySelector(".submenu");
    const isSubMenuOpen = submenu.style.maxHeight === "0px" || submenu.style.maxHeight === "";

    const allSubMenus = document.querySelectorAll(".treeview.drop-down .submenu"); 
    allSubMenus.forEach((sub) => {
        sub.style.maxHeight = "0";
        const menuIcon = sub.previousElementSibling.querySelector("i.fa-angle-down");
        if (menuIcon) {
            menuIcon.classList.replace("fa-angle-down", "fa-angle-right");
        }
    });

    if (isSubMenuOpen) {
        submenu.style.maxHeight = submenu.scrollHeight + "px";
        element.querySelector("i.fa-angle-right").classList.replace("fa-angle-right", "fa-angle-down");
    } else {
        submenu.style.maxHeight = "0px";
        element.querySelector("i.fa-angle-down").classList.replace("fa-angle-down", "fa-angle-right");
    }
}

const sidebarMenu = document.getElementById('sideMenu');

function showMenu() {
    // console.log("Menu function called");
    $('[class="treeview drop-down"]').css("display", "block");
    $('[id="recordListContainer"]').css("display", "none");
    $('[class="search"]').css("display", "none");
}

function showFilter() {
    $('[class="treeview drop-down"]').css("display", "none");
    $('[class="search"]').css("display", "block");
    $('[id="recordListContainer"]').css("display", "block");
}

function go_to_page(e) {
    let url = $(e).attr('id');
    frappe.set_route(url);
}

function gotodashboard(e) {

    frappe.db.get_single_value("Side Menu Settings", "route_logo").then(function(r){
        console.log(frappe.boot.allowed_workspaces);
        for(wrk of frappe.boot.allowed_workspaces){
            console.log(wrk);
            if(wrk == 'users'){
                console.log("logged");
            }
            else{
                console.log("no");
            }
        } 

        console.log("R", r);
        frappe.set_route(r);
    })
}

// Defining Default dynamic workspace

$(window).ready(function(){
    setTimeout(function() {
        windloc = window.location.pathname 
        frappe.db.get_single_value("Side Menu Settings", "route_logo").then(function(r){
            if (windloc== `/app`) {
            var updateroute = windloc + "/"+ r
            frappe.set_route(updateroute)
            }
            else if(windloc== `/app/`){
                var updateroute = windloc + r
                frappe.set_route(updateroute)
            }
        })
    });

})


// function toggleSidebar() {
//     var x = document.getElementById("sideMenu");
//     var mainSection = document.getElementsByClassName("layout-main-section-wrapper")[0];
//     var pageTitle = document.getElementsByClassName("page-title")[0];
//     var navbar = document.getElementsByClassName("navbar")[0];
//     console.log('Sidebar display:', x.style.display);
    
//     if (x.style.display === "none") {
//        x.style.display = "block";
//        mainSection.style.marginLeft = "{{ side_menu_settings.set_width }}px";
//        pageTitle.style.marginLeft = "{{ side_menu_settings.set_width }}px";
//        // navbar.style.marginLeft = "{{ side_menu_settings.set_width }}px";
//     } else  {
//        x.style.display = "none";
//        mainSection.style.marginLeft = "0";
//        pageTitle.style.marginLeft = "0";
//        navbar.style.marginLeft = "0";
//     }
//     }





// frappe.pages.on('page-change', function(route) {
//     console.log('Page changed to:', route);
//     toggleDocumentListVisibility();
// });
