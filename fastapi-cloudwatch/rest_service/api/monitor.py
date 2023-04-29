from os import environ as env
from datetime import datetime
import dateutil.relativedelta
import logging
import inject
from uuid import uuid4
from dotenv import find_dotenv, load_dotenv
from sqlalchemy.orm.session import Session

from rest_service.router import APIRouter
import boto3
from rest_service.model import *

logger = logging.getLogger(__name__)

router = APIRouter(tags=['Monitor'])

ENV_FILE = find_dotenv()

if ENV_FILE:
    load_dotenv(ENV_FILE)


def default_session_factory() -> Session:
    """
    Default DB Session Factory
    :return:
    """
    logger.info("Creating databse Session")
    return inject.instance(Session)


@router.get("/rdsmatrix")
def get_rds_matrix(account_name: str):
    account_name_preserve = account_name
    if not account_name:
        return {}

    for key, val in env.items():
        if val == account_name:
            account_name = key.replace('NAME_ACCOUNT', 'ACCOUNT')
            break

    session = inject.instance(Session)

    aws_access_key_id_account = env.get(f"AWS_ACCESS_KEY_ID_{account_name}")
    aws_secret_access_key_account = env.get(f"AWS_SECRET_ACCESS_KEY_ID_{account_name}")
    region_name_account = env.get(f"REGION_NAME_{account_name}")

    client = boto3.client(
        'cloudwatch',
        aws_access_key_id=aws_access_key_id_account,
        aws_secret_access_key=aws_secret_access_key_account,
        region_name=region_name_account
    )
    get_cache = session.query(RDSMonitorCache).filter_by(account_name=account_name_preserve).all()
    response_data = []
    for rds_instance_identifier in get_cache:
        result = client.get_metric_data(
            MetricDataQueries=[
                {
                    'Id': 'fetching_FreeStorageSpace',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/RDS',
                            'MetricName': 'FreeStorageSpace',
                            'Dimensions': [{
                                "Name": "DBInstanceIdentifier",
                                "Value": rds_instance_identifier.instance_identifier
                            }]
                        },
                        'Period': 600,
                        'Stat': 'Average',
                        'Unit': 'Bytes'
                    }
                },
            ],
            ScanBy='TimestampAscending',
            StartTime=(datetime.datetime.now() + dateutil.relativedelta.relativedelta(days=-int(env.get("FREE_STORAGE_SPACE_MATRIX__LAST_DAYS")))),
            EndTime=datetime.datetime.now(),
        )
        result.update({'request_id': str(uuid4())})
        result.update({'instance_identifier': rds_instance_identifier.instance_identifier})
        response_data.append(result)
        del result
    return response_data


@router.get("/rdsinstance")
def get_rds_instance(account_name: str):
    if not account_name:
        return {}
    session = inject.instance(Session)
    get_cache = session.query(RDSMonitorCache).filter_by(account_name=account_name).all()
    cache_data = []
    for chache_row in get_cache:
        row = {}
        for column in chache_row.__table__.columns:
            row[column.name] = str(getattr(chache_row, column.name))
        cache_data.append(row)

    session.close()
    return cache_data


@router.get("/list-accounts")
def get_list_accounts():
    return [
            env.get(f"NAME_ACCOUNT{str(i)}") for i in range(1, int(env.get("TOTAL_ACCOUNTS")) + 1) if (env.get(f"NAME_ACCOUNT{str(i)}")) is not None
        ]


@router.get("/temp")
def get_list_accounts():
    client1 = boto3.client(
        'rds',
        aws_access_key_id="AKIA4J67HZADKVNCS6CC",
        aws_secret_access_key="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",
        region_name="ap-northeast-1"
    )
    paginator = client1.get_paginator('describe_pending_maintenance_actions')
    response_iterator = paginator.paginate(
        PaginationConfig={
            'MaxItems': 100,
            'PageSize': 20,
            'StartingToken': None
        }
    )

    return [item for item in response_iterator]
