import json
import os

# ANSIBLE
from ansible.module_utils.basic import AnsibleModule

# CC
import os

from cockroachdb_cloud_client import AuthenticatedClient
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_available_regions
from cockroachdb_cloud_client.models import ListAvailableRegionsResponse, CockroachCloudListAvailableRegionsProvider
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

    def __init__(self, provider: str, serverless: bool):

        # vars
        if provider.lower() == 'all':
            self.provider = provider
        elif provider == 'GCP':
            self.provider = CockroachCloudListAvailableRegionsProvider.GCP
        else:
            self.provider = CockroachCloudListAvailableRegionsProvider.AWS

        self.serverless = serverless

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

        if self.provider.lower() == 'all':
            r1 = cockroach_cloud_list_available_regions.sync_detailed(
                client=self.client,
                provider=CockroachCloudListAvailableRegionsProvider.AWS,
                serverless=self.serverless)

            r2 = cockroach_cloud_list_available_regions.sync_detailed(
                client=self.client, 
                provider=CockroachCloudListAvailableRegionsProvider.GCP,
                serverless=self.serverless)

            j1 = json.loads(r1.content)
            j2 = json.loads(r2.content)

            j1['regions'].extend(j2['regions'])

            return j1, False

        else:
            r = cockroach_cloud_list_available_regions.sync_detailed(
                client=self.client,
                provider=self.provider,
                serverless=self.serverless)

            return json.loads(r.content), False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            provider=dict(type='str', choice=[
                          'AWS', 'GCP', 'all'], default='all'),
            serverless=dict(type='bool', default=False),
        ),
        supports_check_mode=False,
    )

    try:
        out, changed = Client(
            module.params['provider'],
            module.params['serverless']
        ).run()

    except Exception as e:
        module.fail_json(msg=e)

    # Outputs
    module.exit_json(changed=changed, out=out)


if __name__ == '__main__':
    main()
