import csv
import gzip
import json
import os
from dataclasses import dataclass
from datetime import datetime

import boto3

# Schema is stored in the second line of the file as this:
# #Fields: date time x-edge-location sc-bytes ...
# We hard-code it here, but you can parse the header with the following ad-hoc sctipt:
# line[0].split(":")[1].strip().lower()
#       .replace('-', '_')
#       .replace('(', '_')
#       .replace(')', '').split()
schema = [
    "date",
    "time",
    "x_edge_location",
    "sc_bytes",
    "c_ip",
    "cs_method",
    "cs_host",
    "cs_uri_stem",
    "sc_status",
    "cs_referer",
    "cs_user_agent",
    "cs_uri_query",
    "cs_cookie",
    "x_edge_result_type",
    "x_edge_request_id",
    "x_host_header",
    "cs_protocol",
    "cs_bytes",
    "time_taken",
    "x_forwarded_for",
    "ssl_protocol",
    "ssl_cipher",
    "x_edge_response_result_type",
    "cs_protocol_version",
    "fle_status",
    "fle_encrypted_fields",
    "c_port",
    "time_to_first_byte",
    "x_edge_detailed_result_type",
    "sc_content_type",
    "sc_content_len",
    "sc_range_start",
    "sc_range_end",
]

# No more than 512MB in size in total,
# see https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html
dest_filename = "/tmp/dest.gz"


@dataclass
class CloudFrontS3Key:
    """
    Parsed key (filename) for CloudFront logs on S3.

    The key name, without a prefix looks like this
    E28YI0R0FWE4XB.2020-07-16-13.005547cc.gz
    """

    edge: str
    dt: datetime
    random: str

    @classmethod
    def from_name(cls, key_name: str):
        key_basename = os.path.basename(key_name)
        chunks = key_basename.split(".")
        assert len(chunks) == 4
        edge, dt, random, ext = chunks
        parsed_dt = datetime.strptime(dt, "%Y-%m-%d-%H")
        return CloudFrontS3Key(edge, parsed_dt, random)

    def get_dest_key(self):
        return f"date={self.dt:%Y-%m-%d}/{self.dt.hour}_{self.random}.json.gz"


def lambda_handler(event, context):
    ev_record = event["Records"][0]
    source_bucket = ev_record["s3"]["bucket"]["name"]
    source_key = ev_record["s3"]["object"]["key"]

    s3 = boto3.client("s3")
    source_obj = s3.get_object(Bucket=source_bucket, Key=source_key)
    with gzip.open(source_obj["Body"], "rt") as source_fd, gzip.open(
        dest_filename, "wt"
    ) as json_writer:
        csv_reader = csv.reader(source_fd, delimiter="\t")
        csv_to_json(csv_reader, json_writer)

    parsed_key = CloudFrontS3Key.from_name(source_key)
    dest_bucket = os.getenv("S3_DEST_BUCKET")
    s3.upload_file(dest_filename, dest_bucket, parsed_key.get_dest_key())


def csv_to_json(csv_reader, json_writer):
    for record in csv_reader:
        if not record or record[0].startswith("#"):
            continue
        record_obj = dict(zip(schema, record))
        date = record_obj.pop("date")
        time = record_obj.pop("time")
        record_obj["datetime"] = f"{date} {time}Z"
        json.dump(record_obj, json_writer, separators=(",", ":"), sort_keys=True)
        json_writer.write("\n")
