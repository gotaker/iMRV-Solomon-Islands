frappe.pages['main-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Main Dashboard',
		single_column: true
	});
}

frappe.pages["main-dashboard"].on_page_load = (wrapper) => {
	frappe.main_dashboard = new Dashboard(wrapper);
};

class Dashboard {
	constructor(parent) {
		frappe.ui.make_app_page({
			parent: parent,
			title: __("Dashboard"),
			single_column: false,
			card_layout: true,
		});

		this.parent = parent;
		this.page = this.parent.page;
		this.page.sidebar.html(
			`<ul class="standard-sidebar main_dashboard-sidebar overlay-sidebar"></ul>`
		);
		this.$sidebar_list = this.page.sidebar.find("ul");
		// alert(frappe.defaults.get_user_default("Order"))
		// this.datatable=null;
		// this.add_card_button_to_toolbar();
		this.make()
		// this.create_date_range_field();
		
		
	}

	make(){
		if(frappe.user_roles.includes("Dashboard Observer") && (!frappe.user_roles.includes("Administrator") || !frappe.user_roles.includes("System Manager"))){
			$('[class="page-content"]').append(`
				<style> 
					.search-bar,.dropdown-notifications,.vertical-bar {
						display: none !important;
					}
					.sidebar .sidebar-menu{
						background:#f9fafa !important;
						box-shadow: #f9fafa 0px 0px 0px 0px !important;
					}
					li.treeview.drop-down{
						display: none !important;
					}
				</style>
				`)
				$('.sidebar-menu li:not(:first)').remove();
		}
		this.$container = $(`
		<div class = "all_html"  style="margin:0;">
		<div class="main-container" style="width:100%"><div><h2 style = "margin:0px 0px 0px 20px">Dashboard</h2></div></div>
		
			<div class="inner-container">
				<div class="widget dashboard-widget-box" style="width:48%;float:left;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head">
						<div class="widget-label label-1">
							<div class="widget-title"><span class="ellipsis" id="project-count-title"></span></div>
						</div>
						<div class="widget-label label-2">
							<div class="widget-title"><div class="ellipsis" style="width: 100%;display: flex;" id="project-count-total"></div></div>
						</div>
					</div>
					<div id='project-count' class="widget-body"></div>
					<div class="chart-legend" id="chart-legend-1"></div>
				</div>

				<div class="widget dashboard-widget-box" style="width:48%;float:right;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head">
						<div class="widget-label label-1">
							<div class="widget-title"><span class="ellipsis" id="status-title"></span></div>
						</div>
						<div class="widget-label label-2">
							<div class="widget-title"><span class="ellipsis" style="width: 100%;display: flex;" id="status-total"></span></div>
						</div>
					</div>
					<div id='project_status' class="widget-body"></div>
					<div class="chart-legend" id="chart-legend-2"></div>
				</div>
				
			</div>


			<div class="inner-container">
				<div class="widget dashboard-widget-box" style="width:48%;float:left;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head">
						<div class="widget-label label-1">
							<div class="widget-title"><span class="ellipsis" id="mitigation-title"></span></div>
						</div>
						<div class="widget-label label-2">
							<div class="widget-title"><span class="ellipsis" style="width: 100%;display: flex;" id="mitigation-total"></span></div>
						</div>
					</div>
					<div id='mitigation-sector' class="widget-body"></div>
					<div class="chart-legend" id="chart-legend-3"></div>
				</div>

				<div class="widget dashboard-widget-box" style="width:48%;float:right;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head">
						<div class="widget-label label-1">
							<div class="widget-title"><span class="ellipsis" id="adaptation-title"></span></div>
						</div>
						<div class="widget-label label-2">
							<div class="widget-title"><span class="ellipsis" style="width: 100%;display: flex;" id="adaptation-total"></span></div>
						</div>
					</div>
					<div id='adaptation-sector' class="widget-body"></div>
					<div class="chart-legend" id="chart-legend-4"></div>
				</div>
			</div>


			<div class="inner-container">
				<div class="widget dashboard-widget-box" style="width:48%;float:left;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head">
						<div class="widget-label label-1">
							<div class="widget-title"><span class="ellipsis" id="project_support_status-title"></span></div>
						</div>
						<div class="widget-label label-2">
							<div class="widget-title"><span class="ellipsis" style="width: 100%;display: flex;" id="project_support_status-total"></span></div>
						</div>
					</div>
					<div id='project_support_status' class="widget-body"></div>
					<div class="chart-legend" id="chart-legend-8"></div>
				</div>

				<div class="widget dashboard-widget-box" style="width:48%;float:right;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head">
						<div class="widget-label label-1">
							<div class="widget-title"><span class="ellipsis" id="usd_support_status-title"></span></div>
						</div>
						<div class="widget-label label-2">
							<div class="widget-title"><span class="ellipsis" style="width: 100%;display: flex;" id="usd_support_status-total"></span></div>
						</div>
					</div>
					<div id='usd_support_status' class="widget-body"></div>
					<div class="chart-legend" id="chart-legend-9"></div>
				</div>
			</div>


			<div class="inner-container">
				<div class="widget dashboard-widget-box" style="width:48%;float:left;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head" style="display: block;">
						<div class="widget-label label-1">
							<div class="widget-title" style = "font-size: 15px !important;"><span class="ellipsis" style="overflow: unset" id="mitigation_till-date-title"></span></div>
						</div>
						<div class="widget-label label-2" style="float:right;">
							<div class="widget-title">
								<span class="ellipsis" style="width: auto;display: flex;flex-direction: column;" id="mitigation_till-date-label"></span>
								<span class="ellipsis" style="width: 54%;display: flex;flex-direction: column;" id="mitigation_till-date-value"></span>
							</div>
						</div>
					</div>
					<div class="widget-head" style="justify-content: end;">
						<div class="widget-label label-2">
							
						</div>
					</div>
					
					<div id='mitigation_till-date' class="widget-body"></div>
					<div class="chart-legend" id="chart-legend-5"></div>
				</div>

				<div class="widget dashboard-widget-box" style="width:48%;float:right;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head" style="display: block;">
						<div class="widget-label label-1">
							<div class="widget-title" style = "font-size: 15px !important;"><span class="ellipsis" style="overflow: unset" id="mitigation_last-year-title"></span></div>
						</div>
						<div class="widget-label label-2" style="float:right;">
							<div class="widget-title">
							<span class="ellipsis" style="width: auto;display: flex;flex-direction: column;" id="mitigation_last-year-label"></span>
							<span class="ellipsis" style="width: 54%;display: flex;flex-direction: column;" flex;" id="mitigation_last-year-value">
							</div>
						</div>
					</div>
					<div class="widget-head" style="justify-content: end;">
						<div class="widget-label label-2">
							<div class="widget-title"></span></div>
						</div>
					</div>
					<div id='mitigation_last-year' class="widget-body"></div>
					<div class="chart-legend" id="chart-legend-6"></div>
				</div>
			</div>

			<div class="inner-container">
				<div class="widget dashboard-widget-box" style="width:98%;float:left;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head">
						<div class="widget-label">
							<div class="widget-title"><span class="ellipsis" id="co2_emission_last_five_years-title"></span></div>
						</div>
					</div>
					<div id='co2_emission_last_five_years' class="widget-body"></div>
					<div class="chart-legend" id="chart-legend-10"></div>
				</div>
			</div>


			<div class="inner-container">
				<div class="widget dashboard-widget-box" style="width:98%;float:left;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head">
						<div class="widget-label label-1">
							<div class="widget-title"><span class="ellipsis" id="co2_emission_latest-title"></span></div>
						</div>
						<div class="widget-label label-2">
							<div class="widget-title"><span class="ellipsis" style="width: 100%;display: flex;" id="co2_emission_latest-total"></span></div>
						</div>
					</div>
					<div id='co2_emission_latest' class="widget-body"></div>
					<div class="chart-legend" id="chart-legend-7"></div>
				</div>
			</div>

			<div class="inner-container">
				<div class="widget dashboard-widget-box" style="width:98%;float:left;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head">
						<div class="widget-label">
							<div class="widget-title"><span class="ellipsis" id="adaptation_ndp-title"></span></div>
						</div>
					</div>
					<div id='adaptation_ndp' class="widget-body"></div>
				</div>
			</div>

			<div class="inner-container">
				<div class="widget dashboard-widget-box" style="width:98%;float:left;box-shadow: 0px 0px 2px 0px gray;" data-widget-name="4034b678d7">
					<div class="widget-head">
						<div class="widget-label">
							<div class="widget-title"><span class="ellipsis" id="sdg_category-title"></span></div>
						</div>
					</div>
					<div id='sdg_category' class="widget-body"></div>
				</div>
			</div>

			
			
		</div>
			`).appendTo(this.page.main);
		this.get_cards_data()
	}

