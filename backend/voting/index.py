import json
import os
import psycopg2
from typing import Dict, Any

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    API для голосования: получение результатов и добавление голосов
    Методы: GET - получить все номинации, POST - проголосовать
    '''
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if method == 'GET':
            cur.execute('SELECT id, title, emoji, description, votes FROM nominations ORDER BY id')
            rows = cur.fetchall()
            nominations = [
                {
                    'id': row[0],
                    'title': row[1],
                    'emoji': row[2],
                    'description': row[3],
                    'votes': row[4]
                }
                for row in rows
            ]
            
            user_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
            cur.execute('SELECT nomination_id FROM user_votes WHERE user_ip = %s', (user_ip,))
            voted_ids = [row[0] for row in cur.fetchall()]
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'nominations': nominations,
                    'votedFor': voted_ids
                }),
                'isBase64Encoded': False
            }
        
        elif method == 'POST':
            body_data = json.loads(event.get('body', '{}'))
            nomination_id = body_data.get('nominationId')
            
            if not nomination_id:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'nominationId is required'}),
                    'isBase64Encoded': False
                }
            
            user_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
            
            cur.execute(
                'SELECT COUNT(*) FROM user_votes WHERE nomination_id = %s AND user_ip = %s',
                (nomination_id, user_ip)
            )
            if cur.fetchone()[0] > 0:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Already voted for this nomination'}),
                    'isBase64Encoded': False
                }
            
            cur.execute(
                'INSERT INTO user_votes (nomination_id, user_ip) VALUES (%s, %s)',
                (nomination_id, user_ip)
            )
            cur.execute(
                'UPDATE nominations SET votes = votes + 1 WHERE id = %s',
                (nomination_id,)
            )
            conn.commit()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'success': True}),
                'isBase64Encoded': False
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Method not allowed'}),
                'isBase64Encoded': False
            }
    
    finally:
        cur.close()
        conn.close()
