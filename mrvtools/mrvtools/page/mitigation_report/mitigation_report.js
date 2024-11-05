frappe.pages['mitigation-report'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Mitigation Report',
		single_column: true
	});
}

frappe.pages["mitigation-report"].on_page_load = (wrapper) => {
	frappe.mitigation_report = new Mitigation(wrapper);
};
class Mitigation {
	constructor(parent) {
		frappe.ui.make_app_page({
			parent: parent,
			title: __("Mitigation Tracking Report"),
			single_column: false,
			card_layout: true,
		});


		this.parent = parent;
		this.page = this.parent.page;
		this.page.sidebar.html(
			`<ul class="standard-sidebar mitigation_report-sidebar overlay-sidebar"></ul>`
		);
		this.$sidebar_list = this.page.sidebar.find("ul");	
		this.datatable=null;
		this.set_default_secondary_action();
		this.mitigation_filter_fields()
		this.render_datatable()
		this.make();
	}

	set_default_secondary_action() {
		this.refresh_button && this.refresh_button.remove();
		this.refresh_button = this.page.add_action_icon("refresh", () => {
			this.$container1.empty()
			this.$heading.empty()
			this.$report.empty()
			$('[class = "mitigation_report page-main-content"]').slice(0, 2).remove()
			this.render_datatable()
			this.make()
		});

		this.download_button = this.page.set_secondary_action('Download', () => {

			frappe.call('mrvtools.mrvtools.page.mitigation_report.mitigation_report.execute',{
				monitoring_year:this.monitoring_year[0].value,
				key_sector:this.key_sector,
				key_sub_sector:this.key_sub_sector,
				location:this.location[0].value,
				ndc:this.ndc[0].value,
				market_mechanism:this.market_mechanism[0].value
			})
				.then((r) => {
					frappe.call('mrvtools.mrvtools.page.mitigation_report.mitigation_report.download_excel',{
						columns:r.message[0],
						data:r.message[1]
					}).then((i) =>{
						window.open(i.message)
					})
				})
		})
	}
	mitigation_filter_fields() {
		this.monitoring_year = this.page.add_select(
			__("Monitoring Year"),[" ","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025","2026","2027","2028","2029","2030","2031","2032","2033","2034","2035","2036","2037","2038","2039","2040","2041","2042","2043","2044","2045","2046","2047","2048","2049","2050"]
			
		)
		this.monitoring_year.on("change",(r) => {
			this.render_datatable()
			this.get_total_mitigation_report1();
			this.get_total_mitigation_report2();
			this.$heading.empty()

		})
		let year_field = $(this.parent).find(
			`.frappe-control[data-original-title="${__("Monitoring Year")}"]`
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
							"key_sector": ["in", [`${frappe.mitigation_report.key_sector}`]]
						}
						
					}
				},
				change:()=>{
					this.key_sub_sector = key_sub_sector.get_value()
					if (this.key_sub_sector) {
						this.render_datatable()
						this.get_total_mitigation_report1();
						this.get_total_mitigation_report2();
						
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
				get_query: function () {
					return {
						"filters": {
							"objective": "Mitigation"
						}
						
					}
				},
				change:() =>{
					this.key_sector = key_sector.get_value()
					if (this.key_sector){
						$('[data-fieldname="key_sub_sector"]').prop("value",null)
						this.key_sub_sector_field.show()
						this.render_datatable()
						this.get_total_mitigation_report1();
						this.get_total_mitigation_report2();
						
					}
					else{
						this.key_sub_sector_field.hide()
						this.key_sub_sector = key_sub_sector.get_value()
						$('[data-fieldname="key_sub_sector"]').prop("value",null)
						this.render_datatable()
						this.get_total_mitigation_report1();
						this.get_total_mitigation_report2();
					}
					
				}
			},
			
			parent: $(this.parent).find(".from-key-sector-field"),
			render_input: 1,
		});
		$('[class="from-key-sector-field"]').find('.clearfix').remove()
		key_sector.refresh();

	this.location = this.page.add_select(
		__("Location"),[" ","National Level","Province Level","City Level","Municipality","Others"]
		
	)
	this.location.on("change",(r) => {
		this.render_datatable()
		this.get_total_mitigation_report1();
		this.get_total_mitigation_report2();
	})
	this.ndc = this.page.add_select(
		__("NDC"),[" ","Yes","No"]
	)
	this.ndc.on("change",(r) => {
		this.render_datatable()
		this.get_total_mitigation_report1();
		this.get_total_mitigation_report2();
	})
	this.market_mechanism = this.page.add_select(
		__("Market Mechanism"),[" ","Yes","No","Not Applicable"]
	)
	this.market_mechanism.on("change",(r) => {
		this.render_datatable()
		this.get_total_mitigation_report1();
		this.get_total_mitigation_report2();
	})
	}
	// hide_btn() {
		// const toggleButtons = (hideBtn, showBtn, targetClass) => {
		//   $(hideBtn).click(() => {
		// 	$('[class="'+targetClass+'"]').toggle();
		// 	$(hideBtn).toggle();
		// 	$(showBtn).toggle();
		//   });
	  
		//   $(showBtn).click(() => {
		// 	$('[class="'+targetClass+'"]').toggle();
		// 	$(hideBtn).toggle();
		// 	$(showBtn).toggle();
		//   });
		  
		//   $(showBtn).toggle();
		// };
	  
		// $(document).ready(() => {
		//   toggleButtons("#hide_btn", "#show_btn", "totalmitigation_report-graph");
		//   toggleButtons("#hide_btn2", "#show_btn2", "totalmitigation_report-chart");

		// });
	//   }

	make() {
		this.$container1 = $(`
		<div class="mitigation_report page-main-content">
			<div class="chart_hide" style="margin: 14px; display: flex; align-items: center; justify-content: space-between;">
				<b id="categories_chart"></b>
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
			<div id="chart-1" class="totalmitigation_report-graph"></div>
			<div class="chart_hide" style="margin: 14px; display: flex; align-items: center; justify-content: space-between;">
				<b id="sector_chart"></b>
				<button id="hide_btn2" class="btn btn-sm" onclick="toggle_chart2()">Hide chart</button>
			</div>
			<div id="chart-2" class="totalmitigation_report-chart"></div>
		</div>`
		).appendTo(this.page.main);
		this.$graph_area = this.$container1.find(".totalmitigation_report-graph");
		
		
		// this.hide_btn()
		this.get_total_mitigation_report1();
		this.get_total_mitigation_report2();

	}
	// toggle_chart() {
	// 	var x = document.getElementById("dummy");
	// 	if (x[0].style.display === "none") {
	// 	  x.style.display = "block";
	// 	} else {
	// 	  x.style.display = "none";
	// 	}
	//   }
	
	get_total_mitigation_report1() {
		frappe.call('mrvtools.mrvtools.page.mitigation_report.mitigation_report.getData',{
			monitoring_year:this.monitoring_year[0].value,
			key_sector:this.key_sector,
			key_sub_sector:this.key_sub_sector,
			location:this.location[0].value,
			ndc:this.ndc[0].value,
			market_mechanism:this.market_mechanism[0].value
		})
			.then((r) => {
				$("#categories_chart").html("No of Projects based on Categories")
				
				let results = r.message[1] || [];
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
						datasets: results.datasets,
						labels: results.labels
					},
					
				};
				frappe.utils.make_chart(".totalmitigation_report-graph", custom_options);
			});
			
	}

	get_total_mitigation_report2() {
		frappe.call('mrvtools.mrvtools.page.mitigation_report.mitigation_report.get_pie_chart',{
			monitoring_year:this.monitoring_year[0].value,
			ndc:this.ndc[0].value
		})
			.then((r) => {
				$("#sector_chart").html("GHG emissions reductions actual sector wise")
				let results = r.message || [];
				const custom_options = {
					type: "pie",	
					
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
				frappe.utils.make_chart(".totalmitigation_report-chart", custom_options);
			});
			
	}

	render_datatable(){
		frappe.call('mrvtools.mrvtools.page.mitigation_report.mitigation_report.execute',{
			monitoring_year:this.monitoring_year[0].value,
			key_sector:this.key_sector,
			key_sub_sector:this.key_sub_sector,
			location:this.location[0].value,
			ndc:this.ndc[0].value,
			market_mechanism:this.market_mechanism[0].value
		})
			.then((r) => {
				$('.report-wrapper:first').remove();
				this.$report = $('<div class="report-wrapper">').appendTo(this.page.main);
				let columns = r.message[0]
				let data = r.message[1]
				$('.headline:first').remove();
				this.$heading = $('<b class="headline" style="margin-left: 30px;">Mitigation Report</b>').insertBefore(this.$report);
				this.datatable = new DataTable(this.$report[0], {
																	columns:columns,
																	data:data,
																	showTotalRow:1,
																	inlineFilters: true,
																}
											);
			})
			
	}


}
