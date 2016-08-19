from django.conf import settings
from django.http import HttpResponse
from jinja2 import Environment, FileSystemLoader, PackageLoader

import codecs
import datetime


#template_dirs = getattr(settings, 'TEMPLATE_DIRS')
#environment = Environment(loader=FileSystemLoader(template_dirs))
template_dirs = getattr(settings, 'TEMPLATES')
environment = Environment(loader=PackageLoader('pools', 'templates'))


#custom filters
def date(datetime_obj, format='%m-%d-%y'):
	"""Formats a datetime object into a string, using strftime's syntax"""
	
	return datetime_obj.strftime(format)
	
	
def phone(phone_number):
	"""Converts 5555551212 into (555) 555-1212
	
	If the filtered value contains more or fewer than 10 characters, it is returned unchanged."""
	
	phone_number = str(phone_number)
	if len(phone_number) == 10:
		phone_number = '(' + phone_number[:3] + ') ' + phone_number[3:6] + '-' + phone_number[6:10]
	return phone_number

	
def to_hex(number):
	"""Renders an integer as a CSS-compatible hexadecimal number."""
	
	if number:
		output = hex(int(number))[2:]
		while len(output) < 6:
			output = '0' + output
		
		return '#' + output
	return ''
	
	
environment.filters['date'] = date
environment.filters['phone'] = phone
environment.filters['to_hex'] = to_hex


environment.globals['now'] = datetime.datetime.now()


def render_to_response(template_path, var_dict):
	template = environment.get_template(template_path)
	
	# Fixes a bug in Python that renders the unicode identifier (0xEF 0xBB 0xBF) as a character.
	# If untreated, it can prevent the page from validating or rendering properly. 
	bom = unicode( codecs.BOM_UTF8, "utf8" )
	html = template.render(**var_dict).replace(bom, '')
	
	return HttpResponse(html)