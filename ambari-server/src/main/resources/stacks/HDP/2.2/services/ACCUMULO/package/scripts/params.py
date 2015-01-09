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
import status_params

config = Script.get_config()

security_enabled = config['configurations']['cluster-env']['security_enabled']

# local structure
log_dir = config['configurations']['accumulo-env']['accumulo_log_dir']
accumulo_conf_dir = "/etc/accumulo/conf"
hadoop_conf_dir = "/etc/hadoop/conf"
hadoop_bin_dir = format("/usr/hdp/current/hadoop-client/bin")
daemon_script_start = format('/usr/hdp/current/accumulo-client/bin/start-server.sh')
daemon_script_stop = format('/usr/hdp/current/accumulo-client/bin/stop-here.sh')
accumulo_cmd = format('/usr/hdp/current/accumulo-client/bin/accumulo')

# user things
accumulo_user = status_params.accumulo_user

#java things
java64_home = config['hostLevelParams']['java_home']
hadoop_prefix = config['configurations']['accumulo-env']['hadoop_prefix']
hadoop_conf_dir = config['configurations']['accumulo-env']['hadoop_conf_dir']
zookeeper_home = config['configurations']['accumulo-env']['zookeeper_home']
master_heapsize = config['configurations']['accumulo-env']['master_heapsize']
tserver_heapsize = config['configurations']['accumulo-env']['tserver_heapsize']
monitor_heapsize = config['configurations']['accumulo-env']['monitor_heapsize']
gc_heapsize = config['configurations']['accumulo-env']['gc_heapsize']
other_heapsize = config['configurations']['accumulo-env']['other_heapsize']
env_sh_template = config['configurations']['accumulo-env']['content']

accumulo_env_sh_template = config['configurations']['accumulo-env']['content']
zookeeper_host = config['configurations']['accumulo-site']['instance.zookeeper.host']

#accumulo initialization parameters
accumulo_instance_name = "hdp-accumulo-instance"
accumulo_root_password = config['configurations']['accumulo-site']['trace.token.property.password']
accumulo_hdfs_root_dir = config['configurations']['accumulo-site']['instance.volumes']

accumulo_excluded_hosts = config['commandParams']['excluded_hosts']
accumulo_included_hosts = config['commandParams']['included_hosts']

# if accumulo is selected the accumulo_ts_hosts, should not be empty, but still default just in case
if 'slave_hosts' in config['clusterHostInfo']:
  ts_hosts = default('/clusterHostInfo/accumulo_ts_hosts', '/clusterHostInfo/slave_hosts') #if accumulo_ts_hosts not given it is assumed that tservers on same nodes as slaves
else:
  ts_hosts = default('/clusterHostInfo/accumulo_ts_hosts', '/clusterHostInfo/all_hosts') 

#log4j.properties
if (('accumulo-log4j' in config['configurations']) and ('content' in config['configurations']['accumulo-log4j'])):
  log4j_props = config['configurations']['accumulo-log4j']['content']
else:
  log4j_props = None

#for create_hdfs_directory
hostname = config["hostname"]
hdfs_user_keytab = config['configurations']['hadoop-env']['hdfs_user_keytab']
hdfs_user = config['configurations']['hadoop-env']['hdfs_user']
hdfs_principal_name = config['configurations']['hadoop-env']['hdfs_principal_name']
kinit_path_local = functions.get_kinit_path(["/usr/bin", "/usr/kerberos/bin", "/usr/sbin"])
import functools
#create partial functions with common arguments for every HdfsDirectory call
#to create hdfs directory we need to call params.HdfsDirectory in accumulo.py
HdfsDirectory = functools.partial(
  HdfsDirectory,
  conf_dir=hadoop_conf_dir,
  hdfs_user=hdfs_user,
  security_enabled = security_enabled,
  keytab = hdfs_user_keytab,
  kinit_path_local = kinit_path_local,
  bin_dir = hadoop_bin_dir
)
