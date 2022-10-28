#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
from cockroachdb_cloud_client.client import AuthenticatedClient
from dataclasses import dataclass

API_VERSION = 'latest'
SCHEME = 'https'
HOST = 'cockroachlabs.cloud'
PORT = '443'
PATH = ''
VERIFY_SSL = True
    
    

@dataclass
class ApiClientArgs():
    cc_key: str
    api_version: str
    scheme: str
    host: str
    port: str
    path: str
    verify_ssl: str


class APIClient(AuthenticatedClient):

    def __init__(self, api_client_args: ApiClientArgs):

        token = api_client_args.cc_key
        if not token:
            if 'CC_KEY' in os.environ:
                token = os.environ['CC_KEY']
            else:
                raise ValueError(
                    'CC_KEY not provided or not exported as environment variable.')

        api_version = api_client_args.api_version if api_client_args.api_version else API_VERSION
        scheme = api_client_args.scheme if api_client_args.scheme else SCHEME
        host = api_client_args.host if api_client_args.host else HOST
        port = api_client_args.port if api_client_args.port else PORT
        path = api_client_args.path if api_client_args.path else PATH
        verify_ssl = api_client_args.verify_ssl if api_client_args.verify_ssl else VERIFY_SSL

        base_url = "%s://%s:%s%s" % (scheme, host, port, path)

        super().__init__(
            base_url=base_url,
            token=token,
            headers={"cc-version": api_version},
            verify_ssl=verify_ssl,
            timeout=20.0
        )
