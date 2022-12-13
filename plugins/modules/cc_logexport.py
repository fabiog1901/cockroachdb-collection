#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = '''
module: cc_logexport

short_description: Manage log export configuration.

description:
  - Enable/Disable log exports to the cloud provider default monitoring solution.
  - A Cockroach Cloud Service Account API Key is required.
  - Export the key as environment variable 'CC_KEY' or pass it on module invokation

version_added: "1.0.0"

author: "Cockroach Labs"

options:
  state:
    description: "Allowed values: enable, disable."
    default: enable
    type: str
  cluster_id:
    description: The UUID or the name of the cluster you want to get information for.
    type: str
    required: True
  auth_principal:
    description: auth_principal is either the AWS Role ARN that identifies a role that the cluster account can assume to write to CloudWatch or the GCP Project ID that the cluster service account has permissions to write to for cloud logging.
    type: str
    required: True
  default_log_name:
    description: log_name is an identifier for the logs in the customer's log sink.
    type: str
    default: cockroach
  default_redact:
    description: redact allows the customer to set a default redaction policy for logs before they are exported to the target sink. If a group config omits a redact flag and this one is set to true, then that group will receive redacted logs.
    type: bool
    default: False
  region:
    description: region allows the customer to override the destination region for all logs for a cluster.
    type: str
  cloud:
    description: "Allowed: AWS┃GCP"
    type: str
  wait:
    description: wait for long operation to complete
    type: bool
    default: True
  groups:
    description: 
      - groups is a collection of log group configurations that allows the customer to define collections of CRDB log channels that are aggregated separately at the target sink.
      - Each item contains an export configuration for a single log group which can route logs for a subset of CRDB channels.
    type: list
    elements: dict
    suboptions:
      channels:
        description: channels is a list of CRDB log channels to include in this group.
        type: list
        elements: str
      log_name:
        description: ''
        type: str
      min_level:
        description: 
          - min_level is the minimum log level to filter to this log group. 
          - Should be one of INFO, WARNING, ERROR, FATAL.
        type: str
        default: INFO
      redact:
        description: ''
        type: bool
        default: False
  
  
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
- name: enable log export to Google Log Explorer
  fabiog1901.cockroachdb.cc_logexport:
    state: present
    cluster_id: fabio-cluster2
    auth_principal: my-gcp-project
    groups: 
      - channels:
          - HEALTH
          - OPS
        log_name: crdb-ops
        min_level: INFO
        redact: no
    
    default_log_name: crdb
    default_redact: no
    region: us-central1
    cloud: GCP
    wait: yes
    api_client:
      api_version: '2022-09-20'
    register: out
'''

RETURN = '''
logexport:
  description: LogExportClusterInfo contains a package of information that fully describes both the intended state of the log export configuration for a specific cluster but also some metadata around its deployment status, any error messages, and some timestamps.
  type: dict
  elements: dict
  contains:
    cluster_id:
      description: ""
      type: str
    created_at:
      description: ""
      type: str
    updated_at:
      description: ""
      type: str
    status:
      description:
        - "LogExportStatus encodes the possible states that a configuration can be in as it is created, deployed, and disabled."
        - "Allowed Values: DISABLED┃DISABLING┃DISABLE_FAILED┃ENABLED┃ENABLING┃ENABLE_FAILED"
    user_message:
      description: ""
      type: str
    spec:
      description: LogExportClusterSpecification contains all the data necessary to configure log export for an individual cluster. Users would supply this data via the API and also receive it back when inspecting the state of their log export configuration.
      type: dict
      elements: dict
      contains:
        auth_principal:
          description: auth_principal is either the AWS Role ARN that identifies a role that the cluster account can assume to write to CloudWatch or the GCP Project ID that the cluster service account has permissions to write to for cloud logging.
          type: str
        log_name:
          description: log_name is an identifier for the logs in the customer's log sink.
          type: str
        redact:
          description: redact controls whether logs are redacted before forwarding to customer sinks. By default they are not redacted.
          type: bool
        region:
          description: region controls whether all logs are sent to a specific region in the customer sink. By default, logs will remain their region of origin depending on the cluster node's region.
          type: str
        type:
          description:
            - LogExportType encodes the cloud selection that we're exporting to along with the cloud logging platform.
            - Currently, each cloud has a single logging platform.
            - "Allowed: AWS_CLOUDWATCH┃GCP_CLOUD_LOGGING"
          type: str
        groups:
          description:
            - groups is a collection of log group configurations to customize which CRDB channels get aggregated into different groups at the target sink. Unconfigured channels will be sent to the default locations via the settings above.
            - LogExportGroup contains an export configuration for a single log group which can route logs for a subset of CRDB channels.
          type: list
          elements: dict
          contains:
            channels:
              description: channels is a list of CRDB log channels to include in this group.
              type: list
              elements: str
            log_name:
              description: log_name is the name of the group, reflected in the log sink
              type: str
            min_level:
              description:
                - min_level is the minimum log level to filter to this log group.
                - Should be one of INFO, WARNING, ERROR, FATAL.
              type: str
            redact:
              description: redact is a boolean that governs whether this log group should aggregate redacted logs. Redaction settings will inherit from the cluster log export defaults if unset.
              type: str
