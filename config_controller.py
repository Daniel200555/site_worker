
import os
import json

from log import *
from pathlib import Path
from sharepoint_client import SharePointClient
from read_env import ReadEnv

class ConfigController:
    def __init__(self):
        self.env = ReadEnv()
        self.sharepoint = SharePointClient()
        self.path = self.env.local_state_path

    def add_config(self, site_name: str, item_id: int, site_data: dict) -> dict:
        path: Path = Path(f"{self.path}\{site_name}.json")
        print_log(self.__class__.__name__, self.add_config.__name__, f"Start to add new config for new site -> {site_name}")
        site_data["item_id"] = item_id
        site_data["site_token"] = self.sharepoint.get_current_change_token(site_name)
        site_data["lists"] = self.sharepoint.get_list_guid(site_name, site_data["lists"])
        site_data.setdefault("lists_dependencies", {})
        print_log(self.__class__.__name__, self.add_config.__name__, f"Finish to set data for new local config for site -> {site_name}")
        with open(path, "w", encoding="utf-8") as file:
            json.dump(site_data, file, ensure_ascii=False, indent=4)
        print_success_log(self.__class__.__name__, self.add_config.__name__, f"Finish of write data for new config for site -> {site_name}")
        return site_data["lists"]


    def rewrite_config(self, site_name: str, new_data: dict) -> None:
        path: Path = Path(f"{self.path}\{site_name}.json")
        print_log(self.__class__.__name__, self.rewrite_config.__name__, f"Start to rewrite local config for site -> {site_name}")
        with open(path, "r", encoding="utf-8") as file:
            old_data: dict = json.load(file)
        old_data["lists"].update(new_data.get("lists", {}))
        print_log(self.__class__.__name__, self.rewrite_config.__name__, f"Finish to set new data for local config for site -> {site_name}")
        with open(path, "w", encoding="utf-8") as file:
            json.dump(old_data, file, ensure_ascii=False, indent=4)
        print_success_log(self.__class__.__name__, self.rewrite_config.__name__, f"Rewrite config is finished successfully for site -> {site_name}")

    def get_changes(self, site_name: str, new_data: dict) :
        path: Path = Path(f"{self.path}\{site_name}.json")
        print_log(self.__class__.__name__, self.get_changes.__name__, f"Start get changes in site -> {site_name}")
        with open(path, "r", encoding="utf-8") as file:
            old_data: dict = json.load(file)
        print_log(self.__class__.__name__, self.get_changes.__name__, f"Data getted from local storage for site -> {site_name}")
        old_lists = old_data.get("lists", {})
        incoming_lists = new_data.get("lists", {})
        old_names = set(old_lists)
        new_names = set(incoming_lists)
        added_lists = new_names - old_names
        deleted_lists = old_names - new_names
        updated_lists = {name: old_lists[name] for name in new_names if name in old_lists}
        missing_guid = [name for name in added_lists if incoming_lists[name] is None]
        print_log(self.__class__.__name__, self.get_changes.__name__, f"Detect changes for site -> {site_name}")
        new_guids = {}
        if missing_guid:
            new_guids = self.sharepoint.get_list_guid(site_name,list(missing_guid))
        for name in added_lists:
            updated_lists[name] = new_guids.get(name,incoming_lists[name])
        old_dependencies = old_data.get("lists_dependencies", {})
        for name in deleted_lists:
            old_dependencies.pop(name, None)
        old_data["lists"] = updated_lists
        old_data["lists_dependencies"] = old_dependencies
        self.write_to_temp_config(site_name, old_data)
        result: dict = {
            "lists": {
                name: updated_lists[name]
                for name in added_lists
            },
            "deleted_lists": list(deleted_lists),
            "libs": {}
        }
        print_success_log(self.__class__.__name__, self.get_changes.__name__, f"Changes is detected for site -> {site_name}, \nchanges is {result}")
        return result

    def changes_lists_dependencies(self, site_name: str, list_guid: str, list_dependencies: list[str] | None = None) -> None:
        path_local: Path = Path(f"{self.path}\{site_name}.json")
        path_temp: Path = Path(f"{self.path}\{site_name}.tmp.json")
        path: Path = (path_temp if path_temp.exists() else path_local)
        print_log(self.__class__.__name__, self.changes_lists_dependencies.__name__, f"Start change dependencies for list -> {list_guid} in site -> {site_name}")
        with open(path, "r", encoding="utf-8") as file:
            data: dict = json.load(file)
        print_log(self.__class__.__name__, self.changes_lists_dependencies.__name__, f"Get data from local storage for site -> {site_name}")
        list_name: str = next((name for name, guid in data["lists"].items() if guid == list_guid), None)
        if list_name is None:
            raise ValueError(f"List GUID {list_guid} not found")
        data["lists_dependencies"][f"{list_name}"] = (None if list_dependencies is None else list_dependencies)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print_success_log(self.__class__.__name__, self.changes_lists_dependencies.__name__, f"Dependencies changed for list -> {list_guid} in site -> {site_name}")

    def write_to_temp_config(self, site_name: str, new_data: dict) -> None:
        path_temp: Path = Path(f"{self.path}\{site_name}.tmp.json")
        print_log(self.__class__.__name__, self.write_to_temp_config.__name__, f"Start write new data for site -> {site_name} to temp config file with path -> {path_temp}")
        with path_temp.open("w", encoding="utf-8") as file:
            json.dump(new_data, file, ensure_ascii=False, indent=4)
            file.flush()
            os.fsync(file.fileno())
        print_success_log(self.__class__.__name__, self.write_to_temp_config.__name__, f"Finish to write new data for site -> {site_name} to temp config with path -> {path_temp}")

    def rewrite_from_temp(self, site_name: str):
        path: Path = Path(f"{self.path}\{site_name}.json")
        path_temp: Path = Path(f"{self.path}\{site_name}.tmp.json")
        print_log(self.__class__.__name__, self.rewrite_from_temp.__name__, f"Start to rewrite from temp config with path -> {path_temp} to orginal config with path -> {path} for site -> {site_name}")
        with path_temp.open("r", encoding="utf-8") as file:
            json.load(file)
        os.replace(path_temp, path)
        print_success_log(self.__class__.__name__, self.rewrite_from_temp.__name__, f"Finish to rewrite from temp config with path -> {path_temp} to orginal config with path -> {path} for site -> {site_name}")
