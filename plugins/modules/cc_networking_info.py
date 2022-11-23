#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = '''
module: cc_networking_info

short_description: List networking details for a cluster.

description:
  - List networking details for a cluster.
  - A Cockroach Cloud Service Account API Key is required.
  - Export the key as environment variable 'CC_KEY' or pass it on module invokation

version_added: "1.0.0"

author: "Cockroach Labs"

options:
  cluster_id:
    description:
      - The UUID or name of the cluster you want to get information for.
    type: str
  show_allowlist:
    description: Get the IP allowlist and propagation status for a cluster
      - If true, show clusters that have been deleted or failed to initialize.
    default: false
    type: bool
  show_aws_endpoints:
    description: Lists all AwsEndpointConnections for a given cluster
    default: false
    type: bool
  show_private_endpoint_services:
    description: Lists all PrivateEndpointServices for a given cluster
    default: false
    type: bool
  show_egress_rules:
    description: List all egress rules associates with a cluster
    default: false
    type: bool
  egress_rule:
    description: Get an existing egress rule, either by name or id
    default: false
    type: str
  api_client:
    description:
      - Define details for the API client
    suboptions:
      cc_key:
        description:
          - The Service Account API key
          - This value is log redacted
          - By default it reads the env variable 'CC_KEY'
        default: 
        type: str

      api_version:
        description:
          - The API version to use
        default: latest
        type: str
      
      scheme:
        description:
          - http or https
        default: https
        type: str
        choices:
          - http
          - https
      host:
        description:
          - the hostname of the API server
        default: cockroachlabs.cloud
        type: str
      
      port:
        description:
          - the port number, as a string, for the API server
        default: '443'
        type: str
      
      path:
        description:
          - the path to the API endpoint
        default: ''
        type: str
      
      verify_ssl:
        description:
          - whether the client should verify the server cert
        default: true
        type: bool
        
requirements:
  - cockroachdb-cloud-client
'''

EXAMPLES = '''
- name: list networking details
  fabiog1901.cockroachdb.cc_networking_info:
    cluster_id: 2ea5b593-8766-4e92-aef2-caba191f0cab
    show_allowlist: yes
    show_aws_endpoints: yes
    show_private_endpoint_services: yes
    show_egress_rules: yes
    api_client:
      api_version: '2022-09-20'
    register: out
