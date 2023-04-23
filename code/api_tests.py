from requests import get, post


# LIST
print(get('http://localhost:5000/api/posts').json())
'''print(post('http://localhost:5000/api/posts', json={'heading': '123',
                                                    'content': '123',
                                                    'user_id': '1',
                                                    'category_id': 10}).json())
WORKS
''' 