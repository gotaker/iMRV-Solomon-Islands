// Editorial reskin — Phase 3
// Plan: /Users/utahjazz/.claude/plans/zesty-wiggling-clock.md
// Post-login landing surface. Renders inside Frappe's Page wrapper.
// All async fetches have an error path that renders an empty state.

frappe.pages['main-dashboard'].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Dashboard',
		single_column: true,
	});

	const $body = $(page.body).addClass('ed-dashboard-wrapper');
	$body.html(buildShell());

	loadStats($body);
	loadActivity($body);
};

function buildShell() {
	const fullName = (frappe.session.user_fullname || '').trim();
	const firstName = fullName ? fullName.split(' ')[0] : 'Welcome';
	const greeting = `${timeOfDay()}, ${escapeHTML(firstName)}`;
	const date = moment().format('dddd, D MMMM YYYY');

	return `
		<div class="ed-dashboard">
			<header class="ed-dashboard-hero">
				<h1>${escapeHTML(greeting)}</h1>
				<p class="ed-date">${escapeHTML(date)}</p>
			</header>

			<section class="ed-stat-row" aria-label="Key metrics">
				${statTileSkeleton('projects', 'Active Projects', 'In the iMRV pipeline')}
				${statTileSkeleton('approvals', 'Pending Approvals', 'Awaiting your review')}
				${statTileSkeleton('reports', 'Monitoring Reports', 'Logged this period')}
			</section>

			<section class="ed-program-row" aria-label="Programs">
				${programCard('adaptation', 'Adaptation', 'Resilience planning & coastal works', '/app/adaptation')}
				${programCard('mitigation', 'Mitigation', 'Emissions reduction projects', '/app/mitigations')}
				${programCard('ghg', 'GHG Inventory', 'National greenhouse gas accounts', '/app/ghg-inventory')}
			</section>

			<section class="ed-activity" aria-label="Recent activity">
				<h2 class="ed-activity-title">Recent Activity</h2>
				<div class="ed-activity-body" data-slot="activity">
					<div class="ed-activity-loading">Loading…</div>
				</div>
			</section>
		</div>
	`;
}

function statTileSkeleton(slot, eyebrow, caption) {
	return `
		<article class="ed-stat-tile" data-slot="${slot}">
			<div class="ed-stat-eyebrow">${escapeHTML(eyebrow)}</div>
			<div class="ed-stat-number" aria-live="polite">…</div>
			<div class="ed-stat-caption">${escapeHTML(caption)}</div>
		</article>
	`;
}

function programCard(slug, title, copy, route) {
	return `
		<a class="ed-program-card ed-program-${slug}" href="${route}">
			<h2 class="ed-program-title">${escapeHTML(title)}</h2>
			<p class="ed-program-copy">${escapeHTML(copy)}</p>
			<span class="ed-arrow" aria-hidden="true">→</span>
		</a>
	`;
}

function loadStats($body) {
	const tiles = [
		{ slot: 'projects', doctype: 'Project', filters: {} },
		{ slot: 'approvals', doctype: 'My Approval', filters: { owner: frappe.session.user } },
		{ slot: 'reports', doctype: 'Adaptation Monitoring Information', filters: {} },
	];

	tiles.forEach((tile) => {
		const $num = $body.find(`.ed-stat-tile[data-slot="${tile.slot}"] .ed-stat-number`);
		frappe.call({
			method: 'frappe.client.get_count',
			args: { doctype: tile.doctype, filters: tile.filters },
			callback: (r) => {
				const n = (r && typeof r.message === 'number') ? r.message : 0;
				$num.text(formatCount(n));
			},
			error: () => $num.text('—'),
		});
	});
}

function loadActivity($body) {
	const $slot = $body.find('.ed-activity-body');
	frappe.db
		.get_list('Activity Log', {
			filters: { user: frappe.session.user },
			fields: ['subject', 'reference_doctype', 'reference_name', 'creation'],
			limit: 5,
			order_by: 'creation desc',
		})
		.then((rows) => $slot.html(renderActivity(rows || [])))
		.catch(() => $slot.html(emptyActivity()));
}

function renderActivity(rows) {
	if (!rows.length) return emptyActivity();
	return rows
		.map(
			(r) => `
			<div class="ed-activity-row">
				<div class="ed-activity-eyebrow">${escapeHTML(r.reference_doctype || 'Activity')}</div>
				<div class="ed-activity-subject">${escapeHTML(stripHTML(r.subject || r.reference_name || ''))}</div>
				<div class="ed-activity-when">${escapeHTML(moment(r.creation).fromNow())}</div>
			</div>
		`
		)
		.join('');
}

function emptyActivity() {
	return `<div class="ed-empty-state">No recent activity yet.</div>`;
}

function timeOfDay() {
	const h = new Date().getHours();
	if (h < 12) return 'Good morning';
	if (h < 17) return 'Good afternoon';
	return 'Good evening';
}

function formatCount(n) {
	if (n >= 1000) return Math.round(n / 100) / 10 + 'k';
	return String(n);
}

function escapeHTML(s) {
	return String(s == null ? '' : s)
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#39;');
}

function stripHTML(s) {
	return String(s == null ? '' : s).replace(/<[^>]*>/g, '');
}
