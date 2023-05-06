import sys
from os import environ as env
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import find_dotenv, load_dotenv
from celery import Celery
from celery.schedules import crontab
import boto3
from functools import lru_cache

from settings import Settings
from model import *

from os.path import abspath, join

# Adjust the paths
sys.path.insert(0, abspath(join(__file__, "../", "../")))


ENV_FILE = find_dotenv()

if ENV_FILE:
    load_dotenv(ENV_FILE)


@lru_cache
def get_settings():
    return Settings()


app = Celery('tasks', broker=env.get('RABBITMQ_URI'))

app.conf.beat_schedule = {
    'add-every-second': {
        'task': 'tasks.fetch_rds_instance',
        'schedule': crontab(hour="*", minute="*", day_of_week="*"),
        'args': None
    }
}


@app.task()
def fetch_rds_instance():
    settings = get_settings()
    for account_arn in settings.arns:
        try:
            update_instance_cache(account_arn)
        except Exception as exp:
            raise


def update_instance_cache(account_arn: dict[str, str]):
    settings = get_settings()
    engine = create_engine(settings.sqlalchemy_uri)
    instance_obj_collect = []
    with Session(engine) as session:
        get_cache = session.query(RDSMonitorCache).filter_by(account_name=account_arn["name"]).all()
        for chache_row in get_cache:
            session.delete(chache_row)
        CURRENT_ACCOUNT_SESSION = boto3.Session()
        STS_CLIENT = CURRENT_ACCOUNT_SESSION.client('sts')
        assumed_role_object = STS_CLIENT.assume_role(
            RoleArn=account_arn["arn"],
            RoleSessionName=account_arn["name"]
        )
        assumed_role_credentials = assumed_role_object['Credentials']

        client1 = boto3.client(
            'rds',
            aws_access_key_id=assumed_role_credentials['AccessKeyId'],
            aws_secret_access_key=assumed_role_credentials['SecretAccessKey'],
            region_name=account_arn["region"],
            aws_session_token=assumed_role_credentials['SessionToken'],
        )

        paginator = client1.get_paginator('describe_db_instances')
        paginator_response = paginator.paginate(
            PaginationConfig={
                'MaxItems': 100,
                'PageSize': 20,
                'StartingToken': None
            }
        )
        for response_item in paginator_response:
            db_instances = response_item["DBInstances"]
            for instance in db_instances:
                instance_obj: RDSMonitorCache = RDSMonitorCache(
                    account_name=account_arn["name"],
                    instance_identifier=instance.get("DBInstanceIdentifier", ""),
                    instance_class=instance.get("DBInstanceClass", ""),
                    instance_status=instance.get("DBInstanceStatus", ""),
                    maintenance_window=instance.get("PreferredMaintenanceWindow", ""),
                    backup_window=instance.get("PreferredBackupWindow", ""),
                    automated_backups=instance.get("BackupRetentionPeriod", ""),
                    storage=instance.get("AllocatedStorage", ""),
                    maximum_storage_threshold=instance.get("MaxAllocatedStorage", ""),
                    multi_az=instance["MultiAZ"],
                )
                instance_obj_collect.append(instance_obj)
                del instance_obj
        session.commit()
    for collect_row in instance_obj_collect:
        try:
            with Session(engine) as session:
                session.add(collect_row)
                session.commit()
        except Exception as e:
            print(e)
