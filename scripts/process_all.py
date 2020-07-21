#!/usr/bin/env python
import json

import boto3
import click


@click.command()
@click.option("--bucket", help="S3 bucket with CloudFront logs")
@click.option("--prefix", default="", help="Prefix for CloudFront logs")
@click.option(
    "--batch-size",
    default=20,
    help="Number of S3 keys that a lambda function will process at once",
)
@click.option(
    "--action", type=click.Choice(["print", "index"]), help="Choose 'print' for dry run"
)
@click.option("--function-name", help="AWS Lambda function name")
def process_all(bucket, prefix, action, batch_size, function_name):
    """
    Call Lambda functions to process all CloudFront logs at once.
    """
    actions = {
        "print": action_print,
        "index": action_index,
    }

    s3_keys = get_s3_keys(bucket, prefix)
    action_fn = actions[action]
    for batch in batch_s3_keys(s3_keys, batch_size):
        action_fn(batch, bucket, function_name)


def get_s3_keys(bucket, prefix):
    """Return all S3 keys from the bucket, matching the prefix."""
    s3 = boto3.client("s3")
    max_keys = 1000
    continuation = {}
    while True:
        resp = s3.list_objects_v2(
            Bucket=bucket, MaxKeys=max_keys, Prefix=prefix, **continuation
        )
        for obj in resp["Contents"]:
            yield obj["Key"]
        if "NextContinuationToken" in resp:
            continuation = {"ContinuationToken": resp["NextContinuationToken"]}
        else:
            break


def batch_s3_keys(s3_keys, batch_size):
    """Batch an iterator of S3 keys with batches of the given size."""
    out = []
    for key in s3_keys:
        out.append(key)
        if len(out) == batch_size:
            yield out
            out = []
    if out:
        yield out


def action_print(batch, bucket, function_name):
    """
    Print the expected function along with the parameters.
    """
    click.echo(f"{function_name}({batch!r})")


def action_index(batch, bucket, function_name):
    """
    Run asynchronously a Lambda function function_name against the batch of records.
    """
    client = boto3.client("lambda")
    client.invoke(
        FunctionName=function_name,
        Payload=create_payload(batch, bucket),
        InvocationType="Event",
    )


def create_payload(batch, bucket):
    """Helper function to create a proper event object for the Lambda function."""
    records = []
    for key in batch:
        records.append({"s3": {"bucket": {"name": bucket}, "object": {"key": key}}})
    ret = {"Records": records}
    return json.dumps(ret, separators=(",", ":"))


if __name__ == "__main__":
    process_all()
