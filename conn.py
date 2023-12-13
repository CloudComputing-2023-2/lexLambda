import pandas as pd
from sqlalchemy import create_engine
import pymysql

csv_file_path = 'D:/CloudComputing/teamPro/medidata.csv'

db_host = 'team10-instance-rds.cq1xmq6wnfs8.us-east-1.rds.amazonaws.com'
db_port = 3306
db_user = 'admin'
db_password = 'admin123'
db_name = 'team10_db'


df = pd.read_csv(csv_file_path)

print(df.head())

# MySQL 연결 엔진 생성
engine = create_engine(f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

# DataFrame을 MySQL 데이터베이스에 저장
df.to_sql(name='medidat', con=engine, if_exists='replace', index=False)

print("Data uploaded to MySQL RDS successfully.")
