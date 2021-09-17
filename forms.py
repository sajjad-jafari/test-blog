from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL,Email,equal_to
from flask_ckeditor import CKEditorField


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")



class registerForm(FlaskForm):
    email=StringField("Enter Your Email:",validators=[DataRequired()])
    name= StringField("Enter Your Name:",validators=[DataRequired()])
    password1=PasswordField("Enter Your Password",validators=[DataRequired()])
    password2=PasswordField("Re-Enter Your Password",validators=[DataRequired(),equal_to(password1)])
    submit=SubmitField("Create your account")

class loginForm(FlaskForm):
    email = StringField("Enter Your Email:", validators=[DataRequired()])
    password1 = PasswordField("Enter Your Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class commentForm(FlaskForm):
    comment=CKEditorField("Comment",validators=[DataRequired()])
    submit=SubmitField('SUBMIT COMMENT')


