#!/usr/bin/env python3
"""Generate the service and area pages, sitemap.xml and 404.html.

Shared blocks (icon sprite, header, estimate form, final CTA, footer) are copied
from index.html between the <!-- @name:start --> / <!-- @name:end --> markers,
so edit them there and re-run:

    python3 tools/build_pages.py
"""
import json
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://christinascleaningservices.com"
PHONE = "(443) 210-6133"
TODAY = date.today().isoformat()
BIZ_ID = f"{SITE}/#business"

INDEX = (ROOT / "index.html").read_text(encoding="utf-8")


def block(name):
    m = re.search(rf"<!-- @{name}:start -->\n(.*?)<!-- @{name}:end -->", INDEX, re.S)
    if not m:
        raise SystemExit(f"marker @{name} not found in index.html")
    return m.group(1)


def for_subpage(html):
    # In-page anchors of the home page become links back to it (#estimate/#top/#main exist on every page).
    return re.sub(r'href="#(results|services|why|about|areas|faq)"', r'href="/#\1"', html)


SPRITE = block("sprite")
HEADER = for_subpage(block("header"))
QUOTE = block("quote")
CTA = block("cta")
FOOTER = for_subpage(block("footer"))

IMG = {
    "table": ("Wood Furniture Restoration", 899, 531, "Wood table covered in dust and stains", "Wood table polished and glowing"),
    "sink": ("Bathroom Vanity", 344, 619, "Bathroom sink with residue", "Bathroom sink shining"),
    "window": ("Window Tracks &amp; Sills", 907, 531, "Window sill full of dirt and debris", "Clean window sill"),
    "toilet": ("Bathroom Floors &amp; Grout", 907, 531, "Toilet base with dark grout", "Toilet base and bright grout"),
    "bathtub": ("Bathtub Deep Clean", 907, 385, "Stained bathtub", "White bathtub"),
    "baseboard": ("Baseboards &amp; Heaters", 907, 531, "Dusty baseboard heater", "Dust-free baseboard heater"),
    "lamp": ("Dusting &amp; Polishing", 344, 619, "Dusty nightstand and lamp", "Polished nightstand and lamp"),
}

SERVICES = {
    "residential-cleaning": ("Residential Cleaning", "i-home", "Weekly, bi-weekly and monthly house cleaning."),
    "deep-cleaning": ("Deep Cleaning", "i-spray", "A top-to-bottom reset for your home."),
    "commercial-cleaning": ("Commercial Cleaning", "i-building", "Offices, pharmacies and retail spaces."),
    "move-in-move-out-cleaning": ("Move In / Move Out", "i-box", "Empty-home cleaning for tenants, owners and realtors."),
    "post-construction-cleaning": ("Post-Construction", "i-hardhat", "Fine dust and residue removed after renovations."),
}
AREAS = {
    "salisbury-md": ("Salisbury, MD", "Salisbury"),
    "lewes-de": ("Lewes, DE", "Lewes"),
    "rehoboth-beach-de": ("Rehoboth Beach, DE", "Rehoboth Beach"),
    "millsboro-de": ("Millsboro, DE", "Millsboro"),
}


def icon(name):
    return f'<svg class="i"><use href="#{name}"/></svg>'


def compare(key, delay=""):
    cap, w, h, before, after = IMG[key]
    style = f' style="--d:{delay}"' if delay else ""
    return f'''      <figure class="ba" data-reveal{style}>
        <div class="compare" data-compare tabindex="0" role="slider" aria-label="{cap} before and after" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50">
          <img class="compare__img compare__before" src="/assets/img/results/{key}-before.webp" alt="{before} before cleaning" loading="lazy" width="{w}" height="{h}">
          <img class="compare__img compare__after" src="/assets/img/results/{key}-after.webp" alt="{after} after cleaning by Christina's Cleaning Services" loading="lazy" width="{w}" height="{h}">
          <span class="compare__tag compare__tag--before">Before</span>
          <span class="compare__tag compare__tag--after">After</span>
          <span class="compare__handle"><span class="compare__knob">{icon("i-drag")}</span></span>
        </div>
        <figcaption>{cap}</figcaption>
      </figure>'''


def strip_tags(html):
    return re.sub(r"<[^>]+>", "", html).replace("&amp;", "&").replace("&nbsp;", " ")


def related_cards(items):
    cards = []
    for href, ico, title, text in items:
        cards.append(f'''      <a class="related__card" href="{href}" data-reveal>
        <span class="svc__icon">{icon(ico)}</span>
        <strong>{title}</strong>
        <span>{text}</span>
        <em>Learn more {icon("i-arrow")}</em>
      </a>''')
    return "\n".join(cards)


