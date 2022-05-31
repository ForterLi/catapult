# Copyright 2021 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging

from apiclient import discovery
from dashboard.common import utils


def GetRBECASService():
  """Get a cached SheriffConfigClient instance.
  Most code should use this rather than constructing a SheriffConfigClient
  directly.
  """
  # pylint: disable=protected-access
  if not hasattr(GetRBECASService, '_client'):
    GetRBECASService._client = RBECASService()
  return GetRBECASService._client


class RBECASService(object):

  def __init__(self):
    """Initializes an object for retrieving files and directories from RBE-CAS.

    This class makes requests to RBE-CAS

    Args:
      http: A Http object that requests will be made through
    """
    self._service = discovery.build(
        'remotebuildexecution',
        'v2',
        http=utils.ServiceAccountHttp(scope=utils.CLOUD_SCOPE),
    )

  # Digest generated by proto is different from RBE-CAS API.
  # Normalize the digest to what RBE-CAS API accepted.
  @staticmethod
  def _NormalizeDigest(digest):
    if 'hash' not in digest:
      raise ValueError('Invalid digest for RBE-CAS')
    return {
        'hash': digest['hash'],
        'sizeBytes': digest.get('sizeBytes') or str(digest.get('size_bytes', 0)),
    }

  def GetTree(self, cas_ref, page_size=None, page_token=None):
    if 'cas_instance' not in cas_ref:
      raise ValueError('cas_instance is required for RBE-CAS')
    digest = self._NormalizeDigest(cas_ref['digest'])

    for i in range(3):
      try:
        return self._service.blobs().getTree(
            instanceName=cas_ref['cas_instance'],
            hash=digest['hash'],
            sizeBytes=digest['sizeBytes'],
            pageSize=page_size,
            pageToken=page_token).execute()
      except Exception as e:  # pylint: disable=broad-except
        logging.debug('GetTree iteration %s raised %s', i, str(e))
        exc = e
        continue
    raise exc

  def BatchRead(self, cas_instance, digests):
    for i in range(3):
      try:
        return self._service.blobs().batchRead(
            instanceName=cas_instance,
            body={
                'digests': [self._NormalizeDigest(d) for d in digests],
            },
        ).execute()
      except Exception as e:  # pylint: disable=broad-except
        logging.debug('BatchRead iteration %s raised %s', i, str(e))
        exc = e
        continue
    raise exc
