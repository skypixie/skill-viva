def insert_categories_into_db(db_sess, category_class, categories):
    for cat in categories:
        categ = category_class(category=cat)
        db_sess.add(categ)
    db_sess.commit()
