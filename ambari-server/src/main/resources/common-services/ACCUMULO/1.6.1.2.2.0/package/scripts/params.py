#!/usr/bin/env python
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

from resource_management import *
from resource_management.libraries.functions.default import default
import status_params

# server configurations
config = Script.get_config()

# accumulo local directory structure
log_dir = config['configurations']['accumulo-env']['accumulo_log_dir']
conf_dir = "/etc/accumulo/conf"
daemon_script = "/usr/hdp/current/accumulo-client/bin/accumulo"

# service locations
hadoop_prefix = "/usr/hdp/current/hadoop-client"
hadoop_bin_dir = format("{hadoop_prefix}/bin")
hadoop_conf_dir = "/etc/hadoop/conf"
zookeeper_home = "/usr/hdp/current/zookeeper-client"

# user and status
accumulo_user = status_params.accumulo_user
user_group = config['configurations']['cluster-env']['user_group']
pid_dir = status_params.pid_dir

# accumulo env
java64_home = config['hostLevelParams']['java_home']
master_heapsize = config['configurations']['accumulo-env']['master_heapsize']
tserver_heapsize = config['configurations']['accumulo-env']['tserver_heapsize']
monitor_heapsize = config['configurations']['accumulo-env']['monitor_heapsize']
gc_heapsize = config['configurations']['accumulo-env']['gc_heapsize']
other_heapsize = config['configurations']['accumulo-env']['other_heapsize']
env_sh_template = config['configurations']['accumulo-env']['content']

# accumulo initialization parameters
instance_name = config['configurations']['accumulo-env']['accumulo_instance_name']
root_password = config['configurations']['accumulo-env']['accumulo_root_password']
instance_volumes = config['configurations']['accumulo-site']['instance.volumes']
parent_dir = instance_volumes[0:instance_volumes.rfind('/')]

# metrics2 properties
ganglia_server_hosts = default('/clusterHostInfo/ganglia_server_host', []) # is not passed when ganglia is not present
ganglia_server_host = '' if len(ganglia_server_hosts) == 0 else ganglia_server_hosts[0]
ams_collector_hosts = default("/clusterHostInfo/metric_collector_hosts", [])
has_metric_collector = not len(ams_collector_hosts) == 0
if has_metric_collector:
  metric_collector_host = ams_collector_hosts[0]
  metric_collector_port = default("/configurations/ams-site/timeline.metrics.service.webapp.address", "0.0.0.0:8188")
  if metric_collector_port and metric_collector_port.find(':') != -1:
    metric_collector_port = metric_collector_port.split(':')[1]
  pass

security_enabled = config['configurations']['cluster-env']['security_enabled']

#for create_hdfs_directory
hostname = config["hostname"]
hdfs_user_keytab = config['configurations']['hadoop-env']['hdfs_user_keytab']
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = config['configurations']['hadoop-env']['hdfs_principal_name']
kinit_path_local = functions.get_kinit_path(["/usr/bin", "/usr/kerberos/bin", "/usr/sbin"])
import functools
#create partial functions with common arguments for every HdfsDirectory call
#to create hdfs directory we need to call params.HdfsDirectory in code
HdfsDirectory = functools.partial(
  HdfsDirectory,
  conf_dir=hadoop_conf_dir,
  hdfs_user=hdfs_user,
  security_enabled = security_enabled,
  keytab = hdfs_user_keytab,
  kinit_path_local = kinit_path_local,
  bin_dir = hadoop_bin_dir
)