def to_users_comments_payload(origin_value, comment, date):
    return {
        'operator': {
            'origin': 'app',
            'value': origin_value
        },
        'message': comment,
        'date': date,
        'allow_duplicate': False  ## important otherwise, it will create same comment
    }
