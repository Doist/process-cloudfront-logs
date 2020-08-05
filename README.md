# Process S3 logs from CloudFront

Process CloudFront logs to convert them from custom CSV format to JSON-encoded, merging date and time fields into a single date-time object.

## Necessary environment

- Environment: Python 3.8
- Event source: S3 bucket, event "ObjectCreated"
- Environment variables:
  - `S3_DEST_BUCKET` to define the destination S3 bucket
- Permissions:
  - Read permissions for the S3 bucket with logs to read the content of the source key.
  - Write permissions for the `S3_DEST_BUCKET` to write the modified file.

Please see detailed IAM policies in the [CloudFormation template](./cloudformation.yml).

## Testing locally

Create a Poetry project.

```sh
poetry install
```

Run tests:

```sh
poetry run pytest
```

## Installing to make it work

- Create a new S3 bucket to store the results of the processing.
- Deploy a new lambda function by running `make deploy` or `make ENV=production deploy`. The default environment is staging. The command creates a lambda function and all required resources. Please see the [CloudFormation template](./cloudformation.yml) for details.
- Test if the function works as expected. For the valid input, it has to create a new object in the destination S3 bucket.

## Making it usable for Athena

To make it usable for AWS Athena, once some JSON files are created, create a new AWS Glue Crawler to process the content, and make it run daily to collect new partitions.

## Invoking the function manually to process existing logfiles

There is a script that you can run locally to process existing log files. The script expects you to provide the bucket name with the CloudFront logs and the name of the lambda function to execute.

Once invoked, the script reads the contents of the S3 bucket and runs asynchornously the Lambda function for each of the batches of the keys. The default batch size is 20, which means that the function will process twenty keys at once.

The script has two modes: "print" or "index". The print mode is a "dry run" mode, it only reads the contents of the S3 bucket and dumps it to stdout. The "index" mode performs the actual indexing.

**Example:**

Print to stdout all S3 keys with CloudFront logs for 16 July 2020.

```sh
poetry run ./scripts/process_all.py \
    --bucket=cloudfront-logs \
    --action=print \
    --prefix=XXXX.2020-07-16 \
    --function-name=process_cloudfront_logs
```

Index the contents of 16 July 2020 asynchronously.

```sh
poetry run ./scripts/process_all.py \
    --bucket=cloudfront-logs \
    --action=index \
    --prefix=XXXX.2020-07-16 \
    --function-name=process_cloudfront_logs
```
