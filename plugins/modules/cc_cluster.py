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
from ...plugins.module_utils.utils import get_cluster_id_from_cluster_name, AnsibleException, APIClient, fetch_cluster_by_id_or_name

from cockroachdb_cloud_client.models.create_cluster_request import CreateClusterRequest
from cockroachdb_cloud_client.models.create_cluster_specification import CreateClusterSpecification
from cockroachdb_cloud_client.models.cloud_provider_type import CloudProviderType
from cockroachdb_cloud_client.models.dedicated_cluster_create_specification import DedicatedClusterCreateSpecification
from cockroachdb_cloud_client.models.serverless_cluster_create_specification import ServerlessClusterCreateSpecification
from cockroachdb_cloud_client.models.usage_limits import UsageLimits
from cockroachdb_cloud_client.models.dedicated_hardware_create_specification import DedicatedHardwareCreateSpecification
from cockroachdb_cloud_client.models.dedicated_machine_type_specification import DedicatedMachineTypeSpecification
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_get_cluster

from cockroachdb_cloud_client.models.dedicated_cluster_create_specification_region_nodes import DedicatedClusterCreateSpecificationRegionNodes
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_create_cluster
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_delete_cluster

import json
import time

class Client:

    def __init__(self, 
                 state: str, name: str, provider: str, plan: str, regions: list[str], 
                 request_unit_limit: int, storage_mib_limit: int    ,
                 version: str, instance_type: str, vcpus: int, disk_iops: int, disk_size: int, wait: bool):

        # cc client
        self.client = APIClient()
        
        # vars
        self.state = state
        self.name = name
        self.plan = plan
        self.regions = regions
        
        if provider.lower() == 'gcp':
            self.provider = CloudProviderType.GCP
        else:
            self.provider = CloudProviderType.AWS
        
        # --> serverless
        self.request_unit_limit = request_unit_limit
        self.storage_mib_limit = storage_mib_limit
        # --> dedicated
        self.version=version
        self.instance_type=instance_type
        self.vcpus=vcpus
        self.disk_iops=disk_iops
        self.disk_size=disk_size
        self.wait=wait
        
        # return vars
        self.out: str = ''
        self.changed: bool = False

    def run(self):

        cluster = {}
        
        def create_cluster(c: CreateClusterRequest, wait: bool):

            r = cockroach_cloud_create_cluster.sync_detailed(
                    client=self.client, json_body=c)

            if r.status_code == 200:
                cluster = json.loads(r.content)
            else:
                # 409 means the cluster already exists
                if r.status_code == 409:
                    return fetch_cluster_by_id_or_name(self.client, self.name), False
                raise AnsibleException(r)

            if wait:
                while r.parsed.state == 'CREATING':
                    r = cockroach_cloud_get_cluster.sync_detailed(
                        client=self.client, cluster_id=r.parsed.id)
                    time.sleep(60) 
                
                
            return cluster, True
        
        
        if self.state == 'present':
          
            # TODO check if cluster already exists, and if new specs are same as current specs.
            cluster = fetch_cluster_by_id_or_name(self.client, self.name)
            if cluster:
                return cluster.to_dict(), False
            # if specs are same, pass and changed=false
            # else, update accordingly and changed=true
            if self.plan == 'serverless':
                sless_create_spec = ServerlessClusterCreateSpecification(
                  regions=self.regions, 
                  usage_limits= UsageLimits(
                    request_unit_limit=str(self.request_unit_limit),
                    storage_mib_limit=str(self.storage_mib_limit)
                  )
                ) 
                
                
                spec = CreateClusterSpecification(serverless=sless_create_spec)                
            
            else: # plan==dedicated
                pass
                # if self.instance_type:
                #     ded_machine = DedicatedMachineTypeSpecification(machine_type=self.instance_type)
                # elif self.vcpus:
                #     ded_machine = DedicatedMachineTypeSpecification(num_virtual_cpus=self.vcpus)
                # else:
                #     raise Exception({"content": "Either one among 'vcpus' or 'instance_type' should be specified."})
                
                # ded_hw = DedicatedHardwareCreateSpecification(machine_spec=ded_machine, 
                #                                               storage_gib=self.disk_size, 
                #                                               disk_iops=self.disk_iops)
                
                # regions = DedicatedClusterCreateSpecificationRegionNodes().from_dict(self.regions)
                
                # ded_create_spec = DedicatedClusterCreateSpecification(
                #   hardware=ded_hw, 
                #   region_nodes=regions, 
                #   cockroach_version=self.version
                #   )
                
                # spec = CreateClusterSpecification(dedicated=ded_create_spec)


            return create_cluster(CreateClusterRequest(name=self.name, provider=self.provider, spec=spec), self.wait)
            
        else: # state=absent
            
            # check if cluster still exists or was already deleted
            id: str = ''
            try:
                #TODO not sure this is right...
                id = get_cluster_id_from_cluster_name(self.client, self.name)
            except AnsibleException as e:
                raise e
            except Exception as e:
                pass
            
            #TODO not necessarly exists as id could be a uuid. need to send call to server 
            if id: # cluster exists, delete it
                r = cockroach_cloud_delete_cluster.sync_detailed(
                    client=self.client, cluster_id=id)

                if r.status_code == 200:
                    cluster = json.loads(r.content)
                else:                
                    raise AnsibleException(r)

                return cluster, True
            
            return cluster, False

def main():
    module = AnsibleModule(argument_spec=dict(
        # api client arguments
        api_client=dict(
            default={},
            type='dict',
            options=dict(
                cc_key=dict(type='str', no_log=True),
                api_version=dict(type='str'),
                scheme=dict(type='str'),
                host=dict(type='str'),
                port=dict(type='str'),
                path=dict(type='str'),
                verify_ssl=dict(type='bool'),
            )
        ),

        # module specific arguments
        state=dict(type='str', choices=['present', 'absent'], default='present'),
        name=dict(type='str', required=True),
        provider=dict(type='str', choices=['AWS', 'GCP'], default='AWS'),
        plan=dict(type='str', choices=['dedicated', 'serverless'], default='serverless'),
        regions=dict(type='raw', required=True),
        # serverless
        request_unit_limit=dict(type='int', default=0),
        storage_mib_limit=dict(type='int', default=0),
        # dedicated
        version=dict(type='str', required=False),
        instance_type=dict(type='str', required=False),
        vcpus=dict(type='int', required=False),
        disk_iops=dict(type='int', default=0),
        disk_size=dict(type='int', default=0),
        wait=dict(type='bool', default=False)
    ),
        supports_check_mode=False,
    )

    try:
        out, changed = Client(
            module.params['state'],
            module.params['name'],
            module.params['provider'],
            module.params['plan'],
            module.params['regions'],
            module.params['request_unit_limit'],
            module.params['storage_mib_limit'],
            module.params['version'],
            module.params['instance_type'],
            module.params['vcpus'],
            module.params['disk_iops'],
            module.params['disk_size'],
            module.params['wait']
        ).run()

        # Outputs
        module.exit_json(meta=module.params, changed=changed, cluster=out)

    except Exception as e:
        module.fail_json(meta=module.params, msg=e.args)


if __name__ == '__main__':
    main()
