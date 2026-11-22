
import sys

from datetime import datetime

def print_log(class_name: str, method_name: str, text: str):
    print(f"{datetime.now()} [WORKER] -- CLASS -> [{class_name}] -- METHOD -> [{method_name}] -- \033[33mWARNING: {text}\033[0m", file=sys.stderr, flush=True)

def print_start_log(class_name: str, method_name: str, text: str) -> None:
    print(f"{datetime.now()} [WORKER] -- CLASS -> [{class_name}] -- METHOD -> [{method_name}] -- \033[34mSTART: {text}\033[0m", file=sys.stderr, flush=True)

def print_success_log(class_name: str, method_name: str, text: str):
    print(f"{datetime.now()} [WORKER] -- CLASS -> [{class_name}] -- METHOD -> [{method_name}] -- \033[32mSUCCESS: {text}\033[0m", file=sys.stderr, flush=True)

def print_error_log(class_name: str, method_name: str, text: str):
    print(f"{datetime.now()} [WORKER] -- CLASS -> [{class_name}] -- METHOD -> [{method_name}] -- \033[31mERROR: {text}\033[0m", file=sys.stderr, flush=True)
