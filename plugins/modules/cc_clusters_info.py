#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
module: cc_clusters_info

short_description: List clusters owned by an organization.

description:
  - List clusters owned by an organization.
  - A Cockroach Cloud Service Account API Key is required.
  - Export the key as environment variable 'CC_KEY' or pass it on module invokation

version_added: "1.0.0"

author: "Cockroach Labs"

options:
  show_inactive:
    description:
      - If true, show clusters that have been deleted or failed to initialize.
    default: false
    type: bool
  show_nodes:
    description:
     - If true, show nodes that compose this cluster. Only available for CUSTOM or DEDICATED clusters.
    default: false
    type: bool
  cluster_id:
    description:
      - The UUID of the cluster you want to get information for.
      - Omit for a full list of clusters under the organization.
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
- name: list CC clusters in my org
  fabiog1901.cockroachdb.cc_clusters_info:
    show_inactive: no
    show_nodes: no
    api_client:
      api_version: '2022-09-20'
    register: out
'''

RETURN = '''
clusters:
  description: A list of regions
  type: list
  elements: dict
  returned: always
  contains:
    account_id:
      description: ''
      type: str
      returned: always
    cloud_provider:
      description:
        - "GCP: The Google Cloud Platform cloud provider."
        - "AWS: The Amazon Web Services cloud provider."
        - "Allowed: GCP┃AWS"
      type: str
      returned: always
    cockroach_version:
      description: ''
      type: str
      returned: always
    config:
      description: config details for either dedicated or serverless.
      type: dict
      returned: always
      contains:
        dedicated:
          description: present only if dedicated cluster
          type: dict
          contains:
            disk_iops:
              description: DiskIOPs is the number of disk I/O operations per second that are permitted on each node in the cluster. Zero indicates the cloud provider-specific default.
              type: int
              returned: always
            machine_type:
              description: MachineType is the machine type identifier within the given cloud provider, ex. m5.xlarge, n2-standard-4.
              type: str
              returned: always
            num_virtual_cpus:
              description: NumVirtualCPUs is the number of virtual CPUs per node in the cluster.
              type: int
              returned: always
            storage_gib:
              description: StorageGiB is the number of storage GiB per node in the cluster.
              type: int
              returned: always
        serverless:
          description: present only if serverless cluster
          type: dict
          contains:
            routing_id: 
              description: Used to build a connection string.
              type: str
              returned: always
            spend_limit:
              description: Spend limit in US cents.
              type: int
              returned: always
    created_at:
      description: date-time
      type: str
      returned: always
    creator_id:
      description: ''
      type: str
      returned: always
    deleted_at:
      description: date-time
      type: str
    id:
      description: ''
      type: str
      returned: always
    name:
      description: ''
      type: str
      returned: always
    nodes:
      description: 
        - list of nodes that make up the cluster. 
        - Only returned if show_nodes is True.
        - Only returned for Dedicated or Custom cluster. Not for Serverless clusters.
      type: list
      contains:
        name:
          description: ''
          type: str
        region_name:
          description: ''
          type: str
        status:
          description: "Allowed: LIVE┃NOT_READY"
          type: str
    operation_status:
      description:
        - "Allowed: CLUSTER_STATUS_UNSPECIFIED┃CRDB_MAJOR_UPGRADE_RUNNING┃CRDB_MAJOR_UPGRADE_FAILED┃CRDB_MAJOR_ROLLBACK_RUNNING┃CRDB_MAJOR_ROLLBACK_FAILED┃CRDB_PATCH_RUNNING┃CRDB_PATCH_FAILED┃CRDB_SCALE_RUNNING┃CRDB_SCALE_FAILED┃MAINTENANCE_RUNNING┃CRDB_INSTANCE_UPDATE_RUNNING┃CRDB_INSTANCE_UPDATE_FAILED┃CRDB_EDIT_CLUSTER_RUNNING┃CRDB_EDIT_CLUSTER_FAILED┃CRDB_CMEK_OPERATION_RUNNING┃CRDB_CMEK_OPERATION_FAILED┃TENANT_RESTORE_RUNNING┃TENANT_RESTORE_FAILED┃CRDB_LOG_EXPORT_OPERATION_RUNNING┃CRDB_LOG_EXPORT_OPERATION_FAILED"
      type: str
      returned: always
    plan:
      description:
        - "DEDICATED: A paid plan that offers dedicated hardware in any location."
        - "CUSTOM: A plan option that is used for clusters whose machine configs are not supported in self-service. All INVOICE clusters are under this plan option."
        - "SERVERLESS: A paid plan that runs on shared hardware and caps the users' maximum monthly spending to a user-specified (possibly 0) amount."
        - "Allowed: DEDICATED┃CUSTOM┃SERVERLESS"
      type: str
      returned: always
    regions:
      description: ''
      type: list
      returned: always
      contains:
        internal_dns:
          description: InternalDns is the internal DNS name of the cluster within the cloud provider's network. It is used to connect to the cluster with PrivateLink or VPC peering.
          type: str
          returned: always
        name:
          description: cluster name
          type: str
          returned: always
        node_count:
          description: NodeCount will be 0 for serverless clusters.
          type: int
          returned: always
        sql_dns:
          description: SqlDns is the DNS name of SQL interface of the cluster. It is used to connect to the cluster with IP allowlisting.
          type: str
          returned: always
        ui_dns:
          description: UiDns is the DNS name used when connecting to the DB Console for the cluster.
          type: str
          returned: always
    state:
      description:
        - "LOCKED: An exclusive operation is being performed on this cluster. Other operations should not proceed if they did not set a cluster into the LOCKED state."
        - "Allowed: CREATING┃CREATED┃CREATION_FAILED┃DELETED┃LOCKED"
      type: str
      returned: always
    updated_at:
      description: ''
      type: str
      returned: always
  sample:
    - account_id: crl-abcd-fg5
      cloud_provider: GCP
      cockroach_version: v22.1.7
      config:
        dedicated:
          disk_iops: 450
          machine_type: n1-standard-2
          memory_gib: 7.5
          num_virtual_cpus: 2
          storage_gib: 15
      created_at: "2022-09-07T15:38:55.339299Z"
      creator_id: zz895zzz-0307-471z-1234-123zzzzzzzz
      deleted_at: null
      id: 25fe8ade-1234-4d8b-1234-506ed445eed7
      name: some-good-cluster
      operation_status: CLUSTER_STATUS_UNSPECIFIED
      plan: DEDICATED
      regions:
        - internal_dns: ""
          name: us-west2
          node_count: 1
          sql_dns: some-good-cluster-gp7.gcp-us-west2.cockroachlabs.cloud
          ui_dns: admin-some-good-cluster-gp7.gcp-us-west2.cockroachlabs.cloud
      state: CREATED
      updated_at: "2022-10-20T17:58:41.008978Z"