	get_cards_data(){
		// frappe.call("mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_cards_data").then((r) =>{
		// 	// let total_ghg_emmission = r.message.total_ghg_emmission
		// 	// let total_projects = r.message.total_projects
		// 	// let total_mitigation_projects = r.message.Mitigation
		// 	// let total_adaptation_projects = r.message.Adaptation
		// 	// let total_cross_cutting_projects = r.message.Cross-Cutting
		// 	// let total_enabler_projects = r.message.Enablers
		// 	// let total_transparency_projects = r.message.Transparency
		// 	// let till_date_finance_disbursed = r.message.till_date_finance_disbursed
		// 	// let till_date_ghg_reduction = r.message.till_date_ghg_reduction

		// 	$('#cur_page_data').html(`
			
			
		// 	`)
		// })
		// this.ghg_emission_reduction_chart()
		// this.finace_dibursment_chart()
		// this.ghg_emissions_chart()
		this.project_count_chart()
		this.mitigation_ghg_till_date()
		this.mitigation_ghg_last_year()
		this.total_co2_emission_latest()
		this.get_total_project_ndp()
		this.get_total_sdg_report()
		this.co2_emission_last_five_years()
		this.get_finance_support()
		
	}
	
	// ghg_emissions_chart(){
	// 	frappe.call('mrvtools.mrvtools.page.main_dashboard.main_dashboard.ghg_emissions_data')
	// 		.then((r) => {
	// 			// $('.title_names1').html("GHG Emissions")
	// 			let results = r.message || [];
	// 			const custom_options = {
	// 				type: "line",
	// 				colors: ["#369fff"],
	// 				height: 240,
	// 				axisOptions: {
	// 					xIsSeries: 0,
	// 					isNavigable :1,
	// 					shortenYAxisNumbers: 0,
	// 					xAxisMode: "tick",
	// 					numberFormatter: frappe.utils.format_chart_axis_number
	// 				},
	// 				data: {
	// 					datasets: [{values: results.data}],
	// 					labels: results.labels
	// 				},
	// 			};
	// 			// frappe.utils.make_chart("#ghg_emissions", custom_options);
	// 		});
	// }

	// ghg_emission_reduction_chart(){
	// 	frappe.call('mrvtools.mrvtools.page.main_dashboard.main_dashboard.ghg_emission_reduction_data')
	// 		.then((r) => {
	// 			// $('.title_names2').html("GHG Emission Reduction")
	// 			let results = r.message || [];
	// 			const custom_options = {
	// 				type: "line",
	// 				colors: ["#369fff"],
	// 				height: 240,
	// 				axisOptions: {
	// 					xIsSeries: 0,
	// 					isNavigable :1,
	// 					shortenYAxisNumbers: 0,
	// 					xAxisMode: "tick",
	// 					numberFormatter: frappe.utils.format_chart_axis_number,
	// 				},
	// 				data: {
	// 					datasets: [{values: results.data}],
	// 					labels: results.labels
	// 				},
	// 			};
	// 			// frappe.utils.make_chart("#ghg_emission_reduction", custom_options);
	// 		});
	// }