def page(p):
    url = f"{SITE}{p['path']}"
    crumbs = [("Home", "/")] + p["crumbs"]

    graph = [
        {
            "@type": "WebPage",
            "@id": f"{url}#webpage",
            "url": url,
            "name": p["title"],
            "description": p["desc"],
            "isPartOf": {"@id": f"{SITE}/#website"},
            "about": {"@id": BIZ_ID},
            "breadcrumb": {"@id": f"{url}#breadcrumb"},
            "inLanguage": "en-US",
        },
        {
            "@type": "BreadcrumbList",
            "@id": f"{url}#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name, "item": f"{SITE}{href}"}
                for i, (name, href) in enumerate(crumbs)
            ],
        },
        {
            "@type": "Service",
            "@id": f"{url}#service",
            "name": p["service_name"],
            "serviceType": p["service_type"],
            "description": p["desc"],
            "url": url,
            "provider": {"@id": BIZ_ID},
            "areaServed": p["area_served"],
        },
        {
            "@type": "FAQPage",
            "@id": f"{url}#faq",
            "mainEntity": [
                {"@type": "Question", "name": strip_tags(q), "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
                for q, a in p["faq"]
            ],
        },
    ]
    schema = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)

    crumb_html = "\n".join(
        f'          <li><a href="{href}">{name}</a></li>' if i < len(crumbs) - 1
        else f'          <li><span aria-current="page">{name}</span></li>'
        for i, (name, href) in enumerate(crumbs)
    )
    checklist = []
    for title, items in p["checklist"]:
        checklist.append(f"        <h3>{title}</h3>\n        <ul>\n" + "\n".join(
            f"          <li>{icon('i-check')} {it}</li>" for it in items) + "\n        </ul>")
    faq_html = "\n".join(
        f'''      <details class="qa"{" open" if i == 0 else ""}>
        <summary>{q}<span class="qa__icon">{icon("i-plus")}</span></summary>
        <div class="qa__body"><p>{a}</p></div>
      </details>''' for i, (q, a) in enumerate(p["faq"]))

    quote = QUOTE.replace('<form class="form" id="quote-form" novalidate',
                          f'<form class="form" id="quote-form" novalidate data-default-service="{p.get("form_service", "")}"')

    results = ""
    if p.get("results"):
        figs = "\n".join(compare(k, f".{i}s" if i else "") for i, k in enumerate(p["results"]))
        results = f'''
<section class="section results">
  <div class="container">
    <header class="section-head" data-reveal>
      <p class="eyebrow">{icon("i-sparkles")} Real results</p>
      <h2 class="section-title">{p["results_title"]}</h2>
      <p class="section-lead">Drag the handle to compare. These are real before and after photos from Christina's team.</p>
    </header>
    <div class="ba-row">
{figs}
    </div>
  </div>
</section>
'''
    if p.get("gallery"):
        results = f'''
<section class="section commercial">
  <div class="container commercial__grid">
    <div class="commercial__media" data-reveal>
      <div class="commercial__img commercial__img--a"><img src="/assets/img/commercial-office.webp" alt="Christina's team cleaning a modern office in Maryland and Delaware" loading="lazy" width="550" height="860"></div>
      <div class="commercial__img commercial__img--b"><img src="/assets/img/commercial-pharmacy.webp" alt="Christina's team cleaning a pharmacy" loading="lazy" width="540" height="1140"></div>
    </div>
    <div class="commercial__copy" data-reveal style="--d:.1s">
      <p class="eyebrow eyebrow--light">{icon("i-building")} Who we clean for</p>
      <h2 class="section-title section-title--light">Clean spaces. <em>Strong impressions.</em></h2>
      <p>{p["gallery"]}</p>
      <a href="#estimate" class="btn btn--gold magnetic"><span>Get a commercial quote</span>{icon("i-arrow")}</a>
    </div>
  </div>
</section>
'''

    trust = f'''      <ul class="hero__trust" data-hero>
        <li>{icon("i-shield")} Licensed &amp; Insured</li>
        <li>{icon("i-leaf")} Eco-Friendly Products</li>
        <li>{icon("i-badge")} Satisfaction Guaranteed</li>
      </ul>'''

    return f'''<!doctype html>
<html lang="en-US">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{p["title"]}</title>
  <meta name="description" content="{escape(p["desc"])}">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#2B0A1F">
  <meta name="geo.region" content="{p.get("geo_region", "US-MD")}">
  <meta name="geo.placename" content="{p.get("geo", "Salisbury, Maryland")}">

  <meta property="og:type" content="website">
  <meta property="og:locale" content="en_US">
  <meta property="og:site_name" content="Christina's Cleaning Services">
  <meta property="og:title" content="{escape(p["title"])}">
  <meta property="og:description" content="{escape(p["desc"])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}/assets/img/og-image.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(p["title"])}">
  <meta name="twitter:description" content="{escape(p["desc"])}">
  <meta name="twitter:image" content="{SITE}/assets/img/og-image.jpg">

  <link rel="icon" type="image/png" href="/assets/img/favicon.png">
  <link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Manrope:wght@400;500;600;700;800&family=Allura&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">

  <script type="application/ld+json">
{schema}
  </script>
</head>
<body class="is-loading" data-page="{p["path"].strip("/").replace("/", "-")}">
<!-- Generated by tools/build_pages.py - edit the data there, not this file. -->

{SPRITE}
<a class="skip-link" href="#main">Skip to content</a>

{HEADER}
<main id="main">

<section class="hero hero--page" id="estimate">
  <canvas class="hero__sparkles" id="sparkles" aria-hidden="true"></canvas>
  <div class="hero__aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="hero__monogram" aria-hidden="true">C</div>

  <div class="container hero__grid">
    <div class="hero__copy">
      <nav class="breadcrumb" aria-label="Breadcrumb" data-hero>
        <ol>
{crumb_html}
        </ol>
      </nav>
      <h1 class="hero__title">
        <span class="line"><span data-hero>{p["h1"][0]}</span></span>
        <span class="line"><span data-hero><em class="shimmer">{p["h1"][1]}</em></span></span>
      </h1>
      <p class="hero__script" data-hero>{p["script"]}</p>
      <p class="hero__lead" data-hero>{p["lead"]}</p>
      <div class="hero__ctas" data-hero>
        <a href="tel:+14432106133" class="btn btn--light magnetic">{icon("i-phone")}<span>Call {PHONE}</span></a>
        <a href="#details" class="btn btn--ghost magnetic"><span>{p["cta2"]}</span>{icon("i-arrow")}</a>
      </div>
{trust}
    </div>

{quote}  </div>
</section>

<section class="section detail" id="details">
  <div class="container detail__grid">
    <div class="prose" data-reveal>
{p["body"]}
    </div>
    <aside class="checklist" data-reveal style="--d:.1s" aria-label="What's included">
{chr(10).join(checklist)}
        <a href="#estimate" class="btn btn--plum magnetic"><span>Get my free estimate</span>{icon("i-arrow")}</a>
    </aside>
  </div>
</section>
{results}
<section class="section faq">
  <div class="container faq__inner">
    <header class="section-head" data-reveal>
      <p class="eyebrow">{icon("i-message")} Good questions</p>
      <h2 class="section-title">{p["faq_title"]}</h2>
    </header>
    <div class="faq__list" data-reveal>
{faq_html}
    </div>
  </div>
</section>

<section class="section related">
  <div class="container">
    <div class="related__head" data-reveal>
      <h2 class="section-title">{p["related_title"]}</h2>
      <a href="/" class="btn btn--ghost-dark btn--sm"><span>Back to home</span>{icon("i-arrow")}</a>
    </div>
    <div class="related__grid">
{related_cards(p["related"])}
    </div>
  </div>
</section>

{CTA}
</main>

{FOOTER}
<script src="/assets/js/main.js" defer></script>
</body>
</html>
'''


