#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = '''
module: cc_invoices_info

short_description: List invoices for a given organization.

description:
  - List invoices for a given organization.
  - A Cockroach Cloud Service Account API Key is required.
  - Export the key as environment variable 'CC_KEY' or pass it on module invokation

version_added: "1.0.0"

author: "Cockroach Labs"

options:
  invoice_id:
    description: ''
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
  fabiog1901.cockroachdb.cc_invoices_info:
    invoice_id: 
    api_client:
      api_version: '2022-09-20'
'''

RETURN = '''

'''


# ANSIBLE
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.fabiog1901.cockroachdb.plugins.module_utils.utils import APIClient, ApiClientArgs

from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_invoices, cockroach_cloud_get_invoice

import json

class Client:

    def __init__(self, api_client_args: ApiClientArgs, invoice_id: str):

        # vars
        self.invoice_id = invoice_id

        # return vars
        self.out: str = ''
        self.changed: bool = False

        # cc client
        self.client = APIClient(api_client_args)

    def run(self):

        invoices: list = []

        if self.invoice_id:
            r = cockroach_cloud_get_invoice.sync_detailed(
                client=self.client,
                invoice_id=self.invoice_id
            )

        else:
            r = cockroach_cloud_list_invoices.sync_detailed(
                client=self.client
            )

        if r.status_code == 200:
            if self.invoice_id:
                invoices = [json.loads(r.content)]
            else:
                invoices = json.loads(r.content)['invoices']
        else:
            raise Exception({'status_code': r.status_code,
                            'content': r.parsed})

        return invoices, False


def main():
    module = AnsibleModule(argument_spec=dict(
        # api client arguments
        api_client=dict(
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
        invoice_id=dict(type='str'),
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
            module.params['invoice_id']
        ).run()

    except Exception as e:
        module.fail_json(meta=module.params, msg=e.args)

    # Outputs
    module.exit_json(meta=module.params, changed=changed, invoices=out)


if __name__ == '__main__':
    main()
