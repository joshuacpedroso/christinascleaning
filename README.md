# Christina's Cleaning Services

Website for Christina's Cleaning Services, residential & commercial cleaning in Sussex County, DE
(Lewes, Rehoboth Beach, Millsboro) and Salisbury, MD.

Static site (HTML + CSS + vanilla JS, no build step). Open `index.html` or deploy the folder
to any static host (Vercel, Netlify, GitHub Pages, Hostinger, etc).

## Structure

- `index.html` - home page (hero with estimate form, before/after sliders, services, about, areas, FAQ)
- `services/*/index.html`, `areas/*/index.html`, `404.html`, `sitemap.xml` - **generated** by
  `python3 tools/build_pages.py` (see below)
- `assets/css/style.css` - styles
- `assets/js/main.js` - loader, sparkles, before/after sliders, animations, form submit
- `assets/img/` - logo, photos and `results/` before/after pairs

## Estimate form

The form posts to [FormSubmit](https://formsubmit.co) and delivers to
`christinascleaningservices4@gmail.com`. **The first submission sends an activation email to that
inbox - click "Activate" once** and every request after that arrives normally.
To change the destination, edit `data-endpoint` on `#quote-form` in `index.html`.

## Adding a before/after

Export both photos with the same size to `assets/img/results/` and copy one of the
`<figure class="ba">` blocks in `index.html`.

## SEO pages

Service and city pages are generated from the data in `tools/build_pages.py`. The icon sprite,
header, estimate form, final CTA and footer are copied from `index.html` (between the
`<!-- @name:start -->` / `<!-- @name:end -->` markers), so after changing any of those in
`index.html`, or any page text in the script, run:

```
python3 tools/build_pages.py
```

Other SEO files: `robots.txt`, `sitemap.xml`, `site.webmanifest`, `llms.txt`, `.htaccess`
(HTTPS + non-www redirects, caching, 404 page on Apache hosting) and `vercel.json`
(keeps the `*.vercel.app` preview out of Google).

## After going live

1. Google Search Console: add `christinascleaningservices.com` and submit `/sitemap.xml`.
2. Google Business Profile: create/verify it as a service-area business (Salisbury MD, Lewes,
   Rehoboth Beach, Millsboro) with the same name, phone and website as the site.
