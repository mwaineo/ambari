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

    try:
      Execute( format("{daemon_script} init --instance-name {accumulo_instance_name} --password {accumulo_root_password} --clear-instance-name >{log_dir}/accumulo-{accumulo_user}-init.out 2>{log_dir}/accumulo-{accumulo_user}-init.err"),
             not_if=format("{hadoop_prefix}/bin/hadoop fs -stat {accumulo_hdfs_root_dir}"),
             user=params.accumulo_user)
    except Exception, e:
      try:
        Execute( format("{hadoop_prefix}/bin/hadoop fs -rm -R {accumulo_hdfs_root_dir}"),
             user=params.accumulo_user)
      except:
        pass
      raise e

  def start(self, env):
      import params
      env.set_params(params)
      self.configure(env)
      
      Execute(format("{daemon_script} master"),
             user=params.accumulo_user
      )
      
  def stop(self, env):
      import params
      env.set_params(params)

      Execute(format("{daemon_script} stopMaster"),
             user=params.accumulo_user
      )

  def status(self, env):
    pass


if __name__ == "__main__":
  AccumuloMaster().execute()