'''


# ANSIBLE
import time
import json
from cockroachdb_cloud_client.api.cockroach_cloud import cockroach_cloud_get_log_export_info, cockroach_cloud_delete_log_export, cockroach_cloud_enable_log_export
from ..module_utils.utils import get_cluster_id, AnsibleException, APIClient, ApiClientArgs
from ansible.module_utils.basic import AnsibleModule

from cockroachdb_cloud_client.models.cockroach_cloud_enable_log_export_enable_log_export_request import CockroachCloudEnableLogExportEnableLogExportRequest as log_exp_req
from cockroachdb_cloud_client.models.log_export_group import LogExportGroup
from cockroachdb_cloud_client.models.log_export_type import LogExportType
from cockroachdb_cloud_client.models.log_export_status import LogExportStatus
from cockroachdb_cloud_client.models.log_export_cluster_info import LogExportClusterInfo

class Client:

    def __init__(self, api_client_args: ApiClientArgs,
                 state: str, cluster_id: str, auth_principal: str, default_log_name: str, default_redact: bool,
                 region: str, cloud: str, groups: list, wait: bool):

        # cc client
        self.client = APIClient(api_client_args)

        # vars
        self.state = state
        self.cluster_id = get_cluster_id(self.client, cluster_id)
        self.auth_principal = auth_principal
        self.default_log_name = default_log_name
        self.default_redact = default_redact
        self.region = region
        self.cloud = cloud
        self.groups: dict[dict] = groups
        self.wait: bool = wait

        # return vars
        self.out: str = ''
        self.changed: bool = False

    def run(self):

        def get_logexport() -> LogExportClusterInfo:
            r = cockroach_cloud_get_log_export_info.sync_detailed(
                client=self.client,
                cluster_id=self.cluster_id)

            if r.status_code == 200:
                return r.parsed
            # check if logexport config is not found as it was never enabled before
            elif r.status_code == 404 and json.loads(r.content)['code'] == 5:
                return LogExportClusterInfo()
            else:
                raise AnsibleException(r)

        logexport: LogExportClusterInfo = get_logexport()
        
        if self.state == 'enable':
            # we should determine if the new config is the same as the current one.
            # if it is, changed=False
            
            if self.cloud == 'AWS':
                t = LogExportType.AWS_CLOUDWATCH
            else:
                t = LogExportType.GCP_CLOUD_LOGGING

            groups: list[LogExportGroup] = []
            for g in self.groups:
                if g.get('channels', []) == []:
                    raise Exception({"content" : "groups.channels must be a list of channels."})
                
                groups.append(
                    LogExportGroup(
                        channels=g.get('channels'),
                        log_name=g['log_name'] if g['log_name'] else '-'.join(g['channels']).lower(),
                        min_level=g.get('min_level', 'INFO'),
                        redact=g.get('redact', False)
                    )
                )

            c = log_exp_req(
                auth_principal=self.auth_principal,
                log_name=self.default_log_name,
                redact=self.default_redact,
                region=self.region,
                type=t,
                groups=groups
            )

            r = cockroach_cloud_enable_log_export.sync_detailed(
                client=self.client,
                cluster_id=self.cluster_id,
                json_body=c)

            if r.status_code == 200:
                if self.wait:
                    while r.parsed.status == LogExportStatus.ENABLING:
                        time.sleep(30) 
                        r = cockroach_cloud_get_log_export_info.sync_detailed(
                            client=self.client, cluster_id=self.cluster_id)
                    
                logexport = r.parsed
            else:
                raise AnsibleException(r)
            
            return logexport.to_dict(), True
        
        else: # self.state == 'disable'
            if logexport.status in [LogExportStatus.ENABLED, LogExportStatus.ENABLING]:
                r = cockroach_cloud_delete_log_export.sync_detailed(
                    client=self.client,
                    cluster_id=self.cluster_id)

                if r.status_code == 200:
                    logexport = r.parsed
                else:
                    raise AnsibleException(r)


                if self.wait:
                    while r.parsed.status == LogExportStatus.DISABLING:
                        time.sleep(30) 
                        r = cockroach_cloud_get_log_export_info.sync_detailed(
                            client=self.client, cluster_id=self.cluster_id)
                        
                    
                return logexport.to_dict(), True
            else:
                return logexport.to_dict(), False
        
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
        state=dict(type='str', choices=[
                   'enable', 'disable'], default='enable'),
        cluster_id=dict(type='str', required=True),

        auth_principal=dict(type='str', required=True),
        default_log_name=dict(type='str', default='cockroach'),
        default_redact=dict(type='bool', default=False),
        region=dict(type='str'),
        cloud=dict(type='str', choices=['AWS', 'GCP']),
        groups=dict(
            default=[],
            type='list',
            elements='dict',
            options=dict(
                channels=dict(type='list', elements='str'),
                log_name=dict(type='str', required=False),
                min_level=dict(type='str', choices=['INFO', 'WARNING', 'ERROR', 'FATAL'], default='INFO'),
                redact=dict(type='bool', default=False)
                
            )
        ),
        wait=dict(type='bool', default='True')
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
            module.params['auth_principal'],
            module.params['default_log_name'],
            module.params['default_redact'],
            module.params['region'],
            module.params['cloud'],
            module.params['groups'],
            module.params['wait']
        ).run()

    except Exception as e:
        module.fail_json(meta=module.params, msg=e.args)

    # Outputs
    module.exit_json(meta=module.params, changed=changed, logexport=out)


if __name__ == '__main__':
    main()
