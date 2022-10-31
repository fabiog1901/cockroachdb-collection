#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = '''
module: cc_cmek_info

short_description: Get CMEK-related information for a cluster.

description:
  - Get CMEK-related information for a cluster.
  - A Cockroach Cloud Service Account API Key is required.
  - Export the key as environment variable 'CC_KEY' or pass it on module invokation

version_added: "1.0.0"

author: "Cockroach Labs"

options:
  cluster_id:
    description:
      - The UUID of the cluster
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
  fabiog1901.cockroachdb.cc_cmek_info:
    cluster_id: 9592afea-2bf8-4dc1-95ec-9369b7f684ca
    api_client:
      api_version: '2022-09-20'
'''

RETURN = '''
cmek:
  description: CMEKClusterInfo contains the status of CMEK across an entire cluster, including within each one its regions.
  type: dict
  elements: dict
  contains:
    region_infos:
      description:
        - CMEKRegionInfo contains the status of CMEK within a region.
        - This includes current and past key specifications used within the region, as well as the status of those specifications
      type: list
      elements: dict
      returned: always
      contains:
        key_infos:
          description: CMEKKeyInfo contains the status of a customer-provided key alongside the specification.
          type: list
          returned: always
          elements: dict
          contains:
            created_at:
              description: ""
              type: str
              returned: always
            spec:
              description: CMEKKeySpecification contains all the details necessary to use a customer-provided encryption key. This involves the type/location of the key and the principal to authenticate as when accessing it.
              type: dict
              returned: always
              contains:
                auth_principal:
                  description: ""
                  type: str
                  returned: always
                type:
                  description:
                    - CMEKKeyType enumerates types of customer-managed keys.
                    - "UNKNOWN_KEY_TYPE: UNKNOWN should never be used; if it is used, it indicates a bug."
                    - "Allowed: AWS_KMS┃GCP_CLOUD_KMS"
                  type: str
                  returned: always
                uri:
                  description: ""
                  type: str
                  returned: always
            status:
              description:
                - CMEKStatus describes the current status of CMEK for an entire CRDB cluster or a CMEK key within a region.
                - "UNKNOWN_STATUS: UNKNOWN should never be used; if it is used, it indicates a bug."
                - "DISABLED: DISABLED corresponds to the state of a cluster or region-level key when CMEK has finished being disabled. By default, CMEK will be disabled for new clusters."
                - "DISABLING: DISABLING corresponds to the state of a cluster or region-level key when CMEK is in the process of being disabled."
                - "DISABLE_FAILED: DISABLE_FAILED corresponds to the state of a cluster or region-level key when CMEK has failed to be disabled."
                - "ENABLED: ENABLED corresponds to the state of a cluster or region-level key when CMEK is enabled."
                - "ENABLING: ENABLING corresponds to the state of a cluster or region-level key when CMEK is in the process of being enabled."
                - "ENABLE_FAILED: ENABLE_FAILED corresponds to the state of a cluster or region-level key when CMEK has failed to be enabled."
                - "ROTATING: ROTATING corresponds to the state of a cluster or region when the a new spec is in the process of being enabled while an existing spec is being disabled."
                - "ROTATE_FAILED: ROTATE_FAILED corresponds to the state of a cluster or region if there was a failure to update from one CMEK spec to another."
                - "REVOKED: REVOKED corresponds to the state of a cluster or region-level key when the customer has revoked CockroachLab's permissions for their key."
                - "REVOKING: REVOKING corresponds to the state of a cluster or region-level key when CMEK is in the process of being revoked."
                - "REVOKE_FAILED: REVOKE_FAILED corresponds to the state of a cluster or region-level key when CMEK has failed to be revoked."
                - "Allowed: DISABLED┃DISABLING┃DISABLE_FAILED┃ENABLED┃ENABLING┃ENABLE_FAILED┃ROTATING┃ROTATE_FAILED┃REVOKED┃REVOKING┃REVOKE_FAILED"
              type: str
              returned: always
            updated_at:
              description: ""
              type: str
              returned: always
            user_message:
              description: ""
              type: str
              returned: always
        region:
          description: ""
          type: str
        status:
          description:
            - CMEKStatus describes the current status of CMEK for an entire CRDB cluster or a CMEK key within a region.
            - "UNKNOWN_STATUS: UNKNOWN should never be used; if it is used, it indicates a bug."
            - "DISABLED: DISABLED corresponds to the state of a cluster or region-level key when CMEK has finished being disabled. By default, CMEK will be disabled for new clusters."
            - "DISABLING: DISABLING corresponds to the state of a cluster or region-level key when CMEK is in the process of being disabled."
            - "DISABLE_FAILED: DISABLE_FAILED corresponds to the state of a cluster or region-level key when CMEK has failed to be disabled."
            - "ENABLED: ENABLED corresponds to the state of a cluster or region-level key when CMEK is enabled."
            - "ENABLING: ENABLING corresponds to the state of a cluster or region-level key when CMEK is in the process of being enabled."
            - "ENABLE_FAILED: ENABLE_FAILED corresponds to the state of a cluster or region-level key when CMEK has failed to be enabled."
            - "ROTATING: ROTATING corresponds to the state of a cluster or region when the a new spec is in the process of being enabled while an existing spec is being disabled."
            - "ROTATE_FAILED: ROTATE_FAILED corresponds to the state of a cluster or region if there was a failure to update from one CMEK spec to another."
            - "REVOKED: REVOKED corresponds to the state of a cluster or region-level key when the customer has revoked CockroachLab's permissions for their key."
            - "REVOKING: REVOKING corresponds to the state of a cluster or region-level key when CMEK is in the process of being revoked."
            - "REVOKE_FAILED: REVOKE_FAILED corresponds to the state of a cluster or region-level key when CMEK has failed to be revoked."
            - "Allowed: DISABLED┃DISABLING┃DISABLE_FAILED┃ENABLED┃ENABLING┃ENABLE_FAILED┃ROTATING┃ROTATE_FAILED┃REVOKED┃REVOKING┃REVOKE_FAILED"
          type: str
          returned: always
    status:
      description:
        - CMEKStatus describes the current status of CMEK for an entire CRDB cluster or a CMEK key within a region.
        - "UNKNOWN_STATUS: UNKNOWN should never be used; if it is used, it indicates a bug."
        - "DISABLED: DISABLED corresponds to the state of a cluster or region-level key when CMEK has finished being disabled. By default, CMEK will be disabled for new clusters."
        - "DISABLING: DISABLING corresponds to the state of a cluster or region-level key when CMEK is in the process of being disabled."
        - "DISABLE_FAILED: DISABLE_FAILED corresponds to the state of a cluster or region-level key when CMEK has failed to be disabled."
        - "ENABLED: ENABLED corresponds to the state of a cluster or region-level key when CMEK is enabled."
        - "ENABLING: ENABLING corresponds to the state of a cluster or region-level key when CMEK is in the process of being enabled."
        - "ENABLE_FAILED: ENABLE_FAILED corresponds to the state of a cluster or region-level key when CMEK has failed to be enabled."
        - "ROTATING: ROTATING corresponds to the state of a cluster or region when the a new spec is in the process of being enabled while an existing spec is being disabled."
        - "ROTATE_FAILED: ROTATE_FAILED corresponds to the state of a cluster or region if there was a failure to update from one CMEK spec to another."
        - "REVOKED: REVOKED corresponds to the state of a cluster or region-level key when the customer has revoked CockroachLab's permissions for their key."
        - "REVOKING: REVOKING corresponds to the state of a cluster or region-level key when CMEK is in the process of being revoked."
        - "REVOKE_FAILED: REVOKE_FAILED corresponds to the state of a cluster or region-level key when CMEK has failed to be revoked."
        - "Allowed: DISABLED┃DISABLING┃DISABLE_FAILED┃ENABLED┃ENABLING┃ENABLE_FAILED┃ROTATING┃ROTATE_FAILED┃REVOKED┃REVOKING┃REVOKE_FAILED"
      type: str
      returned: always

'''


# ANSIBLE
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.fabiog1901.cockroachdb.plugins.module_utils.utils import APIClient, ApiClientArgs

from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_get_cmek_cluster_info

import json

class Client:

    def __init__(self, api_client_args: ApiClientArgs, cluster_id: str):

        # vars
        self.cluster_id = cluster_id

        # return vars
        self.out: str = ''
        self.changed: bool = False

        # cc client
        self.client = APIClient(api_client_args)

    def run(self):

        cmek: str = ''

        r = cockroach_cloud_get_cmek_cluster_info.sync_detailed(
            client=self.client,
            cluster_id=self.cluster_id
        )

        if r.status_code == 200:
            cmek = json.loads(r.content)
        else:
            raise Exception({'status_code': r.status_code,
                            'content': r.parsed})

        return cmek, False


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
    module.exit_json(meta=module.params, changed=changed, cmek=out)


if __name__ == '__main__':
    main()
