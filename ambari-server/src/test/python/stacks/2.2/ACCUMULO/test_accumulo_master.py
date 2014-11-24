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
from mock.mock import MagicMock, patch
from stacks.utils.RMFTestCase import *

@patch("os.path.exists", new = MagicMock(return_value=True))
class TestAccumuloMaster(RMFTestCase):
  def test_configure_default(self):
    self.executeScript("2.0.6/services/ACCUMULO/package/scripts/accumulo_master.py",
                   classname = "AccumuloMaster",
                   command = "configure",
                   config_file="default.json"
    )
    
    self.assert_configure_default()
    self.assertNoMoreResources()

  def test_start_default(self):
    self.executeScript("2.0.6/services/ACCUMULO/package/scripts/accumulo_master.py",
                   classname = "AccumuloMaster",
                   command = "start",
                   config_file="default.json"
    )
    
    self.assert_configure_default()
    self.assertResourceCalled('Execute', '/usr/lib/accumulo/bin/accumulo-daemon.sh --config /etc/accumulo/conf start master',
      not_if = 'ls /var/run/accumulo/accumulo-accumulo-master.pid >/dev/null 2>&1 && ps `cat /var/run/accumulo/accumulo-accumulo-master.pid` >/dev/null 2>&1',
      user = 'accumulo'
    )
    self.assertNoMoreResources()
    
  def test_stop_default(self):
    self.executeScript("2.0.6/services/ACCUMULO/package/scripts/accumulo_master.py",
                   classname = "AccumuloMaster",
                   command = "stop",
                   config_file="default.json"
    )
    
    self.assertResourceCalled('Execute', '/usr/lib/accumulo/bin/accumulo-daemon.sh --config /etc/accumulo/conf stop master',
      user = 'accumulo',
      on_timeout = 'ls /var/run/accumulo/accumulo-accumulo-master.pid >/dev/null 2>&1 && ps `cat /var/run/accumulo/accumulo-accumulo-master.pid` >/dev/null 2>&1 && kill -9 `cat /var/run/accumulo/accumulo-accumulo-master.pid`', 
      timeout = 30,
    )
    
    self.assertResourceCalled('Execute', 'rm -f /var/run/accumulo/accumulo-accumulo-master.pid',
    )
    self.assertNoMoreResources()

  def test_decom_default(self):
    self.executeScript("2.0.6/services/ACCUMULO/package/scripts/accumulo_master.py",
                       classname = "AccumuloMaster",
                       command = "decommission",
                       config_file="default.json"
    )

    self.assertResourceCalled('File', '/usr/lib/accumulo/bin/draining_servers.rb',
                              content = StaticFile('draining_servers.rb'),
                              mode = 0755,
                              )
    self.assertResourceCalled('Execute', ' /usr/lib/accumulo/bin/accumulo --config /etc/accumulo/conf org.jruby.Main /usr/lib/accumulo/bin/draining_servers.rb add host1',
                              logoutput = True,
                              user = 'accumulo',
                              )
    self.assertResourceCalled('Execute', ' /usr/lib/accumulo/bin/accumulo --config /etc/accumulo/conf org.jruby.Main /usr/lib/accumulo/bin/region_mover.rb unload host1',
                              logoutput = True,
                              user = 'accumulo',
                              )
    self.assertResourceCalled('Execute', ' /usr/lib/accumulo/bin/accumulo --config /etc/accumulo/conf org.jruby.Main /usr/lib/accumulo/bin/draining_servers.rb add host2',
                              logoutput = True,
                              user = 'accumulo',
                              )
    self.assertResourceCalled('Execute', ' /usr/lib/accumulo/bin/accumulo --config /etc/accumulo/conf org.jruby.Main /usr/lib/accumulo/bin/region_mover.rb unload host2',
                              logoutput = True,
                              user = 'accumulo',
                              )
    self.assertNoMoreResources()

  def test_decom_default_draining_only(self):
    self.executeScript("2.0.6/services/ACCUMULO/package/scripts/accumulo_master.py",
                       classname = "AccumuloMaster",
                       command = "decommission",
                       config_file="default.accumulodecom.json"
    )

    self.assertResourceCalled('File', '/usr/lib/accumulo/bin/draining_servers.rb',
                              content = StaticFile('draining_servers.rb'),
                              mode = 0755,
                              )
    self.assertResourceCalled('Execute', ' /usr/lib/accumulo/bin/accumulo --config /etc/accumulo/conf org.jruby.Main /usr/lib/accumulo/bin/draining_servers.rb remove host1',
                              logoutput = True,
                              user = 'accumulo',
                              )
    self.assertNoMoreResources()

  def test_configure_secured(self):
    self.executeScript("2.0.6/services/ACCUMULO/package/scripts/accumulo_master.py",
                   classname = "AccumuloMaster",
                   command = "configure",
                   config_file="secured.json"
    )
    
    self.assert_configure_secured()
    self.assertNoMoreResources()
    
  def test_start_secured(self):
    self.executeScript("2.0.6/services/ACCUMULO/package/scripts/accumulo_master.py",
                   classname = "AccumuloMaster",
                   command = "start",
                   config_file="secured.json"
    )
    
    self.assert_configure_secured()
    self.assertResourceCalled('Execute', '/usr/lib/accumulo/bin/accumulo-daemon.sh --config /etc/accumulo/conf start master',
      not_if = 'ls /var/run/accumulo/accumulo-accumulo-master.pid >/dev/null 2>&1 && ps `cat /var/run/accumulo/accumulo-accumulo-master.pid` >/dev/null 2>&1',
      user = 'accumulo',
    )
    self.assertNoMoreResources()
    
  def test_stop_secured(self):
    self.executeScript("2.0.6/services/ACCUMULO/package/scripts/accumulo_master.py",
                   classname = "AccumuloMaster",
                   command = "stop",
                   config_file="secured.json"
    )

    self.assertResourceCalled('Execute', '/usr/lib/accumulo/bin/accumulo-daemon.sh --config /etc/accumulo/conf stop master',
      user = 'accumulo',
      on_timeout = 'ls /var/run/accumulo/accumulo-accumulo-master.pid >/dev/null 2>&1 && ps `cat /var/run/accumulo/accumulo-accumulo-master.pid` >/dev/null 2>&1 && kill -9 `cat /var/run/accumulo/accumulo-accumulo-master.pid`', 
      timeout = 30,
    )
    
    self.assertResourceCalled('Execute', 'rm -f /var/run/accumulo/accumulo-accumulo-master.pid',
    )
    self.assertNoMoreResources()

  def test_decom_secure(self):
    self.executeScript("2.0.6/services/ACCUMULO/package/scripts/accumulo_master.py",
                       classname = "AccumuloMaster",
                       command = "decommission",
                       config_file="secured.json"
    )

    self.assertResourceCalled('File', '/usr/lib/accumulo/bin/draining_servers.rb',
                              content = StaticFile('draining_servers.rb'),
                              mode = 0755,
                              )
    self.assertResourceCalled('Execute', '/usr/bin/kinit -kt /etc/security/keytabs/accumulo.headless.keytab accumulo; /usr/lib/accumulo/bin/accumulo --config /etc/accumulo/conf org.jruby.Main /usr/lib/accumulo/bin/draining_servers.rb add host1',
                              logoutput = True,
                              user = 'accumulo',
                              )
    self.assertResourceCalled('Execute', '/usr/bin/kinit -kt /etc/security/keytabs/accumulo.headless.keytab accumulo; /usr/lib/accumulo/bin/accumulo --config /etc/accumulo/conf org.jruby.Main /usr/lib/accumulo/bin/region_mover.rb unload host1',
                              logoutput = True,
                              user = 'accumulo',
                              )
    self.assertNoMoreResources()

  def assert_configure_default(self):
    self.assertResourceCalled('Directory', '/etc/accumulo/conf',
      owner = 'accumulo',
      group = 'hadoop',
      recursive = True,
    )
    self.assertResourceCalled('Directory', '/hadoop/accumulo',
      owner = 'accumulo',
      recursive = True,
    )
    self.assertResourceCalled('Directory', '/hadoop/accumulo/local/jars',
      owner = 'accumulo',
      group = 'hadoop',
      mode=0775,
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
      owner = 'accumulo',
      content = InlineTemplate(self.getConfig()['configurations']['accumulo-env']['content']),
    )
    self.assertResourceCalled('TemplateConfig', '/etc/accumulo/conf/hadoop-metrics2-accumulo.properties',
      owner = 'accumulo',
      template_tag = 'GANGLIA-MASTER',
    )
    self.assertResourceCalled('TemplateConfig', '/etc/accumulo/conf/regionservers',
      owner = 'accumulo',
      template_tag = None,
    )
    self.assertResourceCalled('Directory', '/var/run/accumulo',
      owner = 'accumulo',
      recursive = True,
    )
    self.assertResourceCalled('Directory', '/var/log/accumulo',
      owner = 'accumulo',
      recursive = True,
    )
    self.assertResourceCalled('File',
                              '/etc/accumulo/conf/log4j.properties',
                              mode=0644,
                              group='hadoop',
                              owner='accumulo',
                              content='log4jproperties\nline2'
    )
    self.assertResourceCalled('HdfsDirectory', 'hdfs://c6401.ambari.apache.org:8020/apps/accumulo/data',
                              security_enabled = False,
                              keytab = UnknownConfigurationMock(),
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = "/usr/bin/kinit",
                              owner = 'accumulo',
                              bin_dir = '/usr/bin',
                              action = ['create_delayed'],
                              )
    self.assertResourceCalled('HdfsDirectory', '/apps/accumulo/staging',
                              security_enabled = False,
                              keytab = UnknownConfigurationMock(),
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = "/usr/bin/kinit",
                              mode = 0711,
                              owner = 'accumulo',
                              bin_dir = '/usr/bin',
                              action = ['create_delayed'],
                              )
    self.assertResourceCalled('HdfsDirectory', None,
                              security_enabled = False,
                              keytab = UnknownConfigurationMock(),
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = "/usr/bin/kinit",
                              bin_dir = '/usr/bin',
                              action = ['create'],
                              )

  def assert_configure_secured(self):
    self.assertResourceCalled('Directory', '/etc/accumulo/conf',
      owner = 'accumulo',
      group = 'hadoop',
      recursive = True,
    )
    self.assertResourceCalled('Directory', '/hadoop/accumulo',
      owner = 'accumulo',
      recursive = True,
    )
    self.assertResourceCalled('Directory', '/hadoop/accumulo/local/jars',
      owner = 'accumulo',
      group = 'hadoop',
      mode=0775,
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
      owner = 'accumulo',
      content = InlineTemplate(self.getConfig()['configurations']['accumulo-env']['content']),
    )
    self.assertResourceCalled('TemplateConfig', '/etc/accumulo/conf/hadoop-metrics2-accumulo.properties',
      owner = 'accumulo',
      template_tag = 'GANGLIA-MASTER',
    )
    self.assertResourceCalled('TemplateConfig', '/etc/accumulo/conf/regionservers',
      owner = 'accumulo',
      template_tag = None,
    )
    self.assertResourceCalled('TemplateConfig', '/etc/accumulo/conf/accumulo_master_jaas.conf',
      owner = 'accumulo',
      template_tag = None,
    )
    self.assertResourceCalled('Directory', '/var/run/accumulo',
      owner = 'accumulo',
      recursive = True,
    )
    self.assertResourceCalled('Directory', '/var/log/accumulo',
      owner = 'accumulo',
      recursive = True,
    )
    self.assertResourceCalled('File',
                              '/etc/accumulo/conf/log4j.properties',
                              mode=0644,
                              group='hadoop',
                              owner='accumulo',
                              content='log4jproperties\nline2'
    )
    self.assertResourceCalled('HdfsDirectory', 'hdfs://c6401.ambari.apache.org:8020/apps/accumulo/data',
                              security_enabled = True,
                              keytab = '/etc/security/keytabs/hdfs.headless.keytab',
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = '/usr/bin/kinit',
                              owner = 'accumulo',
                              bin_dir = '/usr/bin',
                              action = ['create_delayed'],
                              )
    self.assertResourceCalled('HdfsDirectory', '/apps/accumulo/staging',
                              security_enabled = True,
                              keytab = '/etc/security/keytabs/hdfs.headless.keytab',
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = '/usr/bin/kinit',
                              mode = 0711,
                              owner = 'accumulo',
                              bin_dir = '/usr/bin',
                              action = ['create_delayed'],
                              )
    self.assertResourceCalled('HdfsDirectory', None,
                              security_enabled = True,
                              keytab = '/etc/security/keytabs/hdfs.headless.keytab',
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = '/usr/bin/kinit',
                              bin_dir = '/usr/bin',
                              action = ['create'],
                              )