	// finace_dibursment_chart(){
	// 	frappe.call('mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_finance_data')
	// 		.then((r) => {
	// 			// $('.title_names3').html("Finance Disbursement")
	// 			let results = r.message || [];
	// 			const custom_options = {
	// 				type: "line",
	// 				colors: ["#369fff"],
	// 				height: 240,
	// 				axisOptions: {
	// 					xIsSeries: 0,
	// 					isNavigable :1,
	// 					shortenYAxisNumbers: 0,
	// 					xAxisMode: "tick",
	// 					numberFormatter: frappe.utils.format_chart_axis_number,
	// 				},
	// 				data: {
	// 					datasets: [{values: results.data}],
	// 					labels: results.labels
	// 				},
	// 			};
	// 			// frappe.utils.make_chart("#finance_disbursement", custom_options);
	// 		});
			
	// }

	project_count_chart(){
		frappe.call('mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_document_count')
			.then((r) => {
				let project_count_label = []
				let project_count_value = []
				for(let [key, value] of Object.entries(r.message.project_count[0])){
					project_count_label.push(key);
					project_count_value.push(value);
				}
				
				$('#project-count-title').html("Projects - Objective wise")
				let colors_1 = ['#c6a7fe', '#ff8183', '#7feabf', '#cdcdcd','#70bcff']
				if (project_count_value.reduce((accumulator, currentValue) => accumulator + currentValue, 0) != 0){
					$('#project-count-total').html(`<span class="span-1">Total :</span><span class="span-2"> ${project_count_value.reduce((accumulator, currentValue) => accumulator + currentValue, 0)}</span>`)
					const custom_options = {
						type: "donut",
						colors: colors_1,
						height: 250,
						axisOptions: {
							xIsSeries: 0,
							isNavigable :1,
							shortenYAxisNumbers: 0,
							xAxisMode: "tick",
							numberFormatter: frappe.utils.format_chart_axis_number,
						},
						data: {
							datasets: [{values: project_count_value}],
							labels: project_count_label
						},
						axisOptions: {
							xAxisMode: "tick",
							xIsSeries: true,
						}
					};
					
					var legend_html_1 = '';
					for(let i=0;i<project_count_label.length;i++){
						legend_html_1+= `<div class="chart-legend-item">
											<div class="fill-box" style="background-color:${colors_1[i]}"></div>
											<div class="chart-legend-item-label">${project_count_label[i]}<br>
												<span class="chart-values-style" >${project_count_value[i]}</span>
											</div>
										</div>`;
					}
					frappe.utils.make_chart("#project-count", custom_options);
					$('[id="project-count"] [class="chart-container"]').addClass('inner-chart')
					$("#chart-legend-1").append(legend_html_1);

				}
				else{
					var no_image = ''
					no_image=`	<div class="msg-box no-border">
									<div>
										<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
									</div>
									<p>Nothing to show</p>
								</div>
							`
					$("#project-count").append(no_image)
				}


				let project_status_key_list = []
				let project_status_value_list = []
				for (let i of r.message.project_status){
					project_status_key_list.push(i['status'])
					project_status_value_list.push(i['count'])
				}


				$('#status-title').html("Projects - Status wise")
				let colors_2 = ['#9a97ff', '#63e293', '#9eccee','#c6a7fe', '#ff8183', '#7feabf', '#cdcdcd','#70bcff']
				if(project_status_value_list.reduce((accumulator, currentValue) => accumulator + currentValue, 0) != 0){
					$('#status-total').html(`<span class="span-1">Total :</span><span class="span-2"> ${project_status_value_list.reduce((accumulator, currentValue) => accumulator + currentValue, 0)}</span>`)
					const project_status_option = {
						type: "donut",
						colors: colors_2,
						height: 250,
						axisOptions: {
							xIsSeries: 0,
							isNavigable :1,
							shortenYAxisNumbers: 0,
							xAxisMode: "tick",
							numberFormatter: frappe.utils.format_chart_axis_number,
						},
						data: {
							datasets: [{values: project_status_value_list}],
							labels: project_status_key_list
						},
						axisOptions: {
							xAxisMode: "tick",
							xIsSeries: true,
						}
					};
					
					var legend_html_2 = '';
					for(let i=0;i<project_status_key_list.length;i++){
						legend_html_2 += `	<div class="chart-legend-item">
												<div class="fill-box" style="background-color:${colors_2[i]}"></div>
												<div class="chart-legend-item-label">${project_status_key_list[i]}<br>
													<span class="chart-values-style" >${project_status_value_list[i]}</span>
												</div>
											</div>
										`;
					}
					frappe.utils.make_chart("#project_status", project_status_option);
					$('[id="project_status"] [class="chart-container"]').addClass('inner-chart')
					$("#chart-legend-2").append(legend_html_2);
				}
				else{
					var no_image = ''
					no_image=`	<div class="msg-box no-border">
									<div>
										<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
									</div>
									<p>Nothing to show</p>
								</div>
							`
					$("#project_status").append(no_image)
				}
				
				let colors_3 = ["#d56ef5","#7a7fe5","#10d270","#cc6d0f","#d092e4","#ab428a","#04257b","#625b59","#760f99","#e7a8c9","#c2344f","#3a9f7e","#02cfaa","#37f287","#38a7ac","#1e4f97","#d56ef5","#7a7fe5","#980951","#8e93b3","#0cc2b0","#d2bf5f","#a963e8","#86aaf1","#78d1c4","#6e5ee2","#ff0e4c","#2e5ca0","#ba164a","#cc15f3","#cd91a0","#36ca11","#1e4f97","#5aa393","#0528aa","#10a801","#42d45a","#8f6407","#97969a","#0479b5","#a29ae6","#bc1cf2","#396523"]
				let mitigation_key_list = []
				let mitigation_value_list = []
				for (let i of r.message.mitigation){
					mitigation_key_list.push(i['key_sector'])
					mitigation_value_list.push(i['count'])
				}
				$('#mitigation-title').html("Mitigation Projects - Sector wise")
				// colors: ['#6fdf96', '#ff8183', '#c6a7fe', '#e8e565',"#ff92e0","#77cce2","#f29b69","#8c88f7"],
				if(mitigation_value_list.length != 0){
					$('#mitigation-total').html(`<span class="span-1">Total :</span><span class="span-2"> ${mitigation_value_list.reduce((accumulator, currentValue) => accumulator + currentValue, 0)}</span>`)
					const mitigation_option = {
						type: "donut",
						colors: colors_3,
						height: 250,
						axisOptions: {
							xIsSeries: 0,
							isNavigable :1,
							shortenYAxisNumbers: 0,
							xAxisMode: "tick",
							numberFormatter: frappe.utils.format_chart_axis_number,
						},
						data: {
							datasets: [{values: mitigation_value_list}],
							labels: mitigation_key_list
						},
						axisOptions: {
							xAxisMode: "tick",
							xIsSeries: true,
						}
					};
					var legend_html_3 = '';
					for(let i=0;i<mitigation_key_list.length;i++){
						legend_html_3 += `	<div class="chart-legend-item">
												<div class="fill-box" style="background-color:${colors_3[i]}"></div>
												<div class="chart-legend-item-label">${mitigation_key_list[i]}<br>
													<span class="chart-values-style" >${mitigation_value_list[i]}</span>
												</div>
											</div>
										`;
					}
					frappe.utils.make_chart("#mitigation-sector", mitigation_option);
					$('[id="mitigation-sector"] [class="chart-container"]').addClass('inner-chart')
					$("#chart-legend-3").append(legend_html_3);
					
				}
				else{
					var no_image = ''
					no_image=`	<div class="msg-box no-border">
									<div>
										<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
									</div>
									<p>Nothing to show</p>
								</div>
							`
					$("#mitigation-sector").append(no_image)
				}
				
				
				
				// ['#c6a7fe', '#ff8183', '#7feabf', '#d6d6d6','#70bcff', "#f29b69", '#8c88f7','#ff92e0']
				// let colors_3 = ["#adebad","#99e699","#5cd65c","#47d147","#29a329","#248f24","#1f7a1f","#196619","#145214","#0f3d0f","#0a290a","#051405"]
				let adaptation_key_list = []
				let adaptation_value_list = []
				for (let i of r.message.adaptation){
					adaptation_key_list.push(i['key_sector'])
					adaptation_value_list.push(i['count'])
				}
				$('#adaptation-title').html("Adaptation Projects - Sector wise")
				let colors_4 = ["#2E8B57","#FF69B4","#6A5ACD","#FF4500","#20B2AA","#FF8C00","#9370DB","#FFDAB9","#8A2BE2","#FFA07A","#00CED1","#FF69B4","#7B68EE","#FF4500","#20B2AA","#FF8C00","#FFC5A6","#FDAC98","#DC8E90","#A97882","#58545F","#B3D9FF","#FFD700","#C7E5E8","#FF6347","#9370DB","#32CD32","#FF1493","#4682B4","#FFD700","#8B4513","#FF6347","#9932CC","#FFA500","#32CD32","#FF1493","#4682B4","#FFD700","#8B4513","#FF6347"]
				if(adaptation_value_list.length != 0){
					$('#adaptation-total').html(`<span class="span-1">Total :</span><span class="span-2"> ${adaptation_value_list.reduce((accumulator, currentValue) => accumulator + currentValue, 0)}</span>`)
					const adaptation_option = {
						type: "donut",
						colors: colors_4,
						height: 250,
						axisOptions: {
							xIsSeries: 0,
							isNavigable :1,
							shortenYAxisNumbers: 0,
							xAxisMode: "tick",
							numberFormatter: frappe.utils.format_chart_axis_number,
						},
						data: {
							datasets: [{values: adaptation_value_list}],
							labels: adaptation_key_list
						},
						axisOptions: {
							xAxisMode: "tick",
							xIsSeries: true,
						}
					};
					var legend_html_4 = '';
					for(let i=0;i<adaptation_key_list.length;i++){
						legend_html_4 += `	<div class="chart-legend-item">
												<div class="fill-box" style="background-color:${colors_4[i]}"></div>
												<div class="chart-legend-item-label">${adaptation_key_list[i]}<br>
													<span class="chart-values-style" >${adaptation_value_list[i]}</span>
												</div>
											</div>
										`;
					}
					frappe.utils.make_chart("#adaptation-sector", adaptation_option);
					$('[id="adaptation-sector"] [class="chart-container"]').addClass('inner-chart')
					$("#chart-legend-4").append(legend_html_4);

				}
				else{
					var no_image = ''
					no_image=`	<div class="msg-box no-border">
									<div>
										<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
									</div>
									<p>Nothing to show</p>
								</div>
							`
					$("#adaptation-sector").append(no_image)
				}
			});
			
	}
	
