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
import datetime
import  resource_management.libraries.functions

@patch.object(resource_management.libraries.functions, "get_unique_id_and_date", new = MagicMock(return_value=''))
class TestServiceCheck(RMFTestCase):

  def test_service_check_default(self):
    self.executeScript("2.0.6/services/ACCUMULO/package/scripts/service_check.py",
                        classname="AccumuloServiceCheck",
                        command="service_check",
                        config_file="default.json"
    )
    self.assertResourceCalled('File', '/tmp/accumuloSmokeVerify.sh',
      content = StaticFile('accumuloSmokeVerify.sh'),
      mode = 0755,
    )
    self.assertResourceCalled('File', '/tmp/accumulo-smoke.sh',
      content = Template('accumulo-smoke.sh.j2'),
      mode = 0755,
    )
    self.assertResourceCalled('Execute', ' /usr/lib/accumulo/bin/accumulo --config /etc/accumulo/conf shell /tmp/accumulo-smoke.sh',
      logoutput = True,
      tries = 3,
      user = 'ambari-qa',
      try_sleep = 5,
    )
    self.assertResourceCalled('Execute', ' /tmp/accumuloSmokeVerify.sh /etc/accumulo/conf  /usr/lib/accumulo/bin/accumulo',
      logoutput = True,
      tries = 3,
      user = 'ambari-qa',
      try_sleep = 5,
    )
    self.assertNoMoreResources()
    
    
  def test_service_check_secured(self):
    self.executeScript("2.0.6/services/ACCUMULO/package/scripts/service_check.py",
                        classname="AccumuloServiceCheck",
                        command="service_check",
                        config_file="secured.json"
    )
    self.assertResourceCalled('File', '/tmp/accumuloSmokeVerify.sh',
      content = StaticFile('accumuloSmokeVerify.sh'),
      mode = 0755,
    )
    self.assertResourceCalled('File', '/tmp/accumulo-smoke.sh',
      content = Template('accumulo-smoke.sh.j2'),
      mode = 0755,
    )
    self.assertResourceCalled('File', '/tmp/accumulo_grant_permissions.sh',
      content = Template('accumulo_grant_permissions.j2'),
      owner = 'accumulo',
      group = 'hadoop',
      mode = 0644,
    )
    self.assertResourceCalled('Execute', '/usr/bin/kinit -kt /etc/security/keytabs/accumulo.headless.keytab accumulo; /usr/lib/accumulo/bin/accumulo shell /tmp/accumulo_grant_permissions.sh',
      user = 'accumulo',
    )
    self.assertResourceCalled('Execute', '/usr/bin/kinit -kt /etc/security/keytabs/smokeuser.headless.keytab ambari-qa; /usr/lib/accumulo/bin/accumulo --config /etc/accumulo/conf shell /tmp/accumulo-smoke.sh',
      logoutput = True,
      tries = 3,
      user = 'ambari-qa',
      try_sleep = 5,
    )
    self.assertResourceCalled('Execute', '/usr/bin/kinit -kt /etc/security/keytabs/smokeuser.headless.keytab ambari-qa; /tmp/accumuloSmokeVerify.sh /etc/accumulo/conf  /usr/lib/accumulo/bin/accumulo',
      logoutput = True,
      tries = 3,
      user = 'ambari-qa',
      try_sleep = 5,
    )
    self.assertNoMoreResources()
    
