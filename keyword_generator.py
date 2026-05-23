import os, json, re, requests

CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL   = "claude-haiku-4-5-20251001"

DB = {
    "anther":["anther","pollen sac","pollen producer","microsporangium","male floral organ","stamen tip"],
    "stigma":["stigma","pollen receptor","pistil tip","sticky tip","female receptor","style tip"],
    "style":["style","pistil style","floral style","ovary neck","stigma stalk"],
    "ovary":["ovary","flower ovary","seed case","carpel base","fruit precursor","gynoecium base"],
    "ovule":["ovule","egg cell","female gamete","seed precursor","embryo sac"],
    "petal":["petal","flower petal","corolla","floral leaf"],
    "sepal":["sepal","calyx leaf","flower sepal","outer floral leaf"],
    "stamen":["stamen","male organ","microsporophyll","male reproductive part","pollen organ"],
    "pistil":["pistil","female organ","gynoecium","carpel","female reproductive part"],
    "filament":["filament","stamen stalk","anther stalk","stamen filament"],
    "pollen":["pollen","pollen grain","male gamete","microspore","pollen dust"],
    "pollengrain":["pollen grain","pollen","male gamete","microspore"],
    "pollentubes":["pollen tubes","pollen tube","fertilisation tube","germination tube"],
    "polarnuclei":["polar nuclei","polar nucleus","central cell nuclei","endosperm mother nuclei"],
    "spermnuclei":["sperm nuclei","sperm nucleus","male gamete nuclei","generative nuclei"],
    "eggnucleus":["egg nucleus","female nucleus","egg cell nucleus","ovum nucleus"],
    "seed":["seed","plant seed","fertilised ovule","grain","embryo seed"],
    "seedling":["seedling","young plant","germinated seed","sprout","plantlet"],
    "embryo":["embryo","plant embryo","developing plant","early plant","zygote stage"],
    "endosperm":["endosperm","seed food","seed nutrition","seed storage tissue","albumen"],
    "zygote":["zygote","fertilised egg","fertilized egg","first cell","diploid cell"],
    "coat":["coat","seed coat","testa","outer covering","seed shell","integument"],
    "testa":["testa","seed coat","coat","outer covering","seed shell"],
    "fruit":["fruit","ripened ovary","mature ovary","seed container"],
    "receptacle":["receptacle","flower base","torus","floral axis"],
    "peduncle":["peduncle","flower stalk","floral stalk"],
    "lamina":["lamina","leaf blade","leaf lamina","blade","leaf plate"],
    "petiole":["petiole","leaf stalk","stem stalk","leaf stem"],
    "midvein":["midvein","midrib","central vein","main vein","primary vein","mid rib"],
    "secondaryvein":["secondary vein","lateral vein","leaf vein","side vein","branch vein"],
    "leafmargin":["leaf margin","leaf edge","leaf border","margin"],
    "leafbase":["leaf base","base of leaf"],
    "apex":["apex","leaf tip","tip","leaf apex","apical"],
    "bud":["bud","axillary bud","leaf bud","terminal bud","lateral bud"],
    "stem":["stem","plant stem","main stem","axis","stalk"],
    "stipule":["stipule","leaf stipule"],
    "stomata":["stomata","stoma","leaf pore","gas exchange pore","leaf opening"],
    "xylem":["xylem","water vessel","water transport tube","water conducting tissue"],
    "phloem":["phloem","food transport","sieve tube","food conducting tissue","sugar transport"],
    "chloroplast":["chloroplast","green plastid","photosynthesis organelle","chlorophyll container"],
    "chloroplasts":["chloroplasts","chloroplast","green plastids","photosynthesis organelles"],
    "chlorophyll":["chlorophyll","green pigment","leaf pigment","photosynthetic pigment","chlorophyl"],
    "thylakoid":["thylakoid","thylakoid membrane","light reaction site","photosynthetic membrane","granum disc"],
    "grana":["grana","granum","thylakoid stack","stack of thylakoid","chloroplast grana"],
    "stroma":["stroma","chloroplast stroma","dark reaction site","calvin cycle site","chloroplast fluid"],
    "calvincycle":["calvin cycle","dark reaction","light independent reaction","C3 cycle","carbon fixation","calvin benson cycle"],
    "lightenergy":["light energy","solar energy","sunlight","photon energy","radiant energy","sun energy"],
    "sunlight":["sunlight","light energy","solar energy","sun light","sun rays","radiant energy"],
    "water":["water","H2O","dihydrogen oxide","dihydrogen monoxide","aqua","pure water","oxidane","fresh water"],
    "h2o":["H2O","water","dihydrogen oxide","dihydrogen monoxide","aqua","pure water","oxidane"],
    "carbondioxide":["carbon dioxide","CO2","carbonic anhydride","carbon di oxide"],
    "co2":["CO2","carbon dioxide","carbonic anhydride","carbon di oxide"],
    "oxygen":["oxygen","O2","dioxygen","molecular oxygen","atmospheric oxygen"],
    "o2":["O2","oxygen","dioxygen","molecular oxygen"],
    "glucose":["glucose","C6H12O6","blood sugar","dextrose","grape sugar","simple sugar","monosaccharide"],
    "sugar":["sugar","glucose","CH2O","carbohydrate","saccharide","simple sugar"],
    "ch2o":["CH2O","sugar","formaldehyde","carbohydrate unit"],
    "atp":["ATP","adenosine triphosphate","energy molecule","energy currency","cellular energy"],
    "adp":["ADP","adenosine diphosphate","low energy molecule"],
    "nadp":["NADP+","NADP","nicotinamide adenine dinucleotide phosphate","electron carrier"],
    "nadph":["NADPH","reduced NADP","electron donor","reducing agent"],
    "nucleus":["nucleus","cell nucleus","control center","nuclear body","karyosome"],
    "nucleolus":["nucleolus","nucleole","ribosome factory","RNA producer","nuclear body"],
    "mitochondria":["mitochondria","mitochondrion","powerhouse","powerhouse of cell","energy organelle"],
    "mitochondrion":["mitochondrion","mitochondria","powerhouse","powerhouse of cell","energy organelle"],
    "ribosome":["ribosome","ribosomes","protein synthesizer","protein maker","translation site"],
    "ribosomes":["ribosomes","ribosome","protein synthesizer","protein maker","translation site"],
    "cellmembrane":["cell membrane","plasma membrane","plasmalemma","cell surface membrane","phospholipid bilayer"],
    "plasmamembrane":["plasma membrane","cell membrane","plasmalemma","cell surface membrane","phospholipid bilayer"],
    "cellwall":["cell wall","plant cell wall","rigid outer layer","cellulose wall"],
    "vacuole":["vacuole","central vacuole","storage organelle","cell sap bag"],
    "golgi":["golgi","golgi apparatus","golgi body","golgi complex","secretory organelle"],
    "golgiapparatus":["golgi apparatus","golgi body","golgi complex","golgi","secretory organelle"],
    "golgibody":["golgi body","golgi apparatus","golgi complex","golgi","secretory organelle"],
    "endoplasmic":["endoplasmic reticulum","ER","rough ER","smooth ER"],
    "reticulum":["endoplasmic reticulum","ER","rough ER","smooth ER"],
    "endoplasmicreticulum":["endoplasmic reticulum","ER","rough ER","smooth ER","protein transport network"],
    "cytoplasm":["cytoplasm","cytosol","cell fluid","intracellular fluid","cell interior"],
    "peroxisome":["peroxisome","microbody","hydrogen peroxide organelle"],
    "lysosome":["lysosome","digestive organelle","waste recycler","cell stomach"],
    "centrosome":["centrosome","cell centre","microtubule organizer","MTOC"],
    "microtubules":["microtubules","microtubule","cytoskeleton","cell skeleton","tubulin fibers"],
    "amyloplast":["amyloplast","starch storage organelle","starch plastid","leucoplast"],
    "cornea":["cornea","eye cornea","corneal layer","transparent front layer","front of eye"],
    "retina":["retina","retinal layer","eye retina","light sensitive layer","photoreceptor layer"],
    "opticnerve":["optic nerve","visual nerve","eye nerve","cranial nerve 2","CN II","optic tract"],
    "lens":["lens","eye lens","crystalline lens","ocular lens","biconvex lens"],
    "iris":["iris","eye iris","coloured part of eye","iris ring","eye colour"],
    "pupil":["pupil","eye pupil","pupillary opening","dark centre of eye"],
    "sclera":["sclera","white of eye","sclerotic layer","eye white"],
    "choroid":["choroid","choroid layer","vascular layer of eye"],
    "conjunctiva":["conjunctiva","conjunctival layer","eye lining"],
    "aqueoushumour":["aqueous humour","aqueous humor","aqueous fluid","anterior fluid"],
    "vitreoushumour":["vitreous humour","vitreous humor","vitreous body","vitreous gel"],
    "leftatrium":["left atrium","LA","upper left chamber","left upper chamber","left auricle"],
    "rightatrium":["right atrium","RA","upper right chamber","right upper chamber","right auricle"],
    "leftventricle":["left ventricle","LV","lower left chamber","left lower chamber"],
    "rightventricle":["right ventricle","RV","lower right chamber","right lower chamber"],
    "aorta":["aorta","main artery","largest artery","aortic arch"],
    "pulmonaryartery":["pulmonary artery","PA","lung artery","pulmonic artery"],
    "pulmonaryvein":["pulmonary vein","PV","lung vein"],
    "venacava":["vena cava","IVC","SVC","inferior vena cava","superior vena cava"],
    "mitralvalve":["mitral valve","MV","bicuspid valve","left AV valve"],
    "tricuspidvalve":["tricuspid valve","TV","right AV valve","three-leaflet valve"],
    "septum":["septum","heart wall","cardiac septum","dividing wall","interventricular septum"],
    "dendrite":["dendrite","dendrites","nerve dendrite","dendritic branch","receptor branch"],
    "axon":["axon","nerve fiber","nerve fibre","axonal fiber","nerve thread"],
    "cellbody":["cell body","soma","cyton","neuron body","perikaryon"],
    "myelinsheath":["myelin sheath","myelin","nerve sheath","fatty sheath","medullary sheath"],
    "synapse":["synapse","synaptic junction","synaptic gap","synaptic cleft","nerve junction"],
    "axonterminal":["axon terminal","synaptic knob","terminal button","nerve ending"],
    "trachea":["trachea","windpipe","wind pipe","air pipe","breathing tube","airway","throat tube"],
    "esophagus":["esophagus","oesophagus","food pipe","gullet","food tube","alimentary canal"],
    "alveoli":["alveoli","alveolus","air sac","lung sac","gas exchange sac"],
    "bronchus":["bronchus","bronchi","bronchial tube","airway branch"],
    "bronchiole":["bronchiole","small bronchi","small airway"],
    "diaphragm":["diaphragm","breathing muscle","respiratory muscle"],
    "larynx":["larynx","voice box","voice organ","voicebox"],
    "pharynx":["pharynx","throat","throat cavity"],
    "lung":["lung","lungs","respiratory organ","breathing organ"],
    "stomach":["stomach","gastric organ","gastric sac","tummy"],
    "smallintestine":["small intestine","ileum","jejunum","duodenum","small bowel"],
    "largeintestine":["large intestine","colon","large bowel","rectum","cecum"],
    "liver":["liver","hepatic organ","hepatic gland"],
    "pancreas":["pancreas","pancreatic gland"],
    "outermembrane":["outer membrane","external membrane","outermost layer","outer envelope","external layer"],
    "innermembrane":["inner membrane","internal membrane","inner envelope","internal layer"],
    "intermembranespace":["intermembrane space","intermembrane gap","space between membranes"],
    "nacl":["NaCl","sodium chloride","common salt","table salt","salt"],
    "hcl":["HCl","hydrochloric acid","muriatic acid","hydrogen chloride"],
    "h2so4":["H2SO4","sulfuric acid","sulphuric acid","oil of vitriol"],
    "naoh":["NaOH","sodium hydroxide","caustic soda","lye"],
    "nh3":["NH3","ammonia","ammonium hydroxide"],
    "dna":["DNA","deoxyribonucleic acid","genetic material","double helix","genome"],
    "rna":["RNA","ribonucleic acid","messenger RNA","mRNA","genetic messenger"],
    "enzyme":["enzyme","biological catalyst","protein catalyst","biocatalyst"],
    "protein":["protein","polypeptide","amino acid chain","biological macromolecule"],
    "atom":["atom","atomic particle","basic unit of element","smallest particle"],
    "molecule":["molecule","molecular unit","compound particle","bonded atoms"],
    "resistance":["resistance","electrical resistance","ohms","R","opposition to current"],
    "voltage":["voltage","potential difference","PD","EMF","electromotive force","volts","V"],
    "current":["current","electric current","amperes","amps","A","flow of charge"],
    "frequency":["frequency","Hz","hertz","cycles per second","wave frequency","f"],
    "wavelength":["wavelength","wave length","distance per cycle","lambda"],
    "force":["force","F","newtons","N","push or pull","net force"],
    "acceleration":["acceleration","a","rate of change of velocity","speeding up"],
    "velocity":["velocity","v","speed with direction","m/s","vector speed"],
    "momentum":["momentum","p","mass times velocity","inertia of motion"],
    "energy":["energy","E","joules","J","capacity to do work"],
    "power":["power","P","watts","W","rate of energy transfer"],
    "gravity":["gravity","g","gravitational force","weight force"],
    "pressure":["pressure","P","pascals","Pa","force per area"],
    "density":["density","mass per volume","kg/m3","g/cm3"],
    "temperature":["temperature","T","heat level","degrees","kelvin","K"],
    "mass":["mass","m","kg","kilograms","amount of matter"],
    "weight":["weight","W","gravitational force","newtons","N"],
    "speed":["speed","v","distance per time","m/s","rate of motion"],
    "radius":["radius","r","circle radius","half diameter","distance from centre"],
    "diameter":["diameter","d","full width","twice radius","2r","circle diameter"],
    "circumference":["circumference","perimeter of circle","2 pi r","circle perimeter"],
    "pi":["pi","3.14159","3.14","ratio circumference to diameter"],
    "area":["area","A","surface area","square units","space inside"],
    "volume":["volume","V","cubic units","space inside 3D","capacity"],
    "gradient":["gradient","slope","rate of change","steepness","m"],
    "hypotenuse":["hypotenuse","longest side","opposite side","diagonal of right triangle"],
    "mean":["mean","average","arithmetic mean","sum divided by count"],
    "median":["median","middle value","central value"],
    "mode":["mode","most frequent value","most common value"],
}


