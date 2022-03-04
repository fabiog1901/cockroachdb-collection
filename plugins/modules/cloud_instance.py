from ansible.module_utils.basic import AnsibleModule
import threading



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


# Control Logic
def process(module: AnsibleModule):
    # Extracting variables from all args for readability
    state: str = module.params['state']
    deployment_id: str = module.params['deployment_id']
    deployment: list[dict] = module.params['deployment']
    defaults: dict = module.params['defaults']

    if state == 'present':
        return ensure_present(deployment, defaults)
    elif state == 'absent':
        return ensure_absent(deployment)
    else:
        raise ValueError(f'Unexpected state: {state}')


def ensure_present(deployment: list, defaults: dict):
    threads: list[threading.Thread] = []
    
    # loop through each item in the list
    for cluster in deployment:
        cluster_name: str = cluster['cluster_name']
        for x in range(int(cluster.get('copies', 1))):
            cluster['cluster_name'] = cluster_name + '-' + str(x)
            threads += build_cluster(cluster, defaults)

    return threads

def ensure_absent():

    pass
    # check whether the deployment exists or it was already deleted


def build_cluster(cluster: dict, defaults: dict):
    threads: list[threading.Thread] = []
    for instance_group in cluster.get('instance_groups', []):
        instance_group = merge_dicts(cluster, instance_group)
        threads += build_instance_group(instance_group, defaults)
        
    return threads


def build_instance_group(instance_group: dict, defaults: dict):
    threads: list[threading.Thread] = []
    for _ in range(int(instance_group.get('exact_count', 1))):
        threads.append(build_instance(instance_group, defaults))

    return threads

def build_instance(instance_group: dict, defaults: dict):
    cloud = instance_group['cloud'].lower()
    if cloud == 'aws':
        return threading.Thread(target=build_aws_vm, args=(instance_group, defaults), daemon=True)
    elif cloud == 'azure':
        return threading.Thread(target=build_azure_vm, args=(instance_group, defaults), daemon=True)
    elif cloud == 'gcp':
        return threading.Thread(target=build_gcp_vm, args=(instance_group, defaults), daemon=True)
    else:
        raise ValueError(f'Unexpected cloud: {cloud}')


def build_aws_vm(instance: dict, defaults: dict):
    print(instance)
    print('aws vm')
    print()
    

def build_azure_vm(instance: dict, defaults: dict):
    print("azure vm")


def build_gcp_vm(instance: dict, defaults: dict):
    print('gcp vm')


def merge_dicts(parent: dict, child: dict):
    for k, v in parent.items():
        if not k in child:
            child[k] = v
    return child


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default="present", choices=['present', 'absent']),
            deployment_id=dict(type='str', required=True),
            deployment=dict(type='list', default=[]),
            defaults=dict(type='dict', default={}),
        ),
        supports_check_mode=False,
    )

    try:
        threads: list[threading.Thread] = process(module)
               
        for x in threads:
            x.start()

        for x in threads:
            x.join()

        # Outputs
        changed: bool = False
        out: dict = {}

        # module.exit_json(changed=changed, out=out)

    except Exception as e:
        module.fail_json(msg=e)


if __name__ == '__main__':
    main()
