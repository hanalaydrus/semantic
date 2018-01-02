build:
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. helloworld.protoc

run:
	python main.py