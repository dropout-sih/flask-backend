from bokeh.embed import components
from bokeh.plotting import figure, curdoc, ColumnDataSource
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import CustomJS, LabelSet, Slider
from bokeh.models.widgets import Slider
from werkzeug import secure_filename
from bokeh.models.layouts import WidgetBox, Row
from flask import Flask, render_template, flash, request, redirect, url_for, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import sendgrid
import os
from forms import *
import pandas as pd

DEBUG = True
app = Flask(__name__)	#initialising flask
app.config.from_object(__name__)	#configuring flask
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

data = pd.read_csv("test_data.csv")
df = pd.DataFrame(data)
external = df['Normalised_x'].tolist()
internal = df['Normalised_y'].tolist()
names = df['Country'].tolist()



UPLOAD_FOLDER = '/static/internal/'
ALLOWED_EXTENSIONS = set(['csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods = ['GET', 'POST'])
def uploader():
	if request.method == 'POST':
        # check if the post request has the file part
        	if 'file' not in request.files:
            		flash('No file part')
            		return redirect(request.url)
        	file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        	if file.filename == '':
            		flash('No selected file')
            		return redirect(request.url)
        	if file and allowed_file(file.filename):
            		filename = secure_filename(file.filename)
            		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            		return redirect(url_for('visualize'))
	
	return render_template('upload.html')

@app.route("/visualize", methods=['GET', 'POST'])
def visualize():
	form = CompetitionForm()
	js_resources = INLINE.render_js()
	css_resources = INLINE.render_css()
	source = ColumnDataSource(data=dict(external=external, internal=internal,names=names))

	callback = CustomJS(args=dict(source=source), code="""
		var data = source.data;
		var val = year.value;
		var x = data['external'];
		var y = data['internal'];
		for (var i = 0; i < x.length; i++) {
		    x[i] = x[i] + 0.05;
		}
		source.change.emit();
	""")


	fig = figure(plot_width=1000, plot_height=600)
	fig.scatter('external','internal', source=source, marker="inverted_triangle", size=5,line_color="navy", fill_color="green", alpha=0.6)
	fig.xaxis[0].axis_label = 'External Index'
	fig.yaxis[0].axis_label = 'Internal Index'
	labels = LabelSet(x='external', y='internal', text='names', level='glyph', x_offset=5, y_offset=5, source=source, render_mode='canvas')
	fig.add_layout(labels)
	year = Slider(title="Year", value=2000, start=2000, end=2030, step=1, width=250, callback=callback)
	callback.args["year"] = year

	layout = row(
	    fig,
	    widgetbox(year),
	)

	script, div = components(layout)
	html = render_template(
		'index.html',
		form=form,
		layout_script=script,
		layout_div=div,
		js_resources=js_resources,
		css_resources=css_resources,
	)

	return encode_utf8(html)


if __name__ == "__main__":
	app.run(debug=True)
