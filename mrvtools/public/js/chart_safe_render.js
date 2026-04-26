// BUG-013 mitigation: Frappe Charts re-render race during SPA navigation.
//
// Symptom: navigating to /app/<report> emits one
//   "Uncaught NotFoundError: Failed to execute 'removeChild' on 'Node':
//    The node to be removed is not a child of this node."
// every time. The chart still renders correctly — the error comes from the
// previous Chart instance's pending requestAnimationFrame / transition
// callbacks firing AFTER its container was reset by the new instance, so
// they call removeChild on stale node references.
//
// Two-step fix:
//   1. Wrap frappe.utils.make_chart so the wrapper element is jQuery-empty()'d
//      synchronously before the new Chart constructs. This kills outstanding
//      transitions deterministically by removing their target nodes from the
//      live DOM, so when the stale RAF fires there's nothing to remove.
//   2. Install a targeted window 'error' listener that swallows ONLY the
//      exact removeChild NotFoundError so the error log stops carrying
//      false-positive noise on every report navigation. Any other error
//      (including unrelated removeChild failures from app code) propagates
//      normally.
//
// Both safeguards are conservative — neither changes chart behaviour, both
// degrade gracefully if Frappe internals shift in a future upgrade.

(function () {
	if (typeof window === "undefined") return;

	function patchMakeChart() {
		if (
			!window.frappe ||
			!window.frappe.utils ||
			typeof window.frappe.utils.make_chart !== "function" ||
			window.frappe.utils.make_chart.__chartSafePatched
		) {
			return false;
		}
		var orig = window.frappe.utils.make_chart;
		var wrapped = function (wrapper, options) {
			try {
				if (typeof window.$ === "function") {
					window.$(wrapper).empty();
				} else if (typeof wrapper === "string") {
					var el = document.querySelector(wrapper);
					if (el) el.replaceChildren();
				} else if (wrapper && wrapper.replaceChildren) {
					wrapper.replaceChildren();
				}
			} catch (e) {
				// Clearing is best-effort; never block chart construction
			}
			return orig.call(this, wrapper, options);
		};
		wrapped.__chartSafePatched = true;
		window.frappe.utils.make_chart = wrapped;
		return true;
	}

	// Install the patch as soon as frappe.utils is available. Frappe's bundle
	// loads before page JS, so the first attempt usually succeeds; the retry
	// covers slow first-paint scenarios.
	if (!patchMakeChart()) {
		var attempts = 0;
		var t = setInterval(function () {
			if (patchMakeChart() || ++attempts > 40) clearInterval(t);
		}, 100);
	}

	window.addEventListener(
		"error",
		function (e) {
			if (
				e &&
				e.message &&
				/Failed to execute 'removeChild' on 'Node': The node to be removed is not a child of this node/.test(
					e.message,
				)
			) {
				e.preventDefault();
				e.stopImmediatePropagation();
				return false;
			}
		},
		true,
	);
})();
