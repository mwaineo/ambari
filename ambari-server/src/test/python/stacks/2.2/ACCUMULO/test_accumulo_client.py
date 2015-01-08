#!/usr/bin/env python

'''
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
'''
from mock.mock import MagicMock, call, patch
from stacks.utils.RMFTestCase import *

@patch("os.path.exists", new = MagicMock(return_value=True))
class TestAccumuloClient(RMFTestCase):
  
  def test_configure_secured(self):
    self.executeScript("2.2/services/ACCUMULO/package/scripts/accumulo_client.py",
                   classname = "AccumuloClient",
                   command = "configure",
                   config_file="secured.json"
    )
    self.assertNoMoreResources() 
    
  def test_configure_default(self):
    self.executeScript("2.2/services/ACCUMULO/package/scripts/accumulo_client.py",
                   classname = "AccumuloClient",
                   command = "configure",
                   config_file="default.json"
    )
    
    self.assertResourceCalled('Directory', '/etc/accumulo/conf',
      owner = 'accumulo',
      group = 'hadoop',
      recursive = True,
    )

    self.assertResourceCalled('XmlConfig', 'accumulo-site.xml',
      owner = 'accumulo',
      group = 'hadoop',
      conf_dir = '/etc/accumulo/conf',
      configurations = self.getConfig()['configurations']['accumulo-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['accumulo-site']
    )
    self.assertResourceCalled('XmlConfig', 'hdfs-site.xml',
      owner = 'accumulo',
      group = 'hadoop',
      conf_dir = '/etc/accumulo/conf',
      configurations = self.getConfig()['configurations']['hdfs-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['hdfs-site']
    )
    self.assertResourceCalled('XmlConfig', 'hdfs-site.xml',
      owner = 'hdfs',
      group = 'hadoop',
      conf_dir = '/etc/hadoop/conf',
      configurations = self.getConfig()['configurations']['hdfs-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['hdfs-site']
    )
    self.assertResourceCalled('File', '/etc/accumulo/conf/accumulo-policy.xml',
      owner = 'accumulo',
      group = 'hadoop',
    )
    self.assertResourceCalled('File', '/etc/accumulo/conf/accumulo-env.sh',
        content = InlineTemplate(self.getConfig()['configurations']['accumulo-env']['content']),
        owner = 'accumulo',
    )
    self.assertResourceCalled('TemplateConfig', '/etc/accumulo/conf/hadoop-metrics2-accumulo.properties',
      owner = 'accumulo',
      template_tag = 'GANGLIA-RS',
    )
    self.assertResourceCalled('TemplateConfig', '/etc/accumulo/conf/masters',
      owner = 'accumulo',
      template_tag = None,
    )
    self.assertResourceCalled('File',
                              '/etc/accumulo/conf/log4j.properties',
                              mode=0644,
                              group='hadoop',
                              owner='accumulo',
                              content='log4jproperties\nline2'
    )
    self.assertNoMoreResources()
    

    

