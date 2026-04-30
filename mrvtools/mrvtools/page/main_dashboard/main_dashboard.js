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

function canRead(doctype) {
	return !!(frappe.boot && frappe.boot.user && frappe.boot.user.can_read && frappe.boot.user.can_read.indexOf(doctype) !== -1);
}

function loadStats($body) {
	// `My Approval` rows ARE the pending-approval queue (rows are created on
	// submission and deleted on approval — there is no `status` field). The
	// counter for the current admin/approver is the count of rows where
	// `approver = me`. Filtering by `owner` was wrong: `owner` is set to the
	// submitter via insert_record, not the assignee.
	const tiles = [
		{ slot: 'projects', doctype: 'Project', filters: {} },
		{ slot: 'approvals', doctype: 'My Approval', filters: { approver: frappe.session.user } },
		{ slot: 'reports', doctype: 'Adaptation Monitoring Information', filters: {} },
	];

	tiles.forEach((tile) => {
		const $num = $body.find(`.ed-stat-tile[data-slot="${tile.slot}"] .ed-stat-number`);
		// Skip the request entirely if the user lacks read perm — avoids a server
		// 403 + console traceback when widgets reference doctypes the role can't see.
		if (!canRead(tile.doctype)) {
			$num.text('—');
			return;
		}
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
	if (!canRead('Activity Log')) {
		$slot.html(emptyActivity());
		return;
	}
	// Org-wide feed for the dashboard: drop the `user = session.user` filter
	// so admins/approvers see WHO did what across the bench. Limit raised to
	// 10 since we now show actor identity. See reference_recent_activity_widget_filter.md.
	//
	// Drop "Invalid login credentials" rows — those carry the attacker-SUPPLIED
	// email as the `user` column, so without this filter a role with Activity
	// Log read perm would see arbitrary attacker-controlled strings (and a free
	// way to spam the feed). Discovered by 2026-04-29 stress test.
	frappe.db
		.get_list('Activity Log', {
			filters: { subject: ['not like', 'Invalid%'] },
			fields: ['subject', 'user', 'reference_doctype', 'reference_name', 'creation'],
			limit: 10,
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
				<div class="ed-activity-meta">
					<span class="ed-activity-user">${escapeHTML(r.user || 'system')}</span>
					<span class="ed-activity-when">${escapeHTML(formatWhen(r.creation))}</span>
				</div>
			</div>
		`
		)
		.join('');
}

// Past timestamps render as "9 hours ago" — never "in 9 hours". moment().fromNow()
// reports future tense when the parsed timestamp is interpreted as future
// (e.g. server-local string with no zone is read as browser-local UTC offset).
// frappe.datetime.comment_when is the v16-correct helper: it parses the same
// MariaDB-formatted timestamp the way Frappe's desk does and always reports
// past tense for past events. Fall back to a clamped fromNow() if the helper
// is missing on an older Frappe build.
function formatWhen(ts) {
	if (!ts) return '';
	if (frappe && frappe.datetime && typeof frappe.datetime.comment_when === 'function') {
		// comment_when returns HTML wrapped in <span>; strip tags to plain text.
		return stripHTML(frappe.datetime.comment_when(ts));
	}
	const m = moment(ts);
	const now = moment();
	// If the parsed time is in the future (shouldn't happen for Activity Log
	// rows), clamp to "just now" rather than rendering "in N hours".
	if (m.isAfter(now)) return 'just now';
	return m.fromNow();
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
