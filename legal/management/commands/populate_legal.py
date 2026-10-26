from django.core.management.base import BaseCommand
from legal.models import LegalPage, SEOSettings
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate initial legal pages and SEO settings'

    def handle(self, *args, **options):
        # Create Privacy Policy
        privacy_content = '''
        <h2>Information We Collect</h2>
        <p>We collect information you provide directly to us, such as when you create an account, make a booking, contact us, or use our services.</p>
        
        <h3>Personal Information</h3>
        <ul>
            <li>Name, email address, and phone number</li>
            <li>Property preferences and search history</li>
            <li>Booking and transaction information</li>
            <li>Communication preferences</li>
        </ul>
        
        <h3>Automatically Collected Information</h3>
        <ul>
            <li>IP address and device information</li>
            <li>Browser type and operating system</li>
            <li>Pages visited and time spent on our site</li>
            <li>Referral sources and search terms</li>
        </ul>
        
        <h2>How We Use Your Information</h2>
        <p>We use the information we collect to:</p>
        <ul>
            <li>Provide and improve our services</li>
            <li>Process bookings and transactions</li>
            <li>Send you relevant property listings and updates</li>
            <li>Respond to your inquiries and provide customer support</li>
            <li>Analyze usage patterns and improve our website</li>
        </ul>
        
        <h2>Information Sharing</h2>
        <p>We do not sell, trade, or rent your personal information to third parties. We may share your information only in the following circumstances:</p>
        <ul>
            <li>With property owners or agents when you make a booking inquiry</li>
            <li>With service providers who assist us in operating our website</li>
            <li>When required by law or to protect our rights</li>
            <li>With your explicit consent</li>
        </ul>
        
        <h2>Data Security</h2>
        <p>We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.</p>
        
        <h2>Your Rights</h2>
        <p>You have the right to:</p>
        <ul>
            <li>Access and update your personal information</li>
            <li>Request deletion of your data</li>
            <li>Opt-out of marketing communications</li>
            <li>Request a copy of your data</li>
        </ul>
        
        <h2>Contact Us</h2>
        <p>If you have any questions about this Privacy Policy, please contact us at:</p>
        <ul>
            <li>Email: samuelmainer@gmail.com</li>
            <li>Phone: +254 722 359 298</li>
            <li>Address: Nextgen Mall, Mombasa Road, Nairobi</li>
        </ul>
        '''
        
        privacy_policy, created = LegalPage.objects.get_or_create(
            page_type='privacy',
            defaults={
                'title': 'Privacy Policy',
                'content': privacy_content,
                'meta_title': 'Privacy Policy | Kenya Realestate Platform',
                'meta_description': 'Learn how Kenya Realestate Platform protects your privacy and handles your personal information. Read our comprehensive privacy policy.',
                'meta_keywords': 'privacy policy, data protection, personal information, Kenya Realestate Platform'
            }
        )
        
        # Create Terms of Service
        terms_content = '''
        <h2>Acceptance of Terms</h2>
        <p>By accessing and using Kenya Realestate Platform's website and services, you accept and agree to be bound by the terms and provision of this agreement.</p>
        
        <h2>Use License</h2>
        <p>Permission is granted to temporarily download one copy of the materials on Kenya Realestate Platform's website for personal, non-commercial transitory viewing only.</p>
        
        <h3>This license shall automatically terminate if you violate any of these restrictions:</h3>
        <ul>
            <li>Modify or copy the materials</li>
            <li>Use the materials for any commercial purpose or for any public display</li>
            <li>Attempt to reverse engineer any software contained on the website</li>
            <li>Remove any copyright or other proprietary notations from the materials</li>
        </ul>
        
        <h2>Property Listings</h2>
        <p>All property listings on our website are provided for informational purposes. We strive to ensure accuracy but cannot guarantee that all information is current or error-free.</p>
        
        <h3>Booking Terms</h3>
        <ul>
            <li>All bookings are subject to availability and confirmation</li>
            <li>Cancellation policies vary by property and will be clearly stated</li>
            <li>Payment terms and conditions apply as specified for each property</li>
            <li>You are responsible for providing accurate information when booking</li>
        </ul>
        
        <h2>User Conduct</h2>
        <p>You agree not to use our services to:</p>
        <ul>
            <li>Violate any applicable laws or regulations</li>
            <li>Transmit any harmful or malicious content</li>
            <li>Interfere with the proper functioning of the website</li>
            <li>Attempt to gain unauthorized access to our systems</li>
            <li>Harass or harm other users</li>
        </ul>
        
        <h2>Limitation of Liability</h2>
        <p>Kenya Realestate Platform shall not be liable for any damages arising from the use or inability to use our services, including but not limited to direct, indirect, incidental, punitive, and consequential damages.</p>
        
        <h2>Governing Law</h2>
        <p>These terms and conditions are governed by and construed in accordance with the laws of Kenya, and you irrevocably submit to the exclusive jurisdiction of the courts in that State or location.</p>
        
        <h2>Changes to Terms</h2>
        <p>We reserve the right to modify these terms at any time. Changes will be effective immediately upon posting on the website.</p>
        
        <h2>Contact Information</h2>
        <p>For questions about these Terms of Service, please contact us:</p>
        <ul>
            <li>Email: samuelmainer@gmail.com</li>
            <li>Phone: +254 722 359 298</li>
            <li>Address: Nextgen Mall, Mombasa Road, Nairobi</li>
        </ul>
        '''
        
        terms_of_service, created = LegalPage.objects.get_or_create(
            page_type='terms',
            defaults={
                'title': 'Terms of Service',
                'content': terms_content,
                'meta_title': 'Terms of Service | Kenya Realestate Platform',
                'meta_description': 'Read Kenya Realestate Platform\'s terms of service and user agreement. Understand your rights and responsibilities when using our platform.',
                'meta_keywords': 'terms of service, user agreement, terms and conditions, Kenya Realestate Platform'
            }
        )
        
        # Create Cookie Policy
        cookie_content = '''
        <h2>What Are Cookies</h2>
        <p>Cookies are small text files that are placed on your computer or mobile device when you visit our website. They help us provide you with a better experience by remembering your preferences and improving our services.</p>
        
        <h2>Types of Cookies We Use</h2>
        
        <h3>Essential Cookies</h3>
        <p>These cookies are necessary for the website to function properly. They enable basic functions like page navigation and access to secure areas of the website.</p>
        
        <h3>Analytics Cookies</h3>
        <p>We use analytics cookies to understand how visitors interact with our website. This helps us improve our services and user experience.</p>
        
        <h3>Marketing Cookies</h3>
        <p>These cookies track your online activity to help advertisers deliver more relevant advertising or to limit how many times you see an ad.</p>
        
        <h2>Managing Cookies</h2>
        <p>You can control and/or delete cookies as you wish. You can delete all cookies that are already on your computer and you can set most browsers to prevent them from being placed.</p>
        
        <h2>Third-Party Cookies</h2>
        <p>We may use third-party services like Google Analytics, Facebook Pixel, and other analytics tools that place cookies on your device.</p>
        
        <h2>Contact Us</h2>
        <p>If you have any questions about our use of cookies, please contact us at samuelmainer@gmail.com</p>
        '''
        
        cookie_policy, created = LegalPage.objects.get_or_create(
            page_type='cookie',
            defaults={
                'title': 'Cookie Policy',
                'content': cookie_content,
                'meta_title': 'Cookie Policy | Kenya Realestate Platform',
                'meta_description': 'Learn about how Kenya Realestate Platform uses cookies to improve your browsing experience and provide better services.',
                'meta_keywords': 'cookie policy, cookies, privacy, tracking, Kenya Realestate Platform'
            }
        )
        
        # Create SEO Settings
        seo_settings, created = SEOSettings.objects.get_or_create(
            defaults={
                'site_name': 'Kenya Realestate Platform',
                'site_description': 'Kenya\'s premier real estate platform offering luxury homes, apartments, commercial properties, and investment opportunities.',
                'site_keywords': 'real estate Kenya, luxury homes Nairobi, property investment Kenya, apartments for sale, commercial property Kenya, land for sale, property management, real estate agent Kenya',
                'phone': '+254 722 359 298',
                'email': 'samuelmainer@gmail.com',
                'address': 'Nextgen Mall, Mombasa Road, Nairobi',
                'facebook_url': 'https://facebook.com/kenya-realestate-platform',
                'twitter_url': 'https://twitter.com/kenya-realestate-platform',
                'instagram_url': 'https://instagram.com/kenya-realestate-platform',
                'linkedin_url': 'https://linkedin.com/company/kenya-realestate-platform',
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created legal pages and SEO settings!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Legal pages and SEO settings already exist!')
            )