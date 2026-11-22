
import json
from log import *
from sharepoint_client import SharePointClient
from config_controller import ConfigController
from s3_client import S3Client

class Controller:
    def __init__(self):
        self.sharepoint = SharePointClient()
        self.config_controller = ConfigController()
        self.s3 = S3Client()

    def list_create_rewrite(self, site_name: str, list_name: str, list_guid: str):
        print_log("CONTROLLER", "LIST_CREATE_REWRITE", f"Start to create or rewrite list -> {list_name} in site -> {site_name}")
        default_view: dict[str,str] = self.sharepoint.get_default_view(site_name, list_guid)
        list_data, list_dependencies = self.sharepoint.get_list_via_default_view(site_name, list_guid, default_view)
        self.s3.create_rewrite_list(site_name, list_name, list_data)
        self.config_controller.changes_lists_dependencies(site_name, list_guid, list_dependencies)
        print_success_log("CONTROLLER", "LIST_CREATE_REWRITE", f"Finish to create or rewrite list -> {list_name} in site -> {site_name}")

    def site_add(self, master_site_name: str, site_changed: dict):
        print_log("CONTROLLER", "SITE_ADD", f"Start to add site via config from site -> {master_site_name} with changes (site added) -> {site_changed}")
        new_site_data: dict = json.loads(self.sharepoint.get_value_of_file(master_site_name, site_changed['file_path']).decode("utf-8"))
        lists = self.config_controller.add_config(master_site_name, site_changed['item_id'], new_site_data)
        for name, guid in lists.items():
            self.list_create_rewrite(site_changed['file_name'], name, guid)
        print_success_log("CONTROLLER", "SITE_ADD", f"Finish to add site via config from site -> {master_site_name} with changes (site added) -> {site_changed}")

    def site_update(self, master_site_name, site_changed: dict):
        print_log("CONTROLLER", "SITE_UPDATE", f"Start to update site with name -> {master_site_name} with changes -> {site_changed}")
        updated_site_data: dict = json.loads(self.sharepoint.get_value_of_file(master_site_name, site_changed["file_path"]).decode("utf-8"))
        get_changes = self.config_controller.get_changes(site_changed["file_name"], updated_site_data)
        print_log("CONTROLLER", "SITE_UPDATE", f"Changes for site -> {master_site_name} the changes -> {get_changes}")
        for name, guid in get_changes["lists"].items():
            self.list_create_rewrite(site_changed['file_name'], name, guid)
        for name in get_changes["deleted_lists"]:
            self.s3.delete_list(site_changed['file_name'], name)
        self.config_controller.rewrite_from_temp(site_changed["file_name"])
        print_success_log("CONTROLLER", "SITE_UPDATE", f"Finish to update site with name -> {master_site_name} with changes -> {site_changed}")

     