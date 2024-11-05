frappe.pages["adaptation-report"].on_page_load = (wrapper) => {
	frappe.adaptation_report = new Adaptation(wrapper);
};
class Adaptation {
	constructor(parent) {
		frappe.ui.make_app_page({
			parent: parent,
			title: __("Adaptation Tracking Report"),
			single_column: false,
			card_layout: true,
		});


		this.parent = parent;
		this.page = this.parent.page;
		this.page.sidebar.html(
			`<ul class="standard-sidebar adaptation_report-sidebar overlay-sidebar"></ul>`
		);
		this.$sidebar_list = this.page.sidebar.find("ul");	
		this.datatable=null;
		this.set_default_secondary_action();
		this.adaptation_filter_fields()
		this.render_datatable()
		this.make();
	}
	adaptation_filter_fields() {
		this.year_select = this.page.add_select(
			__("Year"),[" ","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025","2026","2027","2028","2029","2030","2031","2032","2033","2034","2035","2036","2037","2038","2039","2040","2041","2042","2043","2044","2045","2046","2047","2048","2049","2050"]
			
		)
		this.year_select.on("change",(r) => {
			this.render_datatable()
			this.get_total_adaptation_report1();
			this.get_total_adaptation_report2();
		})
		let year_field = $(this.parent).find(
			`.frappe-control[data-original-title="${__("Year")}"]`
		);

		this.key_sub_sector_field = $(`<div class="from-key-sub-sector-field"></div>`)
			.insertAfter(year_field);
		let key_sub_sector = frappe.ui.form.make_control({
			df: {
				"fieldtype": "Link",
				"fieldname": "key_sub_sector",
				"placeholder": __("Key Sub Sector"),
				"options": "Project Key Sub Sector",
				"input_class": "input-xs",
				get_query: function () {
					return {
						"filters": {
							"key_sector": ["in", [`${frappe.adaptation_report.key_sector}`]]
						}
						
					}
				},
				change:()=>{
					this.key_sub_sector = key_sub_sector.get_value()
					if (this.key_sub_sector) {
						this.render_datatable()
						this.get_total_adaptation_report1();
						this.get_total_adaptation_report2();
						
					}
				}
			},
			
			parent: $(this.parent).find(".from-key-sub-sector-field"),
			render_input: 1,
		});
		$('[class="from-key-sub-sector-field"]').find('.clearfix').remove()
		key_sub_sector.refresh(); 
		this.key_sub_sector_field.hide()


		this.key_sector_field = $(`<div class="from-key-sector-field"></div>`)
			.insertAfter(year_field);
		let key_sector = frappe.ui.form.make_control({
			df: {
				"fieldtype": "Link",
				"fieldname": "key_sector",
				"placeholder": __("Key Sector"),
				"options": "Project Key Sector",
				"input_class": "input-xs",
				change:() =>{
					this.key_sector = key_sector.get_value()
					if (this.key_sector){
						$('[data-fieldname="key_sub_sector"]').prop("value",null)
						this.key_sub_sector_field.show()
						this.render_datatable()
						this.get_total_adaptation_report1();
						this.get_total_adaptation_report2();
						
					}
					else{
						this.key_sub_sector_field.hide()
						this.key_sub_sector = key_sub_sector.get_value()
						$('[data-fieldname="key_sub_sector"]').prop("value",null)
						this.render_datatable()
						this.get_total_adaptation_report1();
						this.get_total_adaptation_report2();
					}
					
				}
			},
			
			parent: $(this.parent).find(".from-key-sector-field"),
			render_input: 1,
		});
		$('[class="from-key-sector-field"]').find('.clearfix').remove()
		key_sector.refresh();

		this.impact_area = this.page.add_select(
			__("Impact Area"),['','Forest Health', 'Watershed Health', 'Coastal Health', 'Water Security', 'Security of Place', 'Energy Security', 'Income Security', 'Community Health', 'Food Security']
			
		)
		this.impact_area.on("change",(r) => {
			this.render_datatable()
			this.get_total_adaptation_report1();
			this.get_total_adaptation_report2();
		})
	}
	