	get_finance_support(){
		frappe.call('mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_finance_support')
		.then((r) => {
			let project_support_status_label = []
			let project_support_status_value = []
			for(let [key, value] of Object.entries(r.message[0])){
				project_support_status_label.push(key);
				project_support_status_value.push(value);
			}
			for(let [key, value] of Object.entries(r.message[1])){
				project_support_status_label.push(key);
				project_support_status_value.push(value);
			}
			let usd_support_status_label = []
			let usd_support_status_value = []
			for(let [key, value] of Object.entries(r.message[2])){
				usd_support_status_label.push(key);
				usd_support_status_value.push(value);
			}
			for(let [key, value] of Object.entries(r.message[3])){
				usd_support_status_label.push(key);
				usd_support_status_value.push(value);
			}
			let colors_8 = ["#ed7d31","#4472c4"]
			
			$('#project_support_status-title').html("Support Status - Project wise")
			// colors: ['#6fdf96', '#ff8183', '#c6a7fe', '#e8e565',"#ff92e0","#77cce2","#f29b69","#8c88f7"],
			if(project_support_status_value.length != 0){
				$('#project_support_status-total').html(`<span class="span-1">Total :</span><span class="span-2"> ${project_support_status_value.reduce((accumulator, currentValue) => accumulator + currentValue, 0)}</span>`)
				const options = {
					type: "donut",
					colors: colors_8,
					height: 250,
					axisOptions: {
						xIsSeries: 0,
						isNavigable :1,
						shortenYAxisNumbers: 0,
						xAxisMode: "tick",
						numberFormatter: frappe.utils.format_chart_axis_number,
					},
					data: {
						datasets: [{values: project_support_status_value}],
						labels: project_support_status_label
					},
					axisOptions: {
						xAxisMode: "tick",
						xIsSeries: true,
					}
				};
				var legend_html_8 = '';
				for(let i=0;i<project_support_status_label.length;i++){
					legend_html_8 += `	<div class="chart-legend-item">
											<div class="fill-box" style="background-color:${colors_8[i]}"></div>
											<div class="chart-legend-item-label">${project_support_status_label[i]}<br>
												<span class="chart-values-style" >${project_support_status_value[i]}</span>
											</div>
										</div>
									`;
				}
				frappe.utils.make_chart("#project_support_status", options);
				$('[id="project_support_status"] [class="chart-container"]').addClass('inner-chart')
				$("#chart-legend-8").append(legend_html_8);
				
			}
			else{
				var no_image = ''
				no_image=`	<div class="msg-box no-border">
								<div>
									<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
								</div>
								<p>Nothing to show</p>
							</div>
						`
				$("#project_support_status").append(no_image)
			}

			$('#usd_support_status-title').html("Support Status - USD")
			if(usd_support_status_value.length != 0){
				$('#usd_support_status-total').html(`<span class="span-1">Total :</span><span class="span-2"> ${usd_support_status_value.reduce((accumulator, currentValue) => accumulator + currentValue, 0)}</span>`)
				const options = {
					type: "donut",
					colors: colors_8,
					height: 250,
					axisOptions: {
						xIsSeries: 0,
						isNavigable :1,
						shortenYAxisNumbers: 0,
						xAxisMode: "tick",
						numberFormatter: frappe.utils.format_chart_axis_number,
					},
					data: {
						datasets: [{values: usd_support_status_value}],
						labels: usd_support_status_label
					},
					axisOptions: {
						xAxisMode: "tick",
						xIsSeries: true,
					}
				};
				var legend_html_9 = '';
				for(let i=0;i<usd_support_status_label.length;i++){
					legend_html_9 += `	<div class="chart-legend-item">
											<div class="fill-box" style="background-color:${colors_8[i]}"></div>
											<div class="chart-legend-item-label">${usd_support_status_label[i]}<br>
												<span class="chart-values-style" >${usd_support_status_value[i]}</span>
											</div>
										</div>
									`;
				}
				frappe.utils.make_chart("#usd_support_status", options);
				$('[id="usd_support_status"] [class="chart-container"]').addClass('inner-chart')
				$("#chart-legend-9").append(legend_html_9);
				
			}
			else{
				var no_image = ''
				no_image=`	<div class="msg-box no-border">
								<div>
									<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
								</div>
								<p>Nothing to show</p>
							</div>
						`
				$("#usd_support_status").append(no_image)
			}
			
			
			
		})
	}

