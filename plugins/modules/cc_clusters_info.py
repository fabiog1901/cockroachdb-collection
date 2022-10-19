import json
import os

# ANSIBLE
from ansible.module_utils.basic import AnsibleModule

# CC
import os

from cockroachdb_cloud_client import AuthenticatedClient
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_clusters, cockroach_cloud_get_cluster
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

    def __init__(self, cluster_id: str, show_inactive: bool):

        # vars
        self.cluster_id = cluster_id
        self.show_inactive = show_inactive

        # return vars
        self.out: str = ''
        self.changed: bool = False
        self.errors: list = []

        # cc client
        self.client = AuthenticatedClient(
            base_url="https://cockroachlabs.cloud",
            token=os.environ.get('CC_KEY', None),
            headers={"cc-version": "2022-09-20"},
        )

    def run(self):

        if self.cluster_id.lower() == 'all':
            r = cockroach_cloud_list_clusters.sync_detailed(
                client=self.client, show_inactive=self.show_inactive)

        else:
            r = cockroach_cloud_get_cluster.sync_detailed(
                self.cluster_id, client=self.client)

        self.out = json.loads(r.content)
        self.changed = False

        return self.out, self.changed


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cluster_id=dict(type='str', default='all'),
            show_inactive=dict(type='bool', default=False),
        ),
        supports_check_mode=False,
    )

    try:
        out, changed = Client(
            module.params['cluster_id'],
            module.params['show_inactive']
        ).run()

    except Exception as e:
        module.fail_json(msg=e)

    # Outputs
    module.exit_json(changed=changed, out=out)


if __name__ == '__main__':
    main()
