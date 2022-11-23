#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = '''
module: cc_regions_info

short_description: List the regions available for new clusters and nodes.

description:
  - List the regions available for new clusters and nodes.
  - A Cockroach Cloud Service Account API Key is required.
  - Export the key as environment variable 'CC_KEY' or pass it on module invokation

version_added: "1.0.0"

author: "Cockroach Labs"

options:
  provider:
    description:
      - Optional CloudProvider for filtering.
    default: ALL
    type: str
    choices:
      - AWS
      - GCP
      - ALL
  serverless:
    description:
      - Optional filter to only show regions available for serverless clusters.
    default: false
    type: bool

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
- name: list CC regions in GCP excluding serverless
  fabiog1901.cockroachdb.cc_regions_info:
    provider: GCP
    serverless: no
    api_client:
      api_version: '2022-09-20'
    register: out
'''

RETURN = '''
regions:
  description: A list of regions
  type: list
  elements: dict
  returned: always
  contains:
    distance:
      description: Distance in miles, based on client IP address
      type: int
      returned: always
    location:
      description: region name
      type: str
      returned: always
    name:
      description: cloud provider location name
      type: str
      returned: always
    provider:
      description: provider name (AWS, GCP)
      type: str
      returned: always
    serverless:
      description: region available for serverless clusters
      type: bool
      returned: always
  sample:
    - distance: 202.76012
      location: N. Virginia
      name: us-east4
      provider: GCP
      serverless: false
'''

import json

# ANSIBLE
from ansible.module_utils.basic import AnsibleModule


from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_available_regions
from cockroachdb_cloud_client.models.cockroach_cloud_list_available_regions_provider import CockroachCloudListAvailableRegionsProvider
from cockroachdb_cloud_client.models.list_available_regions_response import ListAvailableRegionsResponse

from ansible_collections.fabiog1901.cockroachdb.plugins.module_utils.utils import AnsibleException, APIClient, ApiClientArgs



class Client:

    def __init__(self, api_client_args: ApiClientArgs, provider: str, serverless: bool):

        # vars
        if provider.lower() == 'all':
            self.providers = CockroachCloudListAvailableRegionsProvider
        elif provider.lower() == 'gcp':
            self.providers = [CockroachCloudListAvailableRegionsProvider.GCP]
        else:
            self.providers = [CockroachCloudListAvailableRegionsProvider.AWS]

        self.serverless = serverless

        # return vars
        self.out: str = ''
        self.changed: bool = False

        # cc client
        self.client = APIClient(api_client_args)

    def run(self):

        regions: list  = []
        
        for provider in self.providers:
            r = cockroach_cloud_list_available_regions.sync_detailed(
                client=self.client,
                provider=provider,
                serverless=self.serverless)

            if r.status_code == 200:
                regions += json.loads(r.content)['regions']
            else:
                raise AnsibleException(r)

        return regions, False


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
        provider=dict(type='str',
                      choices=['AWS', 'GCP', 'ALL'],
                      default='ALL'),
        serverless=dict(type='bool', default=False),
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
            module.params['provider'],
            module.params['serverless']
        ).run()

    except Exception as e:
        module.fail_json(meta=module.params, msg=e.args)

    # Outputs
    module.exit_json(meta=module.params, changed=changed, regions=out)


if __name__ == '__main__':
    main()
