import json
import pymysql
import random

def lambda_handler(event, context):
    # AWS Lex에서 전달된 증상 가져오기
    symptom = event['sessionState']['intent']['slots']['prob']['value']['originalValue']

    # RDS 연결 설정
    connection = pymysql.connect(host='team10-instance-rds.cq1xmq6wnfs8.us-east-1.rds.amazonaws.com',
                                 user='admin',
                                 password='admin123',
                                 db='team10_db',
                                 charset='utf8mb4')

    response_content = ''
    try:
        with connection.cursor() as cursor:
            # SQL 쿼리 수정: 랜덤 결과 가져오기 및 NULL이 아닌 결과만 선택
            sql = """
            SELECT itemName, seQesitm, depositMethodQesitm, efcyQesitm, useMethodQesitm 
            FROM medidat 
            WHERE efcyQesitm LIKE %s AND itemName IS NOT NULL AND seQesitm IS NOT NULL 
            AND depositMethodQesitm IS NOT NULL AND efcyQesitm IS NOT NULL AND useMethodQesitm IS NOT NULL 
            ORDER BY RAND() LIMIT 1
            """
            cursor.execute(sql, ('%' + symptom + '%',))

            results = cursor.fetchone()

            if results:
                item_name, side_effect, storage_method, effect, use_method = results
                
                insert_sql = """
                INSERT INTO request (symptom, item_name, side_effect, storage_method, effect, use_method) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (symptom, item_name, side_effect, storage_method, effect, use_method))
                connection.commit()
                
                response_content += f'약 이름: {item_name}, 부작용: {side_effect}, 보관 방법: {storage_method}, 효과: {effect}, 사용 방법: {use_method}'

    finally:
        connection.close()

    if not response_content:
        response_content = '해당 증상에 대한 약 정보를 찾을 수 없습니다.'
    
    print(response_content)
    # AWS Lex에서 기대하는 형식에 맞추어 응답 구성
    response = {
        'dialogAction': {
            'type': 'ConfirmIntent',
            'fulfillmentState': 'Fulfilled',
            'message': {
                'contentType': 'PlainText',
                'content': response_content
            }
        }
    }

    return response
