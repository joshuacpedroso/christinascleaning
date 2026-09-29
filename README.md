# Christina's Cleaning Services

Website for Christina's Cleaning Services, residential & commercial cleaning in Sussex County, DE
(Lewes, Rehoboth Beach, Millsboro).

Static site (HTML + CSS + vanilla JS, no build step). Open `index.html` or deploy the folder
to any static host (Vercel, Netlify, GitHub Pages, Hostinger, etc).

## Structure

- `index.html` - single page (hero with estimate form, before/after sliders, services, about, areas, FAQ)
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
