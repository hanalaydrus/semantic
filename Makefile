build:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. densityContract.proto volumeContract.proto semanticContract.proto

run:
	python -u main.py