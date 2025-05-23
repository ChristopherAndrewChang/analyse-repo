# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: cryptography/asymmetric/key.proto
# Protobuf Python Version: 5.26.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n!cryptography/asymmetric/key.proto\x12(evercore.idvalid.cryptography.asymmetric\"2\n\x07KeyPair\x12\x13\n\x0bprivate_key\x18\x01 \x01(\x0c\x12\x12\n\npublic_key\x18\x02 \x01(\x0c\"\x88\x01\n\x0fGenerateRequest\x12\x11\n\x04\x64\x61ta\x18\x01 \x01(\x0cH\x00\x88\x01\x01\x12K\n\talgorithm\x18\x02 \x01(\x0e\x32\x33.evercore.idvalid.cryptography.asymmetric.AlgorithmH\x01\x88\x01\x01\x42\x07\n\x05_dataB\x0c\n\n_algorithm\"y\n\x10GenerateResponse\x12?\n\x04pair\x18\x01 \x01(\x0b\x32\x31.evercore.idvalid.cryptography.asymmetric.KeyPair\x12\x16\n\tsignature\x18\x02 \x01(\x0cH\x00\x88\x01\x01\x42\x0c\n\n_signature\"0\n\x0bSignRequest\x12\x13\n\x0bprivate_key\x18\x01 \x01(\x0c\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\"!\n\x0cSignResponse\x12\x11\n\tsignature\x18\x01 \x01(\x0c\"D\n\rVerifyRequest\x12\x12\n\npublic_key\x18\x01 \x01(\x0c\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\x12\x11\n\tsignature\x18\x03 \x01(\x0c\"\x1f\n\x0eVerifyResponse\x12\r\n\x05valid\x18\x01 \x01(\x08*x\n\tAlgorithm\x12\x19\n\x15\x41LGORITHM_UNSPECIFIED\x10\x00\x12\x11\n\rALGORITHM_RSA\x10\x01\x12\x11\n\rALGORITHM_DSA\x10\x02\x12\x13\n\x0f\x41LGORITHM_ECDSA\x10\x03\x12\x15\n\x11\x41LGORITHM_ED25519\x10\x04\x32\xfd\x02\n\x03Key\x12\x81\x01\n\x08Generate\x12\x39.evercore.idvalid.cryptography.asymmetric.GenerateRequest\x1a:.evercore.idvalid.cryptography.asymmetric.GenerateResponse\x12u\n\x04Sign\x12\x35.evercore.idvalid.cryptography.asymmetric.SignRequest\x1a\x36.evercore.idvalid.cryptography.asymmetric.SignResponse\x12{\n\x06Verify\x12\x37.evercore.idvalid.cryptography.asymmetric.VerifyRequest\x1a\x38.evercore.idvalid.cryptography.asymmetric.VerifyResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'cryptography.asymmetric.key_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_ALGORITHM']._serialized_start=581
  _globals['_ALGORITHM']._serialized_end=701
  _globals['_KEYPAIR']._serialized_start=79
  _globals['_KEYPAIR']._serialized_end=129
  _globals['_GENERATEREQUEST']._serialized_start=132
  _globals['_GENERATEREQUEST']._serialized_end=268
  _globals['_GENERATERESPONSE']._serialized_start=270
  _globals['_GENERATERESPONSE']._serialized_end=391
  _globals['_SIGNREQUEST']._serialized_start=393
  _globals['_SIGNREQUEST']._serialized_end=441
  _globals['_SIGNRESPONSE']._serialized_start=443
  _globals['_SIGNRESPONSE']._serialized_end=476
  _globals['_VERIFYREQUEST']._serialized_start=478
  _globals['_VERIFYREQUEST']._serialized_end=546
  _globals['_VERIFYRESPONSE']._serialized_start=548
  _globals['_VERIFYRESPONSE']._serialized_end=579
  _globals['_KEY']._serialized_start=704
  _globals['_KEY']._serialized_end=1085
# @@protoc_insertion_point(module_scope)
