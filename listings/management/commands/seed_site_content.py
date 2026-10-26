"""Seed the site with realistic content and real photos.

Populates: verified realtors (founder Sam Maina stays CEO-only, not a team
realtor), property listings with photo galleries, featured services, blog
posts, testimonials, and the property-management portfolio (managed
properties, tenants, rent payments and maintenance schedules).
Idempotent: re-running will not duplicate records.
Usage: python manage.py seed_site_content
"""
import os
import shutil
from datetime import timedelta
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Blog, BlogCategory
from listings.models import Listing
from realtors.models import Realtor
from services.models import Service
from testimonials.models import Testimonial
from property_management.models import (
    ManagedProperty, MaintenanceSchedule, RentPayment, Tenant,
)
from django.contrib.auth.models import User

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)))
STAGING = os.path.join(PROJECT_ROOT, "seed_images")
STATIC_IMG = os.path.join(PROJECT_ROOT, "btre", "static", "img")


def img_bytes(name):
    path = os.path.join(STAGING, name)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()


class Command(BaseCommand):
    help = "Seed realistic demo content (realtors, listings, services, blog, testimonials) with real photos"

    def handle(self, *args, **options):
        self.seed_founder_static_photo()
        self.seed_realtors()
        self.seed_listings()
        self.extend_listings()
        self.new_listings()
        self.seed_managed_properties()
        self.seed_services()
        self.seed_blog()
        self.seed_testimonials()
        self.stdout.write(self.style.SUCCESS("Seeding complete!"))

    # ---------- helpers ----------
    def attach(self, field, filename, name):
        data = img_bytes(name)
        if data:
            field.save(filename, ContentFile(data), save=True)

    def seed_founder_static_photo(self):
        src = os.path.join(STAGING, "founder_sam_maina.jpg")
        dst = os.path.join(STATIC_IMG, "founder-sam-maina.jpg")
        if src and os.path.exists(src) and not os.path.exists(dst):
            shutil.copyfile(src, dst)
            self.stdout.write("Copied founder photo to static img")

    # ---------- realtors ----------
    def seed_realtors(self):
        realtors = [
            dict(
                name="Cynthia Achieng",
                photo="realtor_cynthia.jpg",
                phone="+254 733 555 666",
                email="cynthia.achieng@kenyarealestate.co.ke",
                description="Senior property consultant specialising in first-time buyer sales "
                            "and premium Airbnb portfolios across Kilimani, Kileleshwa and "
                            "Westlands. Cynthia is known for her hands-on service, honest "
                            "advice and sharp negotiation.",
                is_mvp=True,
            ),
            dict(
                name="Grace Wanjiru",
                photo="realtor_grace.jpg",
                phone="+254 700 111 222",
                email="grace.wanjiru@kenyarealestate.co.ke",
                description="Senior realtor specialising in high-end residential sales in Karen, "
                            "Runda and Muthaiga. Known for her deep market knowledge and dedication "
                            "to finding the perfect family home.",
                is_mvp=True,
            ),
            dict(
                name="Brian Otieno",
                photo="realtor_brian.jpg",
                phone="+254 700 333 444",
                email="brian.otieno@kenyarealestate.co.ke",
                description="Rental and Airbnb specialist covering Westlands, Kilimani and the "
                            "Nairobi CBD. Brian helps landlords maximise yields and tenants find "
                            "homes they love.",
                is_mvp=False,
            ),
        ]
        for r in realtors:
            image_bytes = img_bytes(r.pop("photo"))
            realtor, created = Realtor.objects.get_or_create(name=r["name"], defaults=r)
            if created or not realtor.photo:
                if image_bytes:
                    realtor.photo.save(
                        r["name"].lower().replace(" ", "_") + ".jpg",
                        ContentFile(image_bytes), save=True)
                realtor.is_verified = True
                realtor.verified_at = timezone.now()
                realtor.save()
            self.stdout.write(f"{'Created' if created else 'Found   '} realtor: {realtor.name}")

    # ---------- listings ----------
    def seed_listings(self):
        cynthia = Realtor.objects.filter(name="Cynthia Achieng").first()
        grace = Realtor.objects.filter(name="Grace Wanjiru").first()
        brian = Realtor.objects.filter(name="Brian Otieno").first()
        if not (cynthia and grace and brian):
            self.stdout.write(self.style.WARNING("Realtors missing — run realtor seeding first"))
            return

        listings = [
            dict(
                title="Luxury 4-Bedroom Villa with Pool in Karen",
                realtor=grace, property_type="sale",
                address="Marula Lane, Karen", city="Nairobi", state="Nairobi",
                zipcode="00802", price=85000000, bedrooms=4, bathrooms=Decimal("3.5"),
                garage=2, sqft=3400, latitude=-1.3177, longitude=36.7071,
                amenities=["Backup generator", "Borehole water", "Swimming pool", "Solar heating",
                           "Staff quarters", "Gated community", "DSQ", "Garden"],
                description="An exceptional family villa on a quarter-acre in the heart of Karen. "
                            "This elegant home features a spacious open-plan living and dining area, "
                            "a modern fitted kitchen, master ensuite with walk-in closet, and a "
                            "private pool surrounded by a mature garden. Walking distance to Karen "
                            "College, The Hub shopping mall and top international schools.",
                main="listing1_main.jpg",
                gallery=["interior_living.jpg", "interior_kitchen.jpg", "interior_bedroom.jpg",
                         "interior_bathroom.jpg", "exterior_pool.jpg"],
            ),
            dict(
                title="Modern 3-Bedroom Family House in Kilimani",
                realtor=brian, property_type="rent",
                address="Wood Avenue, Kilimani", city="Nairobi", state="Nairobi",
                zipcode="00100", price=120000, bedrooms=3, bathrooms=Decimal("2.5"),
                garage=1, sqft=1800, latitude=-1.2921, longitude=36.7819,
                amenities=["Gym", "Swimming pool", "24/7 security", "Borehole water",
                           "Backup generator", "Fitted kitchen", "Balcony"],
                description="Contemporary 3-bedroom house in a secure compound on Wood Avenue. "
                            "Features an open-plan layout, large windows with natural light, "
                            "modern kitchen with granite worktops, and a cozy family room. "
                            "Ideal for young families — minutes from Yaya Centre, schools and "
                            "the CBD.",
                main="listing2_main.jpg",
                gallery=["interior_living.jpg", "interior_dining.jpg", "interior_bedroom.jpg",
                         "interior_kitchen.jpg"],
            ),
            dict(
                title="Elegant 2-Bedroom Apartment in Westlands",
                realtor=brian, property_type="rent",
                address="Rhapta Road, Westlands", city="Nairobi", state="Nairobi",
                zipcode="00800", price=85000, bedrooms=2, bathrooms=Decimal("2.0"),
                garage=1, sqft=1020, latitude=-1.2673, longitude=36.8063,
                amenities=["High-speed lift", "24/7 security", "CCTV surveillance",
                           "Gym", "Rooftop terrace", "Fibre internet ready", "Parking"],
                description="Bright and airy 2-bedroom apartment on Rhapta Road, the heart of "
                            "Westlands. Modern finishes throughout, master ensuite, fitted wardrobe "
                            "space, and a balcony overlooking the city skyline. Walking distance to "
                            "Sarit Centre, malls, restaurants and nightlife.",
                main="listing3_main.jpg",
                gallery=["interior_living.jpg", "interior_bedroom.jpg", "interior_bathroom.jpg",
                         "interior_office.jpg"],
            ),
        ]
        self._save_listings(listings)

    def extend_listings(self):
        cynthia = Realtor.objects.filter(name="Cynthia Achieng").first()
        grace = Realtor.objects.filter(name="Grace Wanjiru").first()
        more = [
            dict(
                title="Ocean View 2-Bed Airbnb Apartment in Nyali, Mombasa",
                realtor=cynthia, property_type="airbnb",
                address="Links Road, Nyali", city="Mombasa", state="Mombasa",
                zipcode="80100", price=12000, bedrooms=2, bathrooms=Decimal("2.0"),
                garage=1, sqft=950, latitude=-4.0434, longitude=39.6866,
                amenities=["Ocean view", "Swimming pool", "Air conditioning", "Free WiFi",
                           "Fully equipped kitchen", "Backup power", "Daily housekeeping"],
                description="Fabulous ocean-view apartment in Nyali, perfect for a coastal "
                            "getaway. Two ensuite bedrooms, a bright open-plan living area, and a "
                            "balcony with sea breeze and sunrise views. Minutes from Nyali Centre, "
                            "Haller Park and Mombasa Marine Park. Rated 4.9 by our guests.",
                main="listing4_main.jpg",
                gallery=["interior_bedroom.jpg", "interior_living.jpg", "interior_kitchen.jpg",
                         "exterior_pool.jpg"],
            ),
            dict(
                title="Executive 5-Bedroom Townhouse in Runda",
                realtor=grace, property_type="sale",
                address="Ruaka Road, Runda", city="Nairobi", state="Nairobi",
                zipcode="00609", price=120000000, bedrooms=5, bathrooms=Decimal("5.0"),
                garage=2, sqft=4200, latitude=-1.2339, longitude=36.8012,
                amenities=["Gated community", "24/7 security", "Swimming pool", "Home office",
                           "DSQ", "Borehole water", "Solar backup"],
                description="A prestigious 5-bedroom all-ensuite townhouse in Runda. Meticulous "
                            "design with double-height entrance, family room, study, pantry "
                            "kitchen and guest wing. Set in a secure gated court with landscaped "
                            "gardens and club-quality amenities.",
                main="listing5_main.jpg",
                gallery=["interior_office.jpg", "interior_living.jpg", "interior_dining.jpg",
                         "interior_bedroom.jpg", "exterior_pool.jpg"],
            ),
            dict(
                title="Cozy Studio Airbnb in Kileleshwa",
                realtor=cynthia, property_type="airbnb",
                address="Oloitokitok Road, Kileleshwa", city="Nairobi", state="Nairobi",
                zipcode="00609", price=6500, bedrooms=1, bathrooms=Decimal("1.0"),
                garage=0, sqft=420, latitude=-1.2914, longitude=36.7736,
                amenities=["Smart TV", "Fast WiFi", "Full kitchen", "Workspace",
                           "Laundry", "24/7 check-in", "Secure parking"],
                description="A stylish self-contained studio, perfect for business travellers and "
                            "digital nomads. Fully equipped kitchen, dedicated workspace, superfast "
                            "fibre WiFi and blackout curtains for a perfect night's sleep. Quiet, "
                            "secure neighbourhood with easy access to the CBD and Westlands.",
                main="listing6_main.jpg",
                gallery=["interior_bedroom.jpg", "interior_kitchen.jpg", "interior_office.jpg",
                         "interior_bathroom.jpg"],
            ),
        ]
        self._save_listings(more)

    def _save_listings(self, listings):
        for l in listings:
            main_bytes = img_bytes(l.pop("main"))
            gallery = [img_bytes(g) for g in l.pop("gallery")]
            listing, created = Listing.objects.get_or_create(title=l["title"], defaults=l)
            if created or not listing.photo_main:
                if main_bytes:
                    listing.photo_main.save("main.jpg", ContentFile(main_bytes), save=True)
                for idx, gbytes in enumerate([g for g in gallery if g], start=1):
                    field = getattr(listing, f"photo_{idx}")
                    if not field:
                        field.save(f"gallery_{idx}.jpg", ContentFile(gbytes), save=True)
                listing.list_date = timezone.now()
                listing.save()
            self.stdout.write(f"{'Created' if created else 'Found   '} listing: {listing.title}")

    def new_listings(self):
        cynthia = Realtor.objects.filter(name="Cynthia Achieng").first()
        grace = Realtor.objects.filter(name="Grace Wanjiru").first()
        brian = Realtor.objects.filter(name="Brian Otieno").first()
        if not (cynthia and grace and brian):
            self.stdout.write(self.style.WARNING("Realtors missing - run realtor seeding first"))
            return

        newest = [
            dict(
                title="Stylish 3-Bedroom Apartment in Kileleshwa",
                realtor=cynthia, property_type="rent",
                address="Laikipia Road, Kileleshwa", city="Nairobi", state="Nairobi",
                zipcode="00609", price=95000, bedrooms=3, bathrooms=Decimal("2.5"),
                garage=1, sqft=1600, latitude=-1.2821, longitude=36.7795,
                amenities=["Balcony with city views", "Fitted kitchen", "Borehole water",
                           "Backup generator", "Ample parking", "24/7 security", "Lift"],
                description="Sun-filled 3-bedroom apartment on Laikipia Road in the leafy "
                            "heart of Kileleshwa. Master ensuite, a spacious lounge opening "
                            "onto a balcony with sunset views, modern fitted kitchen with "
                            "pantry and secure covered parking. Walking distance to "
                            "Kileleshwa's cafes and schools, with quick access to Kilimani "
                            "and the CBD - ideal for a professional family seeking a premium "
                            "rental in a quiet, secure neighbourhood.",
                main="listing7_main.jpg",
                gallery=["interior_living.jpg", "interior_bedroom.jpg", "interior_kitchen.jpg",
                         "interior_bathroom.jpg"],
            ),
            dict(
                title="Serene 4-Bedroom Maisonette with Garden in Kitengela",
                realtor=grace, property_type="sale",
                address="Acacia Avenue, Kitengela", city="Kitengela", state="Kajiado",
                zipcode="00242", price=14500000, bedrooms=4, bathrooms=Decimal("3.0"),
                garage=2, sqft=2400, latitude=-1.3667, longitude=36.9365,
                amenities=["Gated community", "Master ensuite", "Landscaped garden",
                           "Borehole water", "Solar water heating", "Family room", "DSQ"],
                description="A serene 4-bedroom maisonette on a corner plot in a fast-growing "
                            "Kitengela gated community. All bedrooms upstairs with the master "
                            "ensuite, a bright family room, private landscaped garden and "
                            "double garage. Paved driveway, borehole and solar water heating "
                            "keep running costs low. Ten minutes from Kitengela town and the "
                            "Namanga highway for an easy commute to Nairobi.",
                main="listing8_main.jpg",
                gallery=["interior_living.jpg", "interior_dining.jpg", "interior_kitchen.jpg",
                         "interior_bedroom.jpg", "exterior_pool.jpg"],
            ),
            dict(
                title="Chic 1-Bedroom Serviced Airbnb in Westlands",
                realtor=brian, property_type="airbnb",
                address="Mpaka Road, Westlands", city="Nairobi", state="Nairobi",
                zipcode="00800", price=7500, bedrooms=1, bathrooms=Decimal("1.0"),
                garage=0, sqft=620, latitude=-1.2621, longitude=36.8005,
                amenities=["Daily housekeeping", "Fibre WiFi", "Smart TV", "Workspace",
                           "Gym access", "24/7 check-in", "Rooftop lounge"],
                description="A chic serviced one-bedroom on Mpaka Road, steps away from "
                            "Westlands' malls, restaurants and co-working spaces. Hotel-grade "
                            "finishing with a king bed, dedicated workspace, fibre internet "
                            "and a rooftop lounge for sundowners. Daily housekeeping, gym "
                            "access and secure 24/7 check-in make it effortless for business "
                            "trips and city escapes alike.",
                main="listing9_main.jpg",
                gallery=["interior_bedroom.jpg", "interior_kitchen.jpg", "interior_office.jpg",
                         "interior_bathroom.jpg"],
            ),
        ]
        self._save_listings(newest)

    # ---------- services ----------
    def seed_services(self):
        services = [
            ("Property Sales", "fas fa-tag", "service_sales.jpg",
             "Expert guidance through the entire sales process, from listing to closing.",
             "Our sales team combines deep local market knowledge with a proven marketing engine "
             "to get your property sold at the best possible price.\n\n"
             "We handle professional photography, listing creation, viewings, negotiations and "
             "legal coordination with trusted conveyancing partners — keeping you informed at "
             "every step.\n\nWhether you are selling a family home, an apartment or a commercial "
             "building, we deliver results with transparency and integrity."),
            ("Property Rentals", "fas fa-key", "service_rentals.jpg",
             "Find your perfect rental home — or fill your property with quality tenants, fast.",
             "For tenants: we curate verified rentals across Nairobi, Mombasa and Kisumu with "
             "honest pricing and no hidden fees.\n\nFor landlords: we market your property, screen "
             "tenants thoroughly, prepare legally-sound tenancy agreements and manage move-ins.\n\n"
             "Our goal is long-term matches — happy tenants stay longer and take better care of "
             "your investment."),
            ("Airbnb Management", "fas fa-bed", "service_airbnb.jpg",
             "Turn-key Airbnb management that maximises your occupancy and nightly income.",
             "We transform apartments and homes into five-star short-stay experiences: listing "
             "creation, interior styling advice, dynamic pricing, guest communication, check-in "
             "management and professional cleaning between stays.\n\nOwner dashboards give you "
             "full visibility of bookings and earnings, while our team handles everything on the "
             "ground in Nairobi and at the Coast.\n\nMost hosts see occupancy rates above 85% "
             "within the first three months."),
            ("Property Management", "fas fa-home", "service_management.jpg",
             "Hands-off property management — from rent collection to maintenance and reporting.",
             "We protect your investment with comprehensive management: rent collection with "
             "timely remittance, tenant relations, routine inspections, maintenance coordination "
             "with vetted contractors and transparent monthly statements.\n\nOur proactive "
             "approach keeps tenants satisfied and properties in excellent condition, protecting "
             "both your income and your asset value."),
            ("Property Valuation", "fas fa-balance-scale", "service_valuation.jpg",
             "Independent, professional valuations for sales, mortgages, insurance and investment.",
             "Our valuation team provides accurate market valuations for residential and "
             "commercial properties across Kenya.\n\nTrusted by banks, insurers, landlords and "
             "diplomatic missions, our reports comply with ISVAL and VRB standards and are "
             "delivered within 5 working days."),
            ("Real Estate Consulting", "fas fa-comments", "service_consulting.jpg",
             "Strategic property advice for investors, developers and first-time buyers.",
             "From site selection and feasibility studies to market research and portfolio "
             "strategy, our consultants help you make confident decisions in the Kenyan property "
             "market.\n\nWe have advised individual investors, family offices, developers and "
             "corporate clients on transactions worth over KSh 5 billion."),
        ]
        for order, (title, icon, image_name, short_desc, desc) in enumerate(services, start=1):
            image_bytes = img_bytes(image_name)
            service, created = Service.objects.get_or_create(
                title=title,
                defaults=dict(
                    short_description=short_desc, description=desc,
                    icon_class=icon, is_featured=True, is_active=True, order=order,
                ))
            if image_bytes and not service.image:
                service.image.save(title.lower().replace(" ", "_") + ".jpg",
                                   ContentFile(image_bytes), save=True)
            self.stdout.write(f"{'Created' if created else 'Found   '} service: {service.title}")

    def seed_managed_properties(self):
        """Populate the Property Management page: one ManagedProperty per
        seeded listing; tenants, rent payments and maintenance schedules are
        added by _seed_pm_records so the page, detail views and analytics
        have data."""
        today = timezone.now().date()

        def d(days):
            return today + timedelta(days=days)

        portfolio = [
            # title, status, occupancy, started_days_ago, last_insp, next_insp, maint, notes
            ("Luxury 4-Bedroom Villa with Pool in Karen", "active", "vacant", 210, 40, 50, False,
             "Owner pays service charge; marketed for sale while vacant."),
            ("Modern 3-Bedroom Family House in Kilimani", "active", "occupied", 320, 25, 65, False,
             "Three-year lease in place; tenant pays via standing order."),
            ("Elegant 2-Bedroom Apartment in Westlands", "active", "occupied", 280, 18, 72, False,
             "Rent lands in full every 1st - a top performer."),
            ("Ocean View 2-Bed Airbnb Apartment in Nyali, Mombasa", "active", "occupied", 250, 21, 60, False,
             "Short-stay: housekeeping runs after every checkout."),
            ("Executive 5-Bedroom Townhouse in Runda", "active", "vacant", 190, 60, 30, False,
             "Owner in diaspora; viewings held every Saturday."),
            ("Cozy Studio Airbnb in Kileleshwa", "active", "occupied", 160, 15, 75, False,
             "88% occupancy last quarter; dynamic pricing active."),
            ("Stylish 3-Bedroom Apartment in Kileleshwa", "active", "occupied", 240, 30, 60, False,
             "New lease signed; fortnightly inspection rota."),
            ("Serene 4-Bedroom Maisonette with Garden in Kitengela", "active", "under_maintenance", 45, 10, 20, True,
             "Bathroom seal renewal and repainting before marketing."),
            ("Chic 1-Bedroom Serviced Airbnb in Westlands", "pending", "vacant", 5, None, 30, False,
             "Onboarding: photos, pricing and listing go-live this week."),
        ]
        managed = {}
        for (title, status, occupancy, started, last_insp, next_insp,
             maint, notes) in portfolio:
            listing = Listing.objects.filter(title=title).first()
            if not listing:
                self.stdout.write(self.style.WARNING(f"Listing missing, skipping: {title}"))
                continue
            defaults = dict(
                management_status=status,
                occupancy_status=occupancy,
                management_start_date=d(-started),
                maintenance_required=maint,
                management_notes=notes,
                last_inspection_date=d(-last_insp) if last_insp is not None else None,
                next_inspection_date=d(next_insp) if next_insp is not None else None,
            )
            prop, created = ManagedProperty.objects.get_or_create(
                listing=listing, defaults=defaults)
            self.stdout.write(f"{'Created' if created else 'Found   '} managed property: {listing.title}")
            managed[title] = prop

        self._seed_pm_records(managed)

    def _seed_pm_records(self, managed):
        """Demo tenants and rent payments for the managed long-term rentals."""
        today = timezone.now().date()

        def d(days):
            return today + timedelta(days=days)

        tenants_spec = [
            # first, last, email, phone, national_id, listing title, moved_in_days_ago, lease_days
            ("Esther", "Kamau", "esther.kamau@example.com", "+254 722 601 118",
             "KE-29461507", "Modern 3-Bedroom Family House in Kilimani", 300, 730),
            ("Daniel", "Kiprop", "daniel.kiprop@example.com", "+254 733 118 942",
             "KE-30521884", "Elegant 2-Bedroom Apartment in Westlands", 230, 730),
            ("Faith", "Njeri", "faith.njeri@example.com", "+254 711 344 527",
             "KE-31207745", "Stylish 3-Bedroom Apartment in Kileleshwa", 150, 730),
        ]
        tenants = {}
        for first, last, email, phone, natid, prop_title, moved_in, lease_days in tenants_spec:
            prop = managed.get(prop_title)
            if not prop:
                continue
            tenant, created = Tenant.objects.get_or_create(
                national_id=natid,
                defaults=dict(
                    managed_property=prop, first_name=first, last_name=last,
                    email=email, phone=phone, status="active",
                    move_in_date=d(-moved_in),
                    monthly_rent=prop.listing.price,
                    deposit_amount=prop.listing.price * 2,
                    lease_start_date=d(-moved_in),
                    lease_end_date=d(-moved_in + lease_days),
                    emergency_contact_name=f"{last} family member",
                    emergency_contact_phone="+254 700 000 000",
                    notes="Screened, referenced and placed by our rentals team.",
                ))
            tenants[natid] = tenant
            self.stdout.write(f"{'Created' if created else 'Found   '} tenant: {first} {last} ({prop_title})")

        # ---------- rent payments ----------
        payment_plan = [
            # national_id, due_offset_days, status, method  (last month + current month)
            ("KE-29461507", -32, "paid", "mobile_money"),
            ("KE-29461507", -2, "paid", "bank_transfer"),
            ("KE-30521884", -27, "paid", "bank_transfer"),
            ("KE-30521884", 3, "pending", ""),
            ("KE-31207745", -3, "overdue", ""),
        ]
        for natid, due_off, status, method in payment_plan:
            tenant = tenants.get(natid)
            if not tenant:
                continue
            due = d(due_off)
            payment, created = RentPayment.objects.get_or_create(
                tenant=tenant, due_date=due,
                defaults=dict(
                    amount_due=tenant.monthly_rent,
                    amount_paid=tenant.monthly_rent if status == "paid" else 0,
                    status=status,
                    payment_method=method,
                    payment_date=d(due_off + 2) if status == "paid" else None,
                    reference_number="RNT-{}-{}".format(due.strftime("%Y%m"), natid[-5:]),
                    notes="Seeded demo payment record.",
                ))
            self.stdout.write(f"{'Created' if created else 'Found   '} rent payment: {tenant} due {due} ({status})")

        self._seed_pm_maintenance(managed)

    def _seed_pm_maintenance(self, managed):
        """Maintenance schedules for the managed portfolio."""
        today = timezone.now().date()

        def d(days):
            return today + timedelta(days=days)

        maint_plan = [
            # listing title, task, description, priority, status, scheduled_offset, completed_offset
            ("Modern 3-Bedroom Family House in Kilimani",
             "Quarterly AC service and garden tap fix",
             "Quarterly servicing of all AC units completed; garden tap washer replaced. "
             "Tenant confirmed everything works.",
             "medium", "completed", -22, -19),
            ("Serene 4-Bedroom Maisonette with Garden in Kitengela",
             "Bathroom seal renewal and repaint",
             "Renew shower seals in both bathrooms and repaint the hallway before "
             "marketing the property for sale.",
             "high", "in_progress", 3, None),
        ]
        for prop_title, task, desc, prio, status, sched_off, comp_off in maint_plan:
            prop = managed.get(prop_title)
            if not prop:
                continue
            schedule, created = MaintenanceSchedule.objects.get_or_create(
                managed_property=prop, title=task,
                defaults=dict(
                    description=desc, priority=prio, status=status,
                    scheduled_date=d(sched_off),
                    estimated_duration="1 day",
                    completion_date=d(comp_off) if comp_off is not None else None,
                    completion_notes=("Completed and verified by the property manager."
                                      if comp_off is not None else ""),
                ))
            self.stdout.write(f"{'Created' if created else 'Found   '} maintenance: {task} ({prop_title})")

        self.stdout.write(self.style.SUCCESS(
            f"Managed portfolio: {ManagedProperty.objects.count()} properties, "
            f"{Tenant.objects.count()} tenants, {RentPayment.objects.count()} payments"))

    # ---------- blog ----------
    def seed_blog(self):
        author = User.objects.filter(username="sammaina").first()
        if not author:
            author = User.objects.create_superuser(
                username="sammaina", email="samuelmainer@gmail.com",
                password="Temp!Pass2026", first_name="Sam", last_name="Maina")
            self.stdout.write("Created author user: sammaina (temp password - change in admin)")

        category, _ = BlogCategory.objects.get_or_create(name="Market Insights")

        posts = [
            ("Nairobi Property Market Outlook: What Buyers and Investors Should Know", "blog1.jpg",
             "Prices in prime Nairobi suburbs are stabilising while rental yields in satellite "
             "towns keep climbing. Here is what the data says — and how to position yourself "
             "for 2026.",
             "Nairobi's property market has entered an interesting phase. Prime suburbs such as "
             "Karen, Runda and Lavington are seeing price stability, while areas along new "
             "transport corridors — particularly along Mombasa Road, Kiambu Road and the "
             "Eastern Bypass — continue to record strong rental growth.\n\n"
             "For buyers, this is good news: realistic asking prices are returning to the prime "
             "market, and well-priced homes are selling within weeks. For investors, rental "
             "yields of 6–8% remain achievable in well-managed apartments around Kilimani, "
             "Kileleshwa and Westlands.\n\n"
             "Our advice for 2026: buy quality, insist on verified titles, and take management "
             "seriously — professionally managed units consistently outperform by 15–20% in "
             "net yield."),
            ("A First-Timer's Guide to Buying Property in Kenya", "blog2.jpg",
             "From title searches to stamp duty — everything first-time buyers need to know to "
             "buy property in Kenya safely and confidently.",
             "Buying your first property in Kenya is exciting — and it becomes truly rewarding "
             "when you follow the right process.\n\n"
             "1. Verify the title: always conduct an official search at the Ministry of Lands "
             "to confirm ownership and check for encumbrances.\n\n"
             "2. Budget beyond the price: add stamp duty (4% urban, 2% rural), legal fees, "
             "valuation and transfer costs to your budget.\n\n"
             "3. Use professionals: an independent lawyer and a registered valuer protect you "
             "from costly mistakes.\n\n"
             "4. Work with verified agents: every realtor on Kenya Realestate Platform is "
             "admin-verified before their listings go live.\n\n"
             "Follow these steps and you will join thousands of Kenyans building wealth "
             "through property — safely and with confidence."),
            ("Airbnb Management: Why Nairobi Hosts Are Going Professional", "blog3.jpg",
             "Professional Airbnb management is lifting occupancy above 85% in Nairobi. Here's "
             "how the numbers work for property owners.",
             "Short-stay rentals in Nairobi have matured. The days of simply listing a room and "
             "waiting for bookings are gone — today's guests expect hotel-grade consistency.\n\n"
             "Professionally managed Airbnb units in Nairobi now achieve average occupancy of "
             "85%+ versus roughly 55–60% for self-managed listings. The difference comes from "
             "dynamic pricing, sub-hour guest response times, professional photography and "
             "immaculate cleaning standards.\n\n"
             "For owners, the maths is simple: a professionally managed Kileleshwa studio "
             "grossing KSh 6,500 per night at 85% occupancy outearns a long-term tenant renting "
             "the same unit — with zero day-to-day involvement.\n\n"
             "Our Airbnb team currently manages units in Kileleshwa, Westlands, Kilimani and "
             "Nyali — and we are adding new properties every month."),
            ("Is Professional Property Management Worth It? The Numbers Say Yes", "blog4.jpg",
             "Handing your units to a professional manager lifts on-time rent collection "
             "above 95% and cuts vacancy to weeks. Here is the maths landlords actually use.",
             "Every landlord eventually asks the same question: should I hand my property to "
             "a professional manager, or keep collecting rent myself?\n\n"
             "The numbers from our managed portfolio make the case. Professionally managed "
             "units in Nairobi collect 95%+ of rent on time, versus roughly 70% for "
             "self-managed landlords. Average vacancy between tenants drops from one to two "
             "months to under two weeks, because marketing, screening and move-ins run as a "
             "pipeline rather than a scramble.\n\n"
             "Then weigh it against the fees: management typically costs 7-10% of collected "
             "rent. On a KSh 95,000 Kileleshwa apartment, one avoided vacant month already "
             "covers an entire year of management fees - before a single midnight maintenance "
             "call is handled for you.\n\n"
             "Our management team takes over tenant screening, rent collection with monthly "
             "statements, routine inspections, vetted-contractor repairs and exit management. "
             "Own the property; skip the day-to-day."),
        ]
        for title, image, short_desc, desc in posts:
            image_bytes = img_bytes(image)
            blog, created = Blog.objects.get_or_create(
                title=title,
                defaults=dict(
                    short_description=short_desc[:300], description=desc,
                    author=author, category=category, read_time=5, published=True,
                ))
            if image_bytes and not blog.image:
                blog.image.save(image, ContentFile(image_bytes), save=True)
            self.stdout.write(f"{'Created' if created else 'Found   '} blog: {blog.title}")

    # ---------- testimonials ----------
    def seed_testimonials(self):
        users = []
        demo = [
            ("james_mwangi", "james.mwangi@example.com", "James", "Mwangi"),
            ("sarah_njeri", "sarah.njeri@example.com", "Sarah", "Njeri"),
            ("david_kimani", "david.kimani@example.com", "David", "Kimani"),
            ("amina_hassan", "amina.hassan@example.com", "Amina", "Hassan"),
        ]
        for username, email, first, last in demo:
            user = User.objects.filter(username=username).first()
            if not user:
                user = User.objects.create_user(username=username, email=email,
                                                password="Demo!Pass2026",
                                                first_name=first, last_name=last)
            users.append(user)

        entries = [
            ("James Mwangi", 5, "Found our dream home in Karen",
             "Grace was incredible from the first viewing to the final signing. She understood "
             "exactly what our family needed and negotiated a fantastic price on our Karen "
             "villa. The whole process was transparent and stress-free.",
             "Luxury 4-Bedroom Villa with Pool in Karen", users[0], True),
            ("Sarah Njeri", 5, "Best apartment hunt experience in Nairobi",
             "Brian sent me verified listings that actually matched my budget and taste — no "
             "time-wasting. Moved into my Westlands apartment within two weeks of my first "
             "enquiry. Highly recommended!",
             "Elegant 2-Bedroom Apartment in Westlands", users[1], True),
            ("David Kimani", 4, "Fantastic coastal getaway",
             "The Nyali apartment was exactly as pictured — the ocean view at sunrise is worth "
             "every shilling. Booking, check-in and communication were all seamless. We will "
             "definitely be back!",
             "Ocean View 2-Bed Airbnb Apartment in Nyali, Mombasa", users[2], False),
            ("Amina Hassan", 5, "My property finally earns what it should",
             "I transferred my Kilimani units to their management service and occupancy jumped "
             "from 60% to over 90%. Rent arrives on time every month and maintenance issues are "
             "handled before I even hear about them.",
             None, users[3], True),
        ]
        for name, rating, t_title, content, listing_title, user, featured in entries:
            listing = Listing.objects.filter(title=listing_title).first() if listing_title else None
            entry, created = Testimonial.objects.get_or_create(
                name=name,
                defaults=dict(
                    rating=rating, title=t_title, content=content, client=user,
                    listing=listing, status="approved", is_featured=featured,
                ))
            self.stdout.write(f"{'Created' if created else 'Found   '} testimonial: {entry.name}")





