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
import os

class AccumuloServiceCheck(Script):
  def service_check(self, env):
    import params
    env.set_params(params)

    rpassfile = format("{exec_tmp_dir}/pass0")
    cmdfile = format("{exec_tmp_dir}/cmds")
    try:
      File(rpassfile,
           mode=0600,
           group=params.user_group,
           owner=params.accumulo_user,
           content=InlineTemplate('{{root_password}}\n')
      )
      File(cmdfile,
           mode=0600,
           group=params.user_group,
           owner=params.accumulo_user,
           content=InlineTemplate('createtable testtable\n'
                                  'insert row cf cq val\n'
                                  'scan\n'
                                  'flush -w\n'
                                  'scan\n'
                                  'deletetable testtable\n')
      )
      Execute( format("cat {rpassfile} | {daemon_script} shell -u root "
                      "-f {cmdfile}"),
               user=params.accumulo_user)
    finally:
      try_remove(rpassfile)
      try_remove(cmdfile)

def try_remove(file):
  try:
    os.remove(file)
  except:
    pass

if __name__ == "__main__":
  AccumuloServiceCheck().execute()
