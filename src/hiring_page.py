"""Student Hiring page (MSc / PhD research assistant positions with McGill University).

HIRING_ENDPOINT is the Google Apps Script web-app URL (ends in /exec) that saves
applications to Google Drive and the response spreadsheet. While it is empty the
form is shown but submissions are switched off with an "opening shortly" note.
The script itself is in src/hiring/apps-script.gs.
"""
import html
E = html.escape

HIRING_ENDPOINT = "https://script.google.com/macros/s/AKfycbwciD19uBS2pJPk2f79ebxQiVkr0lR8eSnF7ELGdNC8KIQT_3PU5T77aSvOteYF9QZf6A/exec"

PROJECTS = [
    {
        "id": "p1",
        "num": "01",
        "short": "Autonomous critical-mineral recovery",
        "title": "Development of an autonomous experiment for critical mineral recovery from spent lithium batteries",
        "img": "lab-digital-shaker.jpg",
        "img2": "aiche26-nyuon-jongkuch.jpg",
        "lede": "Spent lithium-ion batteries are a growing source of lithium, nickel, cobalt and manganese. Finding the leaching and separation conditions that recover these metals cleanly takes hundreds of experiments. This project will build a self-driving laboratory that runs, measures and plans those experiments on its own.",
        "do": [
            "Design and assemble an automated leaching and separation platform that combines liquid handling, temperature-controlled mixing and in-line measurements.",
            "Use machine learning and Bayesian optimization so the platform chooses its next experiment from the results it has already measured.",
            "Screen greener lixiviants, including deep eutectic solvents, for selective recovery of Li, Ni, Co and Mn from battery black mass.",
            "Link the best conditions to process models, techno-economic analysis and life-cycle assessment.",
        ],
        "skills": ["Hydrometallurgy", "Lab automation", "Python &amp; ML", "Bayesian optimization", "Analytical chemistry", "TEA / LCA"],
        "works": [
            ("Cathode delamination influences the CO₂ capture performance of Li₄SiO₄ adsorbents derived from spent lithium-ion batteries", "Chemical Engineering Journal, 2026", "https://doi.org/10.1016/j.cej.2026.182552"),
            ("Geo-spatial, techno-economic and life-cycle assessment of spent lithium-ion battery upcycling to CO₂ capture adsorbent", "Process Safety and Environmental Protection, 2026", "https://doi.org/10.1016/j.psep.2025.108380"),
            ("AI-guided design of novel deep eutectic solvents for critical metal recovery from spent lithium-ion batteries", "Bucknell IDEA Grant, 2026", None),
            ("Pathways for the recovery of lithium, nickel and cobalt from spent lithium batteries", "Bucknell College of Engineering grant, 2025", None),
        ],
    },
    {
        "id": "p2",
        "num": "02",
        "short": "Continuous rare-earth recovery",
        "title": "A continuous system using functionalized porous materials for rare earth metal recovery from heterogeneous streams",
        "img": "lab-ozone.jpg",
        "img2": "lab-bet.jpg",
        "lede": "Rare earth elements are present at low concentrations in complex streams such as industrial and mining wastewaters and electronic-waste leachates, alongside many competing ions and solids. This project will develop functionalized porous adsorbents and a continuous-flow system that captures rare earths selectively and can be regenerated and reused.",
        "do": [
            "Synthesize and functionalize porous materials (e.g., biomass-derived carbons, biochar and metal–organic frameworks) with groups that bind rare earth ions selectively.",
            "Characterize the materials by surface area and porosity analysis, spectroscopy and microscopy.",
            "Run batch and continuous fixed-bed tests on realistic multi-component streams, measuring breakthrough, selectivity, elution and regeneration.",
            "Build transport and process models to scale up the column design and assess cost and environmental impact.",
        ],
        "skills": ["Materials synthesis", "Adsorption", "Flow systems", "Characterization", "Process modelling", "TEA / LCA"],
        "works": [
            ("Activated Carbon: Synthesis, Analysis, and Industrial Applications", "Book, Elsevier", "https://doi.org/10.1016/C2022-0-02853-1"),
            ("Advances in the applications of nanomaterials for wastewater treatment", "Environments, 2022", "https://doi.org/10.3390/environments9110141"),
            ("Current trends in the synthesis, characterization and application of metal organic frameworks", "Reaction Chemistry &amp; Engineering, 2023", "https://doi.org/10.1039/d2re00365a"),
            ("Machine learning to study the removal of pharmaceuticals from wastewater using biochar or activated carbon", "Total Environment Research Themes, 2022", "https://doi.org/10.1016/j.totert.2022.100001"),
        ],
    },
]

