import json
import os
import zipfile

import frappe
from frappe.utils import get_files_path


@frappe.whitelist(allow_guest=True)
def after_install():
    load_master_data()
    load_default_files()
    load_single_doc()

@frappe.whitelist(allow_guest=True)
def load_default_files():
    source_path = frappe.get_app_path("mrvtools")
    file_path = os.path.join(source_path, "public", "mrv_default_files.zip")
    with zipfile.ZipFile(file_path, 'r') as file_data:
        for file in file_data.infolist():
            if file.is_dir() or file.filename.startswith("__MACOSX/"):
                continue
            filename = os.path.basename(file.filename)
            if filename.startswith("."):
                continue
            origin = get_files_path()
            item_file_path = os.path.join(origin, file.filename)
            # Decouple the on-disk and DB checks. A Railway volume remount (or
            # any other loss of sites/<site>/public/files/) can leave File DB
            # records whose physical file is gone; previously the compound
            # "skip if EITHER exists" guard turned this function into a no-op
            # in exactly the case where recovery was needed.
            payload = None
            if not os.path.exists(item_file_path):
                payload = file_data.read(file.filename)
                os.makedirs(os.path.dirname(item_file_path) or origin, exist_ok=True)
                with open(item_file_path, "wb") as fh:
                    fh.write(payload)
            if not frappe.db.exists("File", {"file_name": filename}):
                file_doc = frappe.new_doc("File")
                file_doc.content = payload if payload is not None else file_data.read(file.filename)
                file_doc.file_name = filename
                file_doc.folder = "Home"
                file_doc.is_private = 0
                file_doc.save(ignore_permissions=True)
                frappe.db.commit()

        return file_path
    
@frappe.whitelist(allow_guest = True)
def load_master_data():
    source_path = frappe.get_app_path("mrvtools")
    doctype_list = [    "Project Objective","Project Key Sector","Project Key Sub Sector",
                        "Project Included In","Project Tracking Master","Mitigation Target GHGs",
                        "NDP Objective Coverage","NDP Coverage","User Permissions",
                        "Mitigation Non GHG mitigation benefits","Master Data Test","Master Data",
                        "SDG Category","Adaptation Category","Disbursement Category","GHG Sector",
                        "GHG Category","GHG Sub Sector","GHG Sub Category",
                        "Energy Fuel Master List","IPPU GWP Master List",
                        "Livestock Emission Factor Master List","Waste Population Master List",
                        "Livestock Population Master List",
                        "Direct and Indirect Managed Soils Master List",
                        "Forest Category Master List","IPPU Emission Factors Master List",
                        "GHG Inventory Report Categories","GHG Inventory Table Name Master List",
                        "GHG Inventory Report Formulas","Role","Custom DocPerm","Web Page",
                        "Notification","Sub Menu Group","Side Menu"
                    ]
    # Per-doctype try/except — a failure on one master must not abort the rest.
    # Previously a single try wrapped the loop and the first throw silently
    # short-circuited every later doctype.
    for i in doctype_list:
        try:
            file_name = i.lower().replace(" ", "_")
            file_path = os.path.join(source_path, "master_data", f"{file_name}.json")
            data = json.load(open(file_path,"r"))
            for j in data:
                if not frappe.db.exists(j.get("doctype"),j.get("name")):
                    doc = frappe.new_doc(j.get("doctype"))
                    doc.update(j)
                    doc.insert(ignore_permissions=True)
                    frappe.db.commit()
        except Exception:
            frappe.db.rollback()
            frappe.log_error(f"load_master_data: {i}", frappe.get_traceback())

@frappe.whitelist(allow_guest = True)
def load_single_doc():
    source_path = frappe.get_app_path("mrvtools")
    doctype_list = ["MrvFrontend","Side Menu Settings","Website Settings","Navbar Settings"]
    # Per-doctype try/except — a failure on one single must not abort the rest.
    # Previously a single try wrapped the loop and a MrvFrontend save failure
    # silently skipped every other reseed (Side Menu Settings, Website
    # Settings, Navbar Settings stayed at their stale sample-DB values).
    for i in doctype_list:
        try:
            file_name = i.lower().replace(" ", "_")
            file_path = os.path.join(source_path, "master_data", f"{file_name}.json")
            data = json.load(open(file_path,"r"))
            for j in data:
                # get_single() is the v16-safe way to load a Single doctype.
                # v15 tolerated frappe.get_doc(doctype) with only the doctype
                # arg; v16 tightens the signature and expects an explicit name.
                doc = frappe.get_single(j.get("doctype"))
                doc.update(j)
                doc.save(ignore_permissions=True)
                frappe.db.commit()
        except Exception:
            frappe.db.rollback()
            frappe.log_error(f"load_single_doc: {i}", frappe.get_traceback())