$(document).ready(function() {
    // Frappe's first-run setup wizard is a full-width layout with no left
    // margin; prepending the sidebar to <body> covers its form fields.
    // Guard on the wizard route, not `setup_complete === 0`: this project's
    // `on_session_creation` sends users to /app/main-dashboard and bypasses
    // the wizard, so the flag can stay 0 on an otherwise-provisioned site.
    if ((window.location.pathname.startsWith('/app/setup-wizard') || window.location.pathname.startsWith('/desk/setup-wizard'))) return;

    // Floating drawer: inject trigger + backdrop synchronously so the user
    // sees an open-menu affordance during the get_menulist round-trip.
    fsmInjectTrigger();

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
            fsmAttachDrawer();
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
        // Cache for drawer-open re-run; the side-effects (record list visibility,
        // search box, treeview hide/show) are invisible while the drawer is closed.
        fsmLastFrm = frm;
        fsmRerunRefresh = handleFormRefresh;

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
    



    searchInput?.addEventListener('input', function() {
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


// Unified accordion: toggles `.fsm-expanded` on the parent <li class="treeview drop-down">.
// Handles both .treeview-menu (side_menu1.html) and .submenu (drill_down variants).
// Single-open: collapsing siblings before expanding the clicked one.
function toggleSubMenu(element) {
    const parentLi = element.closest('li.treeview.drop-down');
    if (!parentLi) return;

    const childPanel = parentLi.querySelector(':scope > .submenu, :scope > .side-menu > .treeview-menu, :scope > .treeview-menu');
    if (!childPanel) return;

    const isOpen = parentLi.classList.contains('fsm-expanded');

    // Collapse all siblings first
    document.querySelectorAll('li.treeview.drop-down.fsm-expanded').forEach(function(li) {
        if (li === parentLi) return;
        li.classList.remove('fsm-expanded');
        const sibPanel = li.querySelector(':scope > .submenu, :scope > .side-menu > .treeview-menu, :scope > .treeview-menu');
        if (sibPanel) sibPanel.style.maxHeight = '0px';
        const sibIcon = li.querySelector('i.fa-angle-down');
        if (sibIcon) sibIcon.classList.replace('fa-angle-down', 'fa-angle-right');
        const sibToggle = li.querySelector(':scope > a[role="button"]');
        if (sibToggle) sibToggle.setAttribute('aria-expanded', 'false');
    });

    if (isOpen) {
        parentLi.classList.remove('fsm-expanded');
        childPanel.style.maxHeight = '0px';
        const icon = parentLi.querySelector('i.fa-angle-down');
        if (icon) icon.classList.replace('fa-angle-down', 'fa-angle-right');
    } else {
        parentLi.classList.add('fsm-expanded');
        childPanel.style.maxHeight = childPanel.scrollHeight + 'px';
        const icon = parentLi.querySelector('i.fa-angle-right');
        if (icon) icon.classList.replace('fa-angle-right', 'fa-angle-down');
    }
    if (element.getAttribute('role') === 'button') {
        element.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
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
    frappe.set_route("main-dashboard");
}

// Defining Default dynamic workspace

$(window).ready(function(){
    setTimeout(function() {
        var windloc = window.location.pathname;
        if (windloc === "/app" || windloc === "/app/") {
            frappe.set_route("main-dashboard");
        }
    });
})

// Breadcrumb home icon → main-dashboard. v16 ships the first breadcrumb
// <li><a href="/desk"> on a <ul class="navbar-breadcrumbs"> (class, not id).
// Doctype list controllers re-render the breadcrumb DOM AFTER frappe.router's
// `change` event fires, wiping any href/onclick set from a router callback
// (verified Round-2 QA 2026-04-28: home icon on /desk/project went to /desk
// raw root → Frappe workspace switcher). A MutationObserver re-applies the
// rewrite on every breadcrumb insertion/replacement so no re-render escapes.
function setBreadcrumbHome() {
    var $home = $(".navbar-breadcrumbs li:first-child a");
    if (!$home.length) return;
    if ($home.attr("href") === "/app/main-dashboard" && $home.data("fsm-home-wired")) return;
    $home.attr("href", "/app/main-dashboard");
    // The home icon in the breadcrumb is rendered as <a><svg .home-icon/></a>
    // with no visible text. Without an accessible name screen readers announce
    // it as "link" — the audit (Issue #S4) flagged this. Mirror the label on
    // both `aria-label` (assistive tech) and `title` (mouse hover tooltip).
    if (!$home.attr("aria-label")) $home.attr("aria-label", "Home");
    if (!$home.attr("title")) $home.attr("title", "Home");
    $home.data("fsm-home-wired", true);
    $home.off("click.fsm").on("click.fsm", function (e) {
        // Preserve modifier-click escape hatch — let the browser open in a new
        // tab when the user explicitly asks for it.
        if (e.button === 1 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        e.preventDefault();
        gotodashboard();
    });
}

(function wireBreadcrumbHome() {
    // Initial rewrite for the first paint.
    setBreadcrumbHome();

    // Re-wire whenever Frappe replaces the breadcrumb subtree.
    var target = document.querySelector("header, .navbar, body") || document.body;
    if (window.MutationObserver && target) {
        new MutationObserver(function () { setBreadcrumbHome(); })
            .observe(target, { childList: true, subtree: true });
    }

    // Belt-and-suspenders for the router transition itself.
    if (window.frappe && frappe.router && frappe.router.on) {
        frappe.router.on("change", function () { setBreadcrumbHome(); });
    }
})();

// /desk raw root renders the Frappe workspace switcher (Framework / Settings /
// Tools) which is a confusing dead-end for iMRV users. Redirect to the iMRV
// main-dashboard whenever someone lands on bare `/desk` or `/desk/`.
(function redirectDeskRoot() {
    if (location.pathname === "/desk" || location.pathname === "/desk/") {
        location.replace("/desk/main-dashboard");
    }
})();


// =====================================================================
// FSM Floating Drawer
// ---------------------------------------------------------------------
// Owns the trigger button, backdrop, and drawer state machine. The
// drawer DOM (.main-sidebar) is injected by the get_menulist callback
// above; this code wires it once it lands.
// =====================================================================

var fsmTriggerEl = null;
var fsmBackdropEl = null;
var fsmDrawerEl = null;
var fsmCloseBtnEl = null;
var fsmLastFrm = null;
var fsmRerunRefresh = null;

function fsmMakeIconButton(className, ariaLabel, iconClass) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = className;
    btn.setAttribute('aria-label', ariaLabel);
    var icon = document.createElement('i');
    icon.className = iconClass;
    icon.setAttribute('aria-hidden', 'true');
    btn.appendChild(icon);
    return btn;
}

function fsmInjectTrigger() {
    if (document.querySelector('.fsm-trigger')) return;

    fsmTriggerEl = fsmMakeIconButton('fsm-trigger', 'Open navigation menu', 'fi fi-rr-menu-burger');
    fsmTriggerEl.setAttribute('aria-expanded', 'false');
    fsmTriggerEl.setAttribute('aria-controls', 'fsm-drawer');
    fsmTriggerEl.addEventListener('click', fsmOpenDrawer);
    document.body.appendChild(fsmTriggerEl);

    fsmBackdropEl = document.createElement('div');
    fsmBackdropEl.className = 'fsm-backdrop';
    fsmBackdropEl.setAttribute('aria-hidden', 'true');
    fsmBackdropEl.addEventListener('click', fsmCloseDrawer);
    document.body.appendChild(fsmBackdropEl);

    document.documentElement.style.setProperty(
        '--fsm-scrollbar-w',
        (window.innerWidth - document.documentElement.clientWidth) + 'px'
    );

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && document.body.classList.contains('fsm-open')) {
            fsmCloseDrawer();
        }
    });

    window.addEventListener('hashchange', function() {
        if (document.body.classList.contains('fsm-open')) fsmCloseDrawer();
    });

    // Auto-close when any Frappe Bootstrap modal opens — modals (z-index 1050)
    // would otherwise sit above the drawer (z-index 1040) but the dimming and
    // focus would feel wrong. Closing first restores normal modal interaction.
    // Pass returnFocus:false so the trigger doesn't steal focus from the modal.
    // Frappe v16 fires `show` on the modal element (jQuery-only); older
    // Bootstrap fires `show.bs.modal`. Listen for both, gate on .modal class.
    $(document).on('show.bs.modal show', function(e) {
        var t = e.target;
        if (e.type === 'show' && (!t || !t.classList || !t.classList.contains('modal'))) return;
        if (document.body.classList.contains('fsm-open')) {
            fsmCloseDrawer({ returnFocus: false });
        }
    });

    // Hide the floating trigger on the setup wizard route (covers SPA navigation
    // from a non-wizard page to /app/setup-wizard, which the $(document).ready
    // guard at the top of this file does not catch).
    if (frappe && frappe.router && typeof frappe.router.on === 'function') {
        frappe.router.on('change', fsmSyncWizardVisibility);
    }
    fsmSyncWizardVisibility();
}

function fsmSyncWizardVisibility() {
    var p = window.location.pathname;
    var onWizard = p.indexOf('/app/setup-wizard') === 0 || p.indexOf('/desk/setup-wizard') === 0;
    if (fsmTriggerEl) fsmTriggerEl.style.display = onWizard ? 'none' : '';
    if (fsmBackdropEl) fsmBackdropEl.style.display = onWizard ? 'none' : '';
    if (onWizard && document.body.classList.contains('fsm-open')) {
        fsmCloseDrawer({ returnFocus: false });
    }
}

function fsmAttachDrawer() {
    fsmDrawerEl = document.querySelector('.main-sidebar');
    if (!fsmDrawerEl) return;
    if (fsmDrawerEl.id === 'fsm-drawer') return; // idempotent — already wired

    fsmDrawerEl.id = 'fsm-drawer';
    fsmDrawerEl.setAttribute('role', 'dialog');
    fsmDrawerEl.setAttribute('aria-modal', 'true');
    fsmDrawerEl.setAttribute('aria-label', 'Navigation');
    fsmDrawerEl.setAttribute('aria-hidden', 'true');
    fsmDrawerEl.removeAttribute('style');

    fsmCloseBtnEl = fsmMakeIconButton('fsm-close', 'Close navigation', 'fi fi-rr-cross-small');
    fsmCloseBtnEl.addEventListener('click', fsmCloseDrawer);
    fsmDrawerEl.insertBefore(fsmCloseBtnEl, fsmDrawerEl.firstChild);

    fsmDedupeUserInfo();

    fsmDrawerEl.addEventListener('click', function(e) {
        var a = e.target.closest('a');
        if (!a) return;

        // Modifier-click escape hatch: let the browser handle middle-click,
        // ctrl/cmd-click (open in new tab), shift-click (new window),
        // alt-click (download). Without this we strip status-bar preview,
        // copy-link-address, and middle-click-to-new-tab — exactly what the
        // sidebar audit (Issue #S1) flagged when 40 of 41 items had href=null
        // and the click handler always preventDefaulted.
        if (e.button === 1 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) {
            return;
        }

        // side_menu1.html's parent <a class="link menu"> has no onclick, so we
        // delegate the accordion toggle here for ANY anchor that is a direct
        // child of <li class="treeview drop-down"> AND that li has a panel.
        var parentLi = a.parentElement;
        if (parentLi && parentLi.classList.contains('treeview') && parentLi.classList.contains('drop-down')) {
            var hasPanel = parentLi.querySelector(
                ':scope > .submenu, :scope > .side-menu > .treeview-menu, :scope > .treeview-menu'
            );
            if (hasPanel) {
                e.preventDefault();
                toggleSubMenu(a);
                return;
            }
        }

        var onclickAttr = a.getAttribute('onclick') || '';
        if (onclickAttr.indexOf('toggleSubMenu') !== -1) return;

        // Honour real href for SPA navigation: leaf anchors now carry both an
        // `id="/app/..." onclick="go_to_page(this)"` pair AND a real href= so
        // hover preview, right-click copy, and modifier-clicks work natively.
        // For a plain left-click, route through frappe.set_route to keep the
        // SPA navigation feel (no full page reload).
        var href = a.getAttribute('href') || '';
        var hasGoToPage = onclickAttr.indexOf('go_to_page') !== -1;
        var hasGotoDash = onclickAttr.indexOf('gotodashboard') !== -1;
        if (href && href.charAt(0) !== '#' && (hasGoToPage || hasGotoDash || !onclickAttr)) {
            e.preventDefault();
            if (window.frappe && typeof window.frappe.set_route === 'function') {
                // Strip leading /app or /desk so set_route receives the route only.
                var route = href.replace(/^\/(app|desk)\/?/, '');
                if (route) {
                    window.frappe.set_route(route);
                } else {
                    window.location.href = href;
                }
            } else {
                window.location.href = href;
            }
        }
        // Treat any other anchor as nav — close the drawer once nav is en route.
        setTimeout(fsmCloseDrawer, 80);
    });

    // Middle-click (auxclick) — most browsers don't fire `click` for the middle
    // button; let the browser open the href in a new tab natively. We just
    // avoid swallowing the event.
    fsmDrawerEl.addEventListener('auxclick', function(e) {
        if (e.button !== 1) return;
        // No-op: don't preventDefault, browser opens href in background tab.
    });

    fsmDrawerEl.addEventListener('keydown', fsmTrapFocus);

    // Keyboard activation for role="button" accordion toggles (Enter / Space).
    // Without this, tab-focused screen-reader users can't open submenus.
    fsmDrawerEl.addEventListener('keydown', function(e) {
        if (e.key !== 'Enter' && e.key !== ' ') return;
        var target = e.target;
        if (!target || target.getAttribute('role') !== 'button') return;
        var parentLi = target.parentElement;
        if (!parentLi || !parentLi.classList.contains('treeview') || !parentLi.classList.contains('drop-down')) return;
        e.preventDefault();
        toggleSubMenu(target);
    });

    document.body.classList.add('fsm-ready');
}

// Move the first .treeview-menu .user-info into a single drawer footer block
// and REMOVE the rest. side_menu1.html embeds .user-info inside every
// .treeview-menu so without this it would render 7+ duplicate banners.
// Audit Issue #S2 flagged that just hiding via `display:none` still left the
// nodes in the accessibility tree — remove them outright so screen readers
// don't enumerate them.
function fsmDedupeUserInfo() {
    if (!fsmDrawerEl) return;
    var infos = fsmDrawerEl.querySelectorAll('.treeview-menu .user-info');
    if (!infos.length) return;

    // Skip work if we've already deduped (idempotent — guards against repeat
    // calls when the drawer template is re-rendered).
    if (fsmDrawerEl.querySelector('.fsm-user-footer')) {
        infos.forEach(function(node) {
            if (node.parentNode) node.parentNode.removeChild(node);
        });
        return;
    }

    var footer = document.createElement('div');
    footer.className = 'fsm-user-footer';
    // Clone children of the first user-info node into the footer (preserves
    // server-rendered escaped DOM without re-parsing as HTML).
    var children = infos[0].childNodes;
    for (var i = 0; i < children.length; i++) {
        footer.appendChild(children[i].cloneNode(true));
    }
    fsmDrawerEl.appendChild(footer);

    // Remove every embedded .user-info — the canonical instance now lives in
    // the footer. Removal (vs class+display:none) keeps the a11y tree clean.
    infos.forEach(function(node) {
        if (node.parentNode) node.parentNode.removeChild(node);
    });
}

function fsmOpenDrawer() {
    if (!fsmDrawerEl) return;
    document.body.classList.add('fsm-open');
    if (fsmTriggerEl) fsmTriggerEl.setAttribute('aria-expanded', 'true');
    fsmDrawerEl.setAttribute('aria-hidden', 'false');

    // Re-run the per-doctype form-refresh handler so the record list / search /
    // treeview hide-show state matches the current page when the drawer opens.
    if (fsmLastFrm && typeof fsmRerunRefresh === 'function') {
        try { fsmRerunRefresh(fsmLastFrm); } catch (err) { /* swallow */ }
    }

    setTimeout(function() {
        if (!fsmDrawerEl) return;
        var focusable = fsmDrawerEl.querySelector('a[href], a[onclick], button:not([disabled])');
        if (focusable) focusable.focus();
    }, 50);
}

function fsmCloseDrawer(opts) {
    if (!fsmDrawerEl) return;
    document.body.classList.remove('fsm-open');
    if (fsmTriggerEl) {
        fsmTriggerEl.setAttribute('aria-expanded', 'false');
        // Skip focus return when closure is involuntary (e.g., modal opening).
        // Otherwise we'd steal focus from the modal that's about to render.
        if (!opts || opts.returnFocus !== false) {
            fsmTriggerEl.focus();
        }
    }
    fsmDrawerEl.setAttribute('aria-hidden', 'true');
}

function fsmTrapFocus(e) {
    if (e.key !== 'Tab' || !document.body.classList.contains('fsm-open')) return;
    if (!fsmDrawerEl) return;

    var nodes = fsmDrawerEl.querySelectorAll(
        'a[href], a[onclick], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    var focusable = Array.prototype.filter.call(nodes, function(el) {
        return el.offsetWidth > 0 && el.offsetHeight > 0;
    });
    if (!focusable.length) return;

    var first = focusable[0];
    var last = focusable[focusable.length - 1];

    if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
    }
}


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
