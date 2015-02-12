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

def setup_conf_dir(name=None): # 'master' or 'tserver' or 'monitor' or 'gc' or 'tracer' or 'client'
  import params
  import status_params

  # create the conf directory
  Directory( params.conf_dir,
      owner = params.accumulo_user,
      group = params.user_group,
      recursive = True
  )

  # create env file
  File(format("{params.conf_dir}/accumulo-env.sh"),
       mode=0644,
       group=params.user_group,
       owner=params.accumulo_user,
       content=InlineTemplate(params.env_sh_template)
  )

  if name == 'client':
    # create a site file for client processes
    # this special client config will be overwritten if a server process is
    # started on the same node
    XmlConfig( "accumulo-site.xml",
              conf_dir = params.conf_dir,
              configurations = params.config['configurations']['accumulo-site'],
              configuration_attributes=params.config['configuration_attributes']['accumulo-site'],
              owner = params.accumulo_user,
              group = params.user_group,
              mode = 0600
    )
  else:
    # create a site file for server processes
    configs = {}
    configs.update(params.config['configurations']['accumulo-site'])
    configs["instance.secret"] = params.config['configurations']['accumulo-env']['instance_secret']
    configs["trace.token.property.password"] = params.trace_password
    XmlConfig( "accumulo-site.xml",
               conf_dir = params.conf_dir,
               configurations = configs,
               configuration_attributes=params.config['configuration_attributes']['accumulo-site'],
               owner = params.accumulo_user,
               group = params.user_group,
               mode = 0600
    )

  # create pid dir
  Directory( params.pid_dir,
    owner = params.accumulo_user,
    group = params.user_group,
    recursive = True
  )

  # create log dir
  Directory (params.log_dir,
    owner = params.accumulo_user,
    group = params.user_group,
    recursive = True
  )

  # create logging configuration files
  accumulo_StaticFile("log4j.properties")
  accumulo_StaticFile("auditLog.xml")
  accumulo_StaticFile("generic_logger.xml")
  accumulo_StaticFile("monitor_logger.xml")

  # create host files
  accumulo_StaticFile("tracers")
  accumulo_StaticFile("gc")
  accumulo_StaticFile("monitor")
  accumulo_StaticFile("slaves")
  accumulo_StaticFile("masters")

  if params.has_metric_collector:
    accumulo_TemplateConfig( "hadoop-metrics2-accumulo.properties")

  if name == 'master':
    params.HdfsDirectory(format("/user/{params.accumulo_user}"),
                         action="create_delayed",
                         owner=params.accumulo_user,
                         mode=0700
    )
    params.HdfsDirectory(format("{params.parent_dir}"),
                         action="create_delayed",
                         owner=params.accumulo_user,
                         mode=0700
    )
    params.HdfsDirectory(None, action="create")
    passfile = format("{params.conf_dir}/pass")
    try:
      File(passfile,
           mode=0600,
           group=params.user_group,
           owner=params.accumulo_user,
           content=InlineTemplate('{{root_password}}\n'
                                  '{{root_password}}\n')
      )
      Execute( format("cat {passfile} | {params.daemon_script} init "
                      "--instance-name {params.instance_name} "
                      "--clear-instance-name "
                      ">{params.log_dir}/accumulo-{params.accumulo_user}-init.out "
                      "2>{params.log_dir}/accumulo-{params.accumulo_user}-init.err"),
               not_if=as_user(format("{params.hadoop_bin_dir}/hadoop --config "
                                     "{params.hadoop_conf_dir} fs -stat "
                                     "{params.instance_volumes}"),
                              params.accumulo_user),
               user=params.accumulo_user)
    finally:
      os.remove(passfile)

  if name == 'tracer':
    rpassfile = format("{params.conf_dir}/pass0")
    passfile = format("{params.conf_dir}/pass")
    cmdfile = format("{params.conf_dir}/cmds")
    try:
      File(rpassfile,
           mode=0600,
           group=params.user_group,
           owner=params.accumulo_user,
           content=InlineTemplate('{{root_password}}\n')
      )
      File(passfile,
           mode=0600,
           group=params.user_group,
           owner=params.accumulo_user,
           content=InlineTemplate('{{root_password}}\n'
                                  '{{trace_password}}\n'
                                  '{{trace_password}}\n')
      )
      File(cmdfile,
           mode=0600,
           group=params.user_group,
           owner=params.accumulo_user,
           content=InlineTemplate('createuser {{trace_user}}\n'
                                  'grant -s System.CREATE_TABLE -u {{trace_user}}\n')
      )
      Execute( format("cat {passfile} | {params.daemon_script} shell -u root "
                      "-f {cmdfile}"),
               not_if=as_user(format("cat {rpassfile} | {params.daemon_script} "
                                     "shell -u root -e \"userpermissions -u "
                                     "{params.trace_user}\""),
                              params.accumulo_user),
               user=params.accumulo_user)
    finally:
      try_remove(rpassfile)
      try_remove(passfile)
      try_remove(cmdfile)

def try_remove(file):
  try:
    os.remove(file)
  except:
    pass

# create file 'name' from template
def accumulo_TemplateConfig(name,
                         tag=None
                         ):
  import params

  TemplateConfig( format("{params.conf_dir}/{name}"),
      owner = params.accumulo_user,
      group = params.user_group,
      template_tag = tag
  )

# create static file 'name'
def accumulo_StaticFile(name):
  import params

  File(format("{params.conf_dir}/{name}"),
    mode=0644,
    group=params.user_group,
    owner=params.accumulo_user,
    content=StaticFile(name)
  )
