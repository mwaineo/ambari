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

from functions import calc_xmn_from_xms
from resource_management.libraries.functions.version import format_hdp_stack_version, compare_versions
from resource_management import *
import status_params

# server configurations
config = Script.get_config()
exec_tmp_dir = Script.get_tmp_dir()

hdp_stack_version = str(config['hostLevelParams']['stack_version'])
hdp_stack_version = format_hdp_stack_version(hdp_stack_version)
stack_is_hdp22_or_further = hdp_stack_version != "" and compare_versions(hdp_stack_version, '2.2') >= 0

#hadoop params
if stack_is_hdp22_or_further:
  hadoop_bin_dir = format("/usr/hdp/current/hadoop-client/bin")
  daemon_script = format('/usr/hdp/current/accumulo-client/bin/start-here.sh')
  accumulo_cmd = format('/usr/hdp/current/accumulo-client/bin/accumulo')
else:
  hadoop_bin_dir = "/usr/bin"
  daemon_script = format('/usr/hdp/current/accumulo/bin/start-here.sh')
  accumulo_cmd = format('/usr/hdp/current/accumulo/bin/accumulo')

hadoop_conf_dir = "/etc/hadoop/conf"
accumulo_conf_dir = "/etc/accumulo/conf"
accumulo_excluded_hosts = config['commandParams']['excluded_hosts']
accumulo_included_hosts = config['commandParams']['included_hosts']

accumulo_user = status_params.accumulo_user
accumulo_principal_name = config['configurations']['accumulo-site']['general.kerberos.principal']
smokeuser = config['configurations']['cluster-env']['smokeuser']
_authentication = config['configurations']['core-site']['hadoop.security.authentication']
security_enabled = config['configurations']['cluster-env']['security_enabled']

# this is "hadoop-metrics.properties" for 1.x stacks
metric_prop_file_name = "accumulo-metrics.xml"

# not supporting 32 bit jdk.
java64_home = config['hostLevelParams']['java_home']

log_dir = config['configurations']['accumulo-env']['accumulo_log_dir']
master_opts = config['configurations']['accumulo-env']['accumulo_master_opts']

tserver_opts = config['configurations']['accumulo-env']['accumulo_tserver_opts']

# TODO UPGRADE default, update site during upgrade

# TODO Kerberos things need to be verified
client_jaas_config_file = format("{accumulo_conf_dir}/accumulo_client_jaas.conf")
master_jaas_config_file = format("{accumulo_conf_dir}/accumulo_master_jaas.conf")
tserver_jaas_config_file = format("{accumulo_conf_dir}/accumulo_tserver_jaas.conf")

ganglia_server_hosts = default('/clusterHostInfo/ganglia_server_host', []) # is not passed when ganglia is not present
ganglia_server_host = '' if len(ganglia_server_hosts) == 0 else ganglia_server_hosts[0]

# if accumulo is selected the accumulo_ts_hosts, should not be empty, but still default just in case
if 'slave_hosts' in config['clusterHostInfo']:
  ts_hosts = default('/clusterHostInfo/accumulo_ts_hosts', '/clusterHostInfo/slave_hosts') #if accumulo_ts_hosts not given it is assumed that region servers on same nodes as slaves
else:
  ts_hosts = default('/clusterHostInfo/accumulo_ts_hosts', '/clusterHostInfo/all_hosts') 

smoke_test_user = config['configurations']['cluster-env']['smokeuser']
smokeuser_permissions = "RWXCA"
service_check_data = functions.get_unique_id_and_date()
user_group = config['configurations']['cluster-env']["user_group"]

# TODO Kerberos things need to be verified
#if security_enabled:
#  _hostname_lowercase = config['hostname'].lower()
#  master_jaas_princ = config['configurations']['accumulo-site']['general.kerberos.principal'].replace('_HOST',_hostname_lowercase)
#  tserver_jaas_princ = config['configurations']['accumulo-site']['general.kerberos.principal'].replace('_HOST',_hostname_lowercase)
# TODO Kerberos things need to be verified
#master_keytab_path = config['configurations']['accumulo-site']['general.kerberos.keytab']
#tserver_keytab_path = config['configurations']['accumulo-site']['general.kerberos.keytab']
#smoke_user_keytab = config['configurations']['cluster-env']['smokeuser_keytab']
#accumulo_user_keytab = config['configurations']['accumulo-env']['accumulo_user_keytab']
#kinit_path_local = functions.get_kinit_path(["/usr/bin", "/usr/kerberos/bin", "/usr/sbin"])
#if security_enabled:
#  kinit_cmd = format("{kinit_path_local} -kt {accumulo_user_keytab} {accumulo_principal_name};")
#else:
#  kinit_cmd = ""

#log4j.properties
if (('accumulo-log4j' in config['configurations']) and ('content' in config['configurations']['accumulo-log4j'])):
  log4j_props = config['configurations']['accumulo-log4j']['content']
else:
  log4j_props = None
  
accumulo_env_sh_template = config['configurations']['accumulo-env']['content']

accumulo_hdfs_root_dir = config['configurations']['accumulo-site']['instance.volumes']
accumulo_staging_dir = "/apps/accumulo/staging"
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
