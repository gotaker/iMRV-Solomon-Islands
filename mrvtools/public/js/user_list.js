frappe.listview_settings["Mitigations"] = {
	refresh:function(){
        $("[class='user-action']").closest('li').css({"display":"none"});
        $("span.menu-item-label[data-label='Edit']").closest('li').css({"display":"none"});
        $("span.menu-item-label[data-label='Assign%20To']").closest('li').css({"display":"none"});
        $("span.menu-item-label[data-label='Apply%20Assignment%20Rule']").closest('li').css({"display":"none"});
        $("span.menu-item-label[data-label='Add%20Tags']").closest('li').css({"display":"none"});
        $("span.menu-item-label[data-label='Print']").closest('li').css({"display":"none"});
	}
}