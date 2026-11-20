"""Builds the SETD website (static HTML) into /home/claude/site_c from the content below."""
import html, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT/"setd-website"
CONTENT = ROOT/"src"/"content"
E = html.escape

EMAIL = "jude.okolie@bucknell.edu"
LINKS = [("Google Scholar","https://scholar.google.com/citations?user=G-_iMkoAAAAJ&hl=en&oi=ao"),("ORCID","https://orcid.org/0000-0001-7506-551X"),("LinkedIn","https://www.linkedin.com/in/judeaokolie/"),("ResearchGate","https://www.researchgate.net/profile/Jude-Okolie")]
NAV = [("index.html","Home"),("research.html","Research"),("people.html","People"),("facilities.html","Facilities"),("publications.html","Publications"),("teaching.html","Teaching"),("outreach.html","Outreach"),("news.html","News"),("about.html","About"),("contact.html","Contact")]

def ext(t,u,cls=""):
    c=f' class="{cls}"' if cls else ""
    return f'<a href="{E(u)}" target="_blank" rel="noopener"{c}>{t}</a>'

def page(fname, title, desc, body):
    nav = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h==fname else ""}>{n}</a>' for h,n in NAV)
    foot_pages = "".join(f'<a href="{h}">{n}</a>' for h,n in NAV)
    foot_links = "".join(ext(t,u) for t,u in LINKS)
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header"><div class="wrap">
<a class="logo" href="index.html">SETD Research Group<small>Bucknell University · Chemical Engineering</small></a>
<nav class="nav" aria-label="Main">{nav}</nav>
</div></header>
<main>
{body}
</main>
<footer class="site-footer"><div class="wrap">
<div><b>Sustainable Energy Transition &amp; Decarbonization (SETD) Research Group</b>Dr. Jude A. Okolie<br>Department of Chemical Engineering, Bucknell University<br>One Dent Drive, Lewisburg, PA 17837<br><a href="mailto:{EMAIL}">{EMAIL}</a></div>
<div><b>Pages</b>{foot_pages}</div>
<div><b>Profiles</b>{foot_links}</div>
</div></footer>
</body>
</html>
"""
    (OUT/fname).write_text(doc, encoding="utf-8")

def hero(tag, h1, p):
    return f'<div class="page-hero"><div class="wrap"><span class="tag">{tag}</span><h1>{h1}</h1><p>{p}</p></div></div>'

# ---------------- DATA ----------------
INTRO = ("The present society faces the challenges of increasing energy demand, climate change and environmental pollution. "
         "It is imperative to develop innovative processes that can transform waste materials into valuable resources for energy and environmental applications. "
         "Biofuels, biomaterials and green chemicals are envisioned to play a significant role in the global energy transition.")
INTRO2 = "Our research combines experimental analysis with process design and simulation, control and optimization, energy system modelling and life cycle assessment to address several environmental and energy challenges."
QUESTIONS = ["How can waste materials be effectively managed while providing adequate energy to meet the demands of the rising world population?",
             "How do you optimize the cost and efficiency of processes that can transform waste materials into energy and value-added products?",
             "How do you develop new materials to promote sustainable fuel, food security and human health?"]
AREAS = ["Thermochemical conversion of biomass to biofuels","Repurposing electronic waste for environmental applications","Critical metals recovery","Biobased materials for environmental remediation","Process modelling of carbon capture systems","Modelling of hydrogen production systems","Modelling of underground hydrogen storage"]
CLUSTERS = [
 ("Waste to Fuels &amp; Chemicals","lab-htl-reactor-2.jpg","Thermochemical conversion of biomass and waste into biofuels, hydrogen and green chemicals.",
  ["Thermochemical conversion of biomass to biofuels","Integrated chemical looping gasification (with Prof. Fatih Gulec, University of Nottingham)","Design of a mobile pyrolysis unit","Conversion of glycerol to value-added chemicals"]),
 ("Circular Materials &amp; Critical Metals","aiche26-reed-muir.jpg","Repurposing electronic waste and biomass into materials that capture carbon and clean water.",
  ["Repurposing electronic waste and spent batteries for environmental applications","Critical metals recovery","Biochar, hydrochar and biobased materials for environmental remediation","Catalysts for hydrogenolysis of lignin-based compounds (with Prof. Kausn Gunasooriya)"]),
 ("Hydrogen &amp; Carbon Systems","lab-clc-reactor.jpg","Process and system models for the infrastructure of a low-carbon energy economy.",
  ["Process modelling of carbon capture systems","Modelling and process optimization of hydrogen production systems","Underground hydrogen storage (with Dr. Emmanuel Epelle, UWS)","Ni–Co–Fe catalysts for dry methane reforming (ACS-PRF funded)"]),
]
COMPLETED = ["Hydrothermal gasification of waste materials for hydrogen production.","Anaerobic digestion of food waste to biogas.","Modelling and optimization of integrated biomass valorization processes.","Process optimization and preliminary techno-economic analysis of glycerol to propylene glycol.","Biopesticide production from food waste (collaboration with Prof. Burcu Gunes, DCU).","Activated carbon functionalization for carbon capture.","Production of activated carbon for energy storage applications.","Catalyst development for the conversion of glycerol to propylene glycol (collaboration with Prof. Patrick Okoye).","Development of a mobile game app for teaching introductory process engineering."]
CURRENT = ["Metal–support interactions and coke deposition mechanisms in Ni–Co–Fe catalysts for dry methane reforming (ACS Petroleum Research Fund, Jan 2027 – Dec 2028).","Development of an integrated chemical looping gasification system (collaboration with Prof. Fatih Gulec, University of Nottingham).","Conversion of glycerol to value-added chemicals.","Underground hydrogen storage (collaboration with Dr. Emmanuel Epelle, UWS).","Design of a mobile pyrolysis unit.","Modelling and process optimization of hydrogen production systems.","Catalyst development for catalytic hydrogenolysis of lignin-based compounds to sustainable chemicals (collaboration with Prof. Kausn Gunasooriya).","Technology evaluation of waste biomass gasification to sustainable aviation fuel (industry grant, The Catalyst Group Resources)."]
PATENT = "Adekunle A.A., Peter P. Ikubanni, Emmanuel, A., Olayinka O.A., Olarenwaju, O., <mark>Okolie, J.A.</mark>, David A., Jamie K. Odusote. Locally designed and fabricated mini ablative pyrolyzer for dual energy products."
METHODS = ["Experiments","Catalyst development","Process design &amp; simulation","Control &amp; optimization","Energy system modelling","Techno-economic analysis","Life cycle assessment","Machine learning &amp; AI"]

def parse_people(fn):
    txt=(CONTENT/fn).read_text()
    out=[]
    for m in re.finditer(r"^\d+\.\s+(.+?)\s+(?:\[photo\]\s+)?—\s+(.+?)(?=\n\n\d+\.|\n\n\(|\Z)", txt, re.S|re.M):
        out.append((m.group(1).strip(), m.group(2).strip()))
    return out

CURRENT_TEAM = [  # slug, short role
 ("frank-onwudinjo","M.S. student, Chemical Engineering"),("ahsan-khan","Graduate student, Chemical Engineering"),("omuhle-ndhlovu","Undergraduate, Chemical Engineering &amp; Engineering Management"),
 ("priyanka-poplai","Undergraduate, Biochemistry"),("makenzie-krance","Undergraduate, Chemical Engineering"),("reed-muir","Junior, Chemical Engineering"),("noah-thorpe","Senior, Chemical Engineering"),
 ("alnur-gazizuly","Undergraduate, Computer Engineering"),("diego-nunez-castaneda","Undergraduate, Chemical Engineering"),("abasi-ofon-tom","Ph.D. student, University of Oklahoma"),
 ("kaustubh-pandit","Undergraduate, Mechanical Engineering"),("oluwadamilola-oyinloye","Ph.D. candidate, Nile University of Nigeria (co-supervised)"),("hauwau-kaoje","Ph.D. candidate, Nile University of Nigeria (co-supervised)")]
NEW_STUDENTS = [
 ("maura-michalczyk","Maura Michalczyk","Junior, Chemical Engineering",
  "Maura Michalczyk is a junior chemical engineering student at Bucknell University. Her research in the SETD group focuses on food waste valorization to biofuels, most recently the impact of biochar impregnated with battery leachate on methane yield from anaerobic digestion. Maura is from Scranton, Pennsylvania, and is also a student athlete at Bucknell."),
 ("jongkuch-nyuon","Jongkuch Nhial Nyuon","Undergraduate, Chemical Engineering, class of 2027",
  "Jongkuch Nhial Nyuon is a chemical engineering student at Bucknell University, class of 2027. He is studying the impact of impurity carry-over during the upcycling of spent lithium-ion batteries into lithium orthosilicate (Li4SiO4) for CO2 capture. He presented his poster, Influence of Manganese and Aluminum Impurities on Battery-Derived Li4SiO4 for CO2 Capture, at the 2026 AIChE Annual Meeting in Minneapolis."),
 ("aiden-beck","Aiden Beck","Undergraduate, Electrical &amp; Computer Engineering, class of 2029",
  "Aiden Beck is an electrical and computer engineering student at Bucknell University, class of 2029. He studies activated carbon for supercapacitors, combining artificial intelligence with experiments. He presented his poster, Coffee Grounds as Potential Supercapacitor Electrode Material, at the 2026 AIChE Annual Meeting in Minneapolis."),
]
BIO_UPDATES = {
 "makenzie-krance":"Makenzie Krance is a senior chemical engineering student at Bucknell University. In the SETD group, she worked on developing a biochar-based adsorbent for removing pharmaceuticals from wastewater. She loves math and science and participated in many science competitions throughout middle and high school.",
 "oluwadamilola-oyinloye":"Oluwadamilola Oyinloye completed her Ph.D. in the Department of Industrial Chemistry at Nile University of Nigeria, co-supervised by Dr. Okolie and Dr. Adekunle Adeleke. Her doctoral research focused on enhanced biogas production from agricultural and food waste through anaerobic digestion using biochar as a catalyst, including the influence of biochar produced at different temperatures on biogas yield and the techno-economic and life cycle analysis of the integrated process. She holds a B.Sc. and M.Sc. in Industrial Chemistry from the University of Ilorin, Kwara State.",
 "reed-muir":"Reed Muir is a junior chemical engineering major at Bucknell University. His research focuses on optimizing the synthesis of lithium orthosilicate, a material that can capture carbon dioxide at high temperature, from spent lithium-ion batteries. He presented his poster, Influence of Ni and Co Impurities on the CO2 Capture Performance of Lithium Orthosilicate Derived from Spent Lithium-Ion Batteries, at the 2026 AIChE Annual Meeting in Minneapolis. Reed is passionate about the environment and sustainability and hopes to make a difference in these areas.",
 "noah-thorpe":"Noah Thorpe is a senior studying chemical engineering at Bucknell University. His passion for science and mathematics began at an early age, and high school courses in chemistry and engineering solidified his interest in pursuing a career in chemical engineering. At Bucknell, Noah is an active member of the university's Chem-E-Car Team, which qualified to compete at the 2024 national AIChE conference. Originally from Concord, Massachusetts, Noah balances his academic pursuits with interests in ice hockey, golf, and fitness. He is working on a project aimed at repurposing spent lithium batteries and functionalizing their materials for use in carbon dioxide capture.",
 "frank-onwudinjo":"Chimezie Frank Onwudinjo is now a Ph.D. student at the University of Wyoming. In the SETD group, he was a master's student in chemical engineering at Bucknell University, where his research focused on repurposing spent lithium-ion batteries for bifunctional material synthesis for climate change mitigation, and he presented this work at the Kalman Symposium at Bucknell. He is passionate about advancing STEM education, sustainable process optimization and materials discovery, especially embedding the circular economy concept in engineering operations. Frank is a member of the American Institute of Chemical Engineers (AIChE), a registered engineer (R.Engr.) with the Council for the Regulation of Engineering in Nigeria (COREN), a Corporate Member of the Nigerian Society of Engineers (NSE) and a Licensed Professional Teacher certified by the Teachers' Registration Council of Nigeria (TRCN).",
 "hauwau-kaoje":"Hauwau Kaoje is now a lecturer at Nile University of Nigeria. In the SETD group, she was a Ph.D. candidate in the Department of Industrial Chemistry at Nile University of Nigeria, co-supervised by Dr. Okolie and Dr. Adekunle Adeleke. Her research focused on bio-oil production from hybrid lignocellulosic biomass, integrating bio-oil production within broader biorefinery and circular economy frameworks, with attention to feedstock diversification, innovative reactor designs, biochemical upgrading and sustainability. She holds a B.Sc. in Applied Chemistry from Usmanu Danfodiyo University, Sokoto, and an M.Sc. in Industrial Chemistry from Kebbi State University of Science and Technology, Aliero.",
}
PAST_PHOTOS = {"Fredrick Omoarukhe":"fredrick-omoarukhe","Inioluwa Christianah Afolabi":"inioluwa-afolabi","Meshach Tabat":"meshach-tabat","Kwaghtaver S. Desongu":"kwaghtaver-desongu","Arnold Sison":"arnold-sison"}

def linkify(t):
    t=E(t)
    t=re.sub(r"\(?(https?://[^\s)]+)\)?\.?$", lambda m: f' <a href="{m.group(1)}" target="_blank" rel="noopener">View work →</a>', t)
    t=re.sub(r"(Publications|Work|Thesis):\s*(<a )", r"\2", t)
    return t

FAC = [  # img, title, key spec, description(list of paragraphs or bullets)
 ("lab-htl-reactor.jpg","Hydrothermal liquefaction (HTL) reactor","250–374 °C · up to 200 bar",
  ["A lab-scale hydrothermal liquefaction reactor: an advanced high-pressure, high-temperature system designed to convert wet biomass, plastics, or organic waste into bio-crude oil and valuable chemicals under subcritical or supercritical water conditions.",
   "Operated typically between 250–374 °C and at pressures up to 200 bar, it allows researchers to simulate industrial hydrothermal processes on a laboratory scale, enabling precise control of reaction conditions such as temperature, pressure, residence time, and stirring speed to optimize product yields and study reaction mechanisms. This setup is crucial for sustainable fuel research, waste valorization, and developing carbon-neutral energy pathways."]),
 ("lab-clc-reactor.jpg","Chemical looping combustion &amp; in-situ CO₂ capture reactor","600–1000 °C tubular furnace",
  ["Designed for experimental studies on solid-fuel and gas-fuel conversion processes under controlled atmospheres. The horizontal tubular furnace provides uniform heating for the reactor tube, allowing operation at high temperatures (typically 600–1000 °C) to facilitate oxygen carrier redox reactions and CO₂ capture in a single system.",
   "Integrated with precise gas delivery lines, flow meters, and pressure gauges, this setup enables the introduction of reactant gases like methane, syngas, or CO₂ for in-situ capture and conversion, while effluent gases can be analyzed downstream for combustion efficiency and carbon capture performance. It is used for material testing, oxygen carrier cycling stability, and developing low-emission energy systems."]),
 ("lab-microwave-pyrolysis.jpg","VIVTEK Instruments MCR-100 microwave pyrolysis reactor","Rapid, uniform microwave heating",
  ["A laboratory-scale microwave pyrolysis reactor designed for the thermochemical conversion of biomass, plastics, and other organic feedstocks into bio-oil, syngas, and biochar. Microwave energy provides rapid and uniform heating, which enhances reaction kinetics and energy efficiency compared to conventional heating methods.",
   "Key features: touchscreen interface for precise control of temperature, reaction time, and power settings; high-efficiency microwave cavity and integrated quartz reactor tube for effective heat transfer and process stability; temperature control and monitoring system for consistent, reproducible reaction conditions."]),
 ("lab-pyrolysis.jpg","Biomass pyrolysis reactor","400–600 °C · bio-oil, syngas, biochar",
  ["Designed to thermochemically convert organic biomass into bio-oil, syngas, and biochar in the absence of oxygen. Operating typically between 400–600 °C, the reactor rapidly heats feedstocks like agricultural waste, wood chips, or algae to decompose their complex polymers (cellulose, hemicellulose, and lignin) into smaller volatile compounds and solid carbonaceous residues.",
   "The setup enables precise control of heating rate, residence time, and carrier gas flow, which are crucial for optimizing product yields and properties."]),
 ("lab-bet.jpg","Micromeritics 3Flex BET surface area &amp; porosity analyzer","Surface area, pore volume, pore size",
  ["A precision instrument for characterizing surface area, pore volume, and pore size distribution of solid materials through gas adsorption. Based on Brunauer-Emmett-Teller (BET) theory, it measures how much gas (commonly nitrogen at liquid nitrogen temperature) physically adsorbs onto a material's surface.",
   "This data is essential for designing and evaluating catalysts, adsorbents for CO₂ capture, battery materials, and porous supports. Its multi-station design allows high-throughput testing and detailed analysis of micro-, meso-, and macroporous structures."]),
 ("lab-ozone.jpg","Ozone generator, oxygen concentrator &amp; reaction chamber","Advanced oxidation processes",
  ["Designed for controlled ozone exposure experiments or advanced oxidation processes. The oxygen concentrator ensures a stable, high-purity oxygen feed to the ozone generator, which converts molecular oxygen into ozone using a high-voltage electrical discharge.",
   "The ozone is introduced into a sealed chamber where it interacts with target materials or pollutants for surface modification, sterilization, oxidation of volatile organic compounds (VOCs), or catalyst testing under oxidative environments, with precise control over gas composition and ozone concentration."]),
 ("lab-uv-vis.jpg","UV-Vis spectrophotometer","200–800 nm",
  ["Measures the absorbance and transmittance of light by liquid or solid samples across the ultraviolet and visible spectrum, typically 200–800 nm, enabling quantification of molecular concentration via the Beer-Lambert law.",
   "Widely applied in material characterization, reaction monitoring, and environmental analysis, it is used to analyze catalysts, adsorbents, and liquid products from processes like CO₂ capture and conversion, offering quick, non-destructive analysis of metal ions, organic compounds, and functional groups."]),
 ("lab-shaker.jpg","Boekel Jitterbug™ orbital shaker incubator","Controlled agitation &amp; temperature",
  ["A compact benchtop instrument providing controlled shaking and mixing of liquid samples in microplates or small vials, with adjustable speed and temperature.",
   "Uniform orbital agitation supports biochemical reactions, incubation, enzyme kinetics, catalyst suspension preparation, catalyst pre-treatment, adsorption studies, and any process requiring controlled agitation to maintain sample uniformity."]),
]

BOOKS = [("book-ml-thermochemical.jpg","Data-Driven Machine Learning Applications in Thermochemical Conversion Processes","Edited by J. Okolie, A. Giwa, P. Okoye, B. Oboirien · Elsevier · ISBN 978-0-443-33372-9","https://doi.org/10.1016/C2023-0-52756-9"),
         ("book-nanomaterials-hydrogen.jpg","Nanomaterials for Sustainable Hydrogen Production and Storage","Edited by J.A. Okolie, E.I. Epelle, A. Mukherjee, A.E.D. Mahmoud · CRC Press","https://doi.org/10.1201/9781003371007"),
         ("book-activated-carbon.jpg","Activated Carbon: Synthesis, Analysis, and Industrial Applications","J.A. Okolie, A. Mukherjee · Elsevier","https://doi.org/10.1016/C2022-0-02853-1"),
         ("book-lab-at-home.jpg","Lab-at-Home Experiments in Chemistry and Chemical Engineering","J.A. Okolie, U.P. Okoye, with contributions by Maya Fetzer · CRC Press","https://doi.org/10.1201/9781003374503"),
         ("book-biofuel.jpg","Biofuel","Edited by P.U. Okoye, J.A. Okolie, S. Kolisnychenko · Trans Tech Publications","https://doi.org/10.4028/www.scientific.net/978-3-0357-3827-8")]

# news: (img list, date, title, body html, link)
AICHE_GALLERY = [("aiche26-group.jpg","At the 2026 AIChE Annual Meeting in Minneapolis"),("aiche26-omuhle-poster.jpg","Omuhle Ndhlovu: Comparative Assessment of Biochar and Hydrochar from Food-waste"),("aiche26-reed-muir.jpg","Reed Muir: Influence of Ni and Co Impurities on the CO₂ Capture Performance of Lithium Orthosilicate Derived from Spent Lithium-Ion Batteries"),("aiche26-nyuon-jongkuch.jpg","Jongkuch Nhial Nyuon: Influence of Manganese and Aluminum Impurities on Battery-Derived Li₄SiO₄ for CO₂ Capture"),("aiche26-aiden-beck.jpg","Aiden Beck: Coffee Grounds as Potential Supercapacitor Electrode Material")]
NEWS = [
 (["aiche26-reed-muir.jpg"],"September 2026","New article in Chemical Engineering Journal: cathode delamination and CO₂ capture by battery-derived Li₄SiO₄",
  "Frank Onwudinjo, Reed Muir, Ahsan Khan and Dr. Okolie published a study in <em>Chemical Engineering Journal</em> on how cathode delamination affects the recovery of cathode materials from mixed-chemistry spent lithium-ion batteries and their conversion into lithium orthosilicate (Li₄SiO₄) sorbents for CO₂ capture. The study compares delamination strategies including pyrolysis at different temperatures, NaOH treatment and NMP. It is the second publication from Frank's M.S. thesis.",None),
 (["news-kalman-symposium.jpg"],"December 2025","New article: geo-spatial, techno-economic and life-cycle assessment of spent battery upcycling",
  "Published in <em>Process Safety and Environmental Protection</em> (Onwudinjo, Giwa, Jolaoso, Okoye and Okolie). The study integrates techno-economic analysis, GIS-based spatial analysis and life cycle assessment to evaluate upcycling spent lithium-ion batteries into a CO₂ capture adsorbent, using the U.S. Mid-Atlantic region as a case study.","https://doi.org/10.1016/j.psep.2025.108380"),
 (["news-feature-open-door.jpg"],"2026","Bucknell Magazine features Professor Jude Okolie's open-door lab",
  "<em>Bucknell Magazine</em> featured Dr. Okolie for his open-door approach to mentoring student researchers. “I don't turn students away because research is mostly about having a space to explore,” he says. “All they need to work with me is interest, passion and discipline.” The feature highlights his interdisciplinary research on the role of AI in renewable energy, which welcomes student collaborators from a broad range of disciplines, and the friendly culture of the SETD lab. “My lab is very interactive and friendly,” he says. “We have a group chat, we meet weekly, and we share dinners. It's a place where students can find not only new ideas but meaningful friendships.”",None),
 (["aiche26-omuhle-award.jpg"],"November 2026","Omuhle Ndhlovu wins second place in the AIChE Student Poster Competition",
  "Congratulations to Omuhle Ndhlovu, who won second place in the student poster competition at the 2026 AIChE Annual Student Conference in Minneapolis for her poster, <em>Comparative Assessment of Biochar and Hydrochar from Food-waste</em>.",None),
 (["aiche26-group.jpg"],"November 2026","SETD students present their research at the 2026 AIChE Annual Meeting",
  "Several SETD students presented posters at the recently concluded 2026 AIChE Annual Student Conference and Annual Meeting in Minneapolis, Minnesota:<ul><li>Omuhle Ndhlovu: Comparative assessment of biochar and hydrochar from food waste</li><li>Reed Muir: Influence of Ni and Co impurities on the CO₂ capture performance of lithium orthosilicate derived from spent lithium-ion batteries</li><li>Jongkuch Nhial Nyuon: Influence of manganese and aluminum impurities on battery-derived Li₄SiO₄ for CO₂ capture</li><li>Aiden Beck: Coffee grounds as potential supercapacitor electrode material</li></ul>","gallery"),
 (["okolie-portrait.jpg"],"2026","Dr. Okolie receives the 2026 ACS CES Award for Incorporating Sustainability into Chemical Education","Dr. Jude Okolie is one of the 2026 awardees of the American Chemical Society (ACS) Committee on Environment and Sustainability (CES) Award for Incorporating Sustainability into Chemical Education. The international cohort of educators was recognized for creative classroom and laboratory innovations, including systems thinking, environmental and risk assessment, green chemistry, and engagement through gamification. Awardees will present their work in a dedicated symposium at the Spring 2027 ACS meeting in New Orleans.",None),
 (["lab-clc-reactor.jpg"],"2026","Dr. Okolie awarded an ACS Petroleum Research Fund grant for dry methane reforming research","Dr. Okolie was awarded an American Chemical Society Petroleum Research Fund (ACS-PRF) grant for the project <em>Metal–Support Interactions and Coke Deposition Mechanisms in Ni–Co–Fe Catalysts for Dry Methane Reforming</em>. The project runs from January 2027 to December 2028.",None),
 (["news-bucknell-ai-biodiesel.jpg"],"October 15, 2025","Bucknell Professor Jude Okolie harnesses AI to assess sources of biodiesel fuel","Bucknell University featured Dr. Okolie's work using artificial intelligence to evaluate feedstocks for biodiesel production.","https://www.bucknell.edu/news/bucknell-professor-jude-okolie-harnesses-ai-assess-sources-biodiesel-fuel"),
 (["news-aiche-2025-poster.jpg"],"November 2025","My Ly wins first place Poster Award at AIChE 2025","Congratulations My Ly, for the first place Poster Award during the AIChE 2025 conference in Boston.",None),
 (["news-kalman-symposium.jpg"],"2025","Frank Chimezie presents at the Kalman Symposium","Frank Chimezie presented his work on repurposing spent lithium batteries as CO₂ adsorbents during the Kalman Symposium at Bucknell University.",None),
 (["lab-pyrolysis.jpg"],"2025","Industry grant from The Catalyst Group Resources","Dr. Okolie was awarded an industry grant by The Catalyst Group Resources for the project entitled “Technology evaluation of waste biomass gasification to sustainable aviation fuel.”",None),
 (["news-sdg-comics.jpg"],"2025","New article: A team-based activity integrated with comics for introducing the Sustainable Development Goals in classrooms",
  "Published in <em>Education for Chemical Engineers</em> (Okolie, Barakat, Smith, Ogbaga, Iorember and Jellason). The study proposes a team-based activity that aids understanding of the international relations and cooperation needed to achieve the SDGs, and introduces the water-waste-energy nexus. The activity, including the comics, was tested with students from universities in Africa and England grouped into eight simulated countries with distinct resources and challenges. Participants from Africa focused more on urgent local issues such as zero hunger (SDG2), quality education (SDG4) and clean water (SDG6), while UK participants focused more on global, policy-oriented issues such as clean energy (SDG7), sustainable cities (SDG11) and climate change (SDG13). The activity significantly enhanced students' understanding of the SDGs, global challenges and the water-energy nexus.","https://doi.org/10.1016/j.ece.2025.01.004"),
 (["news-brooke-award.jpg","news-brooke-certificate.jpg"],"Spring 2024","Brooke Rogachuk wins first place at Undergraduate Research Day","Congratulations to Brooke Rogachuk for winning first place in the Engineering Pathways section at the University of Oklahoma Undergraduate Research Day. Brooke presented her work on the comparative assessment of pyrolysis and gasification-Fischer Tropsch processes for sustainable aviation fuel production from waste tires. Her dedication and pioneering research are paving the way for more sustainable solutions in aviation fuel.","https://lnkd.in/grmFcH9U"),
 (["news-encyclopedia-award.jpg"],"2023","Dr. Okolie wins the Encyclopedia 2023 Outstanding Contributor Award","Congratulations to Dr. Jude Okolie for winning the MDPI Encyclopedia 2023 Outstanding Contributor Award.",None),
 ([],"2023","New article: Waste tires based biorefinery for biofuels and value-added materials production","Every year, approximately 1.4 billion waste tires are produced, typically ending up in landfills or incinerated. Yet waste tires are a promising source of energy and energetic materials thanks to their low moisture content and high heating value. This study analyzes methods for converting waste tires into biofuels, green chemicals, and innovative materials, includes a bibliometric analysis of research trends, compares traditional management strategies, and proposes a new integrated waste tire biorefinery combining thermochemical and biological processes.","https://www.sciencedirect.com/science/article/pii/S2666821123000339"),
 ([],"2023","New article: Process design, exergy, and economic assessment of a conceptual mobile autothermal methane pyrolysis unit for onsite hydrogen production","The design combines a catalytic plasma methane pyrolysis unit with steam char gasification, combustion, and biomethanation for onsite hydrogen production where pipeline infrastructure is lacking. The levelized cost of hydrogen ranged from 1.3 to 1.47 US$/kg, net present value ranged from 3.76 to 4.35 M US$, and an optimized methane conversion of 76.8% was obtained.","https://www.sciencedirect.com/science/article/pii/S0196890423000535"),
 ([],"2023","New article: Pathways for the valorization of animal and human waste to biofuels, sustainable materials and value-added chemicals","An overview of thermochemical and biological conversion pathways for transforming human- and animal-derived waste into valuable resources, covering physicochemical properties, nutrient recovery strategies, and a bibliometric analysis of research trends and knowledge gaps.","https://www.mdpi.com/2178510"),
 ([],"December 2022","Guest lecture at the Sustainable Bioenergy and Processes Conference, Cape Town","Dr. Okolie delivered a guest lecture entitled “Assessing the Economic and Environmental Impacts of Different Integrated Biomass Conversion Processes: Current Status and Future Prospects” at the Sustainable Bioenergy and Processes Conference, 12–15 December 2022, Cape Town, South Africa.",None),
 ([],"2022","New article: Stochastic economic evaluation of renewable propylene glycol production via catalytic hydrogenolysis of glycerol","This study investigated the economic viability of three renewable propylene glycol production pathways and showed that the source of hydrogen has a significant impact on their economic feasibility.","https://pubs.rsc.org/en/content/articlehtml/2022/re/d2re00281g"),
 ([],"2022","New article: Ozone application in different industries: A review of recent developments","A review of recent advances in using ozone for decontamination in the food, water treatment, pharmaceutical, textile, healthcare and medical sectors, emphasizing key parameters affecting microbial reduction efficiency and ozone stability.","https://www.sciencedirect.com/science/article/pii/S1385894722056686"),
 ([],"2022","New article: Nanoarchitectonics corncob activated carbon as electrode material for enhanced supercapacitor performance","Corncob was converted to activated carbon by K₂CO₃ impregnation and activation at 500–800 °C, giving surface areas of 489–884 m²/g. A specific capacitance of 325 F/g was reached at 5 mV/s, with 88% energy retention and 100% coulombic efficiency after 10,000 cycles.","https://www.sciencedirect.com/science/article/abs/pii/S2352152X22014396"),
 (["news-nanomaterials-wastewater.jpg"],"2022","New article: Advances in the applications of nanomaterials for wastewater treatment","A review of nanomaterials for removing contaminants that conventional treatment struggles with, focusing on carbon nanotubes, graphene-based nanosheets, fullerenes, and silver, copper and iron nanoparticles, with challenges and prospects for their use.","https://www.mdpi.com/2076-3298/9/11/141/htm"),
]

MONTHS={m:i for i,m in enumerate(["january","february","march","april","may","june","july","august","september","october","november","december"],1)}
SEASONS={"spring":4,"summer":7,"fall":10,"autumn":10,"winter":1}
def news_key(item):
    """Sort key from the date label: (year, month, day). Labels with only a year sort after dated items of that year."""
    label=item[1].lower().replace(",","")
    y=int(re.search(r"(19|20)\d\d",label).group(0)) if re.search(r"(19|20)\d\d",label) else 0
    mo=next((n for m,n in MONTHS.items() if m in label),0) or next((n for m,n in SEASONS.items() if m in label),0)
    d=re.search(r"\b(\d{1,2})\b",label); d=int(d.group(1)) if d and mo else 0
    return (y,mo,d)
NEWS=sorted(NEWS,key=news_key,reverse=True)

def news_item_card(n):
    imgs,date,title,body,link=n
    img = f'<img src="img/{imgs[0]}" alt="">' if imgs else '<img src="img/lab-htl-reactor-2.jpg" alt="">'
    return f'<article>{img}<div class="t"><time>{date}</time><h3><a href="news.html" style="text-decoration:none">{title}</a></h3></div></article>'

# ---------------- PAGES ----------------
def build():
    current = parse_people("present_members.md")
    past = parse_people("past_members.md")
    assert len(current)==13 and len(past)>=12, (len(current),len(past))
    allcur=[(slug,name,role,bio) for (slug,role),(name,bio) in zip(CURRENT_TEAM,current)]
    MOVED={"makenzie-krance","frank-onwudinjo","kaustubh-pandit","oluwadamilola-oyinloye","hauwau-kaoje"}
    CUR=[(a,b,c,BIO_UPDATES.get(a,d)) for a,b,c,d in allcur if a not in MOVED]+NEW_STUDENTS
    PAST=[(x[0],x[1],BIO_UPDATES.get(x[0],x[3])) for x in allcur if x[0] in MOVED]+[(PAST_PHOTOS.get(n),n,b) for n,b in past]
    # HOME
    cards="".join(f'<a class="card" href="research.html"><img src="img/{img}" alt=""><div class="b"><span class="tag">Cluster 0{i+1}</span><h3>{t}</h3><p>{d}</p><ul>{"".join(f"<li>{x}</li>" for x in items)}</ul><span class="more">Learn more →</span></div></a>' for i,(t,img,d,items) in enumerate(CLUSTERS))
    team="".join(f'<a class="tm" href="people.html#{slug}">{f'<img src="img/{slug}.jpg" alt="{E(name)}">' if (OUT/"img"/f"{slug}.jpg").exists() else f'<span class="tm-initials">{"".join(w[0] for w in name.split()[:2])}</span>'}<b>{E(name)}</b><span>{role}</span></a>' for slug,name,role,_ in CUR)
    fac="".join(f'<figure><img src="img/{f[0]}" alt="{f[1]}"><figcaption>{f[1]}</figcaption></figure>' for f in FAC)
    def ncard(n):
        imgs,date,title,body,link=n
        return f'<article><img src="img/{imgs[0] if imgs else "lab-htl-reactor-2.jpg"}" alt=""><time>{date}</time><h3><a href="news.html">{title}</a></h3></article>'
    newsl="".join(ncard(n) for n in NEWS[:6])
    books="".join(f'<div><a href="{b[3]}" target="_blank" rel="noopener"><img src="img/{b[0]}" alt="Cover of {E(b[1])}"></a><p>{E(b[1])}<small>{E(b[2])}</small><a class="more" href="{b[3]}" target="_blank" rel="noopener" style="display:inline-block;margin-top:6px">View book →</a></p></div>' for b in BOOKS)
    steps=[("01","Experiments","Reactor studies in hydrothermal liquefaction, pyrolysis, gasification and chemical looping."),("02","Process design","Process design and simulation, control and optimization of integrated conversion routes."),("03","Systems &amp; economics","Energy system modelling, techno-economic analysis and life cycle assessment."),("04","Machine learning","Data-driven models that predict and optimize thermochemical processes.")]
    stepsh="".join(f'<div class="step"><span>Step {a}</span><b>{b}</b><p>{c}</p></div>' for a,b,c in steps)
    home=f"""
