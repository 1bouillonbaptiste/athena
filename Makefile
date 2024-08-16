
SRC :=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))

setup:
	pip install pipx
	pipx install --force pre-commit poetry==1.8.3
	pre-commit install
	poetry install

build:
	docker buildx build \
	--build-arg CACHEBUST=$(date +%s) \
	-t athena-dev:latest -f ./Dockerfile .

local:
	docker run --rm \
	-v /var/run/docker.sock:/var/run/docker.sock \
	-v $(SRC):/athena \
	-v /data:/data \
	--gpus=all \
	--workdir /athena \
	--entrypoint /bin/bash \
	--env-file .credentials \
	-e TF_FORCE_GPU_ALLOW_GROWTH=true \
	-e TF_ENABLE_ONEDNN_OPTS=0 \
	--shm-size 8G \
	-it athena-dev
