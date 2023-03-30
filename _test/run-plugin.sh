#!/bin/bash

pytest --output-polarion-testcase=data/export_testcase.xml --output-polarion-testrun=data/export_testrun.xml --polarion-config=polarion.yaml -vvv