<section class="hero"><img src="img/lab-pyrolysis.jpg" alt=""><div class="wrap"><span class="tag">Sustainable Energy Transition &amp; Decarbonization</span>
<h1>Turning waste into clean energy and sustainable materials</h1>
<p>{INTRO} {INTRO2}</p>
<div class="btns"><a class="btn pri" href="research.html">Our research</a><a class="btn" href="people.html">Meet the team</a></div></div></section>
<section><div class="wrap"><span class="tag">Research</span><h2>What we study</h2><p class="lede">Our research spans three connected clusters, from the reactor bench to system-scale models.</p><div class="cards">{cards}</div></div></section>
<section class="tint"><div class="wrap"><span class="tag">How we work</span><h2>Our approach</h2><p class="lede">We combine experiments with modelling, economics and machine learning to answer three questions: how waste can be managed while meeting rising energy demand; how to optimize the cost and efficiency of waste-to-value processes; and how to develop new materials for sustainable fuel, food security and human health.</p><div class="steps">{stepsh}</div></div></section>
<section><div class="wrap split"><img src="img/news-feature-open-door.jpg" alt="Dr. Jude Okolie demonstrating a furnace to students in the lab" style="aspect-ratio:1">
<div><span class="tag">Principal investigator</span><h2>Dr. Jude A. Okolie</h2>
<p>Dr. Jude A. Okolie is an Assistant Professor in the Department of Chemical Engineering at Bucknell University, where he leads the SETD Research Group. He previously served as an Assistant Professor of Engineering Pathways at the University of Oklahoma.</p>
<p>His research focuses on the thermochemical conversion of waste materials into green fuels, hydrochar and biochar for environmental remediation, and process simulation and AI/machine learning for climate change, environmental pollution and sustainable agriculture. His honors include the 2026 ACS CES Award for Incorporating Sustainability into Chemical Education, the George Ira Hanson Energy Award and the Encyclopedia 2023 Outstanding Contributor Award.</p>
<div class="btns"><a class="btn pri" href="about.html">Full bio &amp; CV</a>{"".join(ext(t,u,"btn") for t,u in LINKS[:2])}</div>
<div class="facts"><div><small>Ph.D., Chemical Engineering</small>University of Saskatchewan</div><div><small>M.Sc., Materials &amp; Sustainable Energetics</small>Tallinn University of Technology</div><div><small>M.Sc., Petroleum Engineering</small>Imperial College London</div><div><small>B.Eng., Chemical Engineering</small>University of Benin</div></div></div></div></section>
<section class="tint"><div class="wrap"><span class="tag">Latest</span><h2>News</h2><p class="lede">Awards, grants, conference presentations and student achievements.</p><div class="news3">{newsl}</div><p style="margin-top:32px"><a class="btn" href="news.html">All news</a></p></div></section>
<section><div class="wrap"><span class="tag">People</span><h2>Meet the team</h2><p class="lede">Graduate and undergraduate researchers at Bucknell, with collaborators at partner institutions.</p><div class="team">{team}</div><p style="margin-top:32px"><a class="btn" href="people.html">Current &amp; past members</a></p></div></section>
<section class="tint"><div class="wrap"><span class="tag">Facilities</span><h2>Laboratory facilities</h2><p class="lede">High-pressure reactors, thermochemical conversion systems and materials characterization in the SETD laboratory.</p><div class="fac">{fac}</div><p style="margin-top:32px"><a class="btn" href="facilities.html">All laboratory resources</a></p></div></section>
<section><div class="wrap"><span class="tag">Books</span><h2>Books</h2><p class="lede">Edited volumes and textbooks on biofuels, hydrogen, carbon materials, machine learning and hands-on learning.</p><div class="books">{books}</div></div></section>
<section style="padding-top:0"><div class="wrap"><div class="join"><div><h2>Join the group</h2><p>“I don't turn students away because research is mostly about having a space to explore. All they need to work with me is interest, passion and discipline.” We welcome undergraduate and graduate students and collaborators interested in waste valorization, hydrogen, carbon capture and process modelling.</p></div><div><a class="btn pri" href="mailto:{EMAIL}">{EMAIL}</a></div></div></div></section>"""
    page("index.html","SETD Research Group · Dr. Jude A. Okolie","Sustainable Energy Transition and Decarbonization (SETD) research group led by Dr. Jude A. Okolie, Chemical Engineering, Bucknell University.",home)

    # RESEARCH
    rows="".join(f'<div class="split" style="margin-bottom:48px"><img src="img/{img}" alt="" style="aspect-ratio:4/3"><div><span class="tag">Cluster 0{i+1}</span><h2 style="font-size:clamp(26px,3vw,38px)">{t}</h2><p>{d}</p><ul class="muted">{"".join(f"<li>{x}</li>" for x in items)}</ul></div></div>' for i,(t,img,d,items) in enumerate(CLUSTERS))
    research=hero("Research","Welcome to our research home",
      "Over the years, Dr. Okolie has acquired skills in catalyst development and process systems engineering, including process design and simulation, control and optimization, energy system modelling and life cycle assessment, and has collaborated with individuals and industrial partners on several research projects.")+f"""
<section><div class="wrap cols"><div class="prose"><span class="tag">Why it matters</span><h2>Our mission</h2><p>{INTRO}</p><p>{INTRO2}</p></div>
<div><span class="tag">Guiding questions</span><ul class="list">{"".join(f"<li>{q}</li>" for q in QUESTIONS)}</ul></div></div></section>
<section><div class="wrap"><span class="tag">Research areas</span><h2>What we work on</h2><div class="chips" style="margin:18px 0 48px">{"".join(f'<span class="chip">{a}</span>' for a in AREAS)}</div>{rows}</div></section>
<section><div class="wrap cols"><div><span class="tag">In progress</span><h2>Current projects</h2><ul class="list">{"".join(f"<li>{x}</li>" for x in CURRENT)}</ul></div>
<div><span class="tag">Done</span><h2>Completed projects</h2><ul class="list">{"".join(f"<li>{x}</li>" for x in COMPLETED)}</ul></div></div></section>
<section><div class="wrap"><span class="tag">Toolkit</span><h2>Methods</h2><div class="chips" style="margin-top:18px">{"".join(f'<span class="chip">{m}</span>' for m in METHODS)}</div></div></section>
<section><div class="wrap"><span class="tag">Intellectual property</span><h2>Patent</h2><div class="callout"><p style="margin:0">{PATENT}</p></div></div></section>"""
    page("research.html","Research · SETD Research Group","Research clusters, current and completed projects, and patent of the SETD group.",research)

    # PEOPLE
    def person(slug,name,role,bio):
        img = f'<img src="img/{slug}.jpg" alt="{E(name)}">' if slug and (OUT/"img"/f"{slug}.jpg").exists() else f'<div class="initials">{"".join(w[0] for w in name.split()[:2])}</div>'
        return f'<article class="person" id="{slug or re.sub(r"[^a-z]+","-",name.lower())}">{img}<div class="b"><span class="tag">{role}</span><h3>{E(name)}</h3><p>{linkify(bio)}</p></div></article>'
    cur="".join(person(slug,name,role,bio) for slug,name,role,bio in CUR)
    pst="".join(person(slug,name,"Past member",bio) for slug,name,bio in PAST)
    people=hero("People","Our team","Current and past members of the SETD Research Group.")+f"""
<section><div class="wrap"><div class="split" style="margin-bottom:12px"><img src="img/okolie-portrait.jpg" alt="Dr. Jude A. Okolie" style="max-width:420px;aspect-ratio:1"><div><span class="tag">Principal investigator</span><h2>Dr. Jude A. Okolie</h2><p>Assistant Professor, Department of Chemical Engineering, Bucknell University.</p><div class="btns"><a class="btn pri" href="about.html">Bio &amp; CV</a><a class="btn" href="mailto:{EMAIL}">Email</a></div></div></div></div></section>
<section><div class="wrap"><span class="tag">Now</span><h2>Current students</h2><div class="people" style="margin-top:24px">{cur}</div></div></section>
<section><div class="wrap"><span class="tag">Alumni</span><h2>Past research students</h2><div class="people" style="margin-top:24px">{pst}</div></div></section>"""
    page("people.html","People · SETD Research Group","Current and past members of the SETD Research Group at Bucknell University.",people)

    # FACILITIES
    inst="".join(f'<div class="inst"><img src="img/{f[0]}" alt="{f[1]}"><div><span class="tag">{f[2]}</span><h3 style="font-size:26px">{f[1]}</h3>{"".join(f"<p>{p}</p>" for p in f[3])}</div></div>' for f in FAC)
    fac=hero("Laboratory resources","Inside the SETD lab","Reactors and analytical instruments for thermochemical conversion, carbon capture and materials characterization.")+f"""
<section><div class="wrap">{inst}<div style="margin-top:36px"><span class="tag">More views</span><div class="gallery" style="margin-top:12px"><figure><img src="img/lab-htl-reactor-2.jpg" alt="HTL reactor and bench setup"><figcaption>High-pressure reactors and gas handling in the SETD lab</figcaption></figure></div></div></div></section>"""
    page("facilities.html","Facilities · SETD Research Group","Laboratory equipment of the SETD Research Group.",fac)

    # PUBLICATIONS
    txt=(CONTENT/"publications.txt").read_text().strip().split("\n")
    blocks=[];cur_t=None
    for ln in txt:
        if ln.startswith("## "): cur_t=[ln[3:],[]]; blocks.append(cur_t)
        elif ln.strip(): cur_t[1].append(ln.strip())
    def hl(s): return E(s).replace("Okolie, J.A.","<mark>Okolie, J.A.</mark>").replace("Onwudinjo, C.F.","Onwudinjo, C.F. (supervised by J.A. Okolie)").replace("Okolie, J.","<mark>Okolie, J.</mark>").replace("<mark><mark>","<mark>").replace("</mark>A.</mark>","A.</mark>")
    pubs="".join(f'<div style="margin-bottom:48px"><span class="tag">Theme {i+1}</span><h3 style="font-size:26px;margin-top:6px">{E(t.split(": ",1)[1])}</h3><ol class="pubs">{"".join("<li><span>"+re.sub(r"(https?://\S+)",lambda m:f'<a href="{m.group(1)}" target="_blank" rel="noopener" style="color:var(--orange-ink)">Link →</a>',hl(p))+"</span></li>" for p in ps)}</ol></div>' for i,(t,ps) in enumerate(blocks))
    pubpage=hero("Publications","Publications","Peer-reviewed articles and book chapters, organized by research theme. For the most up-to-date list, see Google Scholar.")+f"""
<section><div class="wrap"><div class="chips" style="margin-bottom:40px">{"".join(ext(t,u,"chip") for t,u in LINKS)}</div>{pubs}</div></section>
<section><div class="wrap"><span class="tag">Books</span><h2>Books</h2><div class="books" style="margin-top:28px">{books}</div></div></section>"""
    page("publications.html","Publications · SETD Research Group","Publications and books by Dr. Jude A. Okolie and the SETD group.",pubpage)

    # TEACHING
    tp=(CONTENT/"teaching_philosophy.md").read_text().split("## Teaching Philosophy")
    def md_paras(s): return "".join(f"<p>{E(p.strip())}</p>" for p in s.strip().split("\n\n") if p.strip() and not p.startswith("#"))
    tp_bg=md_paras(tp[0].split("\n",1)[1]); tp_main=tp[1]
    tp_main=re.sub(r"\n(\d)\. ([^:]+):", lambda m:f"\n\n<b>{m.group(1)}. {m.group(2)}:</b>", tp_main)
    tp_main="".join(f"<p>{(p.strip() if p.strip().startswith('<b>') else E(p.strip()))}</p>" for p in tp_main.strip().split("\n\n") if p.strip())
    tp_main=re.sub(r"<p><b>(.*?)</b>(.*?)</p>", lambda m:f"<p><b>{m.group(1)}</b>{E(m.group(2))}</p>", tp_main)
    crs=(CONTENT/"courses.md").read_text()
    def courses_html(s):
        out=[]
        for part in re.split(r"\n(?=## )", s):
            if not part.startswith("## "): continue
            head,_,body=part.partition("\n")
            out.append(f'<h3 style="font-size:24px;margin-top:40px">{E(head[3:])}</h3>')
            for blk in re.split(r"\n(?=### )", body):
                if blk.startswith("### "):
                    h,_,blk=blk.partition("\n"); out.append(f'<h4 style="margin:24px 0 6px;color:var(--orange-ink)">{E(h[4:])}</h4>')
                items=[];paras=[]
                for ln in blk.strip().split("\n"):
                    ln=ln.strip()
                    if not ln: continue
                    if ln.startswith("- "): items.append(f"<li>{E(ln[2:])}</li>")
                    elif " — " in ln: c,d=ln.split(" — ",1); paras.append(f"<li><b>{E(c)}</b><br>{E(d)}</li>")
                    elif re.match(r"\d\. ",ln):
                        c,_,d=ln[3:].partition(": "); paras.append(f"<li><b>{E(c)}</b><br>{E(d)}</li>")
                    else: paras.append(f'<li style="border:0">{E(ln)}</li>')
                if paras: out.append(f'<ul class="list">{"".join(paras)}</ul>')
                if items: out.append(f'<ul class="list">{"".join(items)}</ul>')
        return "".join(out)
    aw=[l[2:] for l in (CONTENT/"awards.md").read_text().split("\n") if l.startswith("- ")]
    aw=[a.replace(" (listed twice on site)","") for a in aw]
    awards_html="".join(f'<li><b>{E(a.rsplit(" — ",1)[0])}</b> <span class="muted">· {a.rsplit(" — ",1)[1]}</span></li>' for a in aw)
    teach=hero("Teaching, awards &amp; scholarships","Teaching","Teaching philosophy, courses taught across four institutions, workshops, curriculum development, and awards.")+f"""
<section><div class="wrap cols"><div class="prose"><span class="tag">Background</span><h2>How I came to teaching</h2>{tp_bg}</div><div class="prose"><span class="tag">Philosophy</span><h2>Teaching philosophy</h2>{tp_main}</div></div></section>
<section><div class="wrap"><span class="tag">Courses</span><h2>Courses taught</h2>{courses_html(crs.split(chr(10),1)[1])}</div></section>
<section id="awards"><div class="wrap"><span class="tag">Recognition</span><h2>Honors, awards &amp; scholarships</h2><ul class="list"><li><b>ACS Committee on Environment and Sustainability (CES) Award for Incorporating Sustainability into Chemical Education</b> <span class="muted">· 2026</span></li><li><b>Encyclopedia Outstanding Contributor Award (MDPI)</b> <span class="muted">· 2023</span></li>{awards_html}</ul></div></section>"""
    page("teaching.html","Teaching · SETD Research Group","Teaching philosophy, courses, workshops and awards of Dr. Jude A. Okolie.",teach)

    # OUTREACH
    dei=md_paras((CONTENT/"dei.md").read_text().split("\n",1)[1])
    outreach=hero("Outreach &amp; DEI","Outreach","Educational apps and games, STEM outreach, and our commitment to diversity, equity and inclusion.")+f"""
<section><div class="wrap"><span class="tag">Educational tools</span><h2>Apps, games &amp; learning tools</h2><p class="lede">Interactive tools, virtual reality activities and games developed by Dr. Okolie and team members to make chemical engineering concepts approachable.</p>
<div class="cols" style="align-items:center"><a href="https://teeap-44e62.web.app/" target="_blank" rel="noopener"><img src="img/teeap-app.jpg" alt="TEEAP app start screen" style="border-radius:12px;border:1px solid var(--line)"></a>
<div><span class="tag">Interactive app</span><h3 style="font-size:26px">TEEAP: Economic &amp; environmental assessment of subsurface hydrogen production</h3><p>An interactive web app for understanding the economic and environmental assessment of subsurface hydrogen production technology, through a spreadsheet-based activity integrated with virtual reality. Developed by Emma K. Smith, Jude A. Okolie and Ezeagu Princewill.</p><p class="muted">The approach is described in our ASEE 2024 paper, <em>Spreadsheet-based application integrated with virtual reality for teaching economic and environmental assessment of subsurface gasification for hydrogen production</em>.</p><div class="btns"><a class="btn pri" href="https://teeap-44e62.web.app/" target="_blank" rel="noopener">Open the TEEAP app</a><a class="btn" href="https://doi.org/10.18260/1-2--47989" target="_blank" rel="noopener">Read the paper</a></div></div></div>
<div class="eq" style="margin-top:32px"><article><div><span class="tag">Education for Chemical Engineers, 2025</span><h3>Teaching the SDGs</h3><p>A team-based activity integrated with comics for introducing the Sustainable Development Goals in classrooms. {ext("Read the article →","https://doi.org/10.1016/j.ece.2025.01.004")}</p></div></article>
<article><div><span class="tag">ASEE 2024</span><h3>Game-based learning</h3><p>Engineering design process through game-based learning for first-year engineering students (ASEE 2024). {ext("Read the paper →","https://doi.org/10.18260/1-2--47276")}</p></div></article>
<article><div><span class="tag">ASEE 2026</span><h3>Bringing space to classrooms</h3><p>A modified hands-on CanSat program for promoting STEM education and career aspirations (ASEE 2026). {ext("Read the paper →","https://doi.org/10.18260/1-2--59378")}</p></div></article></div>
<div class="callout" style="margin-top:24px"><h3>The Infusion of Gamification in Promoting Chemical Engineering Laboratory Classes</h3><p class="muted" style="margin:0 0 8px">An encyclopedia entry surveying games used in chemical engineering laboratory courses, including escape games and virtual and augmented reality games for fluid mechanics, organic reactions and process control, and the future of gamification in chemical engineering labs.</p>{ext("Read on MDPI Encyclopedia →","https://www.mdpi.com/2673-8392/3/3/77")}</div></div></section>
<section><div class="wrap cols"><div><span class="tag">Community</span><h2>Science outreach</h2><p class="muted">Dr. Okolie is deeply committed to science outreach, community engagement, and improving adult literacy. He is a regular volunteer with Let's Talk Science at USASK and a two-time recipient of the Outstanding STEM Volunteer Award and the Graduate Service Fellowship at the University of Saskatchewan. He has mentored over 150 high school students, partnered with more than 20 families to improve literacy skills in Saskatchewan, and developed over 15 hands-on experiments for kids and high school students. He is also an active volunteer with the Boys and Girls Club of Saskatoon, helping design hands-on science activities for before- and after-school programs.</p></div>
<div class="prose"><span class="tag">Perception on DEI</span><h2>Diversity, equity &amp; inclusion</h2>{dei}</div></div></section>"""
    page("outreach.html","Outreach & DEI · SETD Research Group","Educational apps, gamification, STEM outreach and DEI statement.",outreach)

    # NEWS
    posts=[]
    for imgs,date,title,body,link in NEWS:
        media=""
        if link=="gallery":
            media='<div class="gallery">'+"".join(f'<figure><img src="img/{f}" alt="{E(c)}"><figcaption>{E(c)}</figcaption></figure>' for f,c in AICHE_GALLERY)+'</div>'; link=None
        elif imgs:
            media='<div class="gallery">'+"".join(f'<figure><img src="img/{f}" alt=""></figure>' for f in imgs)+'</div>'
        more=f'<p>{ext("Read more →",link)}</p>' if link else ""
        posts.append(f'<article class="post"><div><time>{date}</time><h3>{title}</h3><div class="muted">{body if body.startswith("<") else "<p>"+body+"</p>"}</div>{more}</div>{media}</article>')
    page("news.html","News · SETD Research Group","Latest news, awards and publications from the SETD group.",hero("Latest","News","Awards, grants, conference presentations and new publications.")+f'<section><div class="wrap">{"".join(posts)}</div></section>')

    # ABOUT
    ab=(CONTENT/"about.md").read_text().split("## Home intro")[0].split("\n",1)[1]
    abp=md_paras(ab)
    about=hero("About","Dr. Jude A. Okolie","Assistant Professor of Chemical Engineering, Bucknell University.")+f"""
<section><div class="wrap split" style="align-items:start"><img src="img/okolie-portrait.jpg" alt="Dr. Jude A. Okolie" style="aspect-ratio:1">
<div><span class="tag">Career profile</span><h2>Education</h2><ul class="list"><li><b>Ph.D., Chemical Engineering</b> · University of Saskatchewan<br><span class="muted">Thesis: Supercritical water gasification of lignocellulosic biomass materials for hydrogen production.</span></li><li><b>M.Sc., Materials and Sustainable Energetics</b> · Tallinn University of Technology, Estonia</li><li><b>M.Sc., Petroleum Engineering</b> · Imperial College London</li><li><b>B.Eng., Chemical Engineering</b> · University of Benin, Nigeria</li></ul>
<h2 style="margin-top:36px">Experience</h2><ul class="list"><li><b>Assistant Professor</b>, Bucknell University <span class="muted">· Aug 2024 – present</span></li><li><b>Assistant Professor</b>, University of Oklahoma <span class="muted">· Aug 2022 – Jul 2024</span></li><li><b>Research Engineer</b>, Saskatchewan Research Council <span class="muted">· May 2022 – Aug 2022</span></li><li><b>Faculty</b>, St. Peter's College, Muenster <span class="muted">· Jun 2021 – Jul 2022</span></li><li><b>Postdoctoral Fellow</b>, University of Saskatchewan <span class="muted">· Jun 2021 – Jul 2022</span></li></ul></div></div></section>
<section><div class="wrap cols"><div class="prose"><span class="tag">Biography</span><h2>Bio</h2>{abp}</div>
<div><span class="tag">Memberships</span><h2>Professional memberships</h2><ul class="list"><li>American Society for Engineering Education (ASEE)</li><li>Canadian Society for Chemical Engineering (CSChE)</li><li>Association of Professional Engineers and Geoscientists of Saskatchewan (APEGS)</li><li>Nigerian Society of Engineers (NSE)</li></ul>
<h2 style="margin-top:36px">Service</h2><ul class="list"><li>Guest Editor, <em>Fermentation</em></li><li>Reviewer for ACS, Elsevier, RSC, Springer Nature and Wiley journals</li></ul>
<h2 style="margin-top:36px">Profiles</h2><div class="chips">{"".join(ext(t,u,"chip") for t,u in LINKS)}</div></div></div></section>"""
    page("about.html","About Dr. Jude A. Okolie · SETD Research Group","Biography, education and experience of Dr. Jude A. Okolie.",about)

    # CONTACT
    contact=hero("Contact","Get in touch","Prospective students, collaborators and media are welcome to reach out.")+f"""
<section><div class="wrap cols"><div><span class="tag">Contact</span><h2>Dr. Jude A. Okolie</h2><ul class="list"><li><b>Email</b><br><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><b>Address</b><br>Department of Chemical Engineering, Bucknell University<br>One Dent Drive, Lewisburg, PA 17837</li></ul><div class="chips" style="margin-top:24px">{"".join(ext(t,u,"chip") for t,u in LINKS)}</div></div>
<div class="callout"><span class="tag">Join us</span><h2 style="font-size:clamp(26px,3vw,36px)">Interested in joining SETD?</h2><p class="muted">We welcome inquiries from Bucknell undergraduates looking for research experience, prospective graduate students and postdocs, and industry and academic collaborators. Send a short note on your research interests along with your CV.</p><a class="btn pri" href="mailto:{EMAIL}?subject=SETD%20research%20inquiry">Email Dr. Okolie</a></div></div></section>"""
    page("contact.html","Contact · SETD Research Group","Contact Dr. Jude A. Okolie and the SETD Research Group.",contact)

build()
print("built", sorted(p.name for p in OUT.glob("*.html")))
