#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


import json
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_list_sql_users, cockroach_cloud_create_sql_user, cockroach_cloud_update_sql_user_password, cockroach_cloud_delete_sql_user
from cockroachdb_cloud_client.models.cockroach_cloud_update_sql_user_password_update_sql_user_password_request import CockroachCloudUpdateSQLUserPasswordUpdateSQLUserPasswordRequest as upd_usr_req
from cockroachdb_cloud_client.models.cockroach_cloud_create_sql_user_create_sql_user_request import CockroachCloudCreateSQLUserCreateSQLUserRequest as cr_usr_req
from ..module_utils.utils import get_cluster_id, AnsibleException, APIClient, ApiClientArgs
from ansible.module_utils.basic import AnsibleModule
DOCUMENTATION = '''
module: cc_user

short_description: Manage users for a cluster.

description:
  - Create, edit, delete a user.
  - A Cockroach Cloud Service Account API Key is required.
  - Export the key as environment variable 'CC_KEY' or pass it on module invokation

version_added: "1.0.0"

author: "Cockroach Labs"

options:
  state:
    description: "Allowed values: present, absent."
    default: present
    type: str
  cluster_id:
    description: The UUID or the name of the cluster you want to get information for.
    type: str
    required: True
  name:
    description: The user name
    type: str
    required: True
  password:
    description: The user password
    type: str
    required: True
  
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
- name: create a user
  fabiog1901.cockroachdb.cc_user:
    state: present
    cluster_id: dev_cluster
    name: fabio
    password: mypassword1234
    api_client:
      api_version: '2022-09-20'
    register: out
'''

RETURN = '''
user:
  description: ''
  type: dict
  elements: dict
  contains:
    name:
      description: ''
      type: str
'''


# ANSIBLE


class Client:

    def __init__(self, api_client_args: ApiClientArgs,
                 state: str, cluster_id: str, name: str, password: str):

        # cc client
        self.client = APIClient(api_client_args)

        # vars
        self.state = state
        self.name = name
        self.cluster_id = get_cluster_id(self.client, cluster_id)
        self.password = password

        # return vars
        self.out: str = ''
        self.changed: bool = False

    def run(self):

        user = {}

        def get_user(name):

            r = cockroach_cloud_list_sql_users.sync_detailed(
                client=self.client,
                cluster_id=self.cluster_id
            )

            if r.status_code == 200:
                for x in r.parsed.users:
                    if x.name == name:
                        return x
                return None

            else:
                raise AnsibleException(r)

        user = get_user(self.name)

        if self.state == 'present':

            if user:

                c = upd_usr_req(self.password)

                r = cockroach_cloud_update_sql_user_password.sync_detailed(
                    client=self.client,
                    cluster_id=self.cluster_id,
                    name=self.name,
                    json_body=c
                )

                if r.status_code == 200:
                    user = json.loads(r.content)
                else:
                    raise AnsibleException(r)

                return user, True

            else:

                c = cr_usr_req(name=self.name, password=self.password)

                r = cockroach_cloud_create_sql_user.sync_detailed(
                    client=self.client,
                    cluster_id=self.cluster_id,
                    json_body=c)

                if r.status_code == 200:
                    user = json.loads(r.content)
                else:
                    raise AnsibleException(r)

                return user, True

        else:  # state=absent

            if user:
                r = cockroach_cloud_delete_sql_user.sync_detailed(
                    client=self.client,
                    cluster_id=self.cluster_id,
                    name=self.name)

                if r.status_code == 200:
                    user = json.loads(r.content)
                else:
                    raise AnsibleException(r)

                return user, True
            else:
                return user, False


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
        state=dict(type='str', choices=[
                   'present', 'absent'], default='present'),
        cluster_id=dict(type='str', required=True),
        name=dict(type='str', required=True),
        password=dict(type='str', no_log=True, required=True)
    ),
        supports_check_mode=False,
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
            module.params['state'],
            module.params['cluster_id'],
            module.params['name'],
            module.params['password']

        ).run()

    except Exception as e:
        module.fail_json(meta=module.params, msg=e.args)

    # Outputs
    module.exit_json(meta=module.params, changed=changed, user=out)


if __name__ == '__main__':
    main()
