import json
import os

import boto3
from boto3.session import Session
from botocore.config import Config

DEFAULT_BOTO_CONFIG = Config(region_name="us-east-1", retries={"max_attempts": 10, "mode": "standard"})
MANAGED_TEST_RESOURCE_STACK_NAME = "managed-test-resources"


def main():
    env_vars = get_testing_credentials()
    test_session = Session(
        aws_access_key_id=env_vars["accessKey"],
        aws_secret_access_key=env_vars["secretKey"],
        aws_session_token=env_vars["sessionToken"],
    )
    env_vars.update(get_managed_test_resource_outputs(test_session))
    print(json.dumps(env_vars))


def get_managed_test_resource_outputs(session: Session):
    cfn_resource = session.resource("cloudformation", config=DEFAULT_BOTO_CONFIG)
    stack = cfn_resource.Stack(MANAGED_TEST_RESOURCE_STACK_NAME)
    outputs_dict = dict()
    for output in stack.outputs:
        outputs_dict[output["OutputKey"]] = output["OutputValue"]
    return outputs_dict


def get_testing_credentials():
    lambda_arn = os.environ["CREDENTIAL_DISTRIBUTION_LAMBDA_ARN"]
    lambda_client = boto3.client("lambda", config=DEFAULT_BOTO_CONFIG)
    response = lambda_client.invoke(FunctionName=lambda_arn)
    payload = json.loads(response["Payload"].read())
    if response["FunctionError"]:
        raise ValueError(f"Failed to get credential. {payload['errorType']}")
    return payload


if __name__ == "__main__":
    main()
