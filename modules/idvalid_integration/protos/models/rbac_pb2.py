# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: models/rbac.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11models/rbac.proto\x12\x0cidvalid.rbac\"?\n\x08RoleUser\x12\x11\n\ttenant_id\x18\x01 \x01(\x04\x12\x0f\n\x07role_id\x18\x02 \x01(\x04\x12\x0f\n\x07user_id\x18\x03 \x01(\x04\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'models.rbac_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_ROLEUSER']._serialized_start=35
  _globals['_ROLEUSER']._serialized_end=98
# @@protoc_insertion_point(module_scope)
