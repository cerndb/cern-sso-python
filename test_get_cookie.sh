#!/bin/sh

set -eu

cern-get-sso-cookie.py --help
cern-get-sso-cookie.py --kerberos --verbose --url https://dbnas-storage-docs.web.cern.ch
grep -q "dbnas-storage-docs.web.cern.ch" cookies.txt
