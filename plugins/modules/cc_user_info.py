#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = '''
module: cc_user_info

short_description: List SQL users for a cluster.

description:
  - List SQL users for a cluster.
  - A Cockroach Cloud Service Account API Key is required.
  - Export the key as environment variable 'CC_KEY' or pass it on module invokation

version_added: "1.0.0"

author: "Cockroach Labs"

options:
  cluster_id:
    description:
      - The UUID or name of the cluster.
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
- name: list users for my cluster
  fabiog1901.cockroachdb.cc_user_info:
    cluster_id: 9592afea-2bf8-4dc1-95ec-9369b7f684ca
    api_client:
      api_version: '2022-09-20'
'''

RETURN = '''
users:
  description: A list of users
  type: list
  elements: dict
  returned: always
  contains:
    name:
      description: ''
      type: str
      returned: always
    
  sample:
    users:
    - name: chad
    - name: florence
'''


# ANSIBLE
from ansible.module_utils.basic import AnsibleModule
from ..module_utils.utils import get_cluster_id, AnsibleException, APIClient, ApiClientArgs

from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_sql_users

import json

class Client:

    def __init__(self, api_client_args: ApiClientArgs, cluster_id: str):

        # cc client
        self.client = APIClient(api_client_args)
        
        # vars
        self.cluster_id = get_cluster_id(self.client, cluster_id)

        # return vars
        self.out: str = ''
        self.changed: bool = False


    def run(self):

        users: list = []

        r = cockroach_cloud_list_sql_users.sync_detailed(
            client=self.client,
            cluster_id=self.cluster_id
        )

        if r.status_code == 200:
            users = json.loads(r.content)['users']
        else:
            raise AnsibleException(r)

        return users, False


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
            module.params['cluster_id']
        ).run()

    except Exception as e:
        module.fail_json(meta=module.params, msg=e.args)

    # Outputs
    module.exit_json(meta=module.params, changed=changed, users=out)


if __name__ == '__main__':
    main()
