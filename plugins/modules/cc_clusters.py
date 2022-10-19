import json
import logging
import os
import threading
import uuid

# ANSIBLE
from ansible.module_utils.basic import AnsibleModule

# CC
import os

from cockroachdb_cloud_client import AuthenticatedClient
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_clusters
from cockroachdb_cloud_client.models import ListClustersResponse
from cockroachdb_cloud_client.types import Response



ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: cloud_instance

short_description: Creates, updates and deletes role config groups for a given cluster

version_added: "2.9.5"

description:
    - "Creates, updates and deletes new role config groups for a given cluster"

options:
    state:
        description:
            - State of the deployment
        default: "present"
        type: str
        choice: ["present", "absent"]

    deployment:
        description:
            - List of clusters to provision
        default: "[]"
        type: list

requirements: [ "aws", "azure", "gcp" ]

author:
    - Fabio Ghirardello
'''

EXAMPLES = '''
- cloud_instance:
    state: present
    deployment:
      -
      -

'''

RETURN = '''
out:
    description: The response that the module generates
    type: dict
    returned: always
meta:
    description: The parameters passed
    type: dict
    returned: always
'''


class Client:

    def __init__(self, deployment_id: str, present: bool, deployment: list, defaults: dict):

        self.deployment_id = deployment_id
        self.present = present
        self.deployment = deployment
        self.defaults = defaults

        self.threads: list[threading.Thread] = []
        self._lock = threading.Lock()

        self.changed: bool = False

        self.cc_key = os.environ.get('CC_KEY', None)


        self.new_instances = []
        self.instances = []
        self.errors: list = []

    def run(self):

        # fetch all running instances for the deployment_id and append them to the 'instances' list
        logger.info(
            f"Fetching all instances with deployment_id = '{self.deployment_id}'")




def main():
    module = AnsibleModule(
        argument_spec=dict(
            # control
            state=dict(type='str', required=True, choices=['absent', 'present']),

            # parameters for ApiClient
            protocol=dict(type='str', choice=[
                          'http', 'https'], default="https"),
            host=dict(type='str', default="localhost"),
            port=dict(type='int', default=443),
            path=dict(type='str', default="/api/v1"),
            verify_ssl=dict(type='bool', default=True),

            # module specific
            cluster_name=dict(required=True, type='str'),
            service_name=dict(required=True, type='str'),
            comment=dict(type='str', dafault=""),

            # Role Config Group details
            name=dict(type='str', default=None),

        ),
        supports_check_mode=False,
    )

    instances: list = []

    try:
        out, changed = Client(
            module.params['deployment_id'],
            True if module.params['state'] == 'present' else False,
            module.params['deployment'],
            module.params['defaults']
        ).run()

    except Exception as e:
        module.fail_json(msg=e)


    # Outputs
    module.exit_json(changed=changed, out=out)


if __name__ == '__main__':
    main()
