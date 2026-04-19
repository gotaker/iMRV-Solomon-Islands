// frappe.ui.form.on('Project', {
//     refresh: function(frm) {
//         // Add your code here
//         setTimeout(function() {
//             function locations(e) {
//                 let url = $(e).attr('id');
//                 if (!url) {
//                     console.error("ID attribute is missing.");
//                     return;
//                 }

//                 const doctype_name = "Project"; 
//                 const recordListContainer = document.getElementById('recordList');
//                 recordListContainer.style.display = "none";

//                 frappe.call({
//                     method: "frappe.client.get_list",
//                     args: {
//                         doctype: doctype_name,
//                         filters: [],
//                         fields: ["name"],
//                     },
//                     callback: function(response) {
//                         if (response.message) {
//                             const records = response.message;
//                             const recordListContainer = document.getElementById('recordList');

//                             recordListContainer.innerHTML = '';

//                             records.forEach(function(record) {
//                                 const listItem = document.createElement('li');
//                                 const link = document.createElement('a');
//                                 link.href = `/app/${url}/${record.name}`;
//                                 link.textContent = record.name;
//                                 listItem.appendChild(link);
//                                 recordListContainer.appendChild(listItem);
//                             });

//                             frappe.set_route(`/app/${url}/`);
//                             var route = frappe.get_route();
//                             console.log("Route", route);

//                             // Checking the current URL
//                             checkLocation(`/app/${url}/${record.name}`);
//                             recordListContainer.style.display = "block";

//                             docs_list(doctype_name);
//                         } else {
//                             console.log("No records found");
//                         }

//                         frappe.set_route(`/app/${url}/`);
//                     }
//                 });
//             }

//             // Example of how to call the locations function:
//             locations();

//             function checkLocation(targetURL) {
//                 loc = window.location.href;
//                 if (loc === targetURL) {
//                     console.log("Location: ", loc);
//                 } else {
//                     console.log("Not");
//                 }
//             }
//         }, 2000);
//     }
// });
