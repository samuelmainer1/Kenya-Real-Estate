from django.core.management.base import BaseCommand
from services.models import Service

class Command(BaseCommand):
    help = 'Populate initial services data'

    def handle(self, *args, **options):
        services_data = [
            {
                'title': 'Property Sales',
                'short_description': 'Expert guidance for buying and selling residential and commercial properties.',
                'description': '''
                <h2>Professional Property Sales Services</h2>
                <p>Our experienced team provides comprehensive property sales services to help you buy or sell your property with confidence. We understand the Kenyan real estate market and provide expert guidance throughout the entire process.</p>
                
                <h3>What We Offer:</h3>
                <ul>
                    <li>Property valuation and market analysis</li>
                    <li>Professional photography and marketing</li>
                    <li>Negotiation and closing assistance</li>
                    <li>Legal documentation support</li>
                    <li>Market insights and trends analysis</li>
                </ul>
                
                <h3>Why Choose Our Sales Service:</h3>
                <ul>
                    <li>Extensive market knowledge</li>
                    <li>Professional network of buyers and sellers</li>
                    <li>Transparent pricing and processes</li>
                    <li>Dedicated support throughout the transaction</li>
                </ul>
                ''',
                'icon_class': 'fas fa-home',
                'is_featured': True,
                'order': 1
            },
            {
                'title': 'Property Rentals',
                'short_description': 'Find your perfect rental property or manage your rental investments.',
                'description': '''
                <h2>Comprehensive Rental Services</h2>
                <p>Whether you're looking for a place to rent or want to rent out your property, we provide complete rental services to meet your needs.</p>
                
                <h3>For Tenants:</h3>
                <ul>
                    <li>Extensive property listings</li>
                    <li>Virtual and physical property tours</li>
                    <li>Lease negotiation assistance</li>
                    <li>Move-in support and documentation</li>
                </ul>
                
                <h3>For Landlords:</h3>
                <ul>
                    <li>Tenant screening and verification</li>
                    <li>Rent collection and management</li>
                    <li>Property maintenance coordination</li>
                    <li>Legal compliance and documentation</li>
                </ul>
                ''',
                'icon_class': 'fas fa-key',
                'is_featured': True,
                'order': 2
            },
            {
                'title': 'Property Management',
                'short_description': 'Professional property management services for residential and commercial properties.',
                'description': '''
                <h2>Full-Service Property Management</h2>
                <p>Let us handle the day-to-day management of your property investments while you enjoy the returns. Our comprehensive property management services ensure your properties are well-maintained and profitable.</p>
                
                <h3>Our Management Services Include:</h3>
                <ul>
                    <li>Tenant acquisition and screening</li>
                    <li>Rent collection and financial reporting</li>
                    <li>Property maintenance and repairs</li>
                    <li>Regular property inspections</li>
                    <li>Legal compliance and documentation</li>
                    <li>24/7 emergency response</li>
                </ul>
                
                <h3>Benefits of Our Service:</h3>
                <ul>
                    <li>Maximize rental income</li>
                    <li>Reduce vacancy periods</li>
                    <li>Professional tenant relations</li>
                    <li>Detailed financial reporting</li>
                </ul>
                ''',
                'icon_class': 'fas fa-building',
                'is_featured': True,
                'order': 3
            },
            {
                'title': 'Investment Advisory',
                'short_description': 'Strategic real estate investment advice to maximize your portfolio returns.',
                'description': '''
                <h2>Expert Investment Advisory</h2>
                <p>Make informed real estate investment decisions with our expert advisory services. We help you identify profitable opportunities and build a strong property portfolio.</p>
                
                <h3>Investment Services:</h3>
                <ul>
                    <li>Market analysis and research</li>
                    <li>Investment opportunity identification</li>
                    <li>Portfolio diversification strategies</li>
                    <li>Risk assessment and mitigation</li>
                    <li>ROI projections and analysis</li>
                    <li>Exit strategy planning</li>
                </ul>
                
                <h3>Investment Areas:</h3>
                <ul>
                    <li>Residential properties</li>
                    <li>Commercial real estate</li>
                    <li>Land development projects</li>
                    <li>REITs and property funds</li>
                </ul>
                ''',
                'icon_class': 'fas fa-chart-line',
                'is_featured': True,
                'order': 4
            },
            {
                'title': 'Property Valuation',
                'short_description': 'Accurate property valuations for sales, purchases, insurance, and legal purposes.',
                'description': '''
                <h2>Professional Property Valuation</h2>
                <p>Get accurate and reliable property valuations from our certified professionals. Our valuations are accepted by banks, insurance companies, and legal institutions.</p>
                
                <h3>Valuation Services:</h3>
                <ul>
                    <li>Market value assessments</li>
                    <li>Insurance valuations</li>
                    <li>Mortgage valuations</li>
                    <li>Legal and probate valuations</li>
                    <li>Investment analysis valuations</li>
                </ul>
                
                <h3>Our Process:</h3>
                <ul>
                    <li>Comprehensive property inspection</li>
                    <li>Market research and analysis</li>
                    <li>Comparable sales analysis</li>
                    <li>Detailed valuation report</li>
                </ul>
                ''',
                'icon_class': 'fas fa-calculator',
                'is_featured': True,
                'order': 5
            },
            {
                'title': 'Legal Services',
                'short_description': 'Complete legal support for all your real estate transactions and disputes.',
                'description': '''
                <h2>Real Estate Legal Services</h2>
                <p>Navigate the legal complexities of real estate with our experienced legal team. We provide comprehensive legal support for all types of property transactions.</p>
                
                <h3>Legal Services Include:</h3>
                <ul>
                    <li>Property title searches and verification</li>
                    <li>Contract drafting and review</li>
                    <li>Due diligence investigations</li>
                    <li>Property registration and transfers</li>
                    <li>Dispute resolution and litigation</li>
                    <li>Landlord-tenant legal issues</li>
                </ul>
                
                <h3>Why Choose Our Legal Team:</h3>
                <ul>
                    <li>Specialized real estate expertise</li>
                    <li>Up-to-date knowledge of property laws</li>
                    <li>Efficient and cost-effective solutions</li>
                    <li>Strong track record in property law</li>
                </ul>
                ''',
                'icon_class': 'fas fa-gavel',
                'is_featured': False,
                'order': 6
            }
        ]

        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                title=service_data['title'],
                defaults=service_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created service: {service.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Service already exists: {service.title}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated services data!')
        )