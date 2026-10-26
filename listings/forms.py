from django import forms
from .models import Listing
from .widgets import AmenitiesWidget, AmenitiesCheckboxWidget
import json

class AmenitiesField(forms.CharField):
    """Custom field for handling amenities as a list"""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', AmenitiesWidget())
        kwargs.setdefault('required', False)
        kwargs.setdefault('help_text', 'Enter each amenity on a new line. Example: School, Hospital, Park')
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                # Try to parse as JSON first
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                # If not JSON, treat as newline-separated
                return [line.strip() for line in value.split('\n') if line.strip()]
        return []

class ListingAdminForm(forms.ModelForm):
    amenities = AmenitiesField()
    
    class Meta:
        model = Listing
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful text to other fields
        self.fields['price'].help_text = 'Enter price in KSH (e.g., 5000000 for 5M)'
        self.fields['bedrooms'].help_text = 'Number of bedrooms'
        self.fields['bathrooms'].help_text = 'Number of bathrooms (can be decimal like 2.5)'
        self.fields['sqft'].help_text = 'Square footage of the property'
        self.fields['lot_size'].help_text = 'Lot size in acres'
        self.fields['latitude'].help_text = 'Latitude coordinate for map location'
        self.fields['longitude'].help_text = 'Longitude coordinate for map location'

        if 'realtor' in self.fields:
            self.fields['realtor'].help_text = (
                'Every listing must be attached to a realtor. '
                'Only verified realtors can have published listings.'
            )

    def clean(self):
        cleaned_data = super().clean()
        # Note: publishing with an unverified realtor is handled gracefully in
        # ListingAdmin.save_model (it saves the listing as unpublished and warns)
        # instead of raising a hard validation error that would discard the
        # whole form (including any newly selected photos).
        return cleaned_data