'''

RETURN = '''
networking:
  description: ''
  type: dict
  elements: dict
  returned: always
  contains:
    propagating:
      description: 
        - Returned if show_allowlist is true
      type: bool
    allowlist:
      description: 
        - Get the IP allowlist and propagation status for a cluster.
        - Returned if show_allowlist is true
      type: list
      elements: dict
      returned: always
      contains:
        cidr_ip: 
          description: ''
          type: str
        cidr_mask: 
          description: ''
          type: int
        name: 
          description: ''
          type: str
        sql: 
          description: ''
          type: bool
        ui: 
          description: ''
          type: bool
    connections:
      description: 
        - Connections is a list of private endpoints.
        - Returned if show_aws_endpoints is true
      type: list
      elements: dict
      returned: always
      contains:
        cloud_provider:
          description: 
            - 'GCP: The Google Cloud Platform cloud provider.'
            - 'AWS: The Amazon Web Services cloud provider.'
            - 'Allowed: GCP┃AWS'
          type: str
        endpoint_id:
          description: endpoint_id is the client side of the PrivateLink connection.
          type: str
        region_name:
          description: region_name is the cloud provider region name (i.e. us-east-1).
          type: str
        service_id:
          description: service_id is the server side of the PrivateLink connection. This is the same as AWSPrivateLinkEndpoint.service_id.
          type: str
        status:
          description: 
            - The statuses map to the statuses returned by the AWS API.
            - 'Allowed: ENDPOINT_PENDING┃ENDPOINT_PENDING_ACCEPTANCE┃ENDPOINT_AVAILABLE┃ENDPOINT_DELETING┃ENDPOINT_DELETED┃ENDPOINT_REJECTED┃ENDPOINT_FAILED┃ENDPOINT_EXPIRED'
          type: str
    services:
      description: 
        - Services contains a list of all cluster related services.
        - Returned if show_private_endpoint_services is true
      type: list
      elements: dict
      returned: always
      contains:
          aws: 
            description: ''
            type: dict
            contains:
              availability_zone_ids: 
                description: availability_zone_ids are the identifiers for the availability zones that the service is available in.
                type: str
              service_id:
                description: service_id is the server side of the PrivateLink connection. This is the same as AWSPrivateLinkEndpoint.service_id.
                type: str
              service_name: 
                description: service_name is the AWS service name customers use to create endpoints on their end.
                type: str
          cloud_provider:
            description: 
              - 'GCP: The Google Cloud Platform cloud provider.'
              - 'AWS: The Amazon Web Services cloud provider.'
              - 'Allowed: GCP┃AWS'
            type: str 
          region_name: 
            description: region_name is the cloud provider region name (i.e. us-east-1).
            type: str
          status:
            description: 
              - 'Private Endpoints: - ENDPOINT_SERVICE_STATUS_DELETE_FAILED: One note is that if the service is deleted, there is no longer a record, hence there is no "DELETED" status.'
              - 'Allowed: ENDPOINT_SERVICE_STATUS_CREATING┃ENDPOINT_SERVICE_STATUS_AVAILABLE┃ENDPOINT_SERVICE_STATUS_CREATE_FAILED┃ENDPOINT_SERVICE_STATUS_DELETING┃ENDPOINT_SERVICE_STATUS_DELETE_FAILED}]'
    rules:
      description: 
        - Network egress rule.
        - Returned if show_egress_rules is true or egress_rule is specified.
      type: list
      elements: dict
      returned: always
      contains:
        cluster_id:
          description: cluster_id identifies the cluster to which this egress rule applies.
          type: str
        created_at:
          description: created_at is the time at which the time at which the egress rule was created.
          type: str
        crl_managed:
          description: crl_managed indicates this egress rule is managed by CockroachDB Cloud services. This field is set by the server.
          type: bool
        description:
          description: description is a longer that serves to document the rules purpose.
          type: str
        destination:
          description: destination is the endpoint (or subnetwork if CIDR) to which traffic is allowed.
          type: str
        id:
          description: id uniquely identifies this egress rule.
          type: str
        name:
          description: name is the name of the egress rule.
          type: str
        paths:
          description: paths are the allowed URL paths. Only valid if Type="FQDN".
          type: list
          elements: str
        ports:
          description: ports are the allowed ports for TCP protocol. If Empty, all ports are allowed.
          type: list
          elements: int
        state:
          description: state indicates the state of the egress rule.
          type: str
        type:
          description: 'type classifies the destination field. Valid types include: "FQDN", "CIDR".'
          type: str
