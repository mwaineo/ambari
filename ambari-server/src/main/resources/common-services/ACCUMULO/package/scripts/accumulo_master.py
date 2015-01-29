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

import sys
from resource_management import *

from accumulo import accumulo
         
class AccumuloMaster(Script):
  def install(self, env):
    self.install_packages(env)
    self.configure(env)
    
  def configure(self, env):
    import params
    env.set_params(params)
    
    accumulo(name='master')
    
    exec_string = format("{params.accumulo_cmd} init --instance-name {params.accumulo_instance_name} --password {params.accumulo_root_password} --clear-instance-name >{params.log_dir}/accumulo-{params.accumulo_user}-init.out 2>{params.log_dir}/accumulo-{params.accumulo_user}-init.err")

    try:
      Execute( exec_string,
             not_if=format("{params.hadoop_prefix}/bin/hadoop fs -stat {params.accumulo_hdfs_root_dir}/instance_id"),
             user=params.accumulo_user)
    except Exception, e:
      try:
        Execute( format("{params.hadoop_prefix}/bin/hadoop fs -rm -R {params.accumulo_hdfs_root_dir}"),
             user=params.accumulo_user)
      except:
        pass
      raise e

  def start(self, env):
      import params
      env.set_params(params)
      self.configure(env)
      
      Execute(format("{params.daemon_script_start} {params.hostname} master"),
             user=params.accumulo_user
      )
      Execute(format("{params.daemon_script_start} {params.hostname} monitor"),
             user=params.accumulo_user
      )
      Execute(format("{params.daemon_script_start} {params.hostname} gc"),
             user=params.accumulo_user
      )
      
  def stop(self, env):
      import params
      env.set_params(params)

      Execute(format("{params.daemon_script_stop} {params.hostname}"),
             user=params.accumulo_user
      )

  def status(self, env):
    pass


if __name__ == "__main__":
  AccumuloMaster().execute()
