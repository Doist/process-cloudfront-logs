NAME := process-cloudfront-logs
ENV := staging

FUNCTION := $(NAME)-$(ENV)

ifeq ($(ENV), production)
REGION = us-east-1
SRC_BUCKET := process-cloudfront-logs-in
DST_BUCKET := process-cloudfront-logs-out
else
REGION = eu-west-1
SRC_BUCKET := doist-alb-logs
DST_BUCKET := doist-alb-logs-processed
endif

.PHONY: help artifacts deploy delete
.DEFAULT_GOAL := help

help:           ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

clean:
	rm -f cloudformation.packaged.yml

artifacts:    ## Create S3 bucket for lambda artifacts
	aws s3 ls s3://$(FUNCTION)-lambda --region $(REGION) \
		|| aws s3 mb s3://$(FUNCTION)-lambda --region $(REGION)

cloudformation.packaged.yml: cloudformation.yml process.py artifacts
	aws cloudformation package --region $(REGION) \
		--template-file cloudformation.yml \
		--output-template-file cloudformation.packaged.yml \
		--s3-bucket $(FUNCTION)-lambda

deploy: cloudformation.packaged.yml ## Deploy
	aws cloudformation deploy --region $(REGION) \
		--template-file cloudformation.packaged.yml \
		--stack-name $(FUNCTION)-lambda \
		--capabilities CAPABILITY_NAMED_IAM \
		--parameter-overrides \
			Environment=$(ENV) \
			Source=$(SRC_BUCKET) \
			Results=$(DST_BUCKET)

delete:         ## Delete all created AWS resources  (DENGEROUS!)
#	aws cloudformation delete-stack --region $(REGION) \
#		--stack-name $(FUNCTION)-lambda
