#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import json
import uuid
from cockroachdb_cloud_client.client import AuthenticatedClient
from cockroachdb_cloud_client.types import Response
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_clusters, cockroach_cloud_get_cluster
from cockroachdb_cloud_client.models.cluster import Cluster

class AnsibleException(Exception):
    def __init__(self, r: Response):
        super().__init__(
            {'status_code': r.status_code,
            'content': json.loads(r.content)}
        )


class APIClient(AuthenticatedClient):

    def __init__(
        self,
        cc_key: str | None = None,
        api_version: str = '2023-04-10',
        scheme: str = 'https',
        host: str = 'cockroachlabs.cloud',
        port: str = '443',
        path: str = '',
        verify_ssl: bool = True,
        raise_on_unexpected_status: bool = True,
        follow_redirects: bool = True
        ):

        token = cc_key
        if not token:
            if 'CC_KEY' in os.environ:
                token = os.environ['CC_KEY']
            else:
                raise ValueError(
                    'CC_KEY not provided or not exported as environment variable.')

        base_url = "%s://%s:%s%s" % (scheme, host, port, path)

        super().__init__(
            base_url=base_url,
            token=token,
            headers={"cc-version": api_version},
            verify_ssl=verify_ssl,
            timeout=30.0,
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


def fetch_cluster_by_id_or_name(client: APIClient, name: str):

    if is_valid_uuid(name):
        r = cockroach_cloud_get_cluster.sync_detailed(
            client=client,
            cluster_id=name
        )

        if r.status_code == 200 and r.parsed:
            return r.parsed 
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
            
            raise Exception(
                {'content': f'could not fetch cluster details for cluster name: {name}'})
        else:
            raise AnsibleException(r)
