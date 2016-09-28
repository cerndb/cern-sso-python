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


def _init_session(s, url, cookiejar, auth_url_fragment):
    """
    Internal helper function: initialise the sesion by trying to access
    a given URL, setting up cookies etc.


    :param: auth_url_fragment: a URL fragment which will be joined to
    the base URL after the redirect, before the parameters. Examples are
    auth/integrated/ (kerberos) and auth/sslclient/ (SSL)
    """

    s.cookies = cookiejar

    # Try getting the URL we really want, and get redirected to SSO
    log.info("Fetching URL: %s" % url)
    r1 = s.get(url)

    # Parse out the session keys from the GET arguments:
    redirect_url = urlparse(r1.url)
    log.debug("Was redirected to SSO URL: %s" % str(redirect_url))

    # ...and inject them into the Kerberos authentication URL
    final_auth_url = "{auth_url}?{parameters}".format(
        auth_url=urljoin(r1.url, auth_url_fragment),
        parameters=redirect_url.query)

    return final_auth_url


def _finalise_login(s, auth_results):
    """
    Perform the final POST authentication steps to fully authenticate
    the session, saving any cookies in s' cookie jar.
    """

    r2 = auth_results

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

    return s.cookies


def krb_sign_on(url, cookiejar={}):
    """
    Perform Kerberos-backed single-sign on against a provided
    (protected) URL.

    It is assumed that the current session has a working Kerberos
    ticket.

    Returns a Requests `CookieJar`, which can be accessed as a
    dictionary, but most importantly passed directly into a request or
    session via the `cookies` keyword argument.

    If a cookiejar-like object (such as a dictionary) is passed as the
    cookiejar keword argument, this is passed on to the Session.
    """

    kerberos_auth = HTTPKerberosAuth(mutual_authentication=requests_kerberos.OPTIONAL)

    with requests.Session() as s:

        krb_auth_url = _init_session(s=s, url=url, cookiejar=cookiejar,
                                     auth_url_fragment=u"auth/integrated/")

        # Perform actual Kerberos authentication
        log.info("Performing Kerberos authentication against %s" % krb_auth_url)
        r2 = s.get(krb_auth_url, auth=kerberos_auth)

        return _finalise_login(s, auth_results=r2)


def cert_sign_on(url, cert_file, key_file, cookiejar={}):

    with requests.Session() as s:

        # Set up the certificates (this needs to be done _before_ any
        # connection is opened!)
        s.cert = (cert_file, key_file)

        cert_auth_url = _init_session(s=s, url=url, cookiejar=cookiejar,
                                      auth_url_fragment=u"auth/sslclient/")

        log.info("Performing SSL Cert authentication against %s" % cert_auth_url)
        r2 = s.get(cert_auth_url, cookies=cookiejar, verify=False)

        return _finalise_login(s, auth_results=r2)
