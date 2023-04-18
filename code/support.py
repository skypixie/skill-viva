def insert_categories_into_db(db_sess, category_class, categories):
    for cat in categories:
        db_sess.add(category_class(category=cat))