	mitigation_ghg_till_date(){
		frappe.call('mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_commulative_mitigation_till_date')
			.then((r) => {
				$('#mitigation_till-date-title').html("GHG Emission Reductions Achieved - Till Today (tCO2e)")
				// '#6fdf96', '#ff8183', '#c6a7fe', '#e8e565',"#ff92e0","#77cce2","#f29b69","#8c88f7"
				let colors_5 = ["#ffa600","#ff7c43","#f95d6a","#d45087","#a05195","#665191","#2f4b7c","#003f5c","#00545c","#005e7b","#006598","#4f67ad","#8d62b2","#c358a4","#eb5186","#ff5d5d"]
					if (r.message.data.length != 0){
						let expected = 0
						if(r.message.expected.length != 0){
							expected = r.message.expected.reduce((accumulator, currentValue) => accumulator + currentValue, 0)
						}
						else{
							expected = 0
						}
						if(r.message.data.reduce((accumulator, currentValue) => accumulator + currentValue, 0) != 0){
							$('#mitigation_till-date-label').html(`<span class="span-3">Total :</span><span class="span-3">Expected :</span>`)
							$('#mitigation_till-date-value').html(`<span class="span-4"> ${r.message.data.reduce((accumulator, currentValue) => accumulator + currentValue, 0)}</span><span class="span-4"> ${expected}</span>`)
							const mitigation_ghg_till_data = {
								type: "donut",
								colors: colors_5,
								height: 250,
								axisOptions: {
									xIsSeries: 0,
									isNavigable :1,
									shortenYAxisNumbers: 0,
									xAxisMode: "tick",
									numberFormatter: frappe.utils.format_chart_axis_number,
								},
								data: {
									datasets: [{values: r.message.data}],
									labels: r.message.labels
								},
								axisOptions: {
									xAxisMode: "tick",
									xIsSeries: true,
								}
							};
							var legend_html_5 = '';
							for(let i=0;i<r.message.data.length;i++){
								legend_html_5 += `	<div class="chart-legend-item">
														<div class="fill-box" style="background-color:${colors_5[i]}"></div>
														<div class="chart-legend-item-label">${r.message.labels[i]}<br>
															<span class="chart-values-style" >${r.message.data[i]}</span>
														</div>
													</div>
												`;
							}
							frappe.utils.make_chart("#mitigation_till-date", mitigation_ghg_till_data)
							$('[id="mitigation_till-date"] [class="chart-container"]').addClass('inner-chart')
							$("#chart-legend-5").append(legend_html_5);
						}
						else{
							var no_image = ''
							no_image=`	<div class="msg-box no-border">
											<div>
												<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
											</div>
											<p>Nothing to show</p>
										</div>
									`
							$("#mitigation_till-date").append(no_image)
						}
					}
					else{
						var no_image = ''
						no_image=`	<div class="msg-box no-border">
										<div>
											<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
										</div>
										<p>Nothing to show</p>
									</div>
								`
						$("#mitigation_till-date").append(no_image)
					}
					
				
				
			})
	}


	mitigation_ghg_last_year(){
		let today = new Date();
		let lastYearFromDate;
		let lastYearToDate;

		lastYearFromDate = new Date(Date.UTC(today.getUTCFullYear() -1, 0, 1));
		lastYearToDate = new Date(Date.UTC(today.getUTCFullYear() -1, 11, 31));
		let lastYearFromDateStr = lastYearFromDate.toISOString().split('T')[0];
		let lastYearToDateStr = lastYearToDate.toISOString().split('T')[0];
		let fromDateParts = lastYearFromDateStr.split("-");
		let toDateParts = lastYearToDateStr.split("-");
		let formattedFromDate = `${fromDateParts[2]}-${fromDateParts[1]}-${fromDateParts[0]}`
		let formattedToDate = `${toDateParts[2]}-${toDateParts[1]}-${toDateParts[0]}`
		frappe.call('mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_commulative_mitigation_last_year')
			.then((r) => {
				$('#mitigation_last-year-title').html(`GHG Emission Received Achieved - ${formattedFromDate} to ${formattedToDate} (tCO2e)`)
				let colors_6 = ['#6fdf96', '#ff8183', '#c6a7fe', '#e8e565',"#ff92e0","#77cce2","#f29b69","#8c88f7"]
					if(r.message.data.length != 0){
						let expected = 0
						if(r.message.expected.length != 0){
							expected = r.message.expected.reduce((accumulator, currentValue) => accumulator + currentValue, 0)
						}
						else{
							expected = 0
						}
						if(r.message.data.reduce((accumulator, currentValue) => accumulator + currentValue, 0) != 0){
							$('#mitigation_last-year-label').html(`<span class="span-3">Total :</span><span class="span-3">Expected :</span>`)
							$('#mitigation_last-year-value').html(`<span class="span-4"> ${r.message.data.reduce((accumulator, currentValue) => accumulator + currentValue, 0)}</span><span class="span-4"> ${expected}</span>`)
							const mitigation_ghg_last_year = {
								type: "donut",
								colors: colors_6,
								height: 250,
								axisOptions: {
									xIsSeries: 0,
									isNavigable :1,
									shortenYAxisNumbers: 0,
									xAxisMode: "tick",
									numberFormatter: frappe.utils.format_chart_axis_number,
								},
								data: {
									datasets: [{values: r.message.data}],
									labels: r.message.labels
								},
								axisOptions: {
									xAxisMode: "tick",
									xIsSeries: true,
								}
							};
							
							var legend_html_6 = '';
							for(let i=0;i<r.message.data.length;i++){
								legend_html_6 += `	<div class="chart-legend-item">
														<div class="fill-box" style="background-color:${colors_6[i]}"></div>
														<div class="chart-legend-item-label">${r.message.labels[i]}<br>
															<span class="chart-values-style" >${r.message.data[i]}</span>
														</div>
													</div>
												`;
							}
							frappe.utils.make_chart("#mitigation_last-year", mitigation_ghg_last_year);
							$('[id="mitigation_last-year"] [class="chart-container"]').addClass('inner-chart')
							$("#chart-legend-6").append(legend_html_6);
						}
						else{
							
							var no_image = ''
							no_image=`	<div class="msg-box no-border">
											<div>
												<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
											</div>
											<p>Nothing to show</p>
										</div>
									`
							$("#mitigation_last-year").append(no_image)
						}
					}
					else{
							
						var no_image = ''
						no_image=`	<div class="msg-box no-border">
										<div>
											<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
										</div>
										<p>Nothing to show</p>
									</div>
								`
						$("#mitigation_last-year").append(no_image)
					}
					
			})
	}
	
