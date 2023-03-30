#!/bin/bash

betelgeuse test-case --response-property property_key=property_value --automation-script-format "https://github.com/SSSD/sssd/tree/master/{path}#L{line_number}" tests RHEL_IDM data/betelgeuse-test-cases.xml
pytest -vvv --junit-xml=data/junit.xml
betelgeuse test-run --response-property property_key=property_value data/junit.xml tests idm-jenkins RHEL_IDM data/betelgeuse-test-run.xml