STYLE = """
<style>
.hire-hero{position:relative;background:var(--navy);color:#fff;overflow:hidden}
.hire-hero .wrap{display:grid;grid-template-columns:1.15fr .85fr;gap:48px;align-items:center;padding-top:72px;padding-bottom:72px}
.hire-hero h1{color:#fff;font-size:clamp(36px,5vw,60px);margin:10px 0 18px}
.hire-hero p{color:#DCE4EC;font-size:18px;max-width:60ch}
.hire-hero .tag{color:var(--orange)}
.hire-badges{display:flex;flex-wrap:wrap;gap:10px;margin:22px 0 28px}
.hire-badges span{border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:8px 14px;font-size:14px;font-weight:700}
.hire-badges span b{color:var(--orange)}
.hire-collage{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.hire-collage img{width:100%;height:100%;object-fit:cover;border-radius:12px;aspect-ratio:1}
.hire-collage img:first-child{grid-column:span 2;aspect-ratio:16/9}
.hire-glance{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px}
.hire-glance div{border-top:3px solid var(--orange);padding-top:14px}
.hire-glance b{display:block;color:var(--navy);font-size:18px;margin-bottom:4px}
.hire-glance p{margin:0;color:var(--muted);font-size:15px}
.proj{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:48px;align-items:start;padding:48px 0;border-top:1px solid var(--line)}
.proj:nth-of-type(even) .proj-media{order:2}
.proj-media{position:sticky;top:96px;display:grid;gap:12px}
.proj-media img{width:100%;border-radius:14px;object-fit:cover;aspect-ratio:4/3}
.proj-media img+img{aspect-ratio:16/9}
.proj-num{font-size:64px;font-weight:800;line-height:1;color:var(--orange);opacity:.9}
.proj h3{font-size:clamp(24px,2.6vw,32px);margin:8px 0 14px}
.proj .lede{font-size:17px;color:var(--ink)}
.proj h4{margin:24px 0 8px;color:var(--navy);font-size:15px;text-transform:uppercase;letter-spacing:.06em}
.proj ul.do{padding-left:20px;margin:0;color:var(--muted)}
.proj ul.do li{margin-bottom:8px}
.works{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.works li{background:var(--tint);border-radius:8px;padding:12px 14px;font-size:14.5px}
.works li b{display:block;color:var(--navy);font-weight:600}
.works li span{color:var(--muted)}
.works a{color:var(--orange-ink);font-weight:700;text-decoration:none;white-space:nowrap}
.hire-form{background:#fff;border:1px solid var(--line);border-radius:16px;padding:36px;box-shadow:0 14px 34px rgba(15,43,70,.08)}
.hire-form fieldset{border:0;padding:0;margin:0 0 28px}
.hire-form legend{font-weight:800;color:var(--navy);font-size:19px;margin-bottom:14px;padding:0}
.hire-form legend small{display:block;font-weight:500;color:var(--muted);font-size:14px;margin-top:2px}
.f-row{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.f{display:flex;flex-direction:column;gap:6px;margin-bottom:14px}
.f label,.f .lbl{font-weight:700;color:var(--navy);font-size:15px}
.f label small,.f .lbl small{font-weight:500;color:var(--muted)}
.f input[type=text],.f input[type=email],.f textarea{font:inherit;padding:12px 14px;border:1.5px solid var(--line);border-radius:8px;background:#fff;color:var(--ink)}
.f input:focus,.f textarea:focus{outline:none;border-color:var(--orange)}
.f textarea{min-height:120px;resize:vertical}
.opts{display:flex;flex-wrap:wrap;gap:10px}
.opt{display:flex;gap:10px;align-items:flex-start;border:1.5px solid var(--line);border-radius:10px;padding:12px 14px;cursor:pointer;font-size:15px;flex:1 1 220px}
.opt:has(input:checked){border-color:var(--orange);background:#FFF6EE}
.opt input{margin-top:4px;accent-color:var(--orange)}
.drop{border:2px dashed var(--line);border-radius:12px;padding:18px;display:grid;gap:6px;transition:border-color .2s,background .2s}
.drop.ok{border-color:#2E8B57;background:#F1FAF4}
.drop.bad{border-color:#C0392B;background:#FDF2F1}
.drop b{color:var(--navy)}
.drop .hint{font-size:14px;color:var(--muted)}
.drop .st{font-size:14px;font-weight:700}
.drop input{font:inherit;font-size:14px}
.ai-box{background:var(--navy);color:#DCE4EC;border-radius:12px;padding:22px 24px;margin-bottom:16px}
.ai-box b{color:#fff}
.ai-box .tag{color:var(--orange)}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.f-msg{margin-top:16px;padding:14px 16px;border-radius:8px;font-weight:600;display:none}
.f-msg.show{display:block}
.f-msg.ok{background:#F1FAF4;color:#1E6B40}
.f-msg.err{background:#FDF2F1;color:#9B2C20}
.f-msg.info{background:var(--tint);color:var(--navy)}
.hire-form button[disabled]{opacity:.55;cursor:not-allowed}
.hire-form .btn{cursor:pointer;font:inherit;font-weight:700}
@media (max-width:860px){.hire-hero .wrap,.proj,.f-row{grid-template-columns:1fr}.hire-glance{grid-template-columns:1fr 1fr}.proj-media{position:static}.proj:nth-of-type(even) .proj-media{order:0}.hire-form{padding:22px}}
</style>
"""

