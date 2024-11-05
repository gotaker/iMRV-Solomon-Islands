import frappe,json
import os
import zipfile
import shutil
from urllib.request import urlopen
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
            if not os.path.exists(item_file_path) and not frappe.db.exists("File", {"file_name": filename}):
                file_doc = frappe.new_doc("File")
                file_doc.content = file_data.read(file.filename)
                file_doc.file_name = filename
                file_doc.folder = "Home"
                file_doc.is_private = 0
                file_doc.save(ignore_permissions = True)
                frappe.db.commit()

        return file_path
    
@frappe.whitelist(allow_guest = True)
def load_master_data():
    try:
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
        for i in doctype_list:
            file_name = i.lower().replace(" ", "_")
            file_path = os.path.join(source_path, "master_data", f"{file_name}.json")
            data = json.load(open(file_path,"r"))
            for j in data:
                if not frappe.db.exists(j.get("doctype"),j.get("name")):
                    doc = frappe.new_doc(j.get("doctype"))
                    doc.update(j)
                    doc.insert(ignore_permissions=True)
                    
                    frappe.db.commit()
    except:
        frappe.log_error("Error While insterting Data",frappe.get_traceback())

@frappe.whitelist(allow_guest = True)
def load_single_doc():
    try:
        source_path = frappe.get_app_path("mrvtools")
        doctype_list = ["MrvFrontend","Side Menu Settings","Website Settings","Navbar Settings"]
        for i in doctype_list:
            file_name = i.lower().replace(" ", "_")
            file_path = os.path.join(source_path, "master_data", f"{file_name}.json")
            data = json.load(open(file_path,"r"))
            for j in data:
                doc = frappe.get_doc(j.get("doctype"))
                doc.update(j)
                doc.save(ignore_permissions=True)
                frappe.db.commit()
    except:
        frappe.log_error("Error While insterting Data",frappe.get_traceback())