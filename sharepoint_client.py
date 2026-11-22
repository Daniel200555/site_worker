
import requests
from log import *
from read_env import ReadEnv

class SharePointClient:

    def __init__(self):
        self.env = ReadEnv()
        self.headers = {"Accept": "application/json;odata=verbose"}

    def get_current_change_token(self, site_name: str) -> str:
        print_log(self.__class__.__name__, self.get_current_change_token.__name__, f"Start getting current change token for site -> {site_name}")
        url: str = f"http://{self.env.sharepoint_host}/sites/{site_name}/_api/web/CurrentChangeToken"
        try: 
            response = requests.get(url=url, headers=self.headers, timeout=30)
            result = response.json()["d"]["CurrentChangeToken"]["StringValue"]
            print_success_log(self.__class__.__name__, self.get_current_change_token.__name__, f"Success to get response with token via url -> {url}, \n  result is -> {result}")
            return result
        except requests.Timeout as e:
            print_error_log(self.__class__.__name__, self.get_current_change_token.__name__, f"Timeout ERROR in get_current_change_token method for site: {site_name} with exception: {e}")
            raise
        except requests.RequestException as e:
            print_error_log(self.__class__.__name__, self.get_current_change_token.__name__, f"Request Exception ERROR in get_current_change_token method for site: {site_name} with exception: {e}")
            raise
        except (ValueError, KeyError) as e:
            print_error_log(self.__class__.__name__, self.get_current_change_token.__name__, f"Invalid response in get_current_change_token method for site: {site_name} with exception: {e}")
            raise

    def get_list_guid(self, site_name: str, lists_name: list[str]) -> dict[str, str]:
        print_log(self.__class__.__name__, self.get_list_guid.__name__, f"Start to get guid for lists -> {lists_name} in site -> {site_name}")
        url: str = f"http://{self.env.sharepoint_host}/sites/{site_name}/_api/web/lists?$select=Id,Title"
        try:
            response = requests.get(url=url, headers=self.headers, timeout=30)
            result: dict[str, str] = {}
            for data in response.json()['d']['results']:
                if data['Title'] in lists_name:
                    result[data['Title']] = data['Id']
            print_success_log(self.__class__.__name__, self.get_list_guid.__name__, f"Success to get list of guids via url -> {url}, \n result is -> {result}")
            return result
        except requests.Timeout as e:
            print_error_log(self.__class__.__name__, self.get_list_guid.__name__, f"Timeout ERROR in get_list_guid method for site: {site_name} with exception: {e}")
            raise
        except requests.RequestException as e:
            print_error_log(self.__class__.__name__, self.get_list_guid.__name__, f"Request Exception ERROR in get_list_guid method for site: {site_name} with exception: {e}")
            raise
        except (ValueError, KeyError) as e:
            print_error_log(self.__class__.__name__, self.get_list_guid.__name__, f"Invalid response in get_list_guid method for site: {site_name} with exception: {e}")
            raise

    def get_default_view(self, site_name: str, list_guid: str) -> dict:
        print_log(self.__class__.__name__, self.get_default_view.__name__, f"Start get default view of list -> {list_guid} in site -> {site_name}")
        url_default_view: str = f"http://{self.env.sharepoint_host}/sites/{site_name}/_api/web/lists('{list_guid}')/DefaultView/ViewFields"
        try: 
            response = requests.get(url_default_view, headers=self.headers, timeout=30)
            result =  response.json()['d']['Items']['results']
            default_columns: list[str] = [f"OData_{field}"if field.startswith("_x") else field for field in result]
            print_log(self.__class__.__name__, self.get_default_view.__name__, f"Default columns for list -> {list_guid} in site -> {site_name} is getted via url -> {url_default_view}, result -> {default_columns}")
            default_view_filter: str = " or ".join(f"EntityPropertyName eq '{column}'" for column in default_columns)
            print_log(self.__class__.__name__, self.get_default_view.__name__, f"Build default view filter for list -> {list_guid} in site -> {site_name} for use sharepoint api, result -> {default_view_filter}")
            url_fields: str = f"http://{self.env.sharepoint_host}/sites/{site_name}/_api/web/lists('{list_guid}')/fields?$filter={default_view_filter}&$select=EntityPropertyName,Title,TypeAsString,LookupList"
            print_log(self.__class__.__name__, self.get_default_view.__name__, f"Get final result of default view for list -> {list_guid} in site -> {site_name}")
            response = requests.get(url_fields, headers=self.headers, timeout=30)
            fields = response.json()['d']['results']
            field_titles = {
                field["EntityPropertyName"]: {"Title" : field["Title"] ,"EntityPropertyName" : f"{field["EntityPropertyName"]}Id" if field['TypeAsString'] == "Lookup" else field["EntityPropertyName"] , "GUID" : field["LookupList"].strip("{}") if field['TypeAsString'] == "Lookup" else None}
                for field in fields
            }
            ret =  {
                column : field_titles[column]
                for column in default_columns
                if column in field_titles
            }
            print_success_log(self.__class__.__name__, self.get_default_view.__name__, f"Final result of default view getted successfully for list -> {list_guid} in site -> {site_name} via url -> {url_fields}, \n result is -> {ret}")
            return ret
        except requests.Timeout as e:
            print_error_log(self.__class__.__name__, self.get_default_view.__name__, f"Timeout ERROR in get_default_view method for site: {site_name} with exception: {e}")
            raise
        except requests.RequestException as e:
            print_error_log(self.__class__.__name__, self.get_default_view.__name__, f"Request Exception ERROR in get_default_view method for site: {site_name} with exception: {e}")
            raise
        except (ValueError, KeyError) as e:
            print_error_log(self.__class__.__name__, self.get_default_view.__name__, f"Invalid response in get_default_view method for site: {site_name} with exception: {e}")
            raise

    def get_list_tree(self, site_name: str, guid: str, visited: set[str] | None = None, default_views: dict[str, dict] | None = None) -> list[str]:
        if visited is None:
            visited = set()
        if default_views is None:
            default_views = {}
        if guid in visited:
            return []
        visited.add(guid)
        default_view = default_views.get(guid)
        if default_view is None:
            default_view = self.get_default_view(site_name, guid)
            default_views[guid] = default_view
        inner_lists = set()
        for field_data in default_view.values():
            lookup_guid = field_data.get("GUID")
            if not lookup_guid or lookup_guid in visited:
                continue
            inner_lists.add(lookup_guid)
            nested_lists = self.get_list_tree(
                site_name=site_name,
                guid=lookup_guid,
                visited=visited,
                default_views=default_views
            )
            inner_lists.update(nested_lists)
        return list(inner_lists)

    def _get_list_items_expanded(self, site_name: str, list_guid: str, default_view_list: dict, item_ids: set[int] | None = None, visited: set[str] | None = None, default_views: dict[str, dict] | None = None):
        print_log(self.__class__.__name__, self._get_list_items_expanded.__name__, f"Start get values for list -> {list_guid} in site -> {site_name} with default view -> {default_view_list}")
        if visited is None:
            visited = set()
        if default_views is None:
            default_views = {}
        default_views[list_guid] = default_view_list
        url: str = f"http://{self.env.sharepoint_host}/sites/{site_name}/_api/web/lists('{list_guid}')/items"
        select_fields = {"Id", *(field["EntityPropertyName"] for field in default_view_list.values())}
        params = {"$select": ",".join(select_fields)}
        if item_ids is not None:
            if not item_ids:
                return {}
            params["$filter"] = " or ".join(f"Id eq {item_id}" for item_id in item_ids)
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            items = response.json()['d']['results']
            result = {
                item["Id"] : {
                    field["Title"] : item[field["EntityPropertyName"]]
                    for field in default_view_list.values()
                    if field["EntityPropertyName"] in item
                }
                for item in items
            }
            lookup_fields = {
                column : field
                for column, field in default_view_list.items()
                if field["GUID"] is not None
            }
            if not lookup_fields:
                return result
            for column, field in lookup_fields.items():
                lookup_guid = field["GUID"]
                if lookup_guid in visited:
                    continue
                lookup_ids = {
                    item[field["EntityPropertyName"]]
                    for item in items
                    if item.get(field["EntityPropertyName"]) is not None
                }
                if not lookup_ids:
                    continue
                lookup_default_view = default_views.get(lookup_guid)
                if lookup_default_view is None:
                    lookup_default_view = self.get_default_view(site_name, lookup_guid)
                    default_views[lookup_guid] = lookup_default_view
                lookup_items = self._get_list_items_expanded(site_name, lookup_guid, lookup_default_view, lookup_ids, visited | {list_guid}, default_views=default_views)
                for item in items:
                    item_id = item["Id"]
                    lookup_id = item.get(field["EntityPropertyName"])
                    if lookup_id is not None:
                        result[item_id][field["Title"]] = lookup_items.get(lookup_id)
            return result
        except requests.Timeout as e:
            print_error_log(self.__class__.__name__, self._get_list_items_expanded.__name__, f"Timeout ERROR in _get_list_items_expanded: {e}")
            raise
        except requests.RequestException as e:
            print_error_log(self.__class__.__name__, self._get_list_items_expanded.__name__, f"Request ERROR in _get_list_items_expanded: {e}")
            raise
        except (ValueError, KeyError) as e:
            print_error_log(self.__class__.__name__, self._get_list_items_expanded.__name__, f"Invalid response in _get_list_items_expanded: {e}")
            raise

    def get_list_via_default_view(self, site_name: str, list_guid: str, default_view_list: dict):
        default_views = {list_guid: default_view_list}
        list_dependencies: list[str] = self.get_list_tree(site_name=site_name, guid=list_guid, default_views=default_views)
        result = self._get_list_items_expanded(site_name=site_name, list_guid=list_guid, default_view_list=default_views[list_guid], default_views=default_views)
        return list(result.values()), list_dependencies

    def get_value_of_file(self, site_name: str, relative_url: str) -> bytes:
        print_log(self.__class__.__name__, self.get_value_of_file.__name__, f"Start to get content of file with relative url -> {relative_url} in site -> {site_name}")
        url: str = f"http://{self.env.sharepoint_host}/sites/{site_name}/_api/web/getFileByServerRelativeUrl('{relative_url}')/$value"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            print_success_log(self.__class__.__name__, self.get_value_of_file.__name__, f"Success to get content of file via url -> {url}")
            return response.content
        except requests.Timeout as e:
            print_error_log(self.__class__.__name__, self.get_value_of_file.__name__, f"Timeout Exception in get_list_guid method for site: {site_name} with exception: {e}")
            raise
        except requests.RequestException as e:
            print_error_log(self.__class__.__name__, self.get_value_of_file.__name__, f"Request Exception in get_list_guid method for site: {site_name} with exception: {e}")
            raise
        except (ValueError, KeyError) as e:
            print_error_log(self.__class__.__name__, self.get_value_of_file.__name__, f"Invalid response in get_list_guid method for site: {site_name} with exception: {e}")
            raise