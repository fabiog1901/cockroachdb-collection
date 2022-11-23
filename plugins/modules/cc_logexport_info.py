#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = '''
module: cc_logexport_info

short_description: Get the Log Export configuration for a cluster.

description:
  - Get the Log Export configuration for a cluster.
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
- name: show log export config for my cluster
  fabiog1901.cockroachdb.cc_logexport_info:
    cluster_id: 9592afea-2bf8-4dc1-95ec-9369b7f684ca
    api_client:
      api_version: '2022-09-20'
'''

RETURN = '''
logexport:
  description: LogExportClusterInfo contains a package of information that fully describes both the intended state of the log export configuration for a specific cluster but also some metadata around its deployment status, any error messages, and some timestamps.
  type: dict
  elements: dict
  contains:
    cluster_id:
      description: ''
      type: str
      returned: always
    created_at:
      description: ''
      type: str
      returned: always
    spec:
      description: 
        - LogExportClusterSpecification contains all the data necessary to configure log export for an individual cluster. 
        - Users would supply this data via the API and also receive it back when inspecting the state of their log export configuration.
      type: dict
      returned: always
      contains:
        auth_principal:
          description: auth_principal is either the AWS Role ARN that identifies a role that the cluster account can assume to write to CloudWatch or the GCP Project ID that the cluster service account has permissions to write to for cloud logging.
          type: str
          returned: always
        log_name:
          description: log_name is an identifier for the logs in the customer's log sink.
          type: str
          returned: always
        type:
          description:
            - "LogExportType encodes the cloud selection that we're exporting to along with the cloud logging platform. Currently, each cloud has a single logging platform."
            - "Allowed: AWS_CLOUDWATCH┃GCP_CLOUD_LOGGING"
    status:
      description:
        - "LogExportStatus encodes the possible states that a configuration can be in as it is created, deployed, and disabled."
        - "Allowed: DISABLED┃DISABLING┃DISABLE_FAILED┃ENABLED┃ENABLING┃ENABLE_FAILED"
      type: str
      returned: always
    updated_at:
      description: ''
      type: str
      returned: always
    user_message:
      description: ''
      type: str
      returned: always
'''


# ANSIBLE
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.fabiog1901.cockroachdb.plugins.module_utils.utils import get_cluster_id, AnsibleException,APIClient, ApiClientArgs

from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_get_log_export_info

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

        logexport: list = []

        r = cockroach_cloud_get_log_export_info.sync_detailed(
            client=self.client,
            cluster_id=self.cluster_id
        )

        if r.status_code == 200:
            logexport = json.loads(r.content)
        else:
            raise AnsibleException(r)

        return logexport, False


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
    module.exit_json(meta=module.params, changed=changed, logexport=out)


if __name__ == '__main__':
    main()
