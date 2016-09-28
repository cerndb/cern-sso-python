#!/usr/bin/env python2.7

import logging
from cookielib import MozillaCookieJar
import time

import cern_sso

import requests

if __name__ == '__main__':
    # logger = logging.getLogger()
    # handler = logging.StreamHandler()
    # formatter = logging.Formatter(
    #     '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)
    # logger.setLevel(logging.INFO)

    URL = "https://cerntraining.service-now.com"

    cookiejar = MozillaCookieJar("cookies.txt")
    cookies = cern_sso.krb_sign_on(URL, cookiejar=cookiejar)

    API_BASE_URL = URL +"/api/now/v1/table/incident?sys_created_by=dbstoragemon"

    DEFAULT_HEADERS = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

    CERN_SSO_COOKIE_LIFETIME = 86400

    # Rewrite cookies to have different session properties
    for cookie in cookiejar:

        cookie.expires = int(time.time() + CERN_SSO_COOKIE_LIFETIME)

        # This session cookie is not a session cookie. Definitely not.
        cookie.discard = False

    # Write to disk
    cookiejar.save()
