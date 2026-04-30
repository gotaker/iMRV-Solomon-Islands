// var options
frappe.pages["ghg-year-report"].on_page_load = (wrapper) => {
	frappe.ghg_year_report = new GHGInventory(wrapper);
};

class GHGInventory {
	constructor(parent) {
		frappe.ui.make_app_page({
			parent: parent,
			title: __("GHG Year Report"),
			single_column: false,
			card_layout: true,
		});

		this.parent = parent;
		this.page = this.parent.page;
		this.page.sidebar.html(
			`<ul class="standard-sidebar ghg_year_report-sidebar overlay-sidebar"></ul>`
		);
		this.$sidebar_list = this.page.sidebar.find("ul");
		// alert(frappe.defaults.get_user_default("Order"))
		this.datatable=null;
		// this.add_card_button_to_toolbar();
		this.set_default_secondary_action();
		this.ghg_from_year();
		this.ghg_unit_filter();
		// Render the chart container + data table on load. Without these the
		// page sat blank below the filter row until the user changed a filter.
		this.render_datatable();
		this.make();

		// this.create_date_range_field();
	}
	set_default_secondary_action() {
		this.refresh_button && this.refresh_button.remove();
		this.refresh_button = this.page.add_action_icon("refresh", () => {
			this.$container.empty()
			this.$report.empty()
			$('[class="ghg_year_report page-main-content"]:first').remove()
			$('[class="all_html"]:first').remove()
			this.make()
			this.render_datatable()
		});
		this.download_button = this.page.set_secondary_action('Download Excel', () => {

			frappe.call('mrvtools.ghg_inventory.page.ghg_year_report.ghg_year_report.execute',{
				from_year:this.from_year[0].value,
				to_year:this.to_year[0].value,
				inventory_unit:this.inventory_unit[0].value
			})
				.then((r) => {
					frappe.call('mrvtools.ghg_inventory.page.ghg_year_report.ghg_year_report.download_excel',{
						columns:r.message[0],
						data:r.message[1]
					}).then((i) =>{
						window.open(i.message)
					})
				})
		})
		this.page.add_inner_button('Download PDF', () => {
			frappe.call('mrvtools.ghg_inventory.page.ghg_year_report.ghg_year_report.download_pdf', {
				from_year: this.from_year[0].value,
				to_year: this.to_year[0].value,
				inventory_unit: this.inventory_unit[0].value,
			}).then((i) => { if (i.message) window.open(i.message); });
		});
	}
	

