import logging
import os
import threading
import boto3

import google.cloud.compute_v1
from ansible.module_utils.basic import AnsibleModule

# setup global logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s')
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('boto').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

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


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()
        module_return = self._execute_module(module_name='ec2',
                                             module_args=module_args,
                                             task_vars=task_vars, tmp=tmp)
        print(module_return)
        ret = dict()
        if not module_return.get('failed'):
            for key, value in module_return['ansible_facts'].items():
                print(key, value)

        return dict(ansible_facts=dict(ret))
    
    

class CloudInstance:

    def __init__(self, deployment_id: str, present: bool, deployment: list, defaults: dict):

        self.deployment_id = deployment_id
        self.present = present
        self.deployment = deployment
        self.defaults = defaults

        self.threads: list[threading.Thread] = []
        self._lock = threading.Lock()

        self.gcp_project = os.environ.get('GCP_PROJECT', None)
        self.azure_resource_group = os.environ.get(
            'AZURE_RESOURCE_GROUP', None)
        self.new_instances = []
        self.instances = []

    def run(self):

        # fetch all running instances for the deployment_id and append them to the 'instances' list
        logging.debug(f"Fetching all instances with deployment_id = '{self.deployment_id}'")
        self.fetch_all(self.deployment_id, self.gcp_project, self.azure_resource_group)

        logging.debug("Listing pre-existing instances:")
        for x in self.instances:
            logging.debug(f'\t{x}')

        # 3. build the deployment: a list of dict with these attributes:
        #    - public_ip
        #    - public_hostname
        #    - private_ip
        #    - private_hostname
        #    - cloud
        #    - region
        #    - zone
        #    - deployment_id
        #    - cluster_name
        #    - group_name
        #    - inventory_groups
        #    - ansible_user
        #    - extra_vars
        #    - the unique cloud identifier (eg aws instance_id, for easy deleting operations)
        
        # instances of the new deployment will go into the 'new_instances' list
        if self.present:
            logging.debug("Building deployment...")
            self.build_deployment()

        logging.debug("Removing instances...")
        self.destroy_all(self.instances, self.gcp_project,
                         self.azure_resource_group)

        logging.debug("Waiting for all operation threads to complete")
        for x in self.threads:
            x.join()

        logging.debug("Returning new deployment list to client")
        return self.new_instances

    def fetch_all(self, deployment_id: str, gcp_project: str, azure_resource_group: str):
        """For each public cloud, fetch all instances 
        with the given deployment_id and return a clean list of instances

        Args:
            deployment_id (str): the value of the tag deployment_id

        Return:
            list[dict]: the list of instances across all clouds
        """
        # AWS
        thread = threading.Thread(target=self.fetch_aws_instances, args=(self.deployment_id, ))
        thread.start()
        self.threads.append(thread)

        # GCP
        if gcp_project:
            thread = threading.Thread(target=self.fetch_gcp_instances, args=(self.deployment_id, self.gcp_project ))
            thread.start()
            self.threads.append(thread)

        # AZURE
        if azure_resource_group:
            thread = threading.Thread(target=self.fetch_azure_instances, args=(self.deployment_id, ))
            thread.start()
            self.threads.append(thread)

        # wait for all threads to complete
        for x in self.threads:
            x.join()
    
    def fetch_aws_instances_per_region(self, region, deployment_id):
        logging.debug(f'Fetching AWS instances from {region}')
        instances = []
        
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_instances(Filters=[{'Name': 'tag:deployment_id', 'Values': [deployment_id] }])
        
        for x in response['Reservations']:
            for i in x['Instances']:
                
                tags = {}
                for t in i['Tags']:
                    tags[t['Key']] = t['Value']
                    
                instances.append({
                    # cloud instance id, useful for deleting
                    "id": i['InstanceId'],

                    # locality
                    "cloud": "aws",
                    "region": i['Placement']['AvailabilityZone'][:-1],
                    "zone": i['Placement']['AvailabilityZone'][-1],

                    # addresses
                    "public_ip": i['PublicIpAddress'],
                    "public_hostname": i['PublicDnsName'],
                    "private_ip": i['PrivateIpAddress'],
                    "private_hostname": i['PrivateDnsName'],

                    # tags
                    "ansible_user": tags['ansible_user'],
                    "inventory_groups": tags['inventory_groups'],
                    "cluster_name": tags['cluster_name'],
                    "group_name": tags['group_name'],
                    "extra_vars": tags['extra_vars']
                }) 

        self.update_current_deployment(instances)
            
    def fetch_aws_instances(self, deployment_id: str):
        logging.debug(f"Fetching AWS instances for deployment_id={deployment_id}")
        
        threads: list [threading.Thread] = []
        
        ec2 = boto3.client('ec2')
        regions = [x['RegionName'] for x in ec2.describe_regions()['Regions']]

        for region in regions:
            thread = threading.Thread(target=self.fetch_aws_instances_per_region, args=(region, deployment_id), daemon=True)
            thread.start()
            threads.append(thread)
        
        for x in threads:
            x.join()
            
    def fetch_gcp_instances(self, deployment_id: str, project_id: str):
        """
        Return a dictionary of all instances present in a project, grouped by their zone.

        Args:
            project_id: project ID or project number of the Cloud project you want to use.
        Returns:
            A dictionary with zone names as keys (in form of "zones/{zone_name}") and
            iterable collections of Instance objects as values.
        """
        logging.debug(f"Fetching GCP instances for deployment_id={deployment_id}")
        
        instance_client = google.cloud.compute_v1.InstancesClient()
        # Use the `max_results` parameter to limit the number of results that the API returns per response page.
        request = google.cloud.compute_v1.AggregatedListInstancesRequest(
            project=project_id, max_results=5, filter=f'labels.deployment_id:{deployment_id}')

        agg_list = instance_client.aggregated_list(request=request)
        instances = []

        # Despite using the `max_results` parameter, you don't need to handle the pagination
        # yourself. The returned `AggregatedListPager` object handles pagination
        # automatically, returning separated pages as you iterate over the results.
        for zone, response in agg_list:
            if response.instances:
                for x in response.instances:
                    instances.append({
                        # cloud instance id, useful for deleting
                        "id": x.name,

                        # locality
                        "cloud": "gcp",
                        "region": zone[6:-2],
                        "zone": zone[-1],

                        # addresses
                        "public_ip": x.network_interfaces[0].access_configs[0].nat_i_p,
                        "public_hostname": "",
                        "private_ip": x.network_interfaces[0].network_i_p,
                        "private_hostname": f"{x.name}.c.cea-team.internal",

                        # tags
                        "ansible_user": x.labels.get('ansible_user'),
                        "inventory_groups": x.labels.get('inventory_groups'),
                        "cluster_name": x.labels.get('cluster_name'),
                        "group_name": x.labels.get('group_name'),
                        "extra_vars": x.labels.get('extra_vars')
                    })

        self.update_current_deployment(instances)
        
    def fetch_azure_instances(self, deployment_id: str):
        logging.debug(f"Fetching Azure instances for deployment_id={deployment_id}")
        instances = [
            {
                "cloud": "azure",
                "cluster_name": "demo-0",
                "group_name": "crdb",
                "id": 1
            },
            {
                "cloud": "azure",
                "cluster_name": "demo-0",
                "group_name": "crdb",
                "id": 2
            },
            {
                "cloud": "azure",
                "cluster_name": "demo-0",
                "group_name": "crdb",
                "id": 3
            },
            {
                "cloud": "azure",
                "cluster_name": "demo-0",
                "group_name": "crdb",
                "id": 4
            },
            {
                "cloud": "azure",
                "cluster_name": "demo-0",
                "group_name": "crdb",
                "id": 5
            },
            {
                "cloud": "azure",
                "cluster_name": "demo-0",
                "group_name": "crdb",
                "id": 6
            },
            {
                "cloud": "azure",
                "cluster_name": "demo-0",
                "group_name": "crdb",
                "id": 7
            },
            {
                "cloud": "azure",
                "cluster_name": "demo-1",
                "group_name": "crdb",
                "id": 101
            },
            {
                "cloud": "azure",
                "cluster_name": "demo-1",
                "group_name": "crdb",
                "id": 102
            },
            {
                "cloud": "azure",
                "cluster_name": "dem-1",
                "group_name": "crdb",
                "id": 201
            },
            {
                "cloud": "azure",
                "cluster_name": "dem-1",
                "group_name": "crdb",
                "id": 202
            }
        ]
        
        self.update_current_deployment(instances)
    
    def update_current_deployment(self, instances: list):
        with self._lock:
            logging.debug("Updating pre-existing instances list")
            self.instances += instances

    def update_new_deployment(self, instances: list):
        with self._lock:
            logging.debug("Updating new instances list")
            self.new_instances += instances
            
    # 4. loop through the 'deployment' struct
    #    - through each cluster and copies
    #    - through each group within each cluster
    def build_deployment(self):
        # loop through each cluster item in the deployment list
        for cluster in self.deployment:

            # extract the cluster name for all copies,
            # then, for each requested copy, add the index suffix
            cluster_name: str = cluster['cluster_name']
            for x in range(int(cluster.get('copies', 1))):
                self.build_cluster(f'{cluster_name}-{x}', cluster)

    def build_cluster(self, cluster_name: str, cluster: dict):

        # for each group in the cluster,
        # put all cluster defaults into the group
        for group in cluster.get('groups', []):
            self.build_group(cluster_name, self.merge_dicts(cluster, group))

    # 5. for each group, compare what is in 'deployment' to what is in 'current_deployment':
    #     case NO DIFFERENCE
    #       return the details in current_deployment
    #
    #     case TOO FEW
    #       for each exact count, start a thread to create the requested instance
    #       return current_deployment + the details of the newly created instances
    #
    #     case TOO MANY
    #        for each instance that's too many, start a thread to destroy the instance
    #        return current_deployment minus what was distroyed
    def build_group(self, cluster_name, group: dict):
        # get all instances in the current group
        current_group = []
        for x in self.instances[:]:
            if x['cluster_name'] == cluster_name and x['group_name'] == group['group_name']:
                current_group.append(x)
                self.instances.remove(x)

        current_count = len(current_group)
        new_exact_count = group.get('exact_count', 0)

        # CASE 1
        if current_count == new_exact_count:
            self.new_instances += current_group

        # CASE 2: ADD instances
        elif current_count < new_exact_count:
            target = {
                'aws': self.provision_aws_vm,
                'gcp': self.provision_gcp_vm,
                'azure': self.provision_azure_vm
            }
            
            for x in range(new_exact_count - current_count):
                thread = threading.Thread(target=target[group['cloud']], args=(cluster_name, group, x))
                thread.start()
                self.threads.append(thread)

        # CASE 3: REMOVE instances
        else:
            for x in range(current_count - new_exact_count):
                self.instances.append(current_group.pop(-1))

            self.new_instances += current_group

    def provision_aws_vm(self, cluster_name: str, group: dict, x: int):
        logging.debug('++aws %s %s %s' % (cluster_name, group['group_name'], x))
        
        
        gpu = str(group['instance'].get('gpu', "0"))
        cpu = str(group['instance'].get('cpu', "0"))
        mem = str(group['instance'].get('mem', "0"))
        cloud = group['cloud']
        instance_type = self.defaults['instances'][cloud][gpu][cpu][mem]
        volume_defaults = self.defaults['volume_type'][cloud]
        
        os_disk_type = volume_defaults[group['volumes']['os']['type']]

        data_disk_type = [ volume_defaults[x['type']] for x in group['volumes']['data'] ]
        print(data_disk_type)
        
        ec2 = boto3.client('ec2', region_name=group['region'])
        response = ec2.run_instances(
            DryRun=True,
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sdh',
                    'Ebs': {
                        'VolumeSize': 100,
                    },
                },
            ],
            ImageId=group['image'],
            InstanceType=instance_type,
            KeyName=group['public_key_id'],
            MaxCount=group['exact_count'],
            MinCount=group['exact_count'],
            SecurityGroupIds=[
                group['security_group'],
            ],
            SubnetId=group['subnet'],
            UserData=group['user_data'],
            IamInstanceProfile={
                'Name': group['role']
            },
            NetworkInterfaces=[{
                "DeviceIndex": 0,
                "AssociatePublicIpAddress": group['public_ip']
            }],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Purpose',
                            'Value': 'test',
                        },
                    ],
                },
            ],
        )
        
        self.update_new_deployment([{"cloud": "aws", "cluster_name": cluster_name, "group_name": group['group_name'], "id": x}])

    def provision_gcp_vm(self, cluster_name: str, group: dict, x: int):
        logging.debug('++gcp %s %s %s' % (cluster_name, group, x))
        self.update_new_deployment([{"cloud": "gcp", "cluster_name": cluster_name, "group_name": group['group_name'], "id": x}])

    def provision_azure_vm(self, cluster_name: str, group: dict, x: int):
        logging.debug('++azure %s %s %s' % (cluster_name, group, x))
        self.update_new_deployment([{"cloud": "azure", "cluster_name": cluster_name, "group_name": group['group_name'], "id": x}])

    def destroy_all(self, instances: list, gcp_project: str, azure_resource_group: str):
        target = {
            'aws': self.destroy_aws_vm,
            'gcp': self.destroy_gcp_vm,
            'azure': self.destroy_azure_vm
        }
        
        for x in instances:
            thread = threading.Thread(target=target[x['cloud']], args=(x, ))
            thread.start()
            self.threads.append(thread)

            
    def destroy_aws_vm(self, instance: dict):
        ec2 = boto3.client('ec2', region_name=instance['region'])
        response = ec2.terminate_instances(InstanceIds=[instance['id']], )   

        status = response['TerminatingInstances'][0]['CurrentState']['Name']
        
        if status in ['shutting-down', 'terminated']:
            logging.debug(f'Deleted AWS instance: {instance}')
        else:
            logging.error('Unexpected response: {response}}')
            
    def destroy_gcp_vm(self, instance: dict):
        logging.debug(f'--gcp {instance}')

    def destroy_azure_vm(self, instance: dict):
        logging.debug(f'--azure {instance}')

    # UTIL METHODS
    # =========================================================================

    def merge_dicts(self, parent: dict, child: dict):
        for k, v in parent.items():
            if not k in child:
                child[k] = v
        return child


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default="present",
                       choices=['present', 'absent']),
            deployment_id=dict(type='str', required=True),
            deployment=dict(type='list', default=[]),
            defaults=dict(type='dict', default={}),
        ),
        supports_check_mode=False,
    )

    try:
        ci = CloudInstance(module.params['deployment_id'],
                           True if module.params['state'] == 'present' else False,
                           module.params['deployment'],
                           module.params['defaults'])

        g = ci.run()

        logging.debug("Deployment instances list:")
        for x in g:
            logging.debug(f'\t{x}')

        # Outputs
        changed: bool = False
        out: dict = {}

        # module.exit_json(changed=changed, out=out)

    except Exception as e:
        module.fail_json(msg=e)


if __name__ == '__main__':
    main()
