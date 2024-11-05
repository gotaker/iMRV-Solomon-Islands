frappe.pages["ndc-report"].on_page_load = (wrapper) => {
	frappe.ndc_report = new NdcReport(wrapper);
};
class NdcReport {
	constructor(parent) {
		frappe.ui.make_app_page({
			parent: parent,
			title: __("NDC Tracking Report"),
			single_column: false,
			card_layout: true,
		});


		this.parent = parent;
		this.page = this.parent.page;
		this.page.sidebar.html(
			`<ul class="standard-sidebar ndc_report-sidebar overlay-sidebar"></ul>`
		);
		this.$sidebar_list = this.page.sidebar.find("ul");	
		this.datatable=null;
		this.set_default_secondary_action();
		this.ndc_filter_fields();
		
		
	}

	set_default_secondary_action() {
		this.refresh_button && this.refresh_button.remove();
		this.refresh_button = this.page.add_action_icon("refresh", () => {
			this.$container1.empty()
			this.$report.empty()
			$('[class = "ndc_report page-main-content"]').slice(0, 2).remove()
			this.render_datatable()
			this.$heading.empty()
			this.make()
		});
		this.download_button = this.page.set_secondary_action('Download', () => {

			frappe.call('mrvtools.mrvtools.page.ndc_report.ndc_report.execute',{
				year:this.monitoring_year[0].value
			})
				.then((r) => {
					frappe.call('mrvtools.mrvtools.page.ndc_report.ndc_report.download_excel',{
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
	// 	  toggleButtons("#hide_btn", "#show_btn", "totalndc_report-graph");
	// 	  toggleButtons("#hide_btn2", "#show_btn2", "totalndc_report-chart");

	// 	});
	//   }

	make() {
		this.$container1 = $(`
		<div class="ndc_report page-main-content">
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
			<div id="chart-1" class="totalndc_report-graph"></div>
		<div class="chart_hide" style="margin: 14px; display: flex; align-items: center; justify-content: space-between;">
			<b id="sector_chart"></b>
			<button id="hide_btn2" onclick="toggle_chart2()" class="btn btn-sm">Hide chart</button>
		</div>
			<div id="chart-2" class="totalndc_report-chart"></div>
		</div>`
		).appendTo(this.page.main);
		this.$graph_area = this.$container1.find(".totalndc_report-graph");
		
		

		this.get_total_ndc_report1();
		this.get_total_ndc_report2();

	}

	ndc_filter_fields() {
		this.monitoring_year = this.page.add_select(
			__("Monitoring Year"),[" ","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025","2026","2027","2028","2029","2030","2031","2032","2033","2034","2035","2036","2037","2038","2039","2040","2041","2042","2043","2044","2045","2046","2047","2048","2049","2050"]
			
		)
		this.monitoring_year.on("change",(r) => {
			$('.report-wrapper:first').remove();
			this.render_datatable()
			$('.layout-main-section .report-wrapper').css("border", "1px solid #dbdbdb;")
			$('[class = "ndc_report page-main-content"]').slice(0, 2).remove()
			this.make();
			this.$heading.empty()
			
		})
		
	}
	


	get_total_ndc_report1() {
		frappe.call('mrvtools.mrvtools.page.ndc_report.ndc_report.get_chart',{
			year:this.monitoring_year[0].value
		})
			.then((r) => {
				if (this.monitoring_year[0].value != ''){

					$("#categories_chart").html("No of Projects based on Categories")
				}
				else{
					
					$(".chart_hide").html("")
				}
				
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
				frappe.utils.make_chart(".totalndc_report-graph", custom_options);
			});
			
	}

	get_total_ndc_report2() {
		frappe.call('mrvtools.mrvtools.page.ndc_report.ndc_report.get_pie_chart',{
			year:this.monitoring_year[0].value,
			
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
				frappe.utils.make_chart(".totalndc_report-chart", custom_options);
			});
			
	}

	render_datatable(){
		frappe.call('mrvtools.mrvtools.page.ndc_report.ndc_report.execute',{
			year:this.monitoring_year[0].value
		})
			.then((r) => {
				$('.report-wrapper:first').remove();
				this.$report = $('<div class="report-wrapper">').appendTo(this.page.main);
				let columns = r.message[0]
				let data = r.message[1]
				$('.headline:first').remove();
				if(this.monitoring_year[0].value){
					this.$heading = $('<b class="headline" style="margin-left: 30px;">NDC Report</b>').insertBefore(this.$report);
				}
				this.datatable = new DataTable(this.$report[0], {columns:columns,data:data,showTotalRow:1,inlineFilters: true});
			})
	}

}
