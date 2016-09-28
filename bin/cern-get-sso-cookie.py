#!/usr/bin/env python2.7

import logging
from cookielib import MozillaCookieJar

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

    cookiejar.save(ignore_discard=True, ignore_expires=True)
