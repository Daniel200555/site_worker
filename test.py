
import json
from log import *
from s3_client import S3Client
from sharepoint_client import SharePointClient
from controller import Controller

controller = Controller()
sharepoint = SharePointClient()
s3 = S3Client()

# controller.list_update("MarpeArava_NP", {"לקוחות":"93f43064-d6e1-4401-ba01-a28038a3129c", "Stations":"ac74f6be-8a42-4067-8cac-95f43c8f137a"})
# controller.list_update("MarpeArava_NP", {"Stations":"ac74f6be-8a42-4067-8cac-95f43c8f137a"})
print(json.dumps(s3.get_file("MarpeArava_NP/Personnel.json"), ensure_ascii=False, indent=4))
# print(controller.get_list_data("MarpeArava_NP", "PC", controller.list_update("MarpeArava_NP", {"PC":"b1349be6-0ad0-4d8a-a99c-62fc00e4ece1"})))
# print(json.dumps(sharepoint.get_default_view("MarpeArava_NP", "b1349be6-0ad0-4d8a-a99c-62fc00e4ece1"), ensure_ascii=False, indent=4))
# print(json.dumps(sharepoint.get_list_via_default_view("MarpeArava_NP", "PC", "b1349be6-0ad0-4d8a-a99c-62fc00e4ece1", sharepoint.get_default_view("MarpeArava_NP", "b1349be6-0ad0-4d8a-a99c-62fc00e4ece1")), ensure_ascii=False, indent=4))
# print(controller.list_update("MarpeArava_NP", {"PC" : "b1349be6-0ad0-4d8a-a99c-62fc00e4ece1"}))
# print(json.dumps(sharepoint.get_list_tree("MarpeArava_NP", "PC", "b1349be6-0ad0-4d8a-a99c-62fc00e4ece1"), ensure_ascii=False, indent=4))
# print_success_log("EXAMPLE text")