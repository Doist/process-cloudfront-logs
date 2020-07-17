import csv
import io
import json
import os
from datetime import datetime

from process import CloudFrontS3Key, csv_to_json

here = os.path.dirname(__file__)


def test_s3_key_from_name():
    key_name = "prefix/E28YI0R0FWE4XB.2020-07-16-13.005547cc.gz"
    key = CloudFrontS3Key.from_name(key_name)
    assert key.edge == "E28YI0R0FWE4XB"
    assert key.dt == datetime(2020, 7, 16, 13)
    assert key.random == "005547cc"


def test_s3_key_dest_key():
    key_name = "prefix/E28YI0R0FWE4XB.2020-07-16-13.005547cc.gz"
    key = CloudFrontS3Key.from_name(key_name)
    assert key.get_dest_key() == "date=2020-07-16/13_005547cc.json.gz"


def test_csv_to_json():
    csv_reader = csv.reader(open(f"{here}/test_log.csv"), delimiter="\t")
    json_writer = io.StringIO()
    csv_to_json(csv_reader, json_writer)
    lines = json_writer.getvalue().splitlines(keepends=False)
    assert len(lines) == 2
    assert json.loads(lines[0])["cs_user_agent"] == "-"
    assert json.loads(lines[1])["cs_user_agent"] == "Mozilla"