SCRIPT = r"""
<script>
(function(){
  var ENDPOINT = "__ENDPOINT__";
  var MAX = 5*1024*1024;
  var form = document.getElementById('hire-form');
  var msg = document.getElementById('f-msg');
  var btn = document.getElementById('f-submit');
  function show(kind, text, quiet){ msg.className = 'f-msg show ' + kind; msg.textContent = text; if (!quiet) msg.scrollIntoView({behavior:'smooth', block:'nearest'}); }
  if (!ENDPOINT){ btn.disabled = true; show('info', 'Online applications open shortly. Please check back soon.', true); }

  form.querySelectorAll('.drop input[type=file]').forEach(function(inp){
    inp.addEventListener('change', function(){
      var box = inp.closest('.drop'), st = box.querySelector('.st'), f = inp.files[0];
      box.classList.remove('ok','bad'); st.textContent = '';
      if (!f) return;
      if (!/\.pdf$/i.test(f.name)) { box.classList.add('bad'); st.textContent = 'Please choose a PDF file.'; return; }
      if (f.size > MAX) { box.classList.add('bad'); st.textContent = 'This file is larger than 5 MB.'; return; }
      box.classList.add('ok'); st.textContent = '✓ ' + f.name + ' (' + (f.size/1024/1024).toFixed(2) + ' MB)';
    });
  });

  function readB64(file){
    return new Promise(function(res, rej){
      var r = new FileReader();
      r.onload = function(){ res(String(r.result).split(',')[1]); };
      r.onerror = function(){ rej(new Error('Could not read ' + file.name)); };
      r.readAsDataURL(file);
    });
  }

  form.addEventListener('submit', async function(ev){
    ev.preventDefault();
    if (!ENDPOINT) return;
    var fd = new FormData(form);
    var projects = fd.getAll('projects');
    if (!projects.length){ show('err', 'Please choose at least one project.'); return; }
    var files = {coverLetter: form.coverLetter.files[0], cv: form.cv.files[0], proposal: form.proposal.files[0]};
    for (var k in files){
      var f = files[k];
      if (!f || !/\.pdf$/i.test(f.name) || f.size > MAX){ show('err', 'Please attach all three documents as PDF files of 5 MB or less.'); return; }
    }
    btn.disabled = true; btn.textContent = 'Submitting…';
    show('info', 'Uploading your documents. This can take up to a minute; please keep this page open.');
    try {
      var payload = {
        name: fd.get('name'), email: fd.get('email'), degree: fd.get('degree'),
        institution: fd.get('institution'), projects: projects.join('; '),
        aiUsed: fd.get('aiUsed'), aiStatement: fd.get('aiStatement'),
        aiConfirm: !!fd.get('aiConfirm'), website: fd.get('website')
      };
      for (var key in files){ payload[key] = {name: files[key].name, data: await readB64(files[key])}; }
      var r = await fetch(ENDPOINT, {method:'POST', headers:{'Content-Type':'text/plain;charset=utf-8'}, body: JSON.stringify(payload)});
      var out = await r.json();
      if (!out.ok) throw new Error(out.error || 'Submission failed.');
      form.reset(); form.querySelectorAll('.drop').forEach(function(d){ d.classList.remove('ok','bad'); d.querySelector('.st').textContent=''; });
      show('ok', 'Thank you! Your application has been received. We will contact shortlisted candidates by email.');
      btn.textContent = 'Submitted';
    } catch(err){
      show('err', 'Sorry, something went wrong: ' + err.message + ' Please try again, or email your documents to __EMAIL__.');
      btn.disabled = false; btn.textContent = 'Submit application';
    }
  });
})();
</script>
"""


def _project(p):
    works = "".join(
        f'<li><b>{t}</b><span>{m}</span>{f" · <a href=\"{u}\" target=\"_blank\" rel=\"noopener\">Read →</a>" if u else ""}</li>'
        for t, m, u in p["works"])
    return f"""<article class="proj" id="{p['id']}">
<div class="proj-media"><img src="img/{p['img']}" alt=""><img src="img/{p['img2']}" alt=""></div>
<div><span class="proj-num">{p['num']}</span><span class="tag" style="display:block;margin-top:10px">Project {int(p['num'])} · MSc or PhD</span>
<h3>{p['title']}</h3><p class="lede">{p['lede']}</p>
<h4>What you will do</h4><ul class="do">{''.join(f'<li>{x}</li>' for x in p['do'])}</ul>
<h4>Skills you will build</h4><div class="chips">{''.join(f'<span class="chip">{s}</span>' for s in p['skills'])}</div>
<h4>Builds on our work</h4><ul class="works">{works}</ul>
<p style="margin-top:22px"><a class="btn pri" href="#apply">Apply for this project</a></p></div>
</article>"""


def _drop(name, title, hint):
    return f"""<div class="drop f"><label for="{name}"><b>{title}</b></label><span class="hint">{hint}</span>
<input type="file" id="{name}" name="{name}" accept="application/pdf,.pdf" required><span class="st" aria-live="polite"></span></div>"""


