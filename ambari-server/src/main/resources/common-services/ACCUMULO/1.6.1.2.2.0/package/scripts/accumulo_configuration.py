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

  # create a site file for server processes
  XmlConfig( "accumulo-site.xml",
            conf_dir = params.conf_dir,
            configurations = params.config['configurations']['accumulo-site'],
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
    Execute( format("{params.daemon_script} init --instance-name {"
                    "params.instance_name} --password {params.root_password} "
                    "--clear-instance-name >{params.log_dir}/accumulo-"
                    "{params.accumulo_user}-init.out 2>{params.log_dir}/"
                    "accumulo-{params.accumulo_user}-init.err"),
             not_if=as_user(format("{params.hadoop_bin_dir}/hadoop --config "
                                   "{params.hadoop_conf_dir} fs -stat "
                                   "{params.instance_volumes}"),
                            params.accumulo_user),
             user=params.accumulo_user)


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
