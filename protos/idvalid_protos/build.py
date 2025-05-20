import os
from grpc_tools import protoc

basedir = os.path.dirname(os.path.abspath(__file__))
r"""
python -m grpc_tools.protoc 
--proto_path=. 
--python_out=..\..\idvalid-integration-module\idvalid_integration\rpc\protos\ 
--grpc_python_out=..\..\idvalid-integration-module\idvalid_integration\rpc\protos\ 
--pyi_out=..\..\idvalid-integration-module\idvalid_integration\rpc\protos\ 
cryptography\asymmetric\key.proto
"""
output_dir = os.path.join(r"P:\OneHub\valid\services\idvalid-integration-module\idvalid_integration\rpc\protos")
proto_include = "-I{}".format(protoc._get_resource_file_name(
    "grpc_tools", "_proto"))

for dir_path, _, filenames in os.walk(basedir):
    for filename in filenames:
        if filename.endswith(".proto"):
            commands = [
                "grpc_tools.protoc",
                f"--proto_path={basedir}",
                f"--python_out={output_dir}",
                f"--grpc_python_out={output_dir}",
                f"--pyi_out={output_dir}",
                # "--enable_codegen_trace",
                os.path.join(dir_path, filename),
                proto_include,
            ]
            print(commands)
            if protoc.main(commands) != 0:
                raise Exception("Error: Protoc failed to compile the .proto file.")