def hiring_body(email):
    projects = "".join(_project(p) for p in PROJECTS)
    opts = "".join(f'<label class="opt"><input type="checkbox" name="projects" value="Project {int(p["num"])}: {E(p["short"])}"><span><b>Project {int(p["num"])}</b><br>{p["short"]}</span></label>' for p in PROJECTS)
    body = STYLE + f"""
<div class="hire-hero"><div class="wrap">
<div><span class="tag">Now hiring · Research assistants</span>
<h1>Recover the metals the energy transition runs on</h1>
<p>The SETD Research Group, in collaboration with McGill University, is recruiting graduate research assistants for two projects on recovering critical and rare earth metals from waste.</p>
<div class="hire-badges"><span><b>2</b> positions</span><span>MSc or PhD</span><span>Fully funded</span><span>McGill University</span></div>
<div class="btns"><a class="btn pri" href="#apply">Apply now</a><a class="btn" href="#projects">See the projects</a></div></div>
<div class="hire-collage"><img src="img/aiche26-group.jpg" alt="SETD students at the AIChE Annual Meeting"><img src="img/lab-uv-vis.jpg" alt="UV-Vis spectrophotometer in the SETD lab"><img src="img/aiche26-reed-muir.jpg" alt="SETD student presenting battery-recycling research"></div>
</div></div>

<section><div class="wrap">
<div class="hire-glance">
<div><b>Two projects</b><p>Autonomous critical-mineral recovery from spent lithium batteries, and continuous rare earth recovery with functionalized porous materials.</p></div>
<div><b>MSc or PhD</b><p>Both degree levels are open. Students enroll at McGill University.</p></div>
<div><b>Fully funded</b><p>Positions include a stipend and tuition.</p></div>
<div><b>Joint supervision</b><p>Work with the SETD group (Dr. Jude A. Okolie, Bucknell University) in collaboration with McGill University.</p></div>
</div></div></section>

<section id="projects" style="padding-top:0"><div class="wrap">
<span class="tag">The projects</span><h2>Two ways to make critical materials circular</h2>
<p class="muted" style="max-width:70ch">Both projects combine experiments with data science and process modelling, and both build directly on the group's work on spent-battery upcycling, adsorbent materials and AI-guided design.</p>
{projects}
</div></section>

<section style="background:var(--tint)"><div class="wrap cols">
<div><span class="tag">Who should apply</span><h2>What we look for</h2><ul class="list">
<li>A degree in chemical, materials, environmental or mechanical engineering, chemistry or a related field.</li>
<li>Curiosity, passion and discipline: interest matters more than prior experience in every technique listed.</li>
<li>For Project 1, an interest in automation, coding or machine learning; for Project 2, an interest in materials synthesis and separations.</li>
<li>Clear scientific writing and a willingness to share work at conferences and in journals.</li></ul></div>
<div><span class="tag">How to apply</span><h2>Three documents, one form</h2><div class="steps" style="grid-template-columns:1fr;gap:14px">
<div class="step"><span>Document 1</span><b>Cover letter · 1 page</b><p>Your motivation for applying, your preferred project(s) and your future plans.</p></div>
<div class="step"><span>Document 2</span><b>CV · up to 2 pages</b><p>Education, research experience, skills, and any publications or presentations.</p></div>
<div class="step"><span>Document 3</span><b>Research proposal · up to 3 pages</b><p>Your own approach to one of the two projects: the problem, your objectives, methods and expected outcomes.</p></div>
</div></div></div></section>

<section id="apply"><div class="wrap" style="max-width:880px">
<span class="tag">Application form</span><h2>Apply for a research assistant position</h2>
<p class="muted">All fields are required. Upload each document as a PDF of 5 MB or less. You do not need a Google account.</p>
<form id="hire-form" class="hire-form">
<fieldset><legend>About you</legend>
<div class="f-row"><div class="f"><label for="name">Full name</label><input type="text" id="name" name="name" autocomplete="name" required maxlength="120"></div>
<div class="f"><label for="email">Email address</label><input type="email" id="email" name="email" autocomplete="email" required maxlength="200"></div></div>
<div class="f"><label for="institution">Current institution and program <small>(e.g., B.Eng. Chemical Engineering, University of …)</small></label><input type="text" id="institution" name="institution" required maxlength="200"></div>
<div class="f"><span class="lbl">Degree you are applying for</span><div class="opts">
<label class="opt"><input type="radio" name="degree" value="MSc" required><span><b>MSc</b><br>Research master's at McGill</span></label>
<label class="opt"><input type="radio" name="degree" value="PhD"><span><b>PhD</b><br>Doctoral program at McGill</span></label></div></div>
<div class="f"><span class="lbl">Preferred project(s) <small>(choose one or both)</small></span><div class="opts">{opts}</div></div>
<div class="hp" aria-hidden="true"><label for="website">Website</label><input type="text" id="website" name="website" tabindex="-1" autocomplete="off"></div>
</fieldset>
<fieldset><legend>Your documents<small>PDF only, 5 MB maximum each</small></legend>
{_drop("coverLetter","Cover letter (1 page)","Motivation for applying, preferred project(s) and future plans.")}
{_drop("cv","Curriculum vitae (max. 2 pages)","Education, research experience, skills, publications.")}
{_drop("proposal","Research proposal (max. 3 pages)","Problem, objectives, methods and expected outcomes for your chosen project.")}
</fieldset>
<fieldset><legend>Use of AI tools</legend>
<div class="ai-box"><span class="tag">AI disclosure · required</span><p style="margin:8px 0 0"><b>Every applicant must clearly state whether and how AI tools</b> (for example ChatGPT, Claude, Gemini, Copilot or Grammarly) <b>were used to prepare the cover letter, CV or research proposal</b>, such as for brainstorming, drafting, editing, translation or literature search. This statement is reviewed together with your documents.</p></div>
<div class="f"><span class="lbl">Did you use any AI tools to prepare your documents?</span><div class="opts">
<label class="opt"><input type="radio" name="aiUsed" value="Yes" required><span><b>Yes</b></span></label>
<label class="opt"><input type="radio" name="aiUsed" value="No"><span><b>No</b></span></label></div></div>
<div class="f"><label for="aiStatement">AI usage statement <small>— which tools, for which document(s), and for what. If none, write “No AI tools were used.”</small></label><textarea id="aiStatement" name="aiStatement" required maxlength="3000"></textarea></div>
<label class="opt" style="flex:none"><input type="checkbox" name="aiConfirm" value="yes" required><span>I confirm that this AI usage statement is complete and accurate.</span></label>
</fieldset>
<button type="submit" id="f-submit" class="btn pri">Submit application</button>
<div id="f-msg" class="f-msg" role="status" aria-live="polite"></div>
</form>
<p class="muted" style="font-size:14px;margin-top:18px">Your documents are stored privately in the SETD group's Google Drive and used only to assess your application. Questions? Email <a href="mailto:{email}?subject=Graduate%20research%20assistant%20positions">{email}</a>.</p>
</div></section>
"""
    js = SCRIPT.replace("__ENDPOINT__", HIRING_ENDPOINT).replace("__EMAIL__", email)
    return body + js