	set_default_secondary_action() {
		this.refresh_button && this.refresh_button.remove();
		this.refresh_button = this.page.add_action_icon("refresh", () => {
			this.$container1.empty()
			this.$heading.empty()
			this.$report.empty()
			$('[class = "adaptation_report page-main-content"]').slice(0, 2).remove()
			this.make()
			this.render_datatable()
		});
		this.download_button = this.page.set_secondary_action('Download', () => {

			frappe.call('mrvtools.mrvtools.page.adaptation_report.adaptation_report.execute',{
				year:this.year_select[0].value,
				key_sector:this.key_sector,
				key_sub_sector : this.key_sub_sector,
				impact_area : this.impact_area[0].value
			})
				.then((r) => {
					frappe.call('mrvtools.mrvtools.page.adaptation_report.adaptation_report.download_excel',{
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
	// 		$('[class="'+targetClass+'"]').toggle(); $(hideBtn).toggle(); $(showBtn).toggle();
	// 	  });
	  
	// 	  $(showBtn).click(() => {
	// 		$('[class="'+targetClass+'"]').toggle(); $(hideBtn).toggle(); $(showBtn).toggle();
	// 	  });
	// 	  $(showBtn).toggle();
	// 	};
	  
	// 	$(document).ready(() => {
	// 	  toggleButtons("#hide_btn", "#show_btn", "totaladaptation_report-graph");
	// 	  toggleButtons("#hide_btn2", "#show_btn2", "totaladaptation_report-chart");
	// 	});
	//   }
			
	make() {
		this.$container1 = $(`
		<div class="adaptation_report page-main-content">
		<div class="chart_hide" style="margin: 14px; display: flex; align-items: center; justify-content: space-between;">
			<b id="categories_chart"></b>
			<button id="hide_btn" onclick="toggle_chart1()" class="btn btn-sm">Hide chart</button>
		</div>
			<div id="chart-1" class="totaladaptation_report-graph"></div>
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
			<div class="chart_hide" style="margin: 14px; display: flex; align-items: center; justify-content: space-between;">
			<b id="sector_chart"></b>
			<button id="hide_btn2" onclick="toggle_chart2()" class="btn btn-sm">Hide chart</button>
		</div>
			<div id="chart-2" class="totaladaptation_report-chart"></div>
		</div>`
		).appendTo(this.page.main);

		// this.hide_btn();
		this.get_total_adaptation_report1();
		this.get_total_adaptation_report2();

	}
	
	get_total_adaptation_report1() {
		frappe.call('mrvtools.mrvtools.page.adaptation_report.adaptation_report.get_total_adaptation_report_data1',{
			year:this.year_select[0].value,
			key_sector:this.key_sector,
			key_sub_sector : this.key_sub_sector,
			impact_area : this.impact_area[0].value
		})
			.then((r) => {
				$("#categories_chart").html("No of Projects based on Categories")
				
				let results = r.message || [];
				const custom_options = {
					type: "bar",
					colors: ["#48bb74"],
					height: 240,
					axisOptions: {
						xIsSeries: 0,
						isNavigable :1 ,
						shortenYAxisNumbers: 0,
						xAxisMode: "tick",
						numberFormatter: frappe.utils.format_chart_axis_number,
					},
					data: {
						datasets: [{values: results.data}],
						labels: results.categories
					}
				};
				frappe.utils.make_chart(".totaladaptation_report-graph", custom_options);
			});
			
	}

	get_total_adaptation_report2() {
		frappe.call('mrvtools.mrvtools.page.adaptation_report.adaptation_report.get_total_adaptation_report_data2',{
			year:this.year_select[0].value,
			key_sector:this.key_sector,
			key_sub_sector : this.key_sub_sector,
			impact_area : this.impact_area[0].value
		})
			.then((r) => {
				$("#sector_chart").html("No of Projects based on Sector")
				
				let results = r.message || [];
				let keys = Object.keys(r.message);
				let values = Object.values(r.message);				
				const custom_options = {
					type: "bar",
					colors: ["#03a9f4"],
					height: 240,
					axisOptions: {
						xIsSeries: 0,
						isNavigable :1 ,
						shortenYAxisNumbers: 0,
						xAxisMode: "tick",
						numberFormatter: frappe.utils.format_chart_axis_number,
					},
					data: {
						datasets: [{values: values}],
						labels: keys
					}
				};
				frappe.utils.make_chart(".totaladaptation_report-chart", custom_options);
			});
			
	}

	render_datatable(){
		frappe.call('mrvtools.mrvtools.page.adaptation_report.adaptation_report.execute',{
			year:this.year_select[0].value,
			key_sector:this.key_sector,
			key_sub_sector : this.key_sub_sector,
			impact_area : this.impact_area[0].value
		})
		.then((r) => {

			$('.report-wrapper:first').remove();

			this.$report = $('<div class="report-wrapper">').appendTo(this.page.main);
			let columns = r.message[0];
			let data = r.message[1];
			$('.headline:first').remove();
			this.$heading = $('<b class="headline" style="margin-left: 30px;">Adaptation Report</b>').insertBefore(this.$report);
			this.datatable = new DataTable(this.$report[0], { columns: columns, data: data ,showTotalRow:1,inlineFilters: true});
		})
			
	}

}
