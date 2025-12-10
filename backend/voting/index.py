import json
import os
import psycopg2
from typing import Dict, Any

def get_db_connection():
    return psycopg2.connect(os.environ['DATABASE_URL'])

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    '''
    API для голосования: получение номинаций с кандидатами и голосование
    Методы: GET - получить все номинации с кандидатами, POST - проголосовать за кандидата
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
            cur.execute('SELECT id, title, emoji, description FROM nominations ORDER BY id')
            nomination_rows = cur.fetchall()
            
            nominations = []
            for nom_row in nomination_rows:
                nom_id = nom_row[0]
                cur.execute(
                    'SELECT id, name, votes FROM candidates WHERE nomination_id = %s ORDER BY id',
                    (nom_id,)
                )
                candidate_rows = cur.fetchall()
                
                candidates = [
                    {
                        'id': c_row[0],
                        'name': c_row[1],
                        'votes': c_row[2]
                    }
                    for c_row in candidate_rows
                ]
                
                nominations.append({
                    'id': nom_id,
                    'title': nom_row[1],
                    'emoji': nom_row[2],
                    'description': nom_row[3],
                    'candidates': candidates
                })
            
            user_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
            cur.execute('SELECT candidate_id FROM user_votes WHERE user_ip = %s AND candidate_id IS NOT NULL', (user_ip,))
            voted_candidate_ids = [row[0] for row in cur.fetchall()]
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'nominations': nominations,
                    'votedFor': voted_candidate_ids
                }),
                'isBase64Encoded': False
            }
        
        elif method == 'POST':
            body_data = json.loads(event.get('body', '{}'))
            candidate_id = body_data.get('candidateId')
            
            if not candidate_id:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'candidateId is required'}),
                    'isBase64Encoded': False
                }
            
            user_ip = event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
            
            cur.execute(
                'SELECT COUNT(*) FROM user_votes WHERE candidate_id = %s AND user_ip = %s',
                (candidate_id, user_ip)
            )
            if cur.fetchone()[0] > 0:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Already voted for this candidate'}),
                    'isBase64Encoded': False
                }
            
            cur.execute(
                'SELECT nomination_id FROM candidates WHERE id = %s',
                (candidate_id,)
            )
            result = cur.fetchone()
            if not result:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Candidate not found'}),
                    'isBase64Encoded': False
                }
            
            nomination_id = result[0]
            
            cur.execute(
                'SELECT c.id FROM candidates c JOIN user_votes uv ON c.id = uv.candidate_id WHERE c.nomination_id = %s AND uv.user_ip = %s',
                (nomination_id, user_ip)
            )
            if cur.fetchone():
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Already voted in this nomination'}),
                    'isBase64Encoded': False
                }
            
            cur.execute(
                'INSERT INTO user_votes (candidate_id, user_ip) VALUES (%s, %s)',
                (candidate_id, user_ip)
            )
            cur.execute(
                'UPDATE candidates SET votes = votes + 1 WHERE id = %s',
                (candidate_id,)
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
