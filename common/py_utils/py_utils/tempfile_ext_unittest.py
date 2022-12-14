# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import absolute_import
import filecmp
import os
import shutil

from py_utils import tempfile_ext
from pyfakefs import fake_filesystem_unittest


class NamedTemporaryDirectoryTest(fake_filesystem_unittest.TestCase):
  def setUp(self):
    self.setUpPyfakefs()

  def tearDown(self):
    self.tearDownPyfakefs()

  def testBasic(self):
    with tempfile_ext.NamedTemporaryDirectory() as d:
      self.assertTrue(os.path.exists(d))
      self.assertTrue(os.path.isdir(d))
    self.assertFalse(os.path.exists(d))

  def testSuffix(self):
    test_suffix = 'foo'
    with tempfile_ext.NamedTemporaryDirectory(suffix=test_suffix) as d:
      self.assertTrue(os.path.basename(d).endswith(test_suffix))

  def testPrefix(self):
    test_prefix = 'bar'
    with tempfile_ext.NamedTemporaryDirectory(prefix=test_prefix) as d:
      self.assertTrue(os.path.basename(d).startswith(test_prefix))

  def testDir(self):
    test_dir = '/baz'
    self.fs.CreateDirectory(test_dir)
    with tempfile_ext.NamedTemporaryDirectory(dir=test_dir) as d:
      self.assertEquals(test_dir, os.path.dirname(d))


class TemporaryFilesTest(fake_filesystem_unittest.TestCase):
  def setUp(self):
    self.setUpPyfakefs()

  def tearDown(self):
    self.tearDownPyfakefs()

  def testNamedTemporaryFile(self):
    with tempfile_ext.NamedTemporaryFile() as f:
      self.assertTrue(os.path.isfile(f.name))
      f.write(b'<data>')
      f.close()
      self.assertTrue(os.path.exists(f.name))
      with open(f.name) as f2:
        self.assertEqual(f2.read(), '<data>')

    self.assertFalse(os.path.exists(f.name))

  def testTemporaryFileName(self):
    with tempfile_ext.TemporaryFileName('foo') as filepath:
      self.assertTrue(os.path.basename(filepath), 'foo')
      self.assertFalse(os.path.exists(filepath))

      with open(filepath, 'w') as f:
        f.write('<data>')
      self.assertTrue(os.path.exists(filepath))

      shutil.copyfile(filepath, filepath + '.bak')
      self.assertTrue(filecmp.cmp(filepath, filepath + '.bak'))

    self.assertFalse(os.path.exists(filepath))
    self.assertFalse(os.path.exists(os.path.dirname(filepath)))