'''


# ANSIBLE
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.fabiog1901.cockroachdb.plugins.module_utils.utils import get_cluster_id, AnsibleException, APIClient, ApiClientArgs, fetch_cluster_by_id_or_name

from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_egress_rules
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_get_egress_rule
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_private_endpoint_services
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_aws_endpoint_connections
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_allowlist_entries

import json


class Client:

    def __init__(self, api_client_args: ApiClientArgs, cluster_id: str,
                 show_allowlist: bool,
                 show_egress_rules: bool,
                 egress_rule: str,
                 show_aws_endpoints: bool,
                 show_private_endpoint_services: bool):

        # cc client
        self.client = APIClient(api_client_args)
        
        # vars
        self.cluster_id = get_cluster_id(self.client, cluster_id)
        self.show_allowlist = show_allowlist
        self.show_egress_rules = show_egress_rules
        self.egress_rule = egress_rule
        self.show_aws_endpoints = show_aws_endpoints
        self.show_private_endpoint_services = show_private_endpoint_services

        # return vars
        self.out: str = ''
        self.changed: bool = False

        # cc client
        self.client = APIClient(api_client_args)

    def run(self):

        d = {}

        def fetch_egress_rule_by_name(name: str):
            r = cockroach_cloud_list_egress_rules.sync_detailed(
                client=self.client,
                cluster_id=self.cluster_id
            )

            if r.status_code == 200:
                rules = json.loads(r.content)['rules']
                for x in rules:
                    if x['name'] == name:
                        return x
                raise Exception({'content': f'could not fetch rule details for rule name: {name}'})
            else:
                raise AnsibleException(r)

        if self.show_allowlist:
            r = cockroach_cloud_list_allowlist_entries.sync_detailed(
                client=self.client,
                cluster_id=self.cluster_id
            )

            if r.status_code == 200:
                d['allowlist'] = json.loads(r.content)['allowlist']
                d['propagating'] = json.loads(r.content)['propagating']
            else:
                raise AnsibleException(r)

        if self.show_aws_endpoints:
            r = cockroach_cloud_list_aws_endpoint_connections.sync_detailed(
                client=self.client,
                cluster_id=self.cluster_id
            )

            if r.status_code == 200:
                d['connections'] = json.loads(r.content)['connections']
            else:
                raise AnsibleException(r)

        if self.show_private_endpoint_services:
            r = cockroach_cloud_list_private_endpoint_services.sync_detailed(
                client=self.client,
                cluster_id=self.cluster_id
            )

            if r.status_code == 200:
                d['services'] = json.loads(r.content)['services']
            else:
                raise AnsibleException(r)

        if self.show_egress_rules:
            r = cockroach_cloud_list_egress_rules.sync_detailed(
                client=self.client,
                cluster_id=self.cluster_id
            )

            if r.status_code == 200:
                d['rules'] = json.loads(r.content)['rules']
            else:
                raise AnsibleException(r)

        if self.egress_rule:
            r = cockroach_cloud_get_egress_rule.sync_detailed(
                client=self.client,
                cluster_id=self.cluster_id,
                rule_id=self.egress_rule
            )

            if r.status_code == 200:
                d['rules'] = [json.loads(r.content)['rule']]
            elif r.status_code == 400:
                d['rules'] = [fetch_egress_rule_by_name(self.egress_rule)]
            else:
                raise AnsibleException(r)

        return d, False


def main():
    module = AnsibleModule(argument_spec=dict(
        # api client arguments
        api_client=dict(default={},
            type='dict',
            cc_key=dict(type='str', no_log=True),
            api_version=dict(type='str'),

            scheme=dict(type='str'),
            host=dict(type='str'),
            port=dict(type='str'),
            path=dict(type='str'),
            verify_ssl=dict(type='bool'),
        ),

        # module specific arguments
        cluster_id=dict(type='str'),
        show_allowlist=dict(type='bool', default=False),
        show_egress_rules=dict(type='bool', default=False),
        egress_rule=dict(type='str'),
        show_aws_endpoints=dict(type='bool', default=False),
        show_private_endpoint_services=dict(type='bool', default=False),
    ),
        supports_check_mode=True,
    )

    try:
        out, changed = Client(
            ApiClientArgs(
                module.params['api_client'].get('cc_key', None),
                module.params['api_client'].get('api_version', None),
                module.params['api_client'].get('scheme', None),
                module.params['api_client'].get('host', None),
                module.params['api_client'].get('port', None),
                module.params['api_client'].get('path', None),
                module.params['api_client'].get('verify_ssl', None)
            ),
            module.params['cluster_id'],
            module.params['show_allowlist'],
            module.params['show_egress_rules'],
            module.params['egress_rule'],
            module.params['show_aws_endpoints'],
            module.params['show_private_endpoint_services']
        ).run()

    except Exception as e:
        module.fail_json(meta=module.params, msg=e.args)

    # Outputs
    module.exit_json(meta=module.params, changed=changed, networking=out)


if __name__ == '__main__':
    main()
