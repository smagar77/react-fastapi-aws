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
                print(exp)
                print("Some error for update cache, account=AWS_ACCESS_KEY_ID_ACCOUNT{str(i)}")


def update_instance_cache(account_name: str):
    engine = create_engine(env.get('SQLALCHEMY_URI'))
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

        db_instances = client1.describe_db_instances()
        db_instances = db_instances["DBInstances"]
        for instance in db_instances:
            instance_obj: RDSMonitorCache = RDSMonitorCache(
                account_name=f"{account_name}",
                instance_identifier=instance["DBInstanceIdentifier"],
                instance_class=instance["DBInstanceClass"],
                instance_status=instance["DBInstanceStatus"],
                maintenance_window=instance["PreferredMaintenanceWindow"],
                backup_window=instance["PreferredBackupWindow"],
                automated_backups=instance["BackupRetentionPeriod"],
                storage=instance["AllocatedStorage"],
                maximum_storage_threshold=instance["MaxAllocatedStorage"],
                multi_az=instance["MultiAZ"],
            )
            session.add(instance_obj)
            del instance_obj
        session.commit()
