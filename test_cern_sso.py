import cern_sso
import requests

TEST_URL = "https://dbnas-storage-docs.web.cern.ch"


def test_do_nothing():
    pass


def test_krb_signin():
    cookies = cern_sso.krb_sign_on(TEST_URL)

    r1 = requests.get(TEST_URL, cookies=cookies)
    assert r1.status_code == 200
