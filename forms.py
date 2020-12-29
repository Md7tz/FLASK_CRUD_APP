from wtforms import Form, TextAreaField, StringField, PasswordField, validators

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.DataRequired(message='Please fill this field'), validators.Length(min=2, max=50)])
    username = StringField('Username', [validators.DataRequired(message='Please fill this field'), validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.DataRequired(message='Please fill this field'), validators.Length(min=10, max=50)])
    password = PasswordField('Password', [validators.DataRequired(message='Please fill this field'), validators.Length(min=4), validators.equal_to('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password', [validators.DataRequired(message='Please fill this field')])

# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(max=100)])
    body = TextAreaField('Body', [validators.Length(min=30)])

# Login Form Class
class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired(message='Please fill this field'), validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired(message='Please fill this field')])
