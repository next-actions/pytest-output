#!/usr/bin/python3

from __future__ import annotations

import sys
from pathlib import Path

import requests

testcase = sys.argv[1]
testrun = sys.argv[2]
url = sys.argv[3]

print(testcase)
print(testrun)
print(url)

response = requests.post(
    f"{url}/polarion/import/testcase",
    files={"file": (testcase, Path(testcase).open("rb"))},
    verify=False,
    auth=("idm-jenkins", "idm-jenkins"),
)
print(response.text)

response = requests.post(
    f"{url}/polarion/import/xunit",
    files={"file": (testrun, Path(testrun).open("rb"))},
    verify=False,
    auth=("idm-jenkins", "idm-jenkins"),
)
print(response.text)
