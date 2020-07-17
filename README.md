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

To make it usable for AWS Athena, once some JSON files are created, create a new AWS Glue Crawler to process the content, and make it run daily to collect new partitions.