	make() {
		this.$container = $(`
		<div class = "all_html"  style="margin:0;">
			<div id="ghg_chart1"></div>
			
		</div>`
		).appendTo(this.page.main);
		this.wrapper1()
		this.get_chart_report()
	
	}
	wrapper1(){
		$('#ghg_chart1').html(`<div class="ghg_year_report page-main-content">
		<div class="chart_hide" style="margin: 14px; display: flex; align-items: center;justify-content: space-between;">
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
		</script>
			<div id="chart-1" class="totalghg_year_report-graph"></div>
		</div>`)
	}
	get_chart_report() {
		frappe.call('mrvtools.ghg_inventory.page.ghg_year_report.ghg_year_report.get_chart',{
			from_year:this.from_year[0].value,
			to_year:this.to_year[0].value,
			inventory_unit:this.inventory_unit[0].value
		})
			.then((r) => {
				$("#categories_chart").html("No of emissions per gas (CO2, CH4, N2O)")
				
				let results = r.message || [];
				// Forest-and-Sage palette for the three gas series — uses
				// editorial tokens (--ed-forest, --ed-moss, --ed-sage) instead
				// of the previous "pink", "blue", "green" placeholders.
				const series_colors = ["#01472e", "#a3b18a", "#84b29e"];
				const custom_options = {
					type: "bar",
					colors: series_colors,
					height: 260,
					axisOptions: {
						xIsSeries: 0,
						isNavigable: 1,
						// shortenYAxisNumbers: 1 lets axis ticks render compactly
						// (e.g. "1M") rather than clipping a 7-digit "1,000,000".
						shortenYAxisNumbers: 1,
						xAxisMode: "tick",
						numberFormatter: function (v) {
							const n = Number(v);
							if (!isFinite(n)) return String(v);
							try {
								return new Intl.NumberFormat('en-US', {
									notation: 'compact', maximumFractionDigits: 1
								}).format(n);
							} catch (e) { return String(n); }
						},
					},
					data: {
						datasets: results.datasets,
						labels: results.labels
					},
					barOptions: {
						"stacked": 1
					}
				};
				frappe.utils.make_chart(".totalghg_year_report-graph", custom_options);
			});
			
	}
	ghg_from_year() {
		// Empty year list — populated dynamically below via get_years() so
		// 2027–2050 (no data) don't render as picker options.
		this.from_year = this.page.add_select(
			__("From Year"), [" "]
		);
		// Reuse the ghg-inventory-report endpoint that returns distinct years
		// with data, newest first.
		frappe.call('mrvtools.ghg_inventory.page.ghg_inventory_report.ghg_inventory_report.get_years').then((r) => {
			const years = (r && r.message) ? r.message : [];
			const $select = $(this.from_year);
			$select.empty();
			$select.append(new Option(' ', ''));
			years.forEach((y) => $select.append(new Option(String(y), String(y))));
		});
		this.from_year.on("change",(r) => {
			// this.render_datatable()
			// this.get_chart_report();
			// this.$heading.empty();
			if(this.from_year[0].value ==''){
				$('.report-heading').attr('style',"display:none !important")
				$('.all_html').attr('style',"display:none !important")
			}
			else{
				$('[class="report-heading"]:first').remove()
				$('.report-heading').attr('style',"display:block !important;margin-left: 30px")
				$('.all_html').attr('style',"display:block !important")
			}
			if(this.from_year[0].value){
				var options = []
				for(let i = parseInt(this.from_year[0].value);i<=(parseInt(this.from_year[0].value)+10);i++){
					options.push(i)
				}
				$('[data-original-title="To Year"]:first').remove();
				this.ghg_to_year(options)

			}
		})
		
	}

	ghg_to_year(options) {
		this.to_year = this.page.add_select(
			__("To Year"),options
		)
		this.to_year.on("change",(r) => {
			$('[class="all_html"]:first').remove()
			this.render_datatable()
			this.make()
			setTimeout(() => {
				this.get_chart_report();
			}, 300);
			this.$heading.empty();

		})
	}
	ghg_unit_filter() {
		// Display labels carry the Unicode subscript-2 (₂); values stay ASCII
		// so the Python switch in get_chart still matches.
		this.inventory_unit = this.page.add_select(
			__("Unit"),
			[
				{ label: "tCO₂e", value: "tCO2e" },
				{ label: "GgCO₂e", value: "GgCO2e" }
			]
		)
		this.inventory_unit.on("change",(r) => {
			$('[class="all_html"]:first').remove()
			this.render_datatable()
			this.make()
			setTimeout(() => {
				this.get_chart_report();
			}, 300);
			this.$heading.empty();
		})
	}


	render_datatable(){
		frappe.call('mrvtools.ghg_inventory.page.ghg_year_report.ghg_year_report.execute',{
			from_year:this.from_year[0].value,
			to_year:this.to_year[0].value,
			inventory_unit:this.inventory_unit[0].value
		})
			.then((r) => {
				$('.report-wrapper:first').remove();
				this.$report = $('<div class="report-wrapper">').appendTo(this.page.main);
				let columns = r.message[0]
				let data = r.message[1]
				$('.headline:first').remove();
				if(this.to_year[0].value){
					this.$heading = $('<b class="report-heading" style="margin-left: 30px;">GHG Inventory Report - Year wise</b>').insertBefore(this.$report);
				}
				
				this.datatable = new DataTable(this.$report[0], {columns:columns,data:data,treeView:true,inlineFilters: true});
			})
			
	}


}
