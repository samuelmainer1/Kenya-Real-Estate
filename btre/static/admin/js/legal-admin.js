(function($) {
    $(document).ready(function() {
        // Add HTML editor help text
        if ($('#id_content').length) {
            $('#id_content').before(
                '<div class="legal-help">' +
                '<h4>HTML Formatting Tips:</h4>' +
                '<ul>' +
                '<li>Use &lt;h2&gt; for main sections</li>' +
                '<li>Use &lt;h3&gt; for subsections</li>' +
                '<li>Use &lt;ul&gt; and &lt;li&gt; for lists</li>' +
                '<li>Use &lt;p&gt; for paragraphs</li>' +
                '<li>Use &lt;strong&gt; for bold text</li>' +
                '</ul>' +
                '</div>'
            );
        }
        
        // SEO Preview
        function updateSEOPreview() {
            var title = $('#id_meta_title').val() || $('#id_title').val() || 'Page Title';
            var description = $('#id_meta_description').val() || 'Page description...';
            var url = window.location.origin + '/legal/' + ($('#id_slug').val() || 'page-slug') + '/';
            
            var preview = '<div class="seo-preview">' +
                '<div class="seo-title">' + title + '</div>' +
                '<div class="seo-url">' + url + '</div>' +
                '<div class="seo-description">' + description + '</div>' +
                '</div>';
            
            $('#seo-preview-container').html(preview);
        }
        
        if ($('#id_meta_title').length) {
            $('#id_meta_description').after('<div id="seo-preview-container"></div>');
            updateSEOPreview();
            
            $('#id_meta_title, #id_meta_description, #id_title, #id_slug').on('input', updateSEOPreview);
        }
    });
})(django.jQuery);