'''


# ANSIBLE
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.fabiog1901.cockroachdb.plugins.module_utils.utils import APIClient, ApiClientArgs

import json
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_clusters, cockroach_cloud_get_cluster, cockroach_cloud_list_cluster_nodes
from cockroachdb_cloud_client.models.cockroach_cloud_list_available_regions_provider import CockroachCloudListAvailableRegionsProvider
from cockroachdb_cloud_client.models.list_available_regions_response import ListAvailableRegionsResponse


class Client:

    def __init__(self, api_client_args: ApiClientArgs, show_inactive: bool, cluster_id: str, show_nodes: bool):

        # vars
        self.cluster_id = cluster_id
        self.show_inactive = show_inactive
        self.show_nodes = show_nodes

        # return vars
        self.out: str = ''
        self.changed: bool = False

        # cc client
        self.client = APIClient(api_client_args)

    def run(self):

        def fetch_nodes_by_cluster_id(cluster_id):

            r = cockroach_cloud_list_cluster_nodes.sync_detailed(
                client=self.client,
                cluster_id=cluster_id)

            if r.status_code == 200:
                return json.loads(r.content)['nodes']
            else:
                raise Exception({'status_code': r.status_code,
                                 'content': r.parsed})

        clusters: list = []

        if self.cluster_id:
            r = cockroach_cloud_get_cluster.sync_detailed(
                client=self.client,
                cluster_id=self.cluster_id
            )

        else:
            r = cockroach_cloud_list_clusters.sync_detailed(
                client=self.client,
                show_inactive=self.show_inactive)

        if r.status_code == 200:
            if self.cluster_id:
                clusters = [json.loads(r.content)]
            else:
                clusters = json.loads(r.content)['clusters']
        else:
            raise Exception({'status_code': r.status_code,
                            'content': r.parsed})

        if self.show_nodes:
            for x in clusters:
                if x['plan'] == 'SERVERLESS':
                    x['nodes'] = []
                else:
                    x['nodes'] = fetch_nodes_by_cluster_id(x['id'])

        return clusters, False


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
        show_inactive=dict(type='bool', default=False),
        cluster_id=dict(type='str'),
        show_nodes=dict(type='bool', default=False),
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
            module.params['show_inactive'],
            module.params['cluster_id'],
            module.params['show_nodes']
        ).run()

    except Exception as e:
        module.fail_json(meta=module.params, msg=e.args)

    # Outputs
    module.exit_json(meta=module.params, changed=changed, clusters=out)


if __name__ == '__main__':
    main()
