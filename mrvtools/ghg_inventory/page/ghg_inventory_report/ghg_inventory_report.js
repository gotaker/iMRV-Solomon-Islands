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
		// Year + unit filters are added with placeholders, then `boot_filters`
		// queries the backend for the years that actually have data, repopulates
		// the year dropdown, auto-selects the most recent year, and renders.
		// This replaces the old behaviour where 1990–2050 were hard-coded (so
		// 2027–2050 always rendered as blank charts) and the page rendered two
		// chart titles + Hide Chart buttons before a year was selected.
		this.ghg_year_filter();
		this.ghg_unit_filter();
		this.boot_filters();
	}

	boot_filters() {
		frappe.call('mrvtools.ghg_inventory.page.ghg_inventory_report.ghg_inventory_report.get_years').then((r) => {
			const years = (r && r.message) ? r.message : [];
			const $select = $(this.inventory_year);
			$select.empty();
			$select.append(new Option(' ', ''));
			years.forEach((y) => $select.append(new Option(String(y), String(y))));
			if (years.length) {
				const latest = String(years[0]);
				this.inventory_year[0].value = latest;
				$select.val(latest).trigger('change');
			}
		});
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

		this.download_button = this.page.set_secondary_action('Download Excel', () => {

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
		this.page.add_inner_button('Download PDF', () => {
			frappe.call('mrvtools.ghg_inventory.page.ghg_inventory_report.ghg_inventory_report.download_pdf', {
				inventory_year: this.inventory_year[0].value,
				inventory_unit: this.inventory_unit[0].value,
			}).then((i) => { if (i.message) window.open(i.message); });
		});
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
				const unit_label = unitLabel(this.inventory_unit[0].value);
				$("#categories_chart1").html("Total National Emission of all Gases (" + unit_label + ")");
				let results = r.message || [];
				if (!results || !results.data || !results.data.length) {
					$(".totalghg_inventory_report-graph").html(
						`<div class="ghg-empty-state">No data for the selected year.</div>`
					);
					return;
				}
				const values = (results.data[0] || []).map((v) => Number(v) || 0);
				const custom_options = {
					type: "bar",
					colors: ["#01472e"],
					height: 260,
					axisOptions: {
						xIsSeries: 0,
						isNavigable: 1,
						// shortenYAxisNumbers: 1 lets Frappe Charts render compact
						// labels (e.g. "1M" / "1.2k") instead of the raw 7-digit
						// integers that caused the "1,000,000" → ")00000" clip.
						shortenYAxisNumbers: 1,
						xAxisMode: "tick",
						numberFormatter: formatCompactNumber,
					},
					tooltipOptions: {
						formatTooltipY: (v) => formatTooltipNumber(v) + " " + unit_label,
					},
					data: {
						datasets: [{ name: unit_label, values: values }],
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
				const unit_label = unitLabel(this.inventory_unit[0].value);
				$("#categories_chart2").html("Total National Emission of all Gases - Sector Wise (" + unit_label + ")");
				let results = r.message || [];
				if (!results || !results.data || !results.data.length) {
					$(".totalghg_inventory_report-graph2").html(
						`<div class="ghg-empty-state">No sector data for the selected year.</div>`
					);
					return;
				}
				// Backend returns rows as tuples like [(123,), (456,), ...].
				// Frappe Charts wants a flat number array — without this flatten
				// the pie rendered as a single solid blue circle (it summed
				// arrays-as-objects to NaN and fell back to a single slice).
				const values = (results.data || []).map((row) => {
					const v = Array.isArray(row) ? row[0] : row;
					return Number(v) || 0;
				});
				// Forest-and-Sage palette: 6 distinct shades from the editorial
				// tokens (forest, moss, sage, olive, cream-deep, forest-dark).
				// Do NOT introduce new hex codes — these mirror :root tokens.
				const slice_colors = [
					"#01472e", // --ed-forest
					"#a3b18a", // --ed-moss
					"#84b29e", // sage-mid
					"#568f8b", // teal-forest accent
					"#ccd5ae", // --ed-sage
					"#022e1d"  // --ed-forest-dark
				];
				const total = values.reduce((s, n) => s + n, 0) || 1;
				const custom_options = {
					type: "pie",
					colors: slice_colors,
					height: 320,
					axisOptions: {
						xIsSeries: 0,
						isNavigable: 1,
						shortenYAxisNumbers: 1,
						xAxisMode: "tick",
						numberFormatter: formatCompactNumber,
						maxSlices: 6
					},
					tooltipOptions: {
						formatTooltipY: (v) => {
							const pct = ((Number(v) / total) * 100).toFixed(1);
							return formatTooltipNumber(v) + " " + unit_label + " (" + pct + "%)";
						},
					},
					data: {
						labels: results.labels,
						datasets: [{ name: "Sector", values: values }]
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
					const heading_unit = unitLabel(this.inventory_unit[0].value);
				this.$heading = $(`<b class="report-heading" style="margin-left: 30px;">GHG Inventory Report - Gas wise (${heading_unit})</b>`).insertBefore(this.$report);
				}
				this.datatable = new DataTable(this.$report[0], {columns:columns,data:data,treeView:true,inlineFilters: true});
				if(this.inventory_year[0].value ==''){
					$('.report-wrapper').attr('style',"display:none !important;border:none !important")
				}
			})
			
	}

	ghg_year_filter() {
		// Year list is empty here — populated dynamically by boot_filters() so
		// 2027–2050 (which have no GHG Inventory data in this site) don't
		// appear as picker options.
		this.inventory_year = this.page.add_select(__("Year"), [" "]);

		this.inventory_year.on("change",(r) => {
			$('[class="report-heading"]:first').remove()
			$('[class="all_html"]:first').remove()
			this.render_datatable()
			this.make()
			this.get_chart_report();
			this.get_chart_report2();
			if (this.$heading) this.$heading.empty();
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
		// Display labels carry the Unicode subscript-2 (₂) so the chart axis
		// title and unit picker read "tCO₂e" / "GgCO₂e" — the underlying
		// values stay ASCII so the Python switch in get_chart / get_pie_chart
		// (which compares against literal "tCO2e" / "GgCO2e") still matches.
		this.inventory_unit = this.page.add_select(
			__("Unit"),
			[
				{ label: "tCO₂e", value: "tCO2e" },
				{ label: "GgCO₂e", value: "GgCO2e" }
			]
		)
		this.inventory_unit.on("change",(r) => {
			$('[class="report-heading"]:first').remove()
			this.render_datatable()
			this.get_chart_report();
			this.get_chart_report2();
			if (this.$heading) this.$heading.empty();
		})
	}





}

// ---- helpers ---------------------------------------------------------------

// Render the unit label with the Unicode subscript-2 (₂) for chart titles,
// tooltips, and the data-table heading. Backend stays on ASCII keys.
function unitLabel(raw) {
	if (raw === "GgCO2e") return "GgCO₂e";
	return "tCO₂e";
}

// Compact number formatter for Y-axis ticks. Uses Intl when available so a
// 7-digit value like 1,234,567 renders as "1.2M" — fixes the clip where
// raw "1,000,000" was getting cropped to ")00000" because the chart container
// had no left padding for a multi-digit tick. Falls back to a manual switch
// in case Intl.NumberFormat compact notation is unavailable.
function formatCompactNumber(v) {
	const n = Number(v);
	if (!isFinite(n)) return String(v);
	try {
		return new Intl.NumberFormat('en-US', {
			notation: 'compact',
			maximumFractionDigits: 1
		}).format(n);
	} catch (e) {
		const abs = Math.abs(n);
		if (abs >= 1e9) return (n / 1e9).toFixed(1).replace(/\.0$/, '') + 'B';
		if (abs >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
		if (abs >= 1e3) return (n / 1e3).toFixed(1).replace(/\.0$/, '') + 'k';
		return String(n);
	}
}

// Tooltip wants the full thousands-separated value, not the compact one — so
// users can see the exact number on hover even when the axis is compacted.
function formatTooltipNumber(v) {
	const n = Number(v);
	if (!isFinite(n)) return String(v);
	try {
		return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(n);
	} catch (e) {
		return String(n);
	}
}
