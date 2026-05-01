# frappe_side_menu — floating navigation drawer

Independent Frappe app providing the desk's primary navigation as a **click-triggered overlay drawer**, not a fixed left rail. Top-left burger button opens a frosted-glass slide-in panel over a translucent forest backdrop; contextual flyout submenus re-parent to `<body>` and position outside the drawer's right edge.

## Install

From your bench root:

```bash
bench get-app frappe_side_menu <path-or-url>
bench --site <site> install-app frappe_side_menu
bench --site <site> migrate
```

Installed as a separate bench app (not a subpackage of `mrvtools`).

## Key files

- [`frappe_side_menu/api.py`](frappe_side_menu/api.py) — `get_menulist()` (renders Side Menu / Drill Down Menu / Side Menu With Tab), `set_default_route()` (the `on_session_creation` post-login redirect handler), and several guest-accessible helpers.
- [`public/js/frappe_side_menu.js`](public/js/frappe_side_menu.js) — drawer behavior: trigger button injection, `body.fsm-open` toggling, focus trap, scroll-lock, hashchange/Escape/modal-open close handlers, contextual flyout positioning, keyboard navigation.
- [`public/css/frappe_side_menu.css`](public/css/frappe_side_menu.css) — frosted-glass surface, layout invariants (the `margin-left: 60px` clear-the-trigger rule for `.navbar-breadcrumbs` / `.page-head .page-title`).
- [`hooks.py`](hooks.py) — sets `on_session_creation` for post-login routing; injects the drawer JS/CSS on every desk page.

## Doctypes

- `Side Menu`, `Sub Menu`, `Sub Menu Group` — drawer content tree.
- `Side Menu Settings` (Single) — global config; `Post-Login Landing Route` (field still named `route_logo` for backwards compat) drives the post-login redirect.

## More

See the root [`CLAUDE.md`](../CLAUDE.md) for the v16 modal-event compat shim, the drawer permission-filtering pattern (don't substring-test the SQL fragment; always narrow with `frappe.has_permission`), and the nested-import path quirk inside the Railway container (`frappe_side_menu/frappe_side_menu/frappe_side_menu/api.py`).
