from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

class CompetitionForm(Form):
	field1 = TextField('Field 1', validators=[validators.DataRequired()])
	field2 = TextField('Field 2', validators=[validators.DataRequired()])
	field3 = TextField('Field 3', validators=[validators.DataRequired()])
	field4 = TextField('Field 4', validators=[validators.DataRequired()])
