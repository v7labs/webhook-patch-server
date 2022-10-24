IMAGE_NAME="patch_server"
CODE_REPO=$(shell pwd)
PORT=8080

build:
	docker build -t ${IMAGE_NAME} .

run_server:
	docker run -it --rm -v ${CODE_REPO}:/app -e V7_KEY -p 8080:8080 \
	-t ${IMAGE_NAME}

run_lab:
	docker run --rm -p ${PORT}:${PORT} -v ${CODE_REPO}:/app \
	-e V7_KEY \
 	--entrypoint jupyter-lab ${IMAGE_NAME} --ip=0.0.0.0 --port=${PORT} --no-browser --allow-root 