
import os
import sys
import json
import argparse
import traceback

from log import *
from controller import Controller
from read_env import ReadEnv

def main() -> int:
    print_start_log("main", "main", f"WORKER STARTED")
    parser = argparse.ArgumentParser()
    parser.add_argument("--site_name", required=True, type=str)
    parser.add_argument("--guid_dict", type=str, help="JSON with lib of guid")
    parser.add_argument("--files", type=str, help="JSON with list of files") 
    parser.add_argument("--operation", choices=["update"], default=None)
    args = parser.parse_args()
    try:
        site_name: str = args.site_name
        controller = Controller()
        read_env = ReadEnv()
        guid_dict = (json.loads(args.guid_dict) if args.guid_dict is not None else None)
        files = (json.loads(args.files) if args.files is not None else None)
        operation: str | None = args.operation
        if files:
            for file in files:
                if file["change_type"] == 1:
                    print_start_log("main", "main", f"Start worker to add new site in local storage")
                    controller.site_add(read_env.master_site_name, file)
                elif file["change_type"] == 2:
                    print_start_log("main", "main", f"Start worker to upgrage exists site in local storage")
                    controller.site_update(read_env.master_site_name, file)

        if guid_dict:
            print_start_log("main", "main", f"Start update in site {site_name}")
            for name, guid in guid_dict.items():
                print_log("main", "main", f"Start to update list with guid {guid} in site {site_name}")
                controller.list_create_rewrite(site_name, name, guid)
        result: dict = {
            "pid" : os.getpid(),
            "site_name" : site_name,
            "status" : "SUCCESS",
            "message" : "Worker  completed successfully"
        }
        print(json.dumps(result, ensure_ascii=False), flush = True)
        sys.exit(0)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        result: dict = {
            "pid" : os.getpid(),
            "site_name" : site_name,
            "status" : "FAILED",
            "message" : str(e)
        }
        print(json.dumps(result, ensure_ascii=False), flush=True)
        sys.exit(1)


if __name__=="__main__":
    main()
