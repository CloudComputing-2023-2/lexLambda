import json
import pymysql

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
            sql = "SELECT itemName, seQesitm, depositMethodQesitm, efcyQesitm, useMethodQesitm FROM medidat WHERE efcyQesitm LIKE %s LIMIT 1"
            cursor.execute(sql, ('%' + symptom + '%',))

            results = cursor.fetchall()


            for row in results:
                item_name = row[0] if row[0] else "정보 없음"
                side_effect = row[1] if row[1] else "정보 없음"
                storage_method = row[2] if row[2] else "정보 없음"
                effect = row[3] if row[3] else "정보 없음"
                use_method = row[4] if row[4] else "정보 없음"
                
                insert_sql = f"INSERT INTO request (symptom, item_name, side_effect, storage_method, effect, use_method) VALUES (%(symptom)s, %(item_name)s, %(side_effect)s, %(storage_method)s, %(effect)s, %(use_method)s)"
                cursor.execute(insert_sql, {'symptom': symptom, 'item_name': item_name, 'side_effect': side_effect, 'storage_method': storage_method, 'effect': effect, 'use_method': use_method})
                connection.commit()
                
                response_content += '약 이름: ' + item_name + ', '
                response_content += '부작용: ' + side_effect + ', '
                response_content += '보관 방법: ' + storage_method + ', '
                response_content += '효과: ' + effect + ', '
                response_content += '사용 방법: ' + use_method + ', '

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