def svc_related(exclude):
    items = [(f"/services/{s}/", ico, name, text) for s, (name, ico, text) in SERVICES.items() if s != exclude]
    return items[:4]


def area_related():
    return [(f"/areas/{slug}/", "i-pin", f"House Cleaning {name}", f"Residential &amp; commercial cleaning in {short}.")
            for slug, (name, short) in AREAS.items()]


def sussex():
    """Every place we serve: Salisbury, MD plus the Sussex County, DE towns."""
    return ([{"@type": "City", "name": "Salisbury", "containedInPlace": {"@type": "AdministrativeArea", "name": "Wicomico County, Maryland"}}]
            + [{"@type": "City", "name": n, "containedInPlace": {"@type": "AdministrativeArea", "name": "Sussex County, Delaware"}}
               for n in ("Lewes", "Rehoboth Beach", "Millsboro")]
            + [{"@type": "AdministrativeArea", "name": "Sussex County, Delaware"}])


A = lambda slug, text: f'<a href="/services/{slug}/">{text}</a>'
AR = lambda slug, text: f'<a href="/areas/{slug}/">{text}</a>'

PAGES = [
    # ------------------------------------------------------------------ SERVICES
    dict(
        path="/services/residential-cleaning/",
        title="Residential Cleaning Salisbury MD & Sussex DE | Christina's",
        desc="Weekly, bi-weekly & monthly house cleaning in Salisbury, MD and Lewes, Rehoboth Beach & Millsboro, DE. Insured, detail-oriented team. Free estimate.",
        crumbs=[("Services", "/#services"), ("Residential Cleaning", "/services/residential-cleaning/")],
        service_name="Residential House Cleaning", service_type="House cleaning", area_served=sussex(),
        form_service="Residential Cleaning",
        h1=("House Cleaning Services", "in Maryland &amp; Delaware"),
        script="Clean home, happy life.",
        lead="Recurring and one-time house cleaning for homes in Salisbury, MD and in Lewes, Rehoboth Beach, Millsboro and across Sussex County, DE. Kitchens, bathrooms, bedrooms and living areas, cleaned with the detail you'd expect from the owner herself.",
        cta2="What's included",
        body=f'''      <h2>Your home, <em>consistently spotless</em></h2>
      <p>Life on Delmarva is busy, between work, family, the beach and everything in between. Christina's residential cleaning takes the chores off your list so you can come home to a space that feels calm, fresh and cared for.</p>
      <p>Every visit follows a detailed checklist, and every home is different, so we tailor the service to what matters most to you. Want extra attention on the kitchen, the kids' bathroom or the pet hair on the stairs? Just tell us.</p>
      <h3>Recurring plans that fit your routine</h3>
      <p>Most families choose <strong>weekly</strong> or <strong>bi-weekly</strong> house cleaning to keep things under control, while others prefer a <strong>monthly</strong> refresh. You pick the frequency and day, and we show up ready to work.</p>
      <h3>Starting with a deep clean</h3>
      <p>If your home hasn't been professionally cleaned in a while, we often recommend starting with a {A("deep-cleaning", "deep cleaning")}. It resets the whole house, so your recurring visits keep it spotless from then on.</p>
      <h3>Kind to kids, pets and the planet</h3>
      <p>We use eco-friendly products that are tough on dirt and gentle on the people and pets who live in your home.</p>
      <p>Serving {AR("salisbury-md", "Salisbury, MD")}, {AR("lewes-de", "Lewes")}, {AR("rehoboth-beach-de", "Rehoboth Beach")}, {AR("millsboro-de", "Millsboro")} and nearby communities.</p>''',
        checklist=[
            ("Kitchen", ["Countertops &amp; backsplash wiped", "Sink &amp; faucet cleaned and shined", "Appliance exteriors &amp; microwave", "Cabinet fronts &amp; handles", "Floors vacuumed &amp; mopped"]),
            ("Bathrooms", ["Tub, shower &amp; tile scrubbed", "Toilet cleaned inside &amp; out", "Sinks, vanity &amp; mirrors", "Floors &amp; baseboards"]),
            ("Bedrooms &amp; living areas", ["Dusting of reachable surfaces", "Furniture &amp; decor wiped", "Floors vacuumed &amp; mopped", "Trash emptied"]),
        ],
        results=["bathtub", "sink"], results_title="Bathrooms that <em>shine again</em>",
        faq_title="House cleaning <em>questions</em>",
        faq=[
            ("What's included in a standard house cleaning?", "Kitchens, bathrooms, bedrooms and living areas: surfaces wiped and dusted, bathrooms scrubbed, floors vacuumed and mopped and trash emptied. Every plan can be customized to your home."),
            ("How often should I schedule house cleaning?", "Most homes do best with weekly or bi-weekly visits. Monthly cleanings are great for smaller homes or light upkeep, and one-time cleanings are always available."),
            ("How much does house cleaning cost?", f"Every home is different, so pricing depends on size, condition and how often you'd like us to come. Request a free, no-obligation estimate with the form on this page or call {PHONE}."),
            ("Are your cleaners insured?", "Yes. Christina's Cleaning Services is fully licensed and insured, so your home is protected while we work."),
        ],
        related_title="More ways we can <em>help</em>",
        related=svc_related("residential-cleaning")[:2] + area_related()[:2],
    ),
    dict(
        path="/services/deep-cleaning/",
        title="Deep Cleaning Salisbury MD & Sussex County DE | Christina's",
        desc="Top-to-bottom deep cleaning in Salisbury, MD and Sussex County, DE: grout, baseboards, window tracks, vents and every corner. Insured team. Free estimate.",
        crumbs=[("Services", "/#services"), ("Deep Cleaning", "/services/deep-cleaning/")],
        service_name="Deep Cleaning", service_type="Deep cleaning", area_served=sussex(),
        form_service="Deep Cleaning",
        h1=("Deep Cleaning Services", "in Maryland &amp; Delaware"),
        script="Every corner. Every detail.",
        lead="A complete reset for your home. We go after the grout, baseboards, window tracks, vents and hidden spots that regular cleanings skip, so your home feels truly clean again.",
        cta2="See the deep clean checklist",
        body=f'''      <h2>When &quot;clean&quot; <em>isn't enough</em></h2>
      <p>Over time, dust settles into baseboards, grime builds up in grout lines and window tracks fill with debris. A deep cleaning removes that build-up so your home looks and feels brand new.</p>
      <p>Look at the photos on this page: dark grout brought back to bright, window sills cleared of dirt and heaters dusted inside and out. That's the level of detail Christina's team brings to every deep clean.</p>
      <h3>When to book a deep cleaning</h3>
      <p>Deep cleans are perfect as a <strong>first visit</strong> before a recurring plan, for <strong>seasonal</strong> spring or fall refreshes, before hosting family or after a long, busy season at the beach house.</p>
      <h3>Deep cleaning vs. regular cleaning</h3>
      <p>A regular {A("residential-cleaning", "house cleaning")} maintains a home that's already in good shape. A deep clean takes more time and reaches the areas that routine visits don't, like baseboards, door frames, vents, grout and window tracks.</p>
      <p>Moving out? Take a look at our {A("move-in-move-out-cleaning", "move in / move out cleaning")}, designed for empty homes.</p>''',
        checklist=[
            ("Everything in a standard clean, plus", ["Baseboards &amp; door frames hand-wiped", "Grout &amp; tile scrubbed", "Window sills &amp; tracks detailed", "Vents, light fixtures &amp; ceiling fans dusted", "Baseboard heaters cleaned", "Light switches &amp; high-touch points", "Hard-to-reach corners &amp; edges"]),
        ],
        results=["toilet", "window", "baseboard", "table"], results_title="The difference a <em>deep clean</em> makes",
        faq_title="Deep cleaning <em>questions</em>",
        faq=[
            ("What is the difference between deep cleaning and regular cleaning?", "Regular cleaning maintains your home. Deep cleaning also tackles build-up in grout, baseboards, door frames, vents, window tracks and other hard-to-reach areas."),
            ("How long does a deep cleaning take?", "It depends on the size and condition of the home. We'll give you a clear idea of timing along with your free estimate."),
            ("How often do I need a deep cleaning?", "Most homes benefit from a deep clean once or twice a year, or as the first visit before starting a weekly or bi-weekly plan."),
            ("How much does a deep cleaning cost?", f"Pricing depends on the size and condition of your home. Request a free, no-obligation estimate on this page or call {PHONE}."),
        ],
        related_title="More ways we can <em>help</em>",
        related=svc_related("deep-cleaning")[:2] + area_related()[:2],
    ),
    dict(
        path="/services/commercial-cleaning/",
        title="Commercial Cleaning Salisbury MD & Sussex DE | Christina's",
        desc="Office, pharmacy and retail cleaning in Salisbury, MD and Sussex County, DE. Daily, weekly or custom schedules. Licensed & insured. Free estimate.",
        crumbs=[("Services", "/#services"), ("Commercial Cleaning", "/services/commercial-cleaning/")],
        service_name="Commercial Cleaning", service_type="Commercial cleaning", area_served=sussex(),
        form_service="Commercial Cleaning",
        h1=("Commercial Cleaning", "in Maryland &amp; Delaware"),
        script="A cleaner workspace. A better business.",
        lead="Offices, pharmacies, retail stores and workspaces kept clean, healthy and welcoming, on a daily, weekly or custom schedule that never gets in the way of your business.",
        cta2="What we clean",
        body=f'''      <h2>Clean spaces. <em>Strong impressions.</em></h2>
      <p>Your customers and employees notice everything, from the entrance glass to the restroom. Christina's commercial cleaning keeps your business looking professional and feeling healthy, every single day.</p>
      <p>We work with offices, pharmacies, retail stores and other workspaces in Salisbury, MD and across Sussex County, DE. Our uniformed, trained team follows a consistent checklist, so you get the same high standard on every visit.</p>
      <h3>Flexible scheduling</h3>
      <p>Choose <strong>daily</strong>, <strong>weekly</strong> or a <strong>custom</strong> plan. Tell us your business hours and we'll build a schedule that keeps your space clean without disrupting your team or your customers.</p>
      <h3>Licensed, insured and reliable</h3>
      <p>We're fully licensed and insured, and we take pride in showing up on time and doing the job right. When you hand us the keys, you can focus on running your business.</p>
      <p>Just finished a renovation or build-out? See our {A("post-construction-cleaning", "post-construction cleaning")}.</p>''',
        checklist=[
            ("Workspaces &amp; common areas", ["Desks, counters &amp; surfaces wiped", "High-touch points disinfected", "Trash &amp; recycling emptied", "Entry doors &amp; glass cleaned"]),
            ("Restrooms &amp; breakrooms", ["Toilets, sinks &amp; mirrors", "Kitchenette &amp; appliance exteriors", "Supplies area tidied"]),
            ("Floors", ["Vacuuming &amp; mopping", "Baseboards &amp; corners"]),
        ],
        gallery="From busy offices to pharmacies and retail floors, our team keeps your space ready for customers and comfortable for your staff, on a schedule built around your business.",
        faq_title="Commercial cleaning <em>questions</em>",
        faq=[
            ("What types of businesses do you clean?", "We clean offices, pharmacies, retail stores and other commercial spaces in Salisbury, Maryland and across Sussex County, Delaware."),
            ("How often can you clean my business?", "We offer daily, weekly and custom cleaning plans, built around your hours and the needs of your space."),
            ("Are you licensed and insured?", "Yes. Christina's Cleaning Services is fully licensed and insured."),
            ("How do I get a commercial cleaning quote?", f"Use the form on this page or call {PHONE}. Tell us about your space and how often you need cleaning, and we'll send a free, no-obligation estimate."),
        ],
        related_title="More ways we can <em>help</em>",
        related=svc_related("commercial-cleaning")[:2] + area_related()[:2],
    ),
    dict(
        path="/services/move-in-move-out-cleaning/",
        title="Move In/Out Cleaning Salisbury MD & Sussex DE | Christina's",
        desc="Move-in and move-out cleaning in Salisbury, MD and Sussex County, DE. Cabinets, appliances, bathrooms and floors, ready for the next chapter. Free estimate.",
        crumbs=[("Services", "/#services"), ("Move In / Move Out", "/services/move-in-move-out-cleaning/")],
        service_name="Move In / Move Out Cleaning", service_type="Move-out cleaning", area_served=sussex(),
        form_service="Move In / Move Out",
        h1=("Move In &amp; Move Out Cleaning", "in Maryland &amp; Delaware"),
        script="Let us handle the mess!",
        lead="Moving is stressful enough. We make sure the home you're leaving is ready for inspection and the home you're moving into is fresh, clean and ready for you.",
        cta2="See the checklist",
        body=f'''      <h2>A fresh start, <em>without the scrubbing</em></h2>
      <p>Between packing, paperwork and moving trucks, cleaning is the last thing anyone wants to do. Christina's move-in / move-out cleaning covers the whole home, including the inside of cabinets and drawers that are only reachable once everything is out.</p>
      <h3>For tenants, homeowners, landlords and realtors</h3>
      <p>Whether you want your deposit back, need a rental ready for the next guest or tenant, or want a listing to shine for showings, we'll leave the home spotless.</p>
      <h3>Tips for booking</h3>
      <p>Move-out cleanings work best once the home is empty. Book as early as you can, especially at the end of the month and during the busy summer season on the Delmarva coast.</p>
      <p>Staying put but need a reset? Try a {A("deep-cleaning", "deep cleaning")} instead.</p>''',
        checklist=[
            ("Kitchen", ["Inside cabinets &amp; drawers", "Appliances cleaned inside &amp; out", "Countertops, sink &amp; backsplash", "Floors vacuumed &amp; mopped"]),
            ("Bathrooms", ["Tub, shower &amp; tile scrubbed", "Toilet, sink &amp; vanity", "Mirrors &amp; fixtures shined", "Inside cabinets &amp; drawers"]),
            ("Whole home", ["Baseboards &amp; door frames", "Window sills &amp; tracks", "Closets &amp; shelves", "Light switches &amp; outlets wiped"]),
        ],
        results=["window", "bathtub"], results_title="Ready for <em>the next chapter</em>",
        faq_title="Move-out cleaning <em>questions</em>",
        faq=[
            ("Does the home need to be empty?", "Move-out cleanings work best once furniture and boxes are out, so we can reach inside cabinets, closets and every corner."),
            ("Do you clean inside cabinets and appliances?", "Yes. Inside cabinets and drawers and appliances inside and out are part of our move in / move out cleaning."),
            ("Do you work with landlords and realtors?", "Yes. We help landlords, property managers and realtors get homes ready for new tenants, guests and showings."),
            ("How much does move-out cleaning cost?", f"It depends on the size and condition of the home. Request a free estimate on this page or call {PHONE}."),
        ],
        related_title="More ways we can <em>help</em>",
        related=svc_related("move-in-move-out-cleaning")[:2] + area_related()[:2],
    ),
    dict(
        path="/services/post-construction-cleaning/",
        title="Post-Construction Cleaning Salisbury MD & DE | Christina's",
        desc="Post-construction and renovation cleaning in Salisbury, MD and Sussex County, DE. Fine dust, residue and debris removed so your space is move-in ready.",
        crumbs=[("Services", "/#services"), ("Post-Construction", "/services/post-construction-cleaning/")],
        service_name="Post-Construction Cleaning", service_type="Post-construction cleaning", area_served=sussex(),
        form_service="Post-Construction",
        h1=("Post-Construction Cleaning", "in Maryland &amp; Delaware"),
        script="From dusty to dazzling.",
        lead="Renovation finished? We remove the fine dust, stickers, residue and debris that builders leave behind, so your new kitchen, bathroom or business can finally shine.",
        cta2="What's included",
        body=f'''      <h2>The final step of <em>every project</em></h2>
      <p>Construction dust gets everywhere: on top of cabinets, inside drawers, along window tracks and deep into vents. Christina's post-construction cleaning gets your space from job site to move-in ready.</p>
      <h3>Homes and businesses</h3>
      <p>We clean after kitchen and bathroom remodels, additions, new builds and commercial build-outs in Salisbury, MD and across Sussex County, DE. Homeowners, builders and property managers all count on us for the finishing touch.</p>
      <h3>When to book</h3>
      <p>Schedule your cleaning once the trades have finished their work. That way the dust has settled and we can leave everything spotless in one visit.</p>
      <p>Opening a business in a newly renovated space? Keep it clean with our {A("commercial-cleaning", "commercial cleaning")} plans.</p>''',
        checklist=[
            ("Dust &amp; residue", ["Fine dust removed from every surface", "Cabinets &amp; drawers inside and out", "Stickers, labels &amp; residue removed", "Vents &amp; light fixtures dusted"]),
            ("Finishing touches", ["Windows, sills &amp; tracks", "Fixtures, faucets &amp; hardware shined", "Baseboards &amp; door frames", "Floors vacuumed &amp; mopped"]),
        ],
        results=["baseboard", "window"], results_title="From job site to <em>move-in ready</em>",
        faq_title="Post-construction <em>questions</em>",
        faq=[
            ("When should I schedule post-construction cleaning?", "Once contractors have finished their work, so the dust has settled and everything can be cleaned in one visit."),
            ("Do you clean after home renovations?", "Yes. We clean after kitchen and bathroom remodels, additions and new builds, as well as commercial build-outs."),
            ("Do you work with builders and contractors?", "Yes. Builders, contractors and property managers can use our post-construction cleaning to get projects ready for the owner."),
            ("How much does post-construction cleaning cost?", f"It depends on the size of the space and the amount of dust and residue. Request a free estimate on this page or call {PHONE}."),
        ],
        related_title="More ways we can <em>help</em>",
        related=svc_related("post-construction-cleaning")[:2] + area_related()[:2],
    ),
    # ------------------------------------------------------------------ AREAS
    dict(
        path="/areas/salisbury-md/",
        title="House Cleaning in Salisbury, MD | Christina's Cleaning",
        desc="Trusted house cleaning and commercial cleaning in Salisbury, MD 21801 & 21804. Recurring, deep, move-out and post-construction cleaning. Free estimate.",
        crumbs=[("Areas", "/#areas"), ("Salisbury, MD", "/areas/salisbury-md/")],
        service_name="House Cleaning in Salisbury, MD", service_type="House cleaning", geo="Salisbury, Maryland", geo_region="US-MD",
        area_served=[{"@type": "City", "name": "Salisbury", "postalCode": ["21801", "21804"], "containedInPlace": {"@type": "AdministrativeArea", "name": "Wicomico County, Maryland"}}],
        h1=("House Cleaning", "in Salisbury, MD"),
        script="Clean home, happy life.",
        lead="Maryland-based residential and commercial cleaning for homes and businesses in Salisbury. Busy families, homeowners, landlords and local businesses count on Christina's team for a spotless space.",
        cta2="Our services in Salisbury",
        body=f'''      <h2>Salisbury's <em>hometown</em> cleaning team</h2>
      <p>Christina's Cleaning Services is a Maryland business, and Salisbury is home turf. As the largest city on Maryland's Eastern Shore, Salisbury keeps us busy with family homes, rentals, offices and shops, and we bring the same premium standard to every one of them.</p>
      <p>From weekly upkeep for busy households to move-out cleanings at the end of a lease, our detail-obsessed team leaves your space fresh, clean and ready to enjoy.</p>
      <h3>Cleaning services in Salisbury, MD</h3>
      <p>{A("residential-cleaning", "Recurring house cleaning")}, {A("deep-cleaning", "deep cleaning")}, {A("move-in-move-out-cleaning", "move in / move out cleaning")}, {A("post-construction-cleaning", "post-construction cleaning")} and {A("commercial-cleaning", "commercial cleaning")} for Salisbury offices, shops and businesses.</p>
      <h3>From Maryland to the Delaware beaches</h3>
      <p>Besides Salisbury, we also serve {AR("lewes-de", "Lewes")}, {AR("rehoboth-beach-de", "Rehoboth Beach")}, {AR("millsboro-de", "Millsboro")} and surrounding Sussex County, Delaware.</p>''',
        checklist=[
            ("Popular in Salisbury", ["Recurring house cleaning", "Move in / move out cleaning", "Deep cleaning", "Post-construction cleaning", "Office &amp; retail cleaning"]),
            ("Why Salisbury chooses us", ["Local, Maryland-based business", "Licensed &amp; insured", "Eco-friendly products", "Satisfaction guaranteed"]),
        ],
        results=["toilet", "table"], results_title="Real results for <em>Salisbury homes</em>",
        faq_title="Cleaning in Salisbury: <em>questions</em>",
        faq=[
            ("Do you offer house cleaning in Salisbury, MD?", "Yes. Christina's Cleaning Services is based in Maryland and provides recurring, one-time and deep house cleaning throughout Salisbury, MD 21801 and 21804."),
            ("Do you clean businesses in Salisbury?", "Yes. We offer commercial cleaning for offices, retail stores and other local businesses in Salisbury on daily, weekly or custom schedules."),
            ("Do you do move-out cleaning for rentals in Salisbury?", "Yes. Our move in / move out cleaning helps tenants, landlords and property managers get Salisbury homes and apartments ready for the next move."),
            ("How do I get a quote in Salisbury?", f"Fill out the free estimate form on this page or call {PHONE}. Estimates are fast, easy and no obligation."),
        ],
        related_title="Cleaning services <em>in Salisbury</em>",
        related=svc_related("")[:4],
    ),
    dict(
        path="/areas/lewes-de/",
        title="House Cleaning in Lewes, DE | Christina's Cleaning Services",
        desc="Trusted house cleaning and commercial cleaning in Lewes, DE 19958. Recurring, deep, move-out and post-construction cleaning. Licensed & insured. Free estimate.",
        crumbs=[("Areas", "/#areas"), ("Lewes, DE", "/areas/lewes-de/")],
        service_name="House Cleaning in Lewes, DE", service_type="House cleaning", geo="Lewes, Delaware", geo_region="US-DE",
        area_served=[{"@type": "City", "name": "Lewes", "postalCode": "19958", "containedInPlace": {"@type": "AdministrativeArea", "name": "Sussex County, Delaware"}}],
        h1=("House Cleaning", "in Lewes, DE"),
        script="We clean. You shine.",
        lead="Residential and commercial cleaning for homes and businesses in Lewes, Delaware. From historic homes downtown to newer neighborhoods near the beach, Christina's team leaves every room sparkling.",
        cta2="Our services in Lewes",
        body=f'''      <h2>Your Lewes cleaning team, <em>right around the corner</em></h2>
      <p>Lewes is known as the First Town in the First State, and its homes deserve first-class care. Christina's Cleaning Services helps Lewes families and business owners keep their spaces clean, fresh and ready to enjoy.</p>
      <p>Living close to the beach and Cape Henlopen means sand, salt air and plenty of guests. We keep up with all of it, so your home stays comfortable all year long.</p>
      <h3>Cleaning services in Lewes, DE</h3>
      <p>{A("residential-cleaning", "Weekly and bi-weekly house cleaning")}, {A("deep-cleaning", "deep cleaning")}, {A("move-in-move-out-cleaning", "move in / move out cleaning")}, {A("post-construction-cleaning", "post-construction cleaning")} and {A("commercial-cleaning", "commercial cleaning")} for local offices and shops.</p>
      <h3>Nearby areas</h3>
      <p>We also serve {AR("rehoboth-beach-de", "Rehoboth Beach")}, {AR("millsboro-de", "Millsboro")}, surrounding Sussex County communities and {AR("salisbury-md", "Salisbury, MD")}.</p>''',
        checklist=[
            ("Popular in Lewes", ["Recurring house cleaning", "Deep cleaning", "Move in / move out cleaning", "Post-construction cleaning", "Office &amp; retail cleaning"]),
            ("Why Lewes chooses us", ["Licensed &amp; insured", "Eco-friendly products", "Detail-oriented, reliable team", "Satisfaction guaranteed"]),
        ],
        results=["table", "toilet"], results_title="Real results for <em>Lewes homes</em>",
        faq_title="Cleaning in Lewes: <em>questions</em>",
        faq=[
            ("Do you offer house cleaning in Lewes, DE?", "Yes. Christina's Cleaning Services provides recurring, one-time and deep house cleaning throughout Lewes, DE 19958 and nearby communities."),
            ("Do you clean businesses in Lewes?", "Yes. We offer commercial cleaning for offices, retail stores and other businesses in Lewes on daily, weekly or custom schedules."),
            ("Do you clean beach homes?", "Yes. Whether it's your year-round home or your beach house, we'll keep it clean and ready for you and your guests."),
            ("How do I get a quote in Lewes?", f"Fill out the free estimate form on this page or call {PHONE}. Estimates are fast, easy and no obligation."),
        ],
        related_title="Cleaning services <em>in Lewes</em>",
        related=svc_related("")[:4],
    ),
    dict(
        path="/areas/rehoboth-beach-de/",
        title="House Cleaning in Rehoboth Beach, DE | Christina's Cleaning",
        desc="House cleaning and commercial cleaning in Rehoboth Beach, DE 19971. Beach homes, deep cleans, move-outs and local businesses. Insured team. Free estimate.",
        crumbs=[("Areas", "/#areas"), ("Rehoboth Beach, DE", "/areas/rehoboth-beach-de/")],
        service_name="House Cleaning in Rehoboth Beach, DE", service_type="House cleaning", geo="Rehoboth Beach, Delaware", geo_region="US-DE",
        area_served=[{"@type": "City", "name": "Rehoboth Beach", "postalCode": "19971", "containedInPlace": {"@type": "AdministrativeArea", "name": "Sussex County, Delaware"}}],
        h1=("House Cleaning", "in Rehoboth Beach, DE"),
        script="Beach days, clean nights.",
        lead="Professional house cleaning and commercial cleaning in Rehoboth Beach, Delaware. Spend your time on the boardwalk and the beach, and come home to a spotless space.",
        cta2="Our services in Rehoboth",
        body=f'''      <h2>Rehoboth living, <em>without the sand everywhere</em></h2>
      <p>Beach life is the best life, but it brings sand into every room, salty windows and a steady stream of guests. Christina's Cleaning Services keeps Rehoboth Beach homes fresh, clean and ready to enjoy.</p>
      <p>Whether it's your full-time home or your beach house, we tailor every visit to how you use your space, with extra attention to floors, bathrooms and kitchens during the busy summer season.</p>
      <h3>Cleaning services in Rehoboth Beach, DE</h3>
      <p>{A("residential-cleaning", "Recurring house cleaning")}, {A("deep-cleaning", "deep cleaning")}, {A("move-in-move-out-cleaning", "move in / move out cleaning")}, {A("post-construction-cleaning", "post-construction cleaning")} and {A("commercial-cleaning", "commercial cleaning")} for Rehoboth offices, shops and businesses.</p>
      <h3>Nearby areas</h3>
      <p>We also serve {AR("lewes-de", "Lewes")}, {AR("millsboro-de", "Millsboro")}, surrounding Sussex County communities and {AR("salisbury-md", "Salisbury, MD")}.</p>''',
        checklist=[
            ("Popular in Rehoboth Beach", ["Beach house cleaning", "Recurring house cleaning", "Deep cleaning", "Move in / move out cleaning", "Commercial &amp; retail cleaning"]),
            ("Why Rehoboth chooses us", ["Licensed &amp; insured", "Eco-friendly products", "Flexible scheduling", "Satisfaction guaranteed"]),
        ],
        results=["window", "sink"], results_title="Real results for <em>Rehoboth homes</em>",
        faq_title="Cleaning in Rehoboth Beach: <em>questions</em>",
        faq=[
            ("Do you offer house cleaning in Rehoboth Beach, DE?", "Yes. We provide recurring, one-time and deep house cleaning throughout Rehoboth Beach, DE 19971 and nearby communities."),
            ("Do you clean beach houses?", "Yes. We clean full-time homes and beach houses, and we can keep yours ready before you or your guests arrive."),
            ("Do you clean businesses in Rehoboth Beach?", "Yes. We offer commercial cleaning for offices, retail stores and other local businesses on daily, weekly or custom schedules."),
            ("How do I get a quote in Rehoboth Beach?", f"Fill out the free estimate form on this page or call {PHONE}. Estimates are fast, easy and no obligation."),
        ],
        related_title="Cleaning services <em>in Rehoboth Beach</em>",
        related=svc_related("")[:4],
    ),
    dict(
        path="/areas/millsboro-de/",
        title="House Cleaning in Millsboro, DE | Christina's Cleaning",
        desc="House cleaning and commercial cleaning in Millsboro, DE 19966. Recurring, deep, move-out and post-construction cleaning. Licensed & insured. Free estimate.",
        crumbs=[("Areas", "/#areas"), ("Millsboro, DE", "/areas/millsboro-de/")],
        service_name="House Cleaning in Millsboro, DE", service_type="House cleaning", geo="Millsboro, Delaware", geo_region="US-DE",
        area_served=[{"@type": "City", "name": "Millsboro", "postalCode": "19966", "containedInPlace": {"@type": "AdministrativeArea", "name": "Sussex County, Delaware"}}],
        h1=("House Cleaning", "in Millsboro, DE"),
        script="Clean home, happy life.",
        lead="Trusted residential and commercial cleaning in Millsboro, Delaware. Busy families, new homeowners and local businesses count on Christina's team for a spotless space.",
        cta2="Our services in Millsboro",
        body=f'''      <h2>Millsboro's <em>detail-obsessed</em> cleaning team</h2>
      <p>Millsboro keeps growing, with new neighborhoods, new families and new businesses. Christina's Cleaning Services helps them all enjoy clean, healthy spaces without giving up their weekends.</p>
      <p>From weekly upkeep for busy households to move-in cleanings for brand-new homes, we bring the same premium standard to every job in Millsboro.</p>
      <h3>Cleaning services in Millsboro, DE</h3>
      <p>{A("residential-cleaning", "Recurring house cleaning")}, {A("deep-cleaning", "deep cleaning")}, {A("move-in-move-out-cleaning", "move in / move out cleaning")}, {A("post-construction-cleaning", "post-construction cleaning")} for new builds and {A("commercial-cleaning", "commercial cleaning")} for Millsboro businesses.</p>
      <h3>Nearby areas</h3>
      <p>We also serve {AR("lewes-de", "Lewes")}, {AR("rehoboth-beach-de", "Rehoboth Beach")}, surrounding Sussex County communities and {AR("salisbury-md", "Salisbury, MD")}.</p>''',
        checklist=[
            ("Popular in Millsboro", ["Recurring house cleaning", "Move-in cleaning for new homes", "Post-construction cleaning", "Deep cleaning", "Office &amp; retail cleaning"]),
            ("Why Millsboro chooses us", ["Licensed &amp; insured", "Eco-friendly products", "Detail-oriented, reliable team", "Satisfaction guaranteed"]),
        ],
        results=["bathtub", "lamp"], results_title="Real results for <em>Millsboro homes</em>",
        faq_title="Cleaning in Millsboro: <em>questions</em>",
        faq=[
            ("Do you offer house cleaning in Millsboro, DE?", "Yes. We provide recurring, one-time and deep house cleaning throughout Millsboro, DE 19966 and nearby communities."),
            ("Do you clean new construction homes in Millsboro?", "Yes. Our post-construction and move-in cleaning gets newly built homes spotless and ready to live in."),
            ("Do you clean businesses in Millsboro?", "Yes. We offer commercial cleaning for offices, retail stores and other local businesses on daily, weekly or custom schedules."),
            ("How do I get a quote in Millsboro?", f"Fill out the free estimate form on this page or call {PHONE}. Estimates are fast, easy and no obligation."),
        ],
        related_title="Cleaning services <em>in Millsboro</em>",
        related=svc_related("")[:4],
    ),
]


