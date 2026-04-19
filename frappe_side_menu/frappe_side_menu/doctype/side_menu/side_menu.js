// Copyright (c) 2023, NetZeroLabs and contributors
// For license information, please see license.txt

// frappe.ui.form.on('Side Menu', {
//     refresh(frm) {
//         frappe.call({
//             method: 'frappe_side_menu.frappe_side_menu.doctype.side_menu.side_menu.get_current_document_name',
//             args: {
//                 doctype: frm.doc.side_menu_settings
//             },
//             callback: function (r) {
//                 if (r.message) {
//                     console.log('Current Document Names: ' + r.message.join(', '));
//                 } else {
//                     frappe.msgprint('No document found for the specified doctype.');
//                 }
//             }
//         });

//         // Get the current route
//         var current_route = frappe.get_route();
//         var url_pattern = '/app/some_path/some_other_path/';

//         // Check if the current route matches the pattern
//         if (current_route.join('/') === url_pattern) {
//             console.log('Route matches the pattern: ' + url_pattern);
//             // Perform your action here
//         }
//     }
// });
