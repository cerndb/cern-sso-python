#!/usr/bin/env python2.7
import cern_sso

import logging
from six.moves.http_cookiejar import MozillaCookieJar
import time
from argparse import ArgumentParser

CERN_SSO_COOKIE_LIFETIME_S = 24*60*60

APP_DESCRIPTION = ("")

__version__ = '1.2.2'

if __name__ == '__main__':

    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(levelname)-4s  %(name)-4s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    arg_parser = ArgumentParser(description=APP_DESCRIPTION)

    arg_parser.add_argument('-o', '--output', dest='cookie_filename',
                            metavar='cookies.txt', type=str,
                            default='cookies.txt',
                            help=('path to where the cookies should'
                                  ' be stored. Default is cookies.txt.'))

    arg_parser.add_argument('-u', '--url', dest='url',
                            metavar='url', type=str,
                            default='url',
                            required=True,
                            help='the desired URL to authenticate to.')

    verbosity_group = arg_parser.add_mutually_exclusive_group()

    verbosity_group.add_argument('-v', '--verbose', dest='verbose',
                                 action='store_true')

    verbosity_group.add_argument('-d', '--debug', dest='debug',
                                 action='store_true')

    auth_method_group = arg_parser.add_mutually_exclusive_group(required=True)

    auth_method_group.add_argument('-k', '--kerberos', dest='kerberos',
                                   action='store_true',
                                   help='use Kerberos authentication')

    auth_method_group.add_argument('-c', '--cert', dest='cert',
                                   metavar='myCertificate',
                                   type=str,
                                   help=("use Robot (SSL) certificate"
                                         " authentication with this name/path."
                                         " The program will assume that the"
                                         " certificate is in myCertificate.pem"
                                         " and a passwordless key is in"
                                         " myCertificate.key"))

    arg_parser.add_argument('-V', '--version',
                            action='version',
                            version=__version__)

    args = arg_parser.parse_args()

    # DEBUG takes presedence over VERBOSE:
    if args.debug:
        logger.setLevel(logging.DEBUG)

    elif args.verbose:
        logger.setLevel(logging.INFO)

    cookie_filename = args.cookie_filename

    target_url = args.url

    cookiejar = MozillaCookieJar(cookie_filename)

    if args.kerberos:
        cern_sso.krb_sign_on(target_url, cookiejar=cookiejar)
    elif args.cert:
        cert_file = "%s.pem" % args.cert
        key_file = "%s.key" % args.cert

        logger.info("Using SSL certificate file %s and key %s"
                    % (cert_file, key_file))

        cern_sso.cert_sign_on(target_url,
                              cert_file=cert_file,
                              key_file=key_file,
                              cookiejar=cookiejar)
    else:
        assert False, "Either kerberos or cert should ALWAYS be true!"

    if not cookiejar:
        print("Error: the returned cookie jar from the login rain dance"
              " was empty. Either you were not authorised to access"
              " the resourse, or something else went wrong."
              " Sorry, these things are a bit flaky.")
        exit(1)

    # Rewrite cookies to have different session properties
    logger.info("Rewriting cookie expiration dates...")
    for cookie in cookiejar:
        old_expires = cookie.expires

        cookie.expires = int(time.time() + CERN_SSO_COOKIE_LIFETIME_S)
        logger.debug(("Updating expiry date for cookie {name}. Old date was:"
                      " {old_timestamp}, new is"
                      " {new_timestamp}").format(name=cookie.name,
                                                 old_timestamp=old_expires,
                                                 new_timestamp=cookie.expires))

        # This session cookie is not a session cookie. Definitely not.
        cookie.discard = False

    # Write to disk
    cookiejar.save()

    logger.info("Successfully stored cookies in %s" % cookie_filename)
