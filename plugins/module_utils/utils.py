#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import json
import uuid
from cockroachdb_cloud_client.client import AuthenticatedClient
from cockroachdb_cloud_client.types import Response
from dataclasses import dataclass
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_clusters, cockroach_cloud_get_cluster
from cockroachdb_cloud_client.models.cluster import Cluster

API_VERSION = 'latest'
SCHEME = 'https'
HOST = 'cockroachlabs.cloud'
PORT = '443'
PATH = ''
VERIFY_SSL = True
RAISE_ON_UNEXPECTED_STATUS = True
FOLLOW_REDIRECTS = True

@dataclass
class ApiClientArgs():
    cc_key: str
    api_version: str
    scheme: str
    host: str
    port: str
    path: str
    verify_ssl: str
    raise_on_unexpected_status: bool = True
    follow_redirects: bool = True


class AnsibleException(Exception):
    def __init__(self, r: Response):
        super().__init__({'status_code': r.status_code,
                          'content': json.loads(r.content)}
                         )


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
        raise_on_unexpected_status = api_client_args.raise_on_unexpected_status if api_client_args.raise_on_unexpected_status else RAISE_ON_UNEXPECTED_STATUS
        follow_redirects = api_client_args.follow_redirects if api_client_args.follow_redirects else FOLLOW_REDIRECTS

        base_url = "%s://%s:%s%s" % (scheme, host, port, path)

        super().__init__(
            base_url=base_url,
            token=token,
            headers={"cc-version": api_version},
            verify_ssl=verify_ssl,
            timeout=20.0,
            raise_on_unexpected_status=raise_on_unexpected_status,
            follow_redirects=follow_redirects
        )


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


def get_cluster_id(client: APIClient, name: str):
    if is_valid_uuid(name):
        return name
    else:
        r = cockroach_cloud_list_clusters.sync_detailed(
            client=client,
            show_inactive=False)

        if r.status_code == 200 and r.parsed:
            for x in r.parsed.clusters:
                if x.name == name:
                    return x.id
            raise Exception(
                {'content': f'could not fetch cluster details for cluster name: {name}'})
        else:
            raise AnsibleException(r)


def fetch_cluster_by_id_or_name(client: APIClient, name: str) -> Cluster | None:

    if is_valid_uuid(name):
        r = cockroach_cloud_get_cluster.sync_detailed(
            client=client,
            cluster_id=name
        )

        if r.status_code == 200 and r.parsed:
            return r.parsed #json.loads(r.content)
        else:
            raise AnsibleException(r)
    else:
        r = cockroach_cloud_list_clusters.sync_detailed(
            client=client,
            show_inactive=False)

        
        if r.status_code == 200 and r.parsed:
            
            for x in r.parsed.clusters:
                if x.name == name:
                    return x
            
            # clusters = json.loads(r.content)['clusters']
            
            # for x in clusters:
            #     if x['name'] == name:
            #         return x
            # raise Exception(
            #     {'content': f'could not fetch cluster details for cluster name: {name}'})
        else:
            raise AnsibleException(r)
