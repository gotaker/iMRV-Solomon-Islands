frappe.listview_settings[cur_list.doctype] = {
	refresh:function(){
        console.log('cur_list.doctype', cur_list.doctype);
        $('[class="search"]').css("display", "none");
        $('[id="recordListContainer"]').css("display", "none");
        $('[id="treeview"]').css("display", "contents");
	}
}   