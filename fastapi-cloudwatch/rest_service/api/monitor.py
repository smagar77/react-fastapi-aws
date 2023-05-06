from os import environ as env
from datetime import datetime
import dateutil.relativedelta
import logging
import inject
from uuid import uuid4
from dotenv import find_dotenv, load_dotenv
from sqlalchemy.orm.session import Session
from functools import lru_cache

from rest_service.settings import Settings
from rest_service.router import APIRouter
import boto3
from rest_service.model import *

logger = logging.getLogger(__name__)

router = APIRouter(tags=['Monitor'])

ENV_FILE = find_dotenv()

if ENV_FILE:
    load_dotenv(ENV_FILE)


@lru_cache
def get_settings():
    return Settings()


def default_session_factory() -> Session:
    """
    Default DB Session Factory
    :return:
    """
    logger.info("Creating databse Session")
    return inject.instance(Session)


@router.get("/rdsmatrix")
def get_rds_matrix(account_name: str):
    settings = get_settings()
    _account = None
    for account_arn in settings.arns:
        if account_arn["name"] == account_name:
            _account = account_arn
            break
    if _account is None:
        return None
    account_name_preserve = account_name
    if not account_name:
        return {}

    CURRENT_ACCOUNT_SESSION = boto3.Session()
    STS_CLIENT = CURRENT_ACCOUNT_SESSION.client('sts')
    assumed_role_object = STS_CLIENT.assume_role(
        RoleArn=_account["arn"],
        RoleSessionName=_account["name"]
    )
    assumed_role_credentials = assumed_role_object['Credentials']

    session = inject.instance(Session)

    client = boto3.client(
        'cloudwatch',
        aws_access_key_id=assumed_role_credentials['AccessKeyId'],
        aws_secret_access_key=assumed_role_credentials['SecretAccessKey'],
        region_name=account_arn["region"],
        aws_session_token=assumed_role_credentials['SessionToken'],
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
    settings = get_settings()   
    return [account_arn["name"] for account_arn in settings.arns]