def not_found():
    return f'''<!doctype html>
<html lang="en-US">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Page not found | Christina's Cleaning Services</title>
  <meta name="robots" content="noindex, follow">
  <meta name="theme-color" content="#2B0A1F">
  <link rel="icon" type="image/png" href="/assets/img/favicon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Manrope:wght@400;500;600;700;800&family=Allura&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body class="is-loading" data-page="404">
<!-- Generated by tools/build_pages.py -->

{SPRITE}
{HEADER.replace('href="#estimate"', 'href="/#estimate"')}
<main id="main">
<section class="hero notfound">
  <canvas class="hero__sparkles" id="sparkles" aria-hidden="true"></canvas>
  <div class="hero__aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="container">
    <p class="hero__script" data-hero>Oops, this spot is a little too clean.</p>
    <h1 class="hero__title"><span class="line"><span data-hero>Page <em class="shimmer">not found</em></span></span></h1>
    <p class="hero__lead" data-hero style="margin-inline:auto">The page you're looking for moved or doesn't exist. Let's get you back to something sparkling.</p>
    <div class="hero__ctas" data-hero style="justify-content:center">
      <a href="/" class="btn btn--gold magnetic"><span>Back to home</span>{icon("i-arrow")}</a>
      <a href="tel:+14432106133" class="btn btn--ghost magnetic">{icon("i-phone")}<span>{PHONE}</span></a>
    </div>
  </div>
</section>
</main>
{FOOTER.replace('href="#estimate"', 'href="/#estimate"')}
<script src="/assets/js/main.js" defer></script>
</body>
</html>
'''


def sitemap():
    urls = [("/", "1.0")] + [(p["path"], "0.8" if p["path"].startswith("/services") else "0.7") for p in PAGES]
    rows = "\n".join(
        f"  <url>\n    <loc>{SITE}{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <priority>{pr}</priority>\n  </url>"
        for u, pr in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n'


def main():
    for p in PAGES:
        out = ROOT / p["path"].strip("/") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(p), encoding="utf-8")
        print("wrote", out.relative_to(ROOT))
    (ROOT / "404.html").write_text(not_found(), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    print("wrote 404.html, sitemap.xml")


if __name__ == "__main__":
    main()
