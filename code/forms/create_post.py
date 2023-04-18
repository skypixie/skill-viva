from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TextAreaField, StringField
from wtforms.validators import DataRequired


class AddPostForm(FlaskForm):
    def __init__(self, categories):
        super().__init__()

        self.category = SelectField('Категория',
                                validators=[DataRequired()],
                                choices=categories)
        
        self.heading = StringField('Заголовок', validators=[DataRequired()])
        self.content = TextAreaField('Что вы хотите написать?', validators=[DataRequired()])
        self.submit = SubmitField('Создать')