def _key(text):
    return re.sub(r'[^a-z0-9]', '', text.lower().strip())


def _dict_lookup(label):
    k = _key(label)
    if k in DB:
        return list(DB[k])
    for dk, vals in DB.items():
        if dk in k or (len(k) > 3 and k in dk):
            return list(vals)
    return []


def _api_lookup(label, diagram_name=""):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return []
    context = f" in a '{diagram_name}' diagram" if diagram_name else ""
    prompt  = (
        f'For science label "{label}"{context} list synonyms, alternate names, '
        f'common names, abbreviations, chemical formulas. '
        f'Return ONLY a JSON array of strings, minimum 6, no explanation.'
    )
    try:
        r = requests.post(
            CLAUDE_API_URL,
            headers={"Content-Type":"application/json",
                     "x-api-key":api_key,
                     "anthropic-version":"2023-06-01"},
            json={"model":CLAUDE_MODEL,"max_tokens":300,
                  "messages":[{"role":"user","content":prompt}]},
            timeout=12
        )
        if r.status_code != 200:
            return []
        text = r.json()["content"][0]["text"].strip()
        text = text.replace("```json","").replace("```","").strip()
        kws  = json.loads(text)
        return [str(k).strip() for k in kws if str(k).strip()] if isinstance(kws, list) else []
    except Exception:
        return []


def generate_related_words(label, diagram_name=""):
    original = label.strip()
    result   = set()

    result.update(_dict_lookup(original))

    if len(result) < 4:
        result.update(_api_lookup(original, diagram_name))

    result.add(original)

    if len(result) <= 1:
        result.add(original.lower())
        words = original.split()
        if len(words) > 1:
            result.add("".join(words).lower())

    return sorted(list(result), key=lambda x: x.lower())