	total_co2_emission_latest() {
		let today = new Date();
		let lastYearFromDate;
		let lastYearToDate;

		lastYearFromDate = new Date(Date.UTC(today.getUTCFullYear() -1, 0, 1));
		lastYearToDate = new Date(Date.UTC(today.getUTCFullYear() -1, 11, 31));
		let lastYearFromDateStr = lastYearFromDate.toISOString().split('T')[0];
		let lastYearToDateStr = lastYearToDate.toISOString().split('T')[0];
		let fromDateParts = lastYearFromDateStr.split("-");
		let toDateParts = lastYearToDateStr.split("-");
		let formattedFromDate = `${fromDateParts[2]}-${fromDateParts[1]}-${fromDateParts[0]}`
		let formattedToDate = `${toDateParts[2]}-${toDateParts[1]}-${toDateParts[0]}`
		frappe.call('mrvtools.mrvtools.page.main_dashboard.main_dashboard.total_co2_emission_latest')
			.then((r) => {
				$('#co2_emission_latest-title').html(`Total CO2 emmissions : ${formattedFromDate} to ${formattedToDate} Sector Wise (tCO2e)`)
				let colors_7 = ["#b9d5b2", "#84b29e", "#568f8b", "#326b77", "#1b485e", "#122740"]
				let results = r.message || [];
				if (results != []){
					if (results.data.length != 0){
						if (r.message.data.reduce((accumulator, currentValue) => accumulator + currentValue, 0) != 0){
							$('#co2_emission_latest-total').html(`<span class="span-1">Total :</span><span class="span-2"> ${r.message.data.reduce((accumulator, currentValue) => accumulator + currentValue[0], 0)}</span>`)
							
							const custom_options = {
								type: "donut",	
								colors: colors_7,
								height: 250,
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
							
							var legend_html_7 = '';
							for(let i=0;i<r.message.data.length;i++){
								legend_html_7 += `	<div class="chart-legend-item">
														<div class="fill-box" style="background-color:${colors_7[i]}"></div>
														<div class="chart-legend-item-label">${r.message.labels[i]}<br>
															<span class="chart-values-style" >${r.message.data[i]}</span>
														</div>
													</div>
												`;
							}
							frappe.utils.make_chart("#co2_emission_latest", custom_options);
							$('[id="co2_emission_latest"] [class="chart-container"]').addClass('inner-chart')
							$("#chart-legend-7").append(legend_html_7);
						}
						else{
							
							var no_image = ''
							no_image=`	<div class="msg-box no-border">
											<div>
												<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
											</div>
											<p>Nothing to show</p>
										</div>
									`
							$("#co2_emission_latest").append(no_image)
						}
					}
					else{
					
						var no_image = ''
						no_image=`	<div class="msg-box no-border">
										<div>
											<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
										</div>
										<p>Nothing to show</p>
									</div>
								`
						$("#co2_emission_latest").append(no_image)
					}
					
					
				}
				else{
					
					var no_image = ''
					no_image=`	<div class="msg-box no-border">
									<div>
										<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
									</div>
									<p>Nothing to show</p>
								</div>
							`
					$("#co2_emission_latest").append(no_image)
				}
				
			});
			
	}

	get_total_project_ndp() {
		frappe.call('mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_total_project_ndp')
			.then((r) => {
				$("#adaptation_ndp-title").html("No of Adaptation Projects - NDS Coverage wise")
				
				let results = r.message || [];
				let keys = Object.keys(r.message);
				let values = Object.values(r.message);
				if (results != []){
					if (values.length != 0){
						if (values.reduce((accumulator, currentValue) => accumulator + currentValue, 0) != 0){
							const custom_options = {
								type: "bar",
								colors: ["#03a9f4"],
								height: 250,
								axisOptions: {
									xIsSeries: 0,
									isNavigable :1,
									shortenYAxisNumbers: 0,
									xAxisMode: "tick",
									numberFormatter: frappe.utils.format_chart_axis_number,
								},
								data: {
									datasets: [{values: values}],
									labels: keys
								}
							};
							frappe.utils.make_chart("#adaptation_ndp", custom_options);
						}
						else{
							var no_image = ''
							no_image=`	<div class="msg-box no-border">
											<div>
												<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
											</div>
											<p>Nothing to show</p>
										</div>
									`
							$("#adaptation_ndp").append(no_image)
						}
					}
					else{
						var no_image = ''
						no_image=`	<div class="msg-box no-border">
										<div>
											<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
										</div>
										<p>Nothing to show</p>
									</div>
								`
						$("#adaptation_ndp").append(no_image)
					}
					
					
				}
				else{
					var no_image = ''
					no_image=`	<div class="msg-box no-border">
									<div>
										<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
									</div>
									<p>Nothing to show</p>
								</div>
							`
					$("#adaptation_ndp").append(no_image)
				}
			});
			
	}

	get_total_sdg_report() {
		frappe.call('mrvtools.mrvtools.page.main_dashboard.main_dashboard.get_total_sdg_category_wise')
			.then((r) => {
				$("#sdg_category-title").html("No of SDG Projects - SDG Categories")
				let results = r.message || [];
				if (results != []){
					if(r.message.data.reduce((accumulator, currentValue) => accumulator + currentValue, 0) != 0){
						const custom_options = {
							type: "bar",
							colors: ["#48bb74"],
							height: 250,
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
						frappe.utils.make_chart("#sdg_category", custom_options);
					}
					else{
						var no_image = ''
						no_image=`	<div class="msg-box no-border">
										<div>
											<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
										</div>
										<p>Nothing to show</p>
									</div>
								`
						$("#sdg_category").append(no_image)
					}
					
				}
				else{
					var no_image = ''
					no_image=`	<div class="msg-box no-border">
									<div>
										<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
									</div>
									<p>Nothing to show</p>
								</div>
							`
					$("#sdg_category").append(no_image)
				}
				
				
			});
			
			
	}

	co2_emission_last_five_years() {
		frappe.call('mrvtools.mrvtools.page.main_dashboard.main_dashboard.total_co2_emission_last_five_years')
			.then((r) => {
				let value_list = []
				$("#co2_emission_last_five_years-title").html("Historic GHG Inventory - Last Five Years (tCO2e)")
				let colors_10 = ["#b1518f","#d95b5f","#da6d44","#b99b1b","#cf842b","#6ac34d"]
				let results = r.message || [];
				for(let i of results.datasets){
					let a = i["values"].reduce((accumulator, currentValue) => accumulator + currentValue, 0)
					value_list.push(a)
				}


				if(results != 0){
					if(value_list.reduce((accumulator, currentValue) => accumulator + currentValue, 0) != 0){
						const custom_options = {
							type: "bar",
							colors: colors_10,
							height: 250,
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
							barOptions: {
								"stacked": 1
							},
						};
						frappe.utils.make_chart("#co2_emission_last_five_years", custom_options);
						let legend_html_10 = ''
						for(let i=0;i<results.datasets.length;i++){
							legend_html_10 += `	<div class="chart-legend-item">
													<div class="fill-box" style="background-color:${colors_10[i]}"></div>
													<div class="chart-legend-item-label">${results.datasets[i]["name"]}</div>
												</div>
											`;
						}
						$('[id="mitigation_last-year"] [class="chart-container"]').addClass('inner-chart')
						$("#chart-legend-10").append(legend_html_10);
					}
					else{
						var no_image = ''
						no_image=`	<div class="msg-box no-border">
										<div>
											<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
										</div>
										<p>Nothing to show</p>
									</div>
								`
						$("#co2_emission_last_five_years").append(no_image)
					}
				}
				else{
					var no_image = ''
					no_image=`	<div class="msg-box no-border">
									<div>
										<img src="/assets/frappe/images/ui-states/list-empty-state.svg" alt="Generic Empty State" class="null-state">
									</div>
									<p>Nothing to show</p>
								</div>
							`
					$("#co2_emission_last_five_years").append(no_image)
				}
			});
			setTimeout(() => {
				$('#co2_emission_last_five_years').find('g[class="bar-chart chart-draw-area"]').css('transform', 'translate(7%, 17%)')
			}, 2000);
			
	}
}

/* <div class="total_card_div" >
				<div class="total_card_1">
							<div class="widget number-widget-box" data-widget-name="Total GHG Emissions">
								<div class="widget-head">
									<div class="widget-label">
										<a data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
											<img src="/files/GHG Inventory-01.svg" alt="Assemble_logo" width="60" height="60" class="logo_style1">
										</a>
										<span class="ellipse"  title="Total GHG Emissions">Total GHG Emissions</span>
										
									</div>
									<br>
									</div>
									<div class="number_e" id="value-cards">`+total_ghg_emmission+` tCO2e</div>
								<div class="widget-footer"></div>
							</div>
				</div>
				<div class="total_card_2" >
							<div class="widget number-widget-box" data-widget-name="Total Projects">
								<div class="widget-head">
								<div class="widget-label">
								<a data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
								<img src="/files/Projects-01.svg" alt="Assemble_logo" width="60" height="60" class="logo_style1">
								</a>
								<span class="ellipse" title="Total Projects">Total Projects</span>
								
								</div>
								<br>
								</div>
								
								<div class="number_e" id="value-cards">`+total_projects+`</div>
								<div class="widget-footer"></div>
							</div>
				</div>
				<div class="total_card_3" >
						<div class="widget number-widget-box" data-widget-name="Mitigation Projects">
							<div class="widget-head">
			
							<div class="widget-label">
							<a data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
							<img src="/files/Mitigation Actions-01.svg" alt="Assemble_logo" width="60" height="60" class="logo_style1">
							</a>
							<span class="ellipse" title="Mitigation Projects">Mitigation Projects</span>
							
							</div>
							<br>
							</div>
							
							<div class="number_e" id="value-cards">`+total_mitigation_projects+`</div>
								<div class="widget-footer"></div>
							</div>
				</div>
				
			</div>
			<div class="total_card_div" >
				<div class="total_card_4">
								
					<div class="widget number-widget-box" data-widget-name="Adaptation Projects">
						<div class="widget-head">
							<div class="widget-label">
							<a data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
								<img src="/files/Adaptation Actions-01.svg" alt="Assemble_logo" width="60" height="60" class="logo_style1">
							</a>
							<span class="ellipse"  title="Adaptation Projects">Adaptation Projects</span>
							</div>
							<br>
							</div>
							<div class="number_e" id="value-cards">`+total_adaptation_projects+`</div>
					<div class="widget-footer"></div>
					</div>
				</div>
				<div class="total_card_5" >
							<div class="widget number-widget-box" data-widget-name="Cross Cutting Projects">
								<div class="widget-head">
								<div class="widget-label">
								<a data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
								<img src="/files/Climate Finance-01.svg" alt="Assemble_logo" width="60" height="60" class="logo_style1">
								</a>
								<span class="ellipse" title="Cross Cutting Projects">Cross Cutting Projects</span>
								
								</div>
								<br>
								</div>
								<div class="number_e" id="value-cards">`+total_cross_cutting_projects+`</div>
								
								<div class="widget-footer"></div>
							</div>
				</div>
				<div class="total_card_6" >
						<div class="widget number-widget-box" data-widget-name="Enabler Projects">
							<div class="widget-head">

								<div class="widget-label">
									<a data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
										<img src="/files/SDGs ASSESSMENTS-01.svg" alt="Assemble_logo" width="60" height="60" class="logo_style1">
									</a>
									<span class="ellipse" title="Enabler Projects">Enabler Projects</span>
									
									</div>
									</div>
									<div class="number_e" id="value-cards">`+total_enabler_projects+`</div>
							
							<div class="widget-footer"></div>
						</div>
				</div>
				
			</div>
			<div class="total_card_div" >
				<div class="total_card_7">
								
					<div class="widget number-widget-box" data-widget-name="Climate finance disbursed till date">
						<div class="widget-head">
							<div class="widget-label">
								<a data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
									<img src="/files/Mitigation Actions-01.svg" alt="Assemble_logo" width="60" height="60" class="logo_style1">
								</a>
								<span class="ellipse"  title="Climate finance disbursed till date">Climate finance disbursed till date</span>
								</div>
								<br>
								</div>
								<div class="number_e" id="value-cards">USD `+till_date_finance_disbursed+`</div>
								<div class="widget-footer"></div>
					</div>
				</div>
				<div class="total_card_8" >
							<div class="widget number-widget-box" data-widget-name="GHG Reductions Actual till date">
								<div class="widget-head">
									<div class="widget-label">
										<a data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
										<img src="/files/Projects-01.svg" alt="Assemble_logo" width="60" height="60" class="logo_style1">
										</a>
										<span class="ellipse" title="GHG Reductions Actual till date">GHG Reductions Actual till date</span>
										
										</div>
										<br>
										</div>
										<div class="number_e" id="value-cards">`+till_date_ghg_reduction+` tCO2e</div>
								
								<div class="widget-footer"></div>
							</div>
				</div>
				<div class="total_card_9">
					<div class="widget number-widget-box" data-widget-name="GHG Reductions Actual till date">
						<div class="widget-head"></div>
					</div>
				</div> */
