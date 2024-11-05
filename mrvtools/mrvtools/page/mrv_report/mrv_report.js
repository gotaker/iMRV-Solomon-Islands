frappe.pages['mrv-report'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'MRV Report',
		single_column: true
	});
}

frappe.pages["mrv-report"].on_page_load = (wrapper) => {
	frappe.mrv_report = new MRVReport(wrapper);
};

class MRVReport {
	constructor(parent) {
		frappe.ui.make_app_page({
			parent: parent,
			title: __("MRV Report"),
			single_column: false,
			card_layout: true,
		});

		this.parent = parent;
		this.page = this.parent.page;
		this.page.sidebar.html(
			`<ul class="standard-sidebar mrv_report-sidebar overlay-sidebar"></ul>`
		);
		this.$sidebar_list = this.page.sidebar.find("ul");

		this.datatable=null;
		this.make()
		
		this.set_default_secondary_action();
		this.mrv_filter_fields()
		this.render_datatable()
		// this.create_date_range_field();
	}
	set_default_secondary_action() {
		this.refresh_button && this.refresh_button.remove();
		this.refresh_button = this.page.add_action_icon("refresh", () => {
			this.$container.empty()
			// this.$container2.empty()
			this.make()
			this.render_datatable();
		});
		this.download_button = this.page.set_secondary_action('Download', () => {

			frappe.call('mrvtools.mrvtools.page.mrv_report.mrv_report.download_excel',{
				project:this.project
			}).then((i) =>{
				window.open(i.message)
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
	// 		toggleButtons("#hide_btn", "#show_btn", "totalmrv_report-graph");
	// 		toggleButtons("#hide_btn2", "#show_btn2", "totalmrv_report2-graph");
	// 	});
	//   }

	wrapper1(){
		$("#mrv_chart").html(`
		<div class="mrv_report page-main-content">
			<div class="chart_hide1" style="margin: 14px; display: flex; align-items: center; justify-content: space-between;">
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
			<div id="chart-1" class="totalmrv_report-graph"></div>
			
		</div>`)
		$("#mrv_chart2").html(`
		<div class="mrv_report page-main-content">
		<div class="chart_hide2" style="margin: 14px; display: flex; align-items: center; justify-content: space-between;">
			<b id="categories_chart1"></b>
			<button id="hide_btn2" onclick="toggle_chart2()" class="btn btn-sm">Hide chart</button>
		</div>
		<div id="chart-2" class="totalmrv_report2-graph"></div>
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
		</div>`)
	}
	make() {
		$('.all_html').remove();
		if (this.project){
			this.$container = $(`
			<div class = "all_html" style="margin:0;">
				<b class="headline1">Project Details</b>
				<div class="report-wrapper1"></div>
				<div id="mrv_chart"></div>
				<b class="headline2">Mitigation Summary</b>
				<div class="report-wrapper2"></div>
				<b class="headline3">Adaptation Summary</b>
				<div class="report-wrapper3"></div>
				<div id="mrv_chart2"></div>
				<b class="headline5">Finance Summary</b>
				<div class="report-wrapper5"></div>
				<b class="headline4">SDG Summary</b>
				<div class="report-wrapper4"></div>
			</div>
			`).appendTo(this.page.main);
			this.$graph_area = this.$container.find(".totalmrv_report-graph");
		}
		


		// this.$container2 = $(`
		// <body class = "all_html"  style="margin:0;">
		// 	<div id="mrv_chart2"></div>
		// </body>
		// `).appendTo(this.page.main).insertAfter($('#mrv_chart'));
		// this.$graph_area = this.$container2.find(".totalmrv_report2-graph");

		// this.hide_btn()
		this.wrapper1();
	
	}
	mrv_filter_fields() {
		this.report_select = this.page.add_select(
			__("Report"),["","Project Details","Mitigation Summary","Adaptation Summary","Finance Summary","SDG Summary"]
			
		)
		
		let report_field = $(this.parent).find(
			`.frappe-control[data-original-title="${__("Report")}"]`
		);
		$('.frappe-control[data-original-title="Report"]').css("display","none")

		this.project_field = $(`<div class="from-project-field"></div>`)
			.insertBefore(report_field);
		let project = frappe.ui.form.make_control({
			df: {
				"fieldtype": "Link",
				"fieldname": "project",	
				"placeholder": __("Project ID"),
				"options": "Project",
				"input_class": "input-xs", 
				change:()=>{
					this.project = project.get_value()
					if (this.project) {
						this.make()
						this.render_datatable()
						$('[class="page-form row"]').attr("style","height:50px !important;")
					}
					if (this.project == ''){
						this.make()
						this.get_total_mrv_report()
						this.get_total_mrv_report2()
						this.render_datatable()
						$('[class="page-form row"]').attr("style","height:350px !important;")
					}
				},
			},
			
			parent: $(this.parent).find(".from-project-field"),
			render_input: 1,
		});
		$('[class="from-project-field"]').find('.clearfix').remove()
		$('[class="page-form row"]').attr("style","height:350px !important;")
		project.refresh(); 
	}
	
	get_total_mrv_report() {
		frappe.call('mrvtools.mrvtools.page.mrv_report.mrv_report.get_chart',{
			project : this.project
		})
			.then((r) => {
				$("#categories_chart").html(" GHG Emissions redcutions actual year wise")
				let results = r.message || [];
				const custom_options = {
					type: "bar",
					colors: ["#48bb74"],
					height: 240,
					width:20,
					axisOptions: {
						xIsSeries: 0,
						isNavigable :1 ,
						shortenYAxisNumbers: 0,
						xAxisMode: "tick",
						numberFormatter: frappe.utils.format_chart_axis_number,
					},
					data: {
						datasets: [{values: results.data}],
						labels: results.labels
					}
				};
				frappe.utils.make_chart(".totalmrv_report-graph", custom_options);
			});
			
	}
	get_total_mrv_report2() {
		frappe.call('mrvtools.mrvtools.page.mrv_report.mrv_report.get_chart2',{
			project : this.project
		})
			.then((r) => {
				$("#categories_chart1").html("Finance disbursement actual year wise")
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
						labels: results.labels
					}
				};
				frappe.utils.make_chart(".totalmrv_report2-graph", custom_options);
			});
			
	}


	
	render_datatable(){
		frappe.call('mrvtools.mrvtools.page.mrv_report.mrv_report.get_project_details',{
			project : this.project
		})
		.then((r) => {
			// $('.report-wrapper1:first').remove();
			
			// this.$report1 = $('<div class="report-wrapper1">').appendTo(this.page.main).insertAfter($('#mrv_chart2'));
			
			let columns = r.message[0]
			let data = r.message[1]
			// $('.headline1:last').remove();
			// if(this.project){
			// 	this.$heading = $('<b class="headline">Project Details</b>').insertBefore('.report-wrapper1');
			// }

			this.datatable = new DataTable(".report-wrapper1", {columns:columns,data:data});
		})
			
		frappe.call('mrvtools.mrvtools.page.mrv_report.mrv_report.get_mitigation_details',{
			project : this.project
		})
			.then((r) => {
				// $('.report-wrapper2:first').remove();
				// this.$report2 = $('<div class="report-wrapper2">').appendTo(this.page.main).insertAfter($('.report-wrapper1'));
				let columns = r.message[0]
				let data = r.message[1]
				if (data[0][2] == null){
					$('.chart_hide1').attr('style','display:none !important')
				}
				else{
					this.get_total_mrv_report()
					$('.chart_hide1').attr('style','margin: 14px; display: flex; align-items: center; justify-content: space-between;')
				}
				// $('.headline2:last').remove();
				// if(this.project){
				// 	this.$heading = $('<b class="headline">Mitigation Summary</b>').insertBefore(this.$report2);
				// }
				this.datatable = new DataTable(".report-wrapper2", {columns:columns,data:data});
			})
			
		frappe.call('mrvtools.mrvtools.page.mrv_report.mrv_report.get_adaptation_details',{
			project : this.project
		})
			.then((r) => {
				// $('.report-wrapper3:first').remove();
				
				// this.$report3 = $('<div class="report-wrapper3">').appendTo(this.page.main).insertAfter($('.report-wrapper2'));
				let columns = r.message[0]
				let data = r.message[1]
				// $('.headline3:last').remove();
				// if(this.project){
				// 	this.$heading = $('<b class="headline">Adaptation Summary</b>').insertBefore(this.$report3);
				// }

				this.datatable = new DataTable(".report-wrapper3", {columns:columns,data:data,inlineFilters: true});
			})


			frappe.call('mrvtools.mrvtools.page.mrv_report.mrv_report.get_sdg_details',{
				project : this.project
			})
				.then((r) => {
					// $('.report-wrapper4:first').remove();
					
					// this.$report4 = $('<div class="report-wrapper4">').appendTo(this.page.main).insertAfter($('.report-wrapper3'));
					let columns = r.message[0]
					let data = r.message[1]
					// $('.headline4:last').remove();
					// if(this.project){
					// 	this.$heading = $('<b class="headline">SDG Summary</b>').insertBefore(this.$report4);
					// }
					this.datatable = new DataTable(".report-wrapper4", {columns:columns,data:data,inlineFilters: true});
				})

		frappe.call('mrvtools.mrvtools.page.mrv_report.mrv_report.get_finance_details',{
			project : this.project
		})
			.then((r) => {
				// $('.report-wrapper5:first').remove();
				// this.$report5 = $('<div class="report-wrapper5">').appendTo(this.page.main).insertAfter($('.report-wrapper4'));
				let columns = r.message[0]
				let data = r.message[1]
				if (data.length == 0){
					$('.chart_hide2').attr('style','display:none !important')
				}
				else{
					this.get_total_mrv_report2()
					$('.chart_hide2').attr('style','margin: 14px; display: flex; align-items: center; justify-content: space-between;')
				}
				// $('.headline5:last').remove();
				// if(this.project){
				// 	this.$heading = $('<b class="headline">Finance Summary</b>').insertBefore(this.$report5);
				// }

				this.datatable = new DataTable(".report-wrapper5", {columns:columns,data:data});
			})
				
			
		
			
		
	}


}
