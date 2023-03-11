from os import environ as env
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import find_dotenv, load_dotenv
from celery import Celery
from celery.schedules import crontab
import boto3

from model import *


ENV_FILE = find_dotenv()

if ENV_FILE:
    load_dotenv(ENV_FILE)


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
    for i in range(1, int(env.get("TOTAL_ACCOUNTS"))+1):
        if(env.get(f"AWS_ACCESS_KEY_ID_ACCOUNT{str(i)}")) is not None:
            try:
                update_instance_cache(f"ACCOUNT{str(i)}")
            except Exception as exp:
                raise


def update_instance_cache(account_name: str):
    engine = create_engine(env.get('SQLALCHEMY_URI'))
    instance_obj_collect = []
    with Session(engine) as session:
        aws_access_key_id_account = env.get(f"AWS_ACCESS_KEY_ID_{account_name}")
        aws_secret_access_key_account = env.get(f"AWS_SECRET_ACCESS_KEY_ID_{account_name}")
        region_name_account = env.get(f"REGION_NAME_{account_name}")
        account_name = env.get(f"NAME_{account_name}")

        get_cache = session.query(RDSMonitorCache).filter_by(account_name=f"{account_name}").all()
        for chache_row in get_cache:
            session.delete(chache_row)

        client1 = boto3.client(
            'rds',
            aws_access_key_id=aws_access_key_id_account,
            aws_secret_access_key=aws_secret_access_key_account,
            region_name=region_name_account
        )

        paginator = client1.get_paginator('describe_db_instances')
        paginator_response = paginator.paginate(
            PaginationConfig={
                'MaxItems': 100,
                'PageSize': 20,
                'StartingToken': None
            }
        )
        for response_iterator in paginator_response:
            db_instances = response_iterator["DBInstances"]
            for instance in db_instances:
                instance_obj: RDSMonitorCache = RDSMonitorCache(
                    account_name=f"{account_name}",
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
