from bokeh.embed import components
from bokeh.plotting import figure, curdoc, ColumnDataSource
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import CustomJS, LabelSet, Slider
from bokeh.models.widgets import Slider
from bokeh.models.layouts import WidgetBox, Row
from bokeh.layouts import row, widgetbox
from werkzeug import secure_filename
from flask import Flask, render_template, flash, request, redirect, url_for, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import os
from forms import *
import pandas as pd
import plotly
import plotly.plotly as py
import json
import numpy as np
from pandas import ExcelWriter
from pandas import ExcelFile

DEBUG = True
app = Flask(__name__)	#initialising flask
app.config.from_object(__name__)	#configuring flask
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

CURRENT_YEAR = '2015'


data = pd.read_csv("test_data.csv")
df = pd.DataFrame(data)
external = df['Normalised_x'].tolist()
internal = df['Normalised_y'].tolist()
names = df['Country'].tolist()

data_mod = pd.read_excel('final.xlsx', sheet_name=CURRENT_YEAR)
df1 = pd.DataFrame(data_mod)
ext = df1['External'].tolist()
int = df1['Internal'].tolist()
name = df1['Country'].tolist()
code = df1['Code'].tolist()

manip_name = ["India", "Belgium", "England"]
manip_y = [0.3,0.5,0.5]

source = ColumnDataSource(data=dict(external=ext, internal=int, names=name, c1=manip_y, c2=manip_name))

UPLOAD_FOLDER = '/static/internal/'
ALLOWED_EXTENSIONS = set(['csv'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


plotly.tools.set_credentials_file(username='rahulkumaran', api_key='04p6710F0Pcs8tmwLuSf')

'''def callback(attr, old, new):
   	data = source.data
   	val = cb_obj.year.value
   	x, y, names = ext, int, name
	for i in range(0,len(name)):
		if(name[i] in manip_name):
			y[i] = manip_y[manip_name.index(name[i])]

	print("here")
	source.change.emit()'''

app = Flask(__name__)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods = ['GET', 'POST'])
def index():
	return render_template('lp.html')




		

@app.route('/u', methods = ['GET', 'POST'])
def u():
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

@app.route("/relative-market-attractive-index-heatmap", methods=['GET', 'POST'])
def rmai():
	data = [ dict(
	type = 'choropleth',
	locations = code,
	z = ext,
	text = name,
	colorscale = [[0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],[0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"]],
	autocolorscale = False,
	reversescale = True,
 	marker = dict(
		line = dict (
			color = 'rgb(180,180,180)',
		            width = 0.5
		) ),
	colorbar = dict(
		autotick = False,
		tickprefix = 'Relative',
		title = 'Market<br>Attractive Index'),
		) ]

	layout = dict(
	title = 'Relative Market Attractive Index Heatmap',
	geo = dict(
		showframe = False,
		showcoastlines = False,
		projection = dict(
			type = 'Mercator'
		)
	)
	)

	return render_template('heatmap.html')

@app.route("/visualize",methods=['GET','POST'])
def visualize():
	js_resources = INLINE.render_js()
	css_resources = INLINE.render_css()
	callback = CustomJS(args=dict(source=source), code="""
	var data = source.data;
		var val = year.value;
	var get_name = data['c2'];
	var get_y = data[c1];
		var x = data['external'];
		var y = data['internal'];
	var name = data['names'];
		for (var i = 0; i < x.length; i++) {
	if(get_name.includes(name[i])){
		y[i] = y[i] + get_y[(get_name.indexOf(name[i]))];
		}
		}
		source.change.emit();
	""")

	fig = figure(plot_width=1000, plot_height=600)
	fig.scatter('external', 'internal', source=source, marker="circle", size=5,line_color="navy", fill_color="green", alpha=0.6)
	fig.xaxis[0].axis_label = 'External Index'
	fig.xaxis[0].axis_label = 'Internal Index'
	labels = LabelSet(x='external', y='internal', text='names', level='glyph', x_offset=5, y_offset=5, source=source, render_mode='canvas')
	fig.add_layout(labels)
	year = Slider(title="Year ", value=2000, start=1992, end=2030, step=1, width=250, callback=callback)
	callback.args["year"] = year


	layout = row(
	fig,
	widgetbox(year),
	)

	script, div = components(layout)
	html = render_template(
	'index.html',
	layout_script=script,
	layout_div=div,
	js_resources=js_resources,
	css_resources=css_resources,
	)

	return encode_utf8(html)


if __name__ == "__main__":
	app.run(debug=True)

