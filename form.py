
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL


class MyForm(FlaskForm):
    long_url = StringField('Enter url to make shorter', validators=[DataRequired(), URL()], default='Type URL here')
    submit = SubmitField('Create shorter URL!')