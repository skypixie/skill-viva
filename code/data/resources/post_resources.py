from flask_restful import Resource, abort
from flask import jsonify

from ..db_session import create_session
from ..posts import Post
from .parser import parser


def abort_if_post_not_found(id):
    db_sess = create_session()
    post = db_sess.get(Post, id)
    if not post:
        abort(404, message=f"Post {id} is not found")


class PostResource(Resource):
    def get(self, id):
        abort_if_post_not_found(id)
        db_sess = create_session()
        post = db_sess.get(Post, id)
        return jsonify(
            {'post': post.to_dict()}
        )
    
    def delete(self, id):
        abort_if_post_not_found(id)
        db_sess = create_session()
        post = db_sess.get(Post, id)
        db_sess.delete(post)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class PostListResource(Resource):
    def get(self):
        db_sess = create_session()
        posts = db_sess.query(Post).all()
        return jsonify(
            {'posts': [post.to_dict() for post in posts]}
        )
    
    def post(self):
        args = parser.parse_args()
        db_sess = create_session()
        new_post = Post(
            user_id=args['user_id'],
            heading=args['heading'],
            content=args['content'],
            category_id=args['category_id']
        )
        db_sess.add(new_post)
        db_sess.commit()
        return jsonify({'success': 'OK'})
