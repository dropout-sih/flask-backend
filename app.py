from bokeh.embed import components
from bokeh.plotting import figure, curdoc, ColumnDataSource
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import CustomJS, LabelSet, Slider
from bokeh.models.widgets import Slider
from bokeh.models.layouts import WidgetBox, Row
from flask import Flask, render_template, flash, request, redirect, url_for, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import sendgrid
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

source = dict()

'''def callback(source=source):
	data = source.data
	print("httt")
	year_dyn = cb_obj.year.value  # cb_obj.get('a_slider')
	x, y = data['external'], data['internal']

	for i in range(0,len(y)):
		y[i] = y[i] + 0.05

	source.change.emit()
'''

def updatePage2(attrname, old, new):
	print("asdsaD")

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
	form = CompetitionForm(request.form)
	js_resources = INLINE.render_js()
	css_resources = INLINE.render_css()
	global source
	source = ColumnDataSource(data=dict(external=external, internal=internal,names=names))
	fig = figure(plot_width=1000, plot_height=600)
	fig.scatter('external','internal', source=source, marker="inverted_triangle", size=5,line_color="navy", fill_color="green")

	updatePage = CustomJS(args=dict(source=source), code="""
		var data = source.data;
		var year = year.value;
		var x = data['external'];
		var y = data['internal'];
		for (var i = 0; i < x.length; i++) {
		    y[i] = x[i] + year;
		}
	""")
	fig.xaxis[0].axis_label = 'External Factors'
	fig.yaxis[0].axis_label = 'Internal Factors'
	labels = LabelSet(x='external', y='internal', text='names', level='glyph', x_offset=5, y_offset=5, source=source, render_mode='canvas')
	fig.add_layout(labels)
	year = Slider(title="Year Start", value=2000, start=2000, end=2030, step=1, width=500)#, callback=updatePage2)
	#updatePage.args["year"] = year
	year.on_change('value', updatePage)

	script, div = components(fig)
	script_sli, div_sli = components(year)
	#print(script, div, script_sli, div_sli)
	html = render_template(
		'index.html',
		plot_script=script,
		plot_div=div,
		js_resources=js_resources,
		css_resources=css_resources,
		form=form,
		slider_script=script_sli,
		slider_div=div_sli,
	)

	if(request.method == 'POST'):
		if(form.validate()):
			fig = figure(plot_width=600, plot_height=600)
			fig.vbar(x=[1, 2, 3, 4], width=0.5, bottom=0, top=[1.7, 2.2, 4.6, 3.9], color='navy')

			#print(components(fig))
			# grab the static resources
			year = Slider(title="Year Start", value=2000, start=2000, end=2030, step=1, width=500)
			# render template
			script, div = components(year)
			script_sli, div_sli = components(year)

			html = render_template(
			    'index.html',
			    plot_script=script,
			    plot_div=div,
			    js_resources=js_resources,
			    css_resources=css_resources,
				form=form,
				slider_script=script_sli,
				slider_div=div_sli,
			)
			return encode_utf8(html)
	return encode_utf8(html)


if __name__ == "__main__":
	app.run(debug=True)
