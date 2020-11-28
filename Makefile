SHELL:= $(shell which bash)
export LAMBDA_ZIP=donde-echan.zip
export LAMBDA_ZIP_PATH=${PWD}/${LAMBDA_ZIP}
export S3_BUCKET=donde-echan-alexa-skill
export LAMBDA_FUNCTION=dondeEchan

build: _cleanup _python _app

deploy:
	AWS_PROFILE=ivan-personal aws s3 cp ${LAMBDA_ZIP_PATH} s3://${S3_BUCKET}/
	AWS_PROFILE=ivan-personal aws lambda update-function-code --function-name ${LAMBDA_FUNCTION} --s3-bucket ${S3_BUCKET} --s3-key ${LAMBDA_ZIP} --region eu-west-1

_cleanup:
	rm -rf ${LAMBDA_ZIP_PATH}

_python:
	virtualenv --python=python3 virtualenv
	. virtualenv/bin/activate ; pip3 install -r requirements.txt
	cd virtualenv/lib/python*/site-packages ; zip -r ${LAMBDA_ZIP_PATH} ./*

_app:
	zip -jg ${LAMBDA_ZIP_PATH} src/*.py
