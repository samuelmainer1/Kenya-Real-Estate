from django import forms
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
import json

class AmenitiesWidget(forms.Textarea):
    """Custom widget for amenities that shows as a textarea with helpful placeholder"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'rows': 6,
            'cols': 50,
            'placeholder': 'Enter amenities one per line:\n\nSchool\nSupermarket\nHospital\nPark\nGym\nSwimming Pool\nShopping Mall\nPublic Transport',
            'class': 'form-control',
            'style': 'font-family: monospace;'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def format_value(self, value):
        if value is None:
            return ''
        if isinstance(value, list):
            return '\n'.join(value)
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return '\n'.join(parsed)
            except (json.JSONDecodeError, TypeError):
                pass
        return str(value)
    
    def value_from_datadict(self, data, files, name):
        value = data.get(name, '')
        if value:
            # Split by lines and clean up
            amenities = [line.strip() for line in value.split('\n') if line.strip()]
            return amenities
        return []

class AmenitiesCheckboxWidget(forms.CheckboxSelectMultiple):
    """Alternative widget with predefined checkboxes"""
    
    def __init__(self, attrs=None):
        choices = [
            ('school', 'School'),
            ('supermarket', 'Supermarket'),
            ('hospital', 'Hospital'),
            ('park', 'Park'),
            ('gym', 'Gym'),
            ('swimming_pool', 'Swimming Pool'),
            ('shopping_mall', 'Shopping Mall'),
            ('public_transport', 'Public Transport'),
            ('restaurant', 'Restaurant'),
            ('bank', 'Bank'),
            ('pharmacy', 'Pharmacy'),
            ('gas_station', 'Gas Station'),
            ('church', 'Church'),
            ('mosque', 'Mosque'),
            ('police_station', 'Police Station'),
            ('fire_station', 'Fire Station'),
            ('library', 'Library'),
            ('cinema', 'Cinema'),
            ('beach', 'Beach'),
            ('golf_course', 'Golf Course'),
        ]
        super().__init__(attrs, choices)