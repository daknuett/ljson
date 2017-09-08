#!/bin/bash


# This requires .codacy-coverage-key.sh to contain the 
# necessary content to eport the API key for codacy:
#
#	export CODACY_PROJECT_TOKEN="..."
#
source .codacy-coverage-key.sh

py.test --cov=ljson --cov-report=xml:coverage.xml 

python-codacy-coverage -r coverage.xml
