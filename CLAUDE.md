# SETD Research Group website (okolielab)

Static website for Dr. Jude A. Okolie's Sustainable Energy Transition & Decarbonization (SETD) research group, Bucknell University.
Live at https://okolielab.netlify.app. Netlify publishes the `setd-website/` folder automatically on every push to `main` (see `netlify.toml`).

## How the site is built
- Never hand-edit the HTML in `setd-website/`. Edit the sources, then run `python3 src/build.py` from the repo root, which regenerates every page.
- `src/build.py` holds most content as Python data: research clusters, projects, team roles (`CURRENT_TEAM`, `NEW_STUDENTS`, `BIO_UPDATES`, the `MOVED` set), facilities (`FAC`), books (`BOOKS`), and news (`NEWS`, newest first; each item is `(images, date label, title, body, link-or-None)`).
- `src/content/publications.txt` lists publications. `## Theme N:` lines start a theme; each other line is one citation, newest first within a theme, ending with its DOI URL (`https://doi.org/...`) when there is one. The build turns that URL into a "Link →".
- `src/content/*.md` hold longer verbatim text (bios, teaching, DEI, awards, courses).
- Styling: `setd-website/style.css`. Images: `setd-website/img/`.
- After building, check that every page loads with no broken images before pushing.

## Content rules
- Only add facts that come from Dr. Okolie or a verifiable source (Crossref, ORCID 0000-0001-7506-551X, publisher pages, Bucknell news). Never invent dates, venues, awards or DOIs.
- Publications must list Dr. Okolie as an author (ORCID 0000-0001-7506-551X or name match plus Bucknell/Oklahoma/Saskatchewan affiliation). Other people named Jude Okolie are not him.
- Do not show publication counts, phone numbers or personal email addresses.
- Crossref lookups that are blocked from the shell can be done through the browser at `https://api.crossref.org/works?rows=3&select=DOI,title,author,container-title,issued&query.bibliographic=...`.
