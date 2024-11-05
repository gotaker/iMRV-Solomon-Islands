frappe.pages["finance-report"].on_page_load = (wrapper) => {
	frappe.finance_report = new Finance(wrapper);
};

class Finance {
	constructor(parent) {
		frappe.ui.make_app_page({
			parent: parent,
			title: __("Finance Tracking Report"),
			single_column: false,
			card_layout: true,
		});

		this.parent = parent;
		this.page = this.parent.page;
		this.page.sidebar.html(
			`<ul class="standard-sidebar finance_report-sidebar overlay-sidebar"></ul>`
		);
		this.$sidebar_list = this.page.sidebar.find("ul");
		// alert(frappe.defaults.get_user_default("Order"))
		this.datatable=null;
		// this.add_card_button_to_toolbar();
		this.set_default_secondary_action();
		this.finance_filter_fields()
		this.render_datatable()
		this.make()
		// this.create_date_range_field();
	}
	set_default_secondary_action() {
		this.refresh_button && this.refresh_button.remove();
		this.refresh_button = this.page.add_action_icon("refresh", () => {
			this.$container.empty()
			this.$container2.empty()
			this.$report.empty()
			this.$heading.empty()
			$('[class = "finance_report page-main-content"]').slice(0, 2).remove()
			this.make()
			this.render_datatable()
		});
		this.download_button = this.page.set_secondary_action('Download', () => {

			frappe.call('mrvtools.mrvtools.page.finance_report.finance_report.execute',{
				year:this.monitoring_year[0].value,
				objective:this.objective[0].value,
				key_sector:this.key_sector,
				key_sub_sector:this.key_sub_sector
			})
				.then((r) => {
					frappe.call('mrvtools.mrvtools.page.finance_report.finance_report.download_excel',{
						columns:r.message[0],
						data:r.message[1]
					}).then((i) =>{
						
						window.open(i.message)
					})
				})
		})
	}
	hide_btn() {
		const toggleButtons = (hideBtn, showBtn, targetClass) => {
		  $(hideBtn).click(() => {
			$('[class="'+targetClass+'"]').toggle();
			$(hideBtn).toggle();
			$(showBtn).toggle();
		  });
	  
		  $(showBtn).click(() => {
			$('[class="'+targetClass+'"]').toggle();
			$(hideBtn).toggle();
			$(showBtn).toggle();
		  });
		  
		  $(showBtn).toggle();
		};
	  
		$(document).ready(() => {
		  toggleButtons("#hide_btn", "#show_btn", "totalfinance_report-graph");
		  toggleButtons("#hide_btn2", "#show_btn2", "totalfinance_report-chart");

		});
	  }
	make() {
		this.$container = $(`
		<div class="finance_report page-main-content">
		<div class="chart_hide" style="margin: 14px; display: flex; align-items: center; justify-content: space-between;">
			<b id="categories_chart"></b>
			<button id="hide_btn" class="btn btn-sm">Hide chart</button>
			<button id="show_btn" class="btn btn-sm">show chart</button>
		</div>
			<div class="totalfinance_report-graph"></div>
		</div>`
		).appendTo(this.page.main);
		this.$graph_area = this.$container.find(".totalfinance_report-graph");
		
		this.$container2 = $(`
		<div class="finance_report page-main-content">
		<div class="chart_hide" style="margin: 14px; display: flex; align-items: center; justify-content: space-between;">
			<b id="sector_chart"></b>
			<button id="hide_btn2" class="btn btn-sm">Hide chart</button>
			<button id="show_btn2" class="btn btn-sm">show chart</button>
		</div>
			<div class="totalfinance_report-chart"></div>
		</div>`
		).appendTo(this.page.main);
		this.$graph_area = this.$container2.find(".totalfinance_report-chart");
		this.hide_btn();
		this.get_total_finance_report();
		this.get_total_finance_report2();
		

	}

	finance_filter_fields() {
		this.monitoring_year = this.page.add_select(
			__("Year"),[" ","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025","2026","2027","2028","2029","2030","2031","2032","2033","2034","2035","2036","2037","2038","2039","2040","2041","2042","2043","2044","2045","2046","2047","2048","2049","2050"]
			
		)
		this.monitoring_year.on("change",(r) => {
			this.render_datatable()
			this.get_total_finance_report();
			this.get_total_finance_report2()
			this.$heading.empty()
		
		})

		this.objective = this.page.add_select(
			__("Objective"),['', 'Mitigation', 'Adaptation', 'Cross-Cutting', 'Transparency', 'Enablers']
			
		)
		this.objective.on("change",(r) => {
			this.render_datatable()
			this.get_total_finance_report();
			this.get_total_finance_report2()
		})
		let objective_field = $(this.parent).find(
			`.frappe-control[data-original-title="${__("Objective")}"]`
		);

		this.key_sub_sector_field = $(`<div class="from-key-sub-sector-field"></div>`)
			.insertAfter(objective_field);
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
							"key_sector": ["in", [`${frappe.finance_report.key_sector}`]]
						}
						
					}
				},
				change:()=>{
					this.key_sub_sector = key_sub_sector.get_value()
					if (this.key_sub_sector) {
						this.render_datatable()
						this.get_total_finance_report();
						this.get_total_finance_report2()
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
			.insertAfter(objective_field);
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
						this.get_total_finance_report();
						this.get_total_finance_report2()
						
					}
					else{
						this.key_sub_sector_field.hide()
						this.key_sub_sector = key_sub_sector.get_value()
						$('[data-fieldname="key_sub_sector"]').prop("value",null)
						this.render_datatable()
						this.get_total_finance_report();
						this.get_total_finance_report2()
					}
					
				},
				get_query: function () {
					return {
						"filters": {
							"Objective": ["in", [`${frappe.finance_report.objective[0].value}`]]
						}
					}
				}
			},
			
			parent: $(this.parent).find(".from-key-sector-field"),
			render_input: 1,
		});
		$('[class="from-key-sector-field"]').find('.clearfix').remove()
		key_sector.refresh();
	}
	
	get_total_finance_report() {
		frappe.call('mrvtools.mrvtools.page.finance_report.finance_report.get_chart',{
			year:this.monitoring_year[0].value
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
						datasets: results.datasets,
						labels: results.labels
					},
				};
				frappe.utils.make_chart(".totalfinance_report-graph", custom_options);
			});
			
	}
	get_total_finance_report2() {
		frappe.call('mrvtools.mrvtools.page.finance_report.finance_report.get_pie_chart',{
			year:this.monitoring_year[0].value
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
				frappe.utils.make_chart(".totalfinance_report-chart", custom_options);
			});
			
	}

	
	render_datatable(){
		frappe.call('mrvtools.mrvtools.page.finance_report.finance_report.execute',{
			year:this.monitoring_year[0].value,
			objective:this.objective[0].value,
			key_sector:this.key_sector,
			key_sub_sector:this.key_sub_sector
		})
			.then((r) => {
				$('.report-wrapper:first').remove();
				this.$report = $('<div class="report-wrapper">').appendTo(this.page.main);
				let columns = r.message[0]
				let data = r.message[1]
				// his.$heading.empty()
				$('.headline:first').remove();
				this.$heading = $('<b class="headline" style="margin-left: 30px;">Finance Report</b>').insertBefore(this.$report);

				this.datatable = new DataTable(this.$report[0], {columns:columns,data:data,showTotalRow:1,inlineFilters: true});
			})
			
	}


}
