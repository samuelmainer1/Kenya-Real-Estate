document.addEventListener('DOMContentLoaded', function() {
    const amenitiesField = document.querySelector('#id_amenities');
    
    if (amenitiesField) {
        // Add quick-add buttons for common amenities
        const commonAmenities = [
            'School', 'Hospital', 'Supermarket', 'Park', 'Gym', 
            'Swimming Pool', 'Shopping Mall', 'Public Transport',
            'Restaurant', 'Bank', 'Pharmacy', 'Gas Station'
        ];
        
        const quickAddDiv = document.createElement('div');
        quickAddDiv.style.marginTop = '10px';
        quickAddDiv.innerHTML = '<strong>Quick Add:</strong> ';
        
        commonAmenities.forEach(amenity => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = amenity;
            btn.style.margin = '2px';
            btn.style.padding = '4px 8px';
            btn.style.fontSize = '12px';
            btn.style.border = '1px solid #ddd';
            btn.style.borderRadius = '3px';
            btn.style.background = '#f8f9fa';
            btn.style.cursor = 'pointer';
            
            btn.addEventListener('click', function() {
                const currentValue = amenitiesField.value;
                const lines = currentValue.split('\n').filter(line => line.trim());
                
                if (!lines.includes(amenity)) {
                    lines.push(amenity);
                    amenitiesField.value = lines.join('\n');
                }
            });
            
            quickAddDiv.appendChild(btn);
        });
        
        amenitiesField.parentNode.insertBefore(quickAddDiv, amenitiesField.nextSibling);
    }
});