frappe.pages["ghg-inventory-report"].on_page_load = (wrapper) => {
	frappe.ghg_inventory_report = new GHGInventoryGasWise(wrapper);
};

class GHGInventoryGasWise {
	constructor(parent) {
		frappe.ui.make_app_page({
			parent: parent,
			title: __("GHG Inventory Report"),
			single_column: false,
			card_layout: true,
		});

		this.parent = parent;
		this.page = this.parent.page;
		this.page.sidebar.html(
			`<ul class="standard-sidebar ghg_inventory_report-sidebar overlay-sidebar"></ul>`
		);
		this.$sidebar_list = this.page.sidebar.find("ul");
		// alert(frappe.defaults.get_user_default("Order"))
		this.datatable=null;
		// this.add_card_button_to_toolbar();
		this.set_default_secondary_action();
		this.ghg_year_filter();
		this.ghg_unit_filter();
		// this.render_datatable();
		// this.make();

		// this.create_date_range_field();
	}
	set_default_secondary_action() {
		this.refresh_button && this.refresh_button.remove();
		this.refresh_button = this.page.add_action_icon("refresh", () => {
			this.$container.empty()
			this.$report.empty()
			this.$heading.empty()
			// if(this.inventory_year[0].value != null){
			// 	this.wrapper1();
			// }
			// if(this.inventory_unit[0].value !=null){
			// 	this.wrapper2();
			// }
			
			if(this.inventory_year[0].value != null || this.inventory_year[0].value !=null){
				this.make()
				this.get_chart_report();
				this.get_chart_report2();
			}
			$('[class="all_html"]:first').remove()
			$('[class="report-heading"]:first').remove()
			this.render_datatable()
			
		});

		this.download_button = this.page.set_secondary_action('Download', () => {

			frappe.call('mrvtools.ghg_inventory.page.ghg_inventory_report.ghg_inventory_report.execute',{
				inventory_year:this.inventory_year[0].value,
				inventory_unit:this.inventory_unit[0].value
			})
				.then((r) => {
					frappe.call('mrvtools.ghg_inventory.page.ghg_inventory_report.ghg_inventory_report.download_excel',{
						columns:r.message[0],
						data:r.message[1]
					}).then((i) =>{
						window.open(i.message)
					})
				})
		})
	}
	// hide_btn() {
	// 	const toggleButtons = (hideBtn, showBtn, targetClass) => {
	// 	  $(hideBtn).click(() => {
	// 		$('[class="'+targetClass+'"]').toggle();
	// 		$(hideBtn).toggle();
	// 		$(showBtn).toggle();
	// 	  });
	  
	// 	  $(showBtn).click(() => {
	// 		$('[class="'+targetClass+'"]').toggle();
	// 		$(hideBtn).toggle();
	// 		$(showBtn).toggle();
	// 	  });
		  
	// 	  $(showBtn).toggle();
	// 	};
	  
	// 	$(document).ready(() => {
	// 	  toggleButtons("#hide_btn", "#show_btn", "totalghg_inventory_report-graph");
	// 	  toggleButtons("#hide_btn2", "#show_btn2", "totalghg_inventory_report-graph2");
	// 	});
	//   }

	wrapper1(){
		$("#ghg_chart").html(`
		<div class="ghg_inventory_report page-main-content">
			<div class="chart_hide" style="margin: 14px; display: flex; align-items: center; justify-content: space-between;">
				<b id="categories_chart1"></b>
				<button id="hide_btn" onclick="toggle_chart1()" class="btn btn-sm">Hide chart</button>
			</div>
			<script>
				function toggle_chart1() {
					var x = document.getElementById("chart-1");
					if (x.style.display === "none") {
					x.style.display = "block";
					document.getElementById("hide_btn").innerText = "Hide Chart"
					} else {
					x.style.display = "none";
					document.getElementById("hide_btn").innerText = "Show Chart"
					}
					
				}
				function toggle_chart2(){
					var y = document.getElementById("chart-2");
					if (y.style.display === "none") {
					y.style.display = "block";
					document.getElementById("hide_btn2").innerText = "Hide Chart"
					} else {
					y.style.display = "none";
					document.getElementById("hide_btn2").innerText = "Show Chart"
					}
				}
			</script>
			<div id="chart-1" class="totalghg_inventory_report-graph"></div>
		</div>`)
	}
	wrapper2(){
		$("#ghg_chart2").html(`
		<div class="ghg_inventory_report page-main-content">
		<div class="chart_hide" style="margin: 14px; display: flex; align-items: center; justify-content: space-between;">
			<b id="categories_chart2"></b>
			<button id="hide_btn2" onclick="toggle_chart2()" class="btn btn-sm">Hide chart</button>
		</div>
			<div id="chart-2" class="totalghg_inventory_report-graph2"></div>
		</div>`)
	}

	make() {
		this.$container = $(`
		<div class = "all_html"  style="margin:0;">
			<div id="ghg_chart"></div>
			<div id="ghg_chart2"></div>
		</div>
		`).appendTo(this.page.main);
		
		// this.$graph_area = this.$container.find(".totalghg_inventory_report-graph");
		// this.$graph_area2 = this.$container2.find(".totalghg_inventory_report-graph2");
		// this.hide_btn();
		// if(this.inventory_year[0].value != null){
		// 	this.wrapper1();
		// }
		// if(this.inventory_unit[0].value != null){
		// 	this.wrapper2();
		// }
		this.wrapper1();
		this.wrapper2();
		this.get_chart_report();
		this.get_chart_report2();

		// if(this.inventory_year[0].value != null){
			
		// }
		// if(this.inventory_unit[0].value != null){
			
		// }
	}
	

	get_chart_report() {
		
		frappe.call('mrvtools.ghg_inventory.page.ghg_inventory_report.ghg_inventory_report.get_chart',{
			inventory_year:this.inventory_year[0].value,
			inventory_unit:this.inventory_unit[0].value
		})
			.then((r) => {
				$("#categories_chart1").html("Total National Emission of all Gases")
				let results = r.message || [];
				const custom_options = {
					type: "bar",	
					colors: ["#568f8b"],
					height: 220,
					axisOptions: {
						xIsSeries: 0,
						isNavigable :1 ,
						shortenYAxisNumbers: 0,
						xAxisMode: "tick",
						numberFormatter: frappe.utils.format_chart_axis_number,
					},
					data: {
						datasets: [{values: results.data[0]}],
						labels: results.labels
					}
				};
				frappe.utils.make_chart(".totalghg_inventory_report-graph", custom_options);
			});
			
	}
	get_chart_report2() {
		frappe.call('mrvtools.ghg_inventory.page.ghg_inventory_report.ghg_inventory_report.get_pie_chart',{
			inventory_year:this.inventory_year[0].value,
			inventory_unit:this.inventory_unit[0].value
		})
			.then((r) => {
				$("#categories_chart2").html("Total National Emission of all Gases - Sector Wise")
				let results = r.message || [];
				const custom_options = {
					type: "pie",	
					colors: ["#b9d5b2", "#84b29e", "#568f8b", "#326b77", "#1b485e", "#122740"],
					height: 300,
					axisOptions: {
						xIsSeries: 0,
						isNavigable :1 ,
						shortenYAxisNumbers: 1,
						xAxisMode: "tick",
						numberFormatter: frappe.utils.format_chart_axis_number,
						maxSlices: 6
					},
					data: {
						datasets: [{values: results.data}],
						labels: results.labels
					}
				};
				frappe.utils.make_chart(".totalghg_inventory_report-graph2", custom_options);
			});
			
	}
	render_datatable(){
		frappe.call('mrvtools.ghg_inventory.page.ghg_inventory_report.ghg_inventory_report.execute',{
			inventory_year:this.inventory_year[0].value,
			inventory_unit:this.inventory_unit[0].value
		})
			.then((r) => {
				$('.report-wrapper:first').remove();
				this.$report = $('<div class="report-wrapper">').appendTo(this.page.main);
				let columns = r.message[0]
				let data = r.message[1]
				$('.headline:first').remove();
				if(this.inventory_year[0].value){
					this.$heading = $('<b class="report-heading" style="margin-left: 30px;">GHG Inventory Report - Gas wise</b>').insertBefore(this.$report);
				}
				this.datatable = new DataTable(this.$report[0], {columns:columns,data:data,treeView:true,inlineFilters: true});
				if(this.inventory_year[0].value ==''){
					$('.report-wrapper').attr('style',"display:none !important;border:none !important")
				}
			})
			
	}

	ghg_year_filter() {
		this.inventory_year = this.page.add_select(
			__("Year"),[" ","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025","2026","2027","2028","2029","2030","2031","2032","2033","2034","2035","2036","2037","2038","2039","2040","2041","2042","2043","2044","2045","2046","2047","2048","2049","2050"]
			
		)
		
		this.inventory_year.on("change",(r) => {
			$('[class="report-heading"]:first').remove()
			this.render_datatable()
			this.make()
			this.get_chart_report();
			this.get_chart_report2();
			this.$heading.empty();
			if(this.inventory_year[0].value ==''){
				$('.report-heading').attr('style',"display:none !important")
				$('.all_html').attr('style',"display:none !important")
			}
			else{
				$('.report-heading').attr('style',"display:block !important;margin-left: 30px")
				$('.all_html').attr('style',"display:block !important")
			}
		})
		
	}
	ghg_unit_filter() {
		this.inventory_unit = this.page.add_select(
			__("Unit"),["tCO2e","GgCO2e"]
			
		)
		this.inventory_unit.on("change",(r) => {
			$('[class="report-heading"]:first').remove()
			this.render_datatable()
			this.get_chart_report();
			this.get_chart_report2();
			this.$heading.empty();
		})
	}


	


}
