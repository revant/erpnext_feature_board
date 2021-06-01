# Copyright (c) 2021, ERPNext Community and contributors
# For license information, please see license.txt

# import frappe
from frappe.website.website_generator import WebsiteGenerator


class Improvement(WebsiteGenerator):
	# the WebsiteGenerator class overrides the naming_series in the
	# doctype definition, overriding the override
	autoname = "naming_series:"
