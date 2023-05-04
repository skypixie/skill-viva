from data import db_session
from data.posts import Post
from random import randint, shuffle


class SelectionOfPosts:
    def __init__(self, filters=False):
        self.filters = filters

    def random_selection_of_posts(self, posts, quantity):
        '''
        Всю функцию можно написать в 1 строку :)
        return random.sample(posts, quantity)

        P.S. Мог поставить больше за чистоту кода, но тогда уменьшил бы размер кода
        '''
        use_index = []
        ans = []
        for i in range(quantity):
            index = randint(0, len(posts) - 1)
            while index in use_index:
                index = randint(0, len(posts) - 1)
            ans.append(posts[index])
            use_index.append(index)

        return ans

    def selection(self):
        db_sess = db_session.create_session()
        if not self.filters:
            posts = list(reversed(db_sess.query(Post).all()))
        else:
            posts = db_sess.query(Post).filter(Post.category_id.in_(self.filters))

        current_posts = posts[:40]  # Остается только 30 - не понял)
        other_posts = posts[40:]  # Остается только 20 - и это тоже)
        total_number_of_relevant_posts = int(len(current_posts) * 0.75)
        '''
        Внизу происходит что-то страшное. Явно можно было написать короче, как минимум тернраниками
        или же не делать два if'а для проверки одного и того же условия total_number_of_relevant_posts == 30
        '''
        if total_number_of_relevant_posts == 30:
            random_relevant_posts = self.random_selection_of_posts(current_posts, total_number_of_relevant_posts)
        else:
            random_relevant_posts = self.random_selection_of_posts(current_posts, len(current_posts))
        random_other_posts = []

        if total_number_of_relevant_posts == 30:
            if len(other_posts) <= 20:
                random_other_posts = other_posts
            else:
                random_other_posts = self.random_selection_of_posts(other_posts, 20)

        result = random_relevant_posts + random_other_posts
        shuffle(result)

        return result
