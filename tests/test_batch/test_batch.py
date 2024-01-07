import boto3
import pytest

from moto import mock_aws


@pytest.mark.parametrize("region", ["us-west-2", "cn-northwest-1"])
@mock_aws
def test_batch_regions(region):
    client = boto3.client("batch", region_name=region)
    resp = client.describe_jobs(jobs=[""])
    assert resp["ResponseMetadata"]["HTTPStatusCode"] == 200
