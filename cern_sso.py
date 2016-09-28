import logging
import xml.etree.ElementTree as ET
from future import standard_library
standard_library.install_aliases()
from urllib.parse import urlparse, urljoin

import requests
import requests_kerberos
from requests_kerberos import HTTPKerberosAuth

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def krb_sign_on(url):
    """
    Perform Kerberos-backed single-sign on against a provided
    (protected) URL.

    It is assumed that the current session has a working Kerberos
    ticket.

    Returns a Requests `CookieJar`, which can be accessed as a
    dictionary, but most importantly passed directly into a request or
    session via the `cookies` keyword argument.
    """

    kerberos_auth = HTTPKerberosAuth(mutual_authentication=requests_kerberos.OPTIONAL)

    with requests.Session() as s:

        # Try getting the URL we really want, and get redirected to SSO
        log.info("Fetching URL: %s" % url)
        r1 = s.get(url)

        # Parse out the session keys from the GET arguments:
        redirect_url = urlparse(r1.url)
        log.debug("Was redirected to SSO URL: %s" % str(redirect_url))

        # ...and inject them into the Kerberos authentication URL
        krb_auth_url = "{auth_url}?{parameters}".format(
            auth_url=urljoin(r1.url, u"auth/integrated/"),
            parameters=redirect_url.query)

        # Perform actual Kerberos authentication
        log.info("Performing Kerberos authentication...")
        r2 = s.get(krb_auth_url, auth=kerberos_auth)

        # Did it work? Raise Exception otherwise.
        r2.raise_for_status()

        # Get the contents
        tree = ET.fromstring(r2.content)

        action = tree.findall("body/form")[0].get('action')

        # Unpack the hidden form data fields
        form_data = {elm.get('name'): elm.get('value')
                     for elm in tree.findall("body/form/input")}

        # ...and submit the form (WHY IS THIS STEP EVEN HERE!?)
        log.debug("Performing final authentication POST to %s" % action)
        r3 = s.post(url=action, data=form_data)

        # Did _that_ work?
        r3.raise_for_status()

        # The session cookie jar should now contain the necessary cookies.
        log.debug("Cookie jar now contains: %s" % str(s.cookies))
        return s.cookies.copy()


def cert_sign_on(url, cert_filename):
    pass


if __name__ == '__main__':

    URL = "https://cerntraining.service-now.com"

    logging.getLogger().setLevel(logging.DEBUG)

    cookies = krb_sign_on(URL)

    API_BASE_URL = URL +"/api/now/v1/table/incident?sys_created_by=dbstoragemon"

    DEFAULT_HEADERS = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}

    request = requests.get(API_BASE_URL, headers=DEFAULT_HEADERS,
                           cookies=cookies)

    #print request.status_code
    #print(request.content)
    #print(cookies)
