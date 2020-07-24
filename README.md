# Process S3 logs from CloudFront

Process CloudFront logs to convert them from custom CSV format to JSON-encoded, merging date and time fields into a single datetime object.

## Necessary environment

- Environment: Python 3.8
- Event source: S3 bucket, event "ObjectCreated"
- Environment variables:
  - `S3_DEST_BUCKET` to define the destination S3 bucket
- Permissions:
  - Read permissions for the S3 bucket with logs to read the content of the source key.
  - Write permissions for the `S3_DEST_BUCKET` to write the modified file.

## Testing locally

Create a Poetry project.

```
poetry install
```

Run tests:

```
poetry run pytest
```

## Installing to make it work

- Create a new S3 bucket to store the results of the processing.
- Create a new lambda function, set necessary permissions, set environment variable `S3_DEST_BUCKET`.
- Create a trigger S3, event type "ObjectCreated", and connect it to the lambda function.
- Test if the function works as expected. For the valid input, it has to create a new object in the destination S3 bucket.

## Making it usable for Athena

To make it usable for AWS Athena, once some JSON files are created, create a new AWS Glue Crawler to process the content. Then set up a so-called [partition projection](https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html) to make Athena recognize new partitions without manually adding them daily.

Go to "Edit table details" in AWS Glue catalog and add the following new properties:

- `projection.date.type: date`
- `projection.date.format: yyyy-MM-dd`
- `projection.date.range: 2020-07-01,NOW`, but replace "2020-07-01" with the date of your first record.
- `projection.enabled: true`


## Invoking the function manually to process existing logfiles

There is a script that you can run locally to process existing log files. The script expects you to provide the bucket name with the CloudFront logs and the name of the lambda function to execute.

Once invoked, the script reads the contents of the S3 bucket and runs asynchornously the Lambda function for each of the batches of the keys. The default batch size is 20, which means that the function will process twenty keys at once.

The script has two modes: "print" or "index". The print mode is a "dry run" mode, it only reads the contents of the S3 bucket and dumps it to stdout. The "index" mode performs the actual indexing.

**Example:**

Print to stdout all S3 keys with CloudFront logs for 16 July 2020.

```
poetry run ./scripts/process_all.py \
    --bucket=cloudfront-logs \
    --action=print \
    --prefix=XXXX.2020-07-16 \
    --function-name=process_cloudfront_logs
```

Index the contents of 16 July 2020 asynchronously.

```
poetry run ./scripts/process_all.py \
    --bucket=cloudfront-logs \
    --action=index \
    --prefix=XXXX.2020-07-16 \
    --function-name=process_cloudfront_logs
```
