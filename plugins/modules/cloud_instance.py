#!/usr/bin/python

import json
import logging
import os
import random
import threading

# ANSIBLE
from ansible.module_utils.basic import AnsibleModule

# AWS
import boto3

# GCP
import google.cloud.compute_v1
import google.cloud.compute_v1.types
from google.api_core.extended_operation import ExtendedOperation

# AZURE
from azure.identity import EnvironmentCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient


# setup global logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.FileHandler(filename="/tmp/cloud_instance.log")
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


DOCUMENTATION = '''
---
module: cloud_instance

short_description: Creates, deletes public cloud instances

version_added: "1.0.0"

description:
    - Creates, deletes public cloud instances

options:
    state:
        description:
            - State of the deployment
        default: "present"
        type: str
        choices: 
          - present
          - absent


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


class CloudInstance:

    def __init__(self, deployment_id: str, present: bool, deployment: list, defaults: dict):

        self.deployment_id = deployment_id
        self.present = present
        self.deployment = deployment
        self.defaults = defaults

        self.threads: list[threading.Thread] = []
        self._lock = threading.Lock()

        self.changed: bool = False

        self.gcp_project = os.environ.get('GCP_PROJECT', None)
        self.azure_resource_group = os.environ.get(
            'AZURE_RESOURCE_GROUP', None)
        self.azure_subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

        self.new_instances = []
        self.instances = []
        self.errors: list = []

    def run(self):

        # fetch all running instances for the deployment_id and append them to the 'instances' list
        logger.info(
            f"Fetching all instances with deployment_id = '{self.deployment_id}'")
        self.__fetch_all(self.deployment_id, self.gcp_project,
                         self.azure_resource_group)

        if self.instances:
            logger.debug("Listing pre-existing instances:")
            for x in self.instances:
                logger.debug(f'\t{x}')

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
            logger.info("Building deployment...")
            self.__build_deployment()

        if self.instances:
            logger.info("Removing instances...")
            self.__destroy_all(self.instances, self.gcp_project,
                               self.azure_resource_group)
            logger.info("Removed all instances marked for deletion")

        logger.info("Waiting for all operation threads to complete")
        for x in self.threads:
            x.join()
        logger.info("All operation threads have completed")

        if self.errors:
            logger.error(str(self.errors))
            raise ValueError(self.errors)

        logger.debug("Returning new deployment list to client")
        return self.new_instances, self.changed

    def __fetch_all(self, deployment_id: str, gcp_project: str, azure_resource_group: str):
        """For each public cloud, fetch all instances
        with the given deployment_id and return a clean list of instances

        Args:
            deployment_id (str): the value of the tag deployment_id

        Return:
            list[dict]: the list of instances across all clouds
        """
        # AWS
        thread = threading.Thread(
            target=self.__fetch_aws_instances, args=(self.deployment_id, ))
        thread.start()
        self.threads.append(thread)

        # GCP
        if gcp_project:
            thread = threading.Thread(target=self.__fetch_gcp_instances, args=(
                self.deployment_id, self.gcp_project))
            thread.start()
            self.threads.append(thread)

        # AZURE
        if azure_resource_group:
            thread = threading.Thread(
                target=self.__fetch_azure_instances, args=(self.deployment_id, ))
            thread.start()
            self.threads.append(thread)

        # wait for all threads to complete
        for x in self.threads:
            x.join()

    def __parse_aws_query(self, response):
        instances: list = []

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
        return instances

    def __parse_gcp_query(self, instance: google.cloud.compute_v1.types.compute.Instance, region, zone):

        tags = {}
        for x in instance.metadata.items:
            tags[x.key] = x.value

        ip = instance.network_interfaces[0].access_configs[0].nat_i_p.split(
            '.')
        public_dns = '.'.join(
            [ip[3], ip[2], ip[1], ip[0], 'bc.googleusercontent.com'])

        return {
            # cloud instance id, useful for deleting
            "id": instance.name,

            # locality
            "cloud": "gcp",
            "region": region,
            "zone": zone,

            # addresses
            "public_ip": instance.network_interfaces[0].access_configs[0].nat_i_p,
            "public_hostname": public_dns,
            "private_ip": instance.network_interfaces[0].network_i_p,
            "private_hostname": f"{instance.name}.c.cea-team.internal",

            # tags
            "ansible_user": tags['ansible_user'],
            "inventory_groups": json.loads(tags['inventory_groups']),
            "cluster_name": tags['cluster_name'],
            "group_name": tags['group_name'],
            "extra_vars": json.loads(tags.get('extra_vars', '{}'))
        }

    def __parse_azure_query(self, vm, private_ip, public_ip, public_hostname):
        return [{
            # cloud instance id, useful for deleting
            "id": vm.name,

            # locality
            "cloud": "azure",
            "region": vm.location,
            "zone": 'default',

            # addresses
            "public_ip": public_ip,
            "public_hostname": public_hostname,
            "private_ip": private_ip,
            "private_hostname": vm.name+'.internal.cloudapp.net',

            # tags
            "ansible_user": vm.tags['ansible_user'],
            "inventory_groups": vm.tags['inventory_groups'],
            "cluster_name": vm.tags['cluster_name'],
            "group_name": vm.tags['group_name'],
            "extra_vars": vm.tags['extra_vars']
        }]

    # def __fetch_aws_instances_per_region(self, region, deployment_id):
    #     logger.debug(f'Fetching AWS instances from {region}')

    #     ec2 = boto3.client('ec2', region_name=region)
    #     response = ec2.describe_instances(
    #         Filters=[{'Name': 'instance-state-name', 'Values': ['pending', 'running']},
    #                  {'Name': 'tag:deployment_id', 'Values': [deployment_id]}])

    #     instances: list = self.__parse_aws_query(response)

    #     self.__update_current_deployment(instances)

    def __fetch_aws_instances(self, deployment_id: str):
        logger.debug(
            f"Fetching AWS instances for deployment_id = '{deployment_id}'")

        threads: list[threading.Thread] = []

        def fetch_aws_instances_per_region(region, deployment_id):
            logger.debug(f'Fetching AWS instances from {region}')

            try:
                ec2 = boto3.client('ec2', region_name=region)
                response = ec2.describe_instances(
                    Filters=[{'Name': 'instance-state-name', 'Values': ['pending', 'running']},
                             {'Name': 'tag:deployment_id', 'Values': [deployment_id]}])

                instances: list = self.__parse_aws_query(response)
            except Exception as e:
                self.__log_error(e)

            if instances:
                self.__update_current_deployment(instances)
        try:
            ec2 = boto3.client('ec2', region_name='us-east-1')
            regions = [x['RegionName']
                       for x in ec2.describe_regions()['Regions']]

            for region in regions:
                thread = threading.Thread(target=fetch_aws_instances_per_region, args=(
                    region, deployment_id), daemon=True)
                thread.start()
                threads.append(thread)

            for x in threads:
                x.join()
        except Exception as e:
            self.__log_error(e)

    def __fetch_gcp_instances(self, deployment_id: str, project_id: str):
        """
        Return a dictionary of all instances present in a project, grouped by their zone.

        Args:
            project_id: project ID or project number of the Cloud project you want to use.
        Returns:
            A dictionary with zone names as keys (in form of "zones/{zone_name}") and
            iterable collections of Instance objects as values.
        """
        logger.debug(
            f"Fetching GCP instances for deployment_id = '{deployment_id}'")

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
                    if x.status in ('PROVISIONING', 'STAGING', 'RUNNING'):
                        instances.append(self.__parse_gcp_query(
                            x, zone[6:-2], zone[-1]))
        if instances:
            self.__update_current_deployment(instances)

    def __fetch_azure_instance_network_config(self, vm):

        try:
            credential = EnvironmentCredential()

            client = ComputeManagementClient(
                credential, self.azure_subscription_id)
            netclient = NetworkManagementClient(
                credential, self.azure_subscription_id)

            # check VM is in running state
            statuses = client.virtual_machines.instance_view(
                self.azure_resource_group, vm.name).statuses
            status = len(statuses) >= 2 and statuses[1]

            if status and status.code == 'PowerState/running':
                nic_id = vm.network_profile.network_interfaces[0].id
                nic = netclient.network_interfaces.get(
                    self.azure_resource_group, nic_id.split('/')[-1])

                private_ip = nic.ip_configurations[0].private_ip_address
                pip = netclient.public_ip_addresses.get(
                    self.azure_resource_group,
                    nic.ip_configurations[0].public_ip_address.name)
                public_ip = pip.ip_address
                public_hostname = ''

            return private_ip, public_ip, public_hostname

        except Exception as e:
            logger.error(e)
            self.__log_error(e)

    def __get_azure_instance_details(self, vm):

        self.__update_current_deployment(
            self.__parse_azure_query(
                vm, *self.__fetch_azure_instance_network_config(vm))
        )

    def __fetch_azure_instances(self, deployment_id: str):
        logger.debug(
            f"Fetching Azure instances for deployment_id = '{deployment_id}'")

        threads: list[threading.Thread] = []

        try:
            # Acquire a credential object.
            credential = EnvironmentCredential()

        except Exception as e:
            logger.warning(e)
            return

        client = ComputeManagementClient(
            credential, self.azure_subscription_id)

        vm_list = client.virtual_machines.list(self.azure_resource_group)
        for vm in vm_list:
            if vm.tags.get('deployment_id', '') == deployment_id:
                thread = threading.Thread(
                    target=self.__get_azure_instance_details, args=(vm,), daemon=True)
                thread.start()
                threads.append(thread)

        for x in threads:
            x.join()

    def __update_current_deployment(self, instances: list):
        with self._lock:
            logger.debug("Updating pre-existing instances list")
            self.instances += instances

    def __update_new_deployment(self, instances: list):
        with self._lock:
            logger.debug("Updating new instances list")
            self.new_instances += instances

    def __log_error(self, error: str):
        with self._lock:
            logger.debug("Updating errors list")
            self.errors.append(error)

    def __build_deployment(self):
        # 4. loop through the 'deployment' struct
        #    - through each cluster and copies
        #    - through each group within each cluster

        # loop through each cluster item in the deployment list
        for cluster in self.deployment:

            # extract the cluster name for all copies,
            # then, for each requested copy, add the index suffix
            cluster_name: str = cluster['cluster_name']
            for x in range(int(cluster.get('copies', 1))):
                self.__build_cluster(f'{cluster_name}-{x}', cluster)

    def __build_cluster(self, cluster_name: str, cluster: dict):

        # for each group in the cluster,
        # put all cluster defaults into the group
        for group in cluster.get('groups', []):
            self.__build_group(
                cluster_name, self.__merge_dicts(cluster, group))

    def __build_group(self, cluster_name, group: dict):
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

        # get all instances in the current group
        current_group = []
        for x in self.instances[:]:
            if x['cluster_name'] == cluster_name \
                    and x['group_name'] == group['group_name'] \
                    and x['region'] == group['region'] \
                    and x['zone'] == group['zone']:
                current_group.append(x)
                self.instances.remove(x)

        current_count = len(current_group)
        new_exact_count = int(group.get('exact_count', 0))

        # CASE 1
        if current_count == new_exact_count:
            pass

        # CASE 2: ADD instances
        elif current_count < new_exact_count:
            self.changed = True
            target = {
                'aws': self.__provision_aws_vm,
                'gcp': self.__provision_gcp_vm,
                'azure': self.__provision_azure_vm
            }

            for x in range(new_exact_count - current_count):
                thread = threading.Thread(
                    target=target[group['cloud']], args=(cluster_name, group, x))
                thread.start()
                self.threads.append(thread)

        # CASE 3: REMOVE instances
        else:
            self.changed = True
            for x in range(current_count - new_exact_count):
                self.instances.append(current_group.pop(-1))

        self.__update_new_deployment(current_group)

    def __provision_aws_vm(self, cluster_name: str, group: dict, x: int):
        logger.debug('++aws %s %s %s' %
                     (cluster_name, group['region'], x))
        # volumes

        def get_type(x):
            return {
                'standard_ssd': 'gp3',
                'premium_ssd': 'io2',
                'standard_hdd': 'sc1',
                'premium_hdd': 'st1'
            }.get(x, 'gp3')

        vols = [group['volumes']['os']] + group['volumes']['data']

        bdm = []

        for i, x in enumerate(vols):
            dev = {
                'DeviceName': '/dev/sd' + (chr(ord('e')+i)),
                'Ebs': {
                    'VolumeSize': int(x.get('size', 100)),
                    'VolumeType': get_type(x.get('type', 'standard_ssd')),
                    'DeleteOnTermination': bool(x.get('delete_on_termination', True)),
                }
            }

            if x.get('type', 'standard_ssd') in ['premium_ssd', 'standard_ssd']:
                dev['Ebs']['Iops'] = int(x.get('iops', 3000))

            if x.get('throughput', False) and x.get('type', 'standard_ssd') == 'standard_ssd':
                dev['Ebs']['Throughput'] = x.get('throughput', 125)

            bdm.append(dev)

        # hardcoded value for root
        bdm[0]['DeviceName'] = '/dev/sda1'

        # tags
        tags = [{'Key': k, "Value": v} for k, v in group['tags'].items()]
        tags.append({'Key': 'deployment_id', 'Value': self.deployment_id})
        tags.append({'Key': 'ansible_user', 'Value': group['user']})
        tags.append({'Key': 'cluster_name', 'Value': cluster_name})
        tags.append({'Key': 'group_name', 'Value': group['group_name']})
        tags.append({'Key': 'inventory_groups',
                    'Value': str(group['inventory_groups'] + [cluster_name])})
        tags.append({'Key': 'extra_vars', 'Value': str(
            group.get('extra_vars', {}))})

        if group.get('role', None):
            role = {'Name': group['role']}
        else:
            role = {}
        ec2 = boto3.client('ec2', region_name=group['region'])
        try:
            response = ec2.run_instances(
                DryRun=False,
                BlockDeviceMappings=bdm,
                ImageId=group['image'],
                InstanceType=self.__get_instance_type(group),
                KeyName=group['public_key_id'],
                MaxCount=1,
                MinCount=1,
                UserData=group.get('user_data', ''),
                IamInstanceProfile=role,
                NetworkInterfaces=[{
                    "Groups": group['security_groups'],
                    "DeviceIndex": 0,
                    "SubnetId": group['subnet'],
                    "AssociatePublicIpAddress": group['public_ip']
                }],
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': tags,
                    },
                ],
            )

            # wait until instance is running
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(InstanceIds=[response['Instances'][0]['InstanceId']])

            # fetch details about the newly created instance
            response = ec2.describe_instances(
                InstanceIds=[response['Instances'][0]['InstanceId']])

            # add the instance to the list
            self.__update_new_deployment(self.__parse_aws_query(response))
        except Exception as e:
            logger.error(e)
            self.__log_error(e)

    def __provision_gcp_vm(self, cluster_name: str, group: dict, x: int):
        logger.debug('++gcp %s %s %s' %
                     (cluster_name, group['group_name'], x))

        gcpzone = '-'.join([group['region'], group['zone']])

        instance_name = self.deployment_id + '-' + str(random.randint(0, 1e16)).zfill(16)

        instance_client = google.cloud.compute_v1.InstancesClient()

        # volumes
        def get_type(x):
            return {
                'standard_ssd': 'pd-balanced',
                'premium_ssd': 'pd-ssd',
                'local_ssd': 'local-ssd',
                'standard_hdd': 'pd-standard',
                'premium_hdd': 'pd-standard'
            }.get(x, 'pd-standard')

        vols = []

        boot_disk = google.cloud.compute_v1.AttachedDisk()
        boot_disk.boot = True
        initialize_params = google.cloud.compute_v1.AttachedDiskInitializeParams()
        initialize_params.source_image = group['image']
        initialize_params.disk_size_gb = int(
            group['volumes']['os'].get('size', 30))
        initialize_params.disk_type = 'zones/%s/diskTypes/%s' % (
            gcpzone, get_type(group['volumes']['os'].get('type', 'standard_ssd')))
        boot_disk.initialize_params = initialize_params
        boot_disk.auto_delete = group['volumes']['os'].get(
            'delete_on_termination', True)
        vols.append(boot_disk)

        for i, x in enumerate(group['volumes']['data']):
            disk = google.cloud.compute_v1.AttachedDisk()
            init_params = google.cloud.compute_v1.AttachedDiskInitializeParams()
            init_params.disk_size_gb = int(x.get('size', 100))

            # local-ssd peculiarities
            if get_type(x.get('type', 'standard_ssd')) == 'local-ssd':
                disk.type = "SCRATCH"
                disk.interface = "NVME"
                del init_params.disk_size_gb

            init_params.disk_type = 'zones/%s/diskTypes/%s' % (
                gcpzone, get_type(x.get('type', 'standard_ssd')))

            disk.initialize_params = init_params
            disk.auto_delete = x.get('delete_on_termination', True)
            disk.device_name = f'disk-{i}'

            vols.append(disk)

        # tags
        tags = google.cloud.compute_v1.types.Metadata()
        item = google.cloud.compute_v1.types.Items()
        l = []

        for k, v in group.get('tags', {}).items():
            item = google.cloud.compute_v1.types.Items()
            item.key = k
            item.value = v
            l.append(item)

        item = google.cloud.compute_v1.types.Items()
        item.key = 'ansible_user'
        item.value = group['user']
        l.append(item)

        item = google.cloud.compute_v1.types.Items()
        item.key = 'cluster_name'
        item.value = cluster_name
        l.append(item)

        item = google.cloud.compute_v1.types.Items()
        item.key = 'group_name'
        item.value = group['group_name']
        l.append(item)

        item = google.cloud.compute_v1.types.Items()
        item.key = 'inventory_groups'
        item.value = json.dumps(group['inventory_groups'] + [cluster_name])
        l.append(item)

        item = google.cloud.compute_v1.types.Items()
        item.key = 'extra_vars'
        item.value = json.dumps(group.get('extra_vars', {}))
        l.append(item)

        tags.items = l

        # Use the network interface provided in the network_link argument.
        network_interface = google.cloud.compute_v1.NetworkInterface()
        network_interface.name = group['subnet']

        if group['public_ip']:
            access = google.cloud.compute_v1.AccessConfig()
            access.type_ = google.cloud.compute_v1.AccessConfig.Type.ONE_TO_ONE_NAT.name
            access.name = "External NAT"
            access.network_tier = access.NetworkTier.PREMIUM.name

            network_interface.access_configs = [access]

        # Collect information into the Instance object.
        instance = google.cloud.compute_v1.Instance()
        instance.name = instance_name
        instance.disks = vols
        instance.machine_type = f'zones/{gcpzone}/machineTypes/{self.__get_instance_type(group)}'
        instance.metadata = tags
        instance.labels = {'deployment_id': self.deployment_id}

        t = google.cloud.compute_v1.Tags()
        t.items = group['security_groups']
        instance.tags = t

        instance.network_interfaces = [network_interface]

        # Wait for the create operation to complete.
        try:
            operation = instance_client.insert(
                instance_resource=instance,
                project=self.gcp_project,
                zone=gcpzone)

            self.__wait_for_extended_operation(operation)

            logger.debug(f"GCP instance created: {instance.name}")

            # fetch details
            instance = instance_client.get(
                project=self.gcp_project,
                zone=gcpzone,
                instance=instance_name)

            # add the instance to the list
            self.__update_new_deployment(
                [self.__parse_gcp_query(instance, group['region'], group['zone'])])

        except Exception as e:
            logger.error(e)
            self.__log_error(e)

    def __provision_azure_vm(self, cluster_name: str, group: dict, x: int):
        logger.debug('++azure %s %s %s' %
                     (cluster_name, group['group_name'], x))

        try:
            # Acquire a credential object using CLI-based authentication.
            credential = EnvironmentCredential()
            client = ComputeManagementClient(
                credential, self.azure_subscription_id)

            instance_name = self.deployment_id + \
                '-' + str(random.randint(0, 1e16)).zfill(16)

            def get_type(x):
                return {
                    'standard_ssd': 'Standard_LRS',
                    'premium_ssd': 'Standard_LRS',
                    'local_ssd': 'Standard_LRS',
                    'standard_hdd': 'Standard_LRS',
                    'premium_hdd': 'Standard_LRS'
                }.get(x, 'pd-standard')

            vols = []
            i: int
            x: dict

            for i, x in enumerate(group['volumes']['data']):

                poller = client.disks.begin_create_or_update(
                    self.azure_resource_group,
                    instance_name + '-disk-' + str(i),
                    {
                        "location": group['region'],
                        "sku": {
                            "name": get_type(x.get('type', 'standard_ssd'))
                        },
                        "disk_size_gb": int(x.get('size', 100)),
                        "creation_data": {
                            "create_option": "Empty"
                        }
                    }

                )

                data_disk = poller.result()

                disk = {
                    "lun": i,
                    "name": instance_name + '-disk-' + str(i),
                    "create_option": "Attach",
                    "delete_option": "Delete" if x.get('delete_on_termination', True) else "Detach",
                    "managed_disk": {
                        "id": data_disk.id
                    }

                }
                vols.append(disk)

            # Provision the virtual machine
            publisher, offer, sku, version = group['image'].split(':')

            nsg = None
            if group['security_groups']:
                nsg = {
                    "id": "/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/networkSecurityGroups/%s" %
                    (self.azure_subscription_id,
                     self.azure_resource_group, group['security_groups'][0])
                }

            poller = client.virtual_machines.begin_create_or_update(
                self.azure_resource_group,
                instance_name,
                {
                    "location": group['region'],
                    "tags": {
                        "deployment_id": self.deployment_id,
                        "ansible_user": group['user'],
                        "cluster_name": cluster_name,
                        "group_name": group['group_name'],
                        "inventory_groups": str(group['inventory_groups'] + [cluster_name]),
                        "extra_vars": str(group.get('extra_vars', {}))
                    },
                    "storage_profile": {
                        "osDisk": {
                            "createOption": "fromImage",
                            "managedDisk": {
                                "storageAccountType": "Premium_LRS"
                            },
                            "deleteOption": "delete"
                        },
                        "image_reference": {
                            "publisher": publisher,
                            "offer": offer,
                            "sku": sku,
                            "version": version
                        },
                        "data_disks": vols
                    },
                    "hardware_profile": {
                        "vm_size": self.__get_instance_type(group),
                    },
                    "os_profile": {
                        "computer_name": instance_name,
                        "admin_username": group['user'],
                        "linux_configuration": {
                            "ssh": {
                                "public_keys": [
                                    {
                                        "path": "/home/%s/.ssh/authorized_keys" % group['user'],
                                        "key_data": group['public_key_id']
                                    }
                                ]
                            }
                        }
                    },
                    "network_profile": {
                        "network_api_version": "2021-04-01",
                        "network_interface_configurations": [
                            {
                                "name": instance_name+'-nic',
                                "delete_option": "delete",
                                "network_security_group": nsg,
                                "ip_configurations": [
                                    {
                                        "name": instance_name+'-nic',
                                        "subnet": {
                                            "id": "/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Network/virtualNetworks/%s/subnets/%s" %
                                            (self.azure_subscription_id, self.azure_resource_group,
                                             group['vpc_id'], group['subnet'])
                                        },
                                        "public_ip_address_configuration": {
                                            "name": instance_name+'-pip',
                                            "sku": {
                                                "name": "Standard",
                                                "tier": "Regional"
                                            },
                                            "delete_option": "delete",
                                            "public_ip_allocation_method": "static"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            )

            instance = poller.result()

            # add the instance to the list
            self.__update_new_deployment(
                self.__parse_azure_query(
                    instance, *
                    self.__fetch_azure_instance_network_config(instance)
                )
            )

        except Exception as e:
            logger.error(e)
            self.__log_error(e)

    def __destroy_all(self, instances: list, gcp_project: str, azure_resource_group: str):
        target = {
            'aws': self.__destroy_aws_vm,
            'gcp': self.__destroy_gcp_vm,
            'azure': self.__destroy_azure_vm
        }

        for x in instances:
            self.changed = True
            thread = threading.Thread(target=target[x['cloud']], args=(x, ))
            thread.start()
            self.threads.append(thread)

    def __destroy_aws_vm(self, instance: dict):
        logger.debug('--aws %s' % instance['id'])

        ec2 = boto3.client('ec2', region_name=instance['region'])

        response = ec2.terminate_instances(InstanceIds=[instance['id']], )

        status = response['TerminatingInstances'][0]['CurrentState']['Name']

        if status in ['shutting-down', 'terminated']:
            logger.debug(f'Deleted AWS instance: {instance}')
        else:
            logger.error('Unexpected response: {response}}')

    def __destroy_gcp_vm(self, instance: dict):
        logger.debug('--gcp %s' % instance['id'])
        """
        Send an instance deletion request to the Compute Engine API and wait for it to complete.

        Args:
            project_id: project ID or project number of the Cloud project you want to use.
            zone: name of the zone you want to use. For example: “us-west3-b”
            machine_name: name of the machine you want to delete.
        """

        instance_client = google.cloud.compute_v1.InstancesClient()

        operation = instance_client.delete(
            project=self.gcp_project,
            zone='-'.join([instance['region'], instance['zone']]),
            instance=instance['id']
        )
        # self.__wait_for_extended_operation(operation)
        logger.debug(f"Deleting GCP instance: {instance}")

    def __destroy_azure_vm(self, instance: dict):
        logger.debug('--azure %s' % instance['id'])

        # Acquire a credential object using CLI-based authentication.
        try:
            credential = EnvironmentCredential()

            client = ComputeManagementClient(
                credential, self.azure_subscription_id)

            async_vm_delete = client.virtual_machines.begin_delete(
                self.azure_resource_group, instance['id'])
            async_vm_delete.wait()
        except Exception as e:
            logger.error(e)
            self.__log_error(e)

    # UTIL METHODS
    # =========================================================================

    def __get_instance_type(self, group):
        # instance type
        gpu = str(group['instance'].get('gpu', '0'))
        cpu = str(group['instance'].get('cpu', '0'))
        mem = str(group['instance'].get('mem', '0'))
        cloud = group['cloud']
        return self.defaults['instances'][cloud][gpu][cpu][mem]

    def __merge_dicts(self, parent: dict, child: dict):

        merged = {}

        # add all kv pairs of 'import'
        for k, v in parent.get('import', {}).items():
            merged[k] = v

        # parent explicit override parent imports
        for k, v in parent.items():
            merged[k] = v

        # child imports override parent
        for k, v in child.get('import', {}).items():
            merged[k] = v

        # child explicit override child import and parent
        for k, v in child.items():
            merged[k] = v

        # merge the items in tags, child overrides parent
        tags_dict = parent.get('tags', {})
        for k, v in child.get('tags', {}).items():
            tags_dict[k] = v

        merged['tags'] = tags_dict

        # aggregate the inventory groups
        merged['inventory_groups'] = list(set(parent.get(
            'inventory_groups', []) + merged.get('inventory_groups', [])))

        # aggregate the security groups
        merged['security_groups'] = list(set(parent.get(
            'security_groups', []) + merged.get('security_groups', [])))

        # group_name
        merged.setdefault('group_name', sorted(merged['inventory_groups'])[0])

        # aggregate the volumes
        # TODO

        return merged

    def __wait_for_extended_operation(self, operation: ExtendedOperation):

        result = operation.result(timeout=300)

        if operation.error_code:
            logger.debug(
                f"GCP Error: {operation.error_code}: {operation.error_message}")

        return result


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

    instances: list = []

    try:
        instances, changed = CloudInstance(
            module.params['deployment_id'],
            True if module.params['state'] == 'present' else False,
            module.params['deployment'],
            module.params['defaults']
        ).run()

    except Exception as e:
        module.fail_json(msg=e)

    logger.debug("Deployment instances list:")
    for x in instances:
        logger.debug(f'\t{x}')

    # Outputs
    module.exit_json(changed=changed, out=instances)


if __name__ == '__main__':
    main()
