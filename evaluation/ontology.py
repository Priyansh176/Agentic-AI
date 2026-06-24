import re

DISEASE_CATEGORIES = {
    "respiratory": {
        "asthma exacerbation",
        "community acquired pneumonia",
        "copd exacerbation",
        "pulmonary embolism",
        "tuberculosis",
        "influenza",
        "covid-19",
        "bronchitis",
        "common cold",
        "pneumothorax",
        "sinusitis",
        "lung cancer",
    },

    "cardiovascular": {
        "acute coronary syndrome",
        "heart failure exacerbation",
        "atrial fibrillation",
        "hypertensive emergency",
        "deep vein thrombosis",
        "aortic dissection",
        "supraventricular tachycardia",
        "pneumothorax",
    },

    "neurological": {
        "ischemic stroke",
        "migraine",
        "seizure disorder",
        "meningitis",
        "parkinson disease",
        "subarachnoid hemorrhage",
        "encephalitis",
        "essential tremor",
        "drug-induced parkinsonism",
        "normal pressure hydrocephalus",
        "tension headache",
        "syncope",
    },

    "endocrine": {
        "diabetic ketoacidosis",
        "hypothyroidism",
        "hyperthyroidism",
        "addison disease",
        "cushing syndrome",
        "hypoglycemia",
        "hyperosmolar state",
        "pheochromocytoma",
        "metabolic syndrome",
        "adrenal crisis",
    },

    "infectious": {
        "sepsis",
        "urinary tract infection",
        "cellulitis",
        "fungal infection",
        "chronic infection",
        "abscess",
    },

    "gastrointestinal": {
        "acute appendicitis",
        "gastroesophageal reflux disease",
        "peptic ulcer disease",
        "acute pancreatitis",
        "inflammatory bowel disease flare",
        "gastritis",
        "gastroenteritis",
        "cholecystitis",
        "esophagitis",
        "irritable bowel syndrome",
        "infectious colitis",
        "malabsorption",
        "liver disease",
        "colon cancer",
    },

    "dermatological": {
        "atopic dermatitis",
        "psoriasis",
        "herpes zoster",
        "melanoma",
        "scabies",
        "contact dermatitis",
        "seborrheic dermatitis",
        "seborrheic keratosis",
        "basal cell carcinoma",
        "benign nevus",
        "bedbug bites",
    },

    "psychiatric": {
        "major depressive disorder",
        "generalized anxiety disorder",
        "bipolar disorder",
        "post traumatic stress disorder",
        "anorexia nervosa",
        "panic disorder",
        "panic attack",
        "adhd",
        "acute stress disorder",
        "grief reaction",
        "substance-induced mood disorder",
    },

    "renal": {
        "acute kidney injury",
        "chronic kidney disease",
        "kidney stone",
        "pyelonephritis",
        "nephrotic syndrome",
        "renal failure",
        "urinary obstruction",
    },

    "musculoskeletal": {
        "osteoarthritis",
        "rheumatoid arthritis",
        "gout",
        "osteoporosis",
        "septic arthritis",
        "muscle strain",
        "baker cyst",
        "pseudogout",
        "viral arthritis",
        "osteomalacia",
    },

    "oncological_hematologic": {
        "anemia",
        "lung cancer",
        "colon cancer",
        "multiple myeloma",
        "metastatic bone disease",
        "melanoma",
        "basal cell carcinoma",
    },

    "genitourinary": {
        "pelvic inflammatory disease",
        "vaginitis",
        "polycystic ovary syndrome",
        "ovarian torsion",
        "urinary obstruction",
        "urinary tract infection",
        "pyelonephritis",
    },

    "general_nonspecific": {
        "dehydration",
        "syncope",
        "chronic infection",
        "abscess",
        "bedbug bites",
        "fungal infection",
        "muscle strain",
    },
}

DIAGNOSIS_SYNONYMS = {
    "asthma exacerbation": {
        "acute asthma exacerbation",
        "asthma attack",
        "asthma flare",
        "acute asthma",
    },

    "community acquired pneumonia": {
        "cap",
        "pneumonia",
        "bacterial pneumonia",
    },

    "copd exacerbation": {
        "acute copd exacerbation",
        "copd flare",
        "copd attack",
    },

    "pulmonary embolism": {
        "pe",
        "lung embolism",
    },

    "tuberculosis": {
        "tb",
        "pulmonary tuberculosis",
    },

    "acute coronary syndrome": {
        "acs",
        "heart attack",
        "myocardial infarction",
        "mi",
        "stemi",
        "nstemi",
    },

    "heart failure exacerbation": {
        "heart failure",
        "congestive heart failure",
        "chf",
        "acute decompensated heart failure",
    },

    "atrial fibrillation": {
        "af",
        "afib",
        "a fib",
    },

    "hypertensive emergency": {
        "malignant hypertension",
    },

    "deep vein thrombosis": {
        "dvt",
    },

    "ischemic stroke": {
        "stroke",
        "cerebral infarction",
        "brain infarction",
    },

    "migraine": {
        "migraine headache",
        "migraine aura",
    },

    "seizure disorder": {
        "epilepsy",
        "seizure",
    },

    "meningitis": {
        "bacterial meningitis",
        "viral meningitis",
    },

    "parkinson disease": {
        "parkinsons disease",
        "pd",
    },

    "diabetic ketoacidosis": {
        "dka",
    },

    "hypothyroidism": {
        "underactive thyroid",
    },

    "hyperthyroidism": {
        "overactive thyroid",
        "thyrotoxicosis",
    },

    "addison disease": {
        "primary adrenal insufficiency",
    },

    "cushing syndrome": {
        "cushings syndrome",
    },

    "influenza": {
        "flu",
    },

    "covid-19": {
        "covid",
        "coronavirus infection",
        "sars cov 2 infection",
    },

    "sepsis": {
        "septicemia",
        "bloodstream infection",
    },

    "urinary tract infection": {
        "uti",
    },

    "cellulitis": {
        "skin infection",
    },

    "acute appendicitis": {
        "appendicitis",
    },

    "gastroesophageal reflux disease": {
        "gerd",
        "acid reflux",
    },

    "peptic ulcer disease": {
        "pud",
        "gastric ulcer",
    },

    "acute pancreatitis": {
        "pancreatitis",
    },

    "inflammatory bowel disease flare": {
        "ibd flare",
        "crohn flare",
        "ulcerative colitis flare",
    },

    "atopic dermatitis": {
        "eczema",
    },

    "psoriasis": {
        "plaque psoriasis",
    },

    "herpes zoster": {
        "shingles",
    },

    "major depressive disorder": {
        "depression",
        "mdd",
        "major depression",
        "clinical depression",
    },

    "generalized anxiety disorder": {
        "gad",
        "anxiety disorder",
    },

    "bipolar disorder": {
        "bipolar",
    },

    "post traumatic stress disorder": {
        "ptsd",
    },

    "anorexia nervosa": {
        "anorexia",
    },

    "acute kidney injury": {
        "aki",
    },

    "chronic kidney disease": {
        "ckd",
    },

    "kidney stone": {
        "renal stone",
        "nephrolithiasis",
    },

    "pyelonephritis": {
        "kidney infection",
    },

    "nephrotic syndrome": {
        "nephrosis",
    },

    "osteoarthritis": {
        "oa",
    },

    "rheumatoid arthritis": {
        "ra",
        "rheumatoid arthritis flare",
    },

    "gout": {
        "gout flare",
    },

    "osteoporosis": {
        "bone loss disease",
    },

    "septic arthritis": {
        "joint infection",
    },

    "melanoma": {
        "malignant melanoma",
        "skin cancer",
    },

    "scabies": {
        "scabies infestation",
    },

    "bronchitis": {
        "acute bronchitis",
    },

    "common cold": {
        "upper respiratory infection",
        "uri",
        "viral uri",
    },

    "pneumothorax": {
        "collapsed lung",
    },

    "sinusitis": {
        "acute sinusitis",
        "rhinosinusitis",
    },

    "lung cancer": {
        "pulmonary malignancy",
        "bronchogenic carcinoma",
    },

    "aortic dissection": {
        "dissecting aneurysm",
    },

    "supraventricular tachycardia": {
        "svt",
    },

    "subarachnoid hemorrhage": {
        "sah",
        "brain bleed",
    },

    "encephalitis": {
        "viral encephalitis",
    },

    "essential tremor": {
        "benign essential tremor",
    },

    "drug-induced parkinsonism": {
        "medication-induced parkinsonism",
    },

    "normal pressure hydrocephalus": {
        "nph",
    },

    "tension headache": {
        "tension-type headache",
    },

    "syncope": {
        "fainting",
        "vasovagal syncope",
    },

    "hypoglycemia": {
        "low blood sugar",
    },

    "hyperosmolar state": {
        "hyperosmolar hyperglycemic state",
        "hhs",
    },

    "pheochromocytoma": {
        "pheo",
    },

    "metabolic syndrome": {
        "syndrome x",
    },

    "adrenal crisis": {
        "addisonian crisis",
        "acute adrenal insufficiency",
    },

    "fungal infection": {
        "mycosis",
        "fungal skin infection",
    },

    "chronic infection": {
        "persistent infection",
    },

    "abscess": {
        "skin abscess",
        "soft tissue abscess",
    },

    "gastritis": {
        "acute gastritis",
    },

    "gastroenteritis": {
        "stomach flu",
        "viral gastroenteritis",
    },

    "cholecystitis": {
        "gallbladder inflammation",
        "acute cholecystitis",
    },

    "esophagitis": {
        "acute esophagitis",
    },

    "irritable bowel syndrome": {
        "ibs",
    },

    "infectious colitis": {
        "bacterial colitis",
    },

    "malabsorption": {
        "malabsorption syndrome",
    },

    "liver disease": {
        "hepatic disease",
        "liver dysfunction",
    },

    "colon cancer": {
        "colorectal cancer",
    },

    "contact dermatitis": {
        "allergic contact dermatitis",
        "irritant contact dermatitis",
    },

    "seborrheic dermatitis": {
        "dandruff dermatitis",
    },

    "seborrheic keratosis": {
        "benign skin growth",
    },

    "basal cell carcinoma": {
        "bcc",
        "skin cancer",
    },

    "benign nevus": {
        "benign mole",
    },

    "bedbug bites": {
        "bed bug bites",
    },

    "panic disorder": {
        "panic attacks disorder",
    },

    "panic attack": {
        "anxiety attack",
    },

    "adhd": {
        "attention deficit hyperactivity disorder",
    },

    "acute stress disorder": {
        "asd (psychiatric)",
    },

    "grief reaction": {
        "bereavement",
        "normal grief",
    },

    "substance-induced mood disorder": {
        "substance-induced depression",
    },

    "renal failure": {
        "kidney failure",
    },

    "urinary obstruction": {
        "obstructive uropathy",
        "blocked urinary tract",
    },

    "muscle strain": {
        "pulled muscle",
        "musculoskeletal strain",
    },

    "baker cyst": {
        "popliteal cyst",
    },

    "pseudogout": {
        "calcium pyrophosphate deposition disease",
        "cppd",
    },

    "viral arthritis": {
        "reactive arthritis",
    },

    "osteomalacia": {
        "vitamin d deficiency bone disease",
    },

    "anemia": {
        "low hemoglobin",
        "low red blood cell count",
    },

    "multiple myeloma": {
        "plasma cell myeloma",
    },

    "metastatic bone disease": {
        "bone metastases",
    },

    "pelvic inflammatory disease": {
        "pid",
    },

    "vaginitis": {
        "vaginal infection",
    },

    "polycystic ovary syndrome": {
        "pcos",
    },

    "ovarian torsion": {
        "torsed ovary",
    },

    "dehydration": {
        "fluid depletion",
        "volume depletion",
    },

    "allergic rhinitis": {
        "hay fever",
    },

    "herpes simplex": {
        "hsv",
        "cold sore",
    },

    "lupus": {
        "systemic lupus erythematosus",
        "sle",
    },

    "psychogenic episode": {
        "psychogenic non-epileptic seizure",
        "pnes",
    },
}

TREATMENT_CLASSES = {
    "bronchodilator": {
        "albuterol",
        "salbutamol",
        "ipratropium",
        "tiotropium",
        "inhaled bronchodilator",
        "bronchodilator therapy",
        "bronchodilators",
    },

    "corticosteroid": {
        "prednisone",
        "prednisolone",
        "dexamethasone",
        "methylprednisolone",
        "inhaled corticosteroid",
        "systemic corticosteroid",
        "systemic corticosteroids",
        "steroid",
    },

    "antibiotic": {
        "amoxicillin",
        "azithromycin",
        "ceftriaxone",
        "doxycycline",
        "penicillin",
        "antibiotics",
        "antibiotics if infectious signs",
        "antibiotics selected by risk profile",
        "early antibiotics",
        "empiric antibiotics",
        "urgent antibiotics",
        "multi-drug tuberculosis therapy",
    },

    "oxygen therapy": {
        "oxygen support",
        "supplemental oxygen",
        "oxygen if hypoxic",
    },

    "anticoagulation": {
        "heparin",
        "warfarin",
        "apixaban",
        "anticoagulation",
        "anticoagulation assessment",
    },

    "iv fluids": {
        "fluid resuscitation",
        "intravenous fluids",
        "hydration",
        "fluid management",
    },

    "insulin therapy": {
        "insulin",
        "insulin infusion",
    },

    "diuretic": {
        "furosemide",
        "loop diuretic",
        "diuretics",
    },

    "antiviral": {
        "oseltamivir",
        "antiviral therapy",
        "antiviral if high risk",
    },

    "pain control": {
        "analgesia",
        "pain management",
        "acetaminophen",
        "acetaminophen or topical nsaid if safe",
        "ice",
        "antiemetic",
        "triptan if appropriate",
        "nsaid if safe",
        "nsaid bridge if safe",
        "nsaid or colchicine if safe",
    },

    "psychotherapy": {
        "cognitive behavioral therapy",
        "cbt",
        "therapy",
        "trauma-focused psychotherapy",
    },

    "antiplatelet_cardiac": {
        "aspirin if not allergic",
        "antiplatelet therapy if appropriate",
        "nitroglycerin if appropriate",
        "thrombolysis if unstable",
        "beta blocker if appropriate",
        "urgent cardiology evaluation",
        "urgent stroke protocol",
        "controlled iv blood pressure reduction",
        "blood pressure control",
    },

    "supportive_care": {
        "supportive care",
        "bowel rest",
    },

    "referral_followup": {
        "cardiology follow-up",
        "endocrinology follow-up",
        "endocrinology referral",
        "nephrology follow-up",
        "neurology follow-up",
        "gastroenterology follow-up",
        "rheumatology referral",
        "dermatology referral",
        "urgent dermatology referral",
        "psychiatry referral",
        "orthopedic consultation",
        "urology referral if obstructed",
        "icu evaluation",
        "surgical consultation",
        "follow up appointment",
        "follow-up",
    },

    "psychiatric_medication_management": {
        "ssri consideration",
        "mood stabilizer evaluation",
        "antiepileptic medication review",
        "dmard evaluation",
    },

    "hormone_replacement": {
        "levothyroxine",
        "glucocorticoid replacement",
        "mineralocorticoid replacement",
        "antithyroid medication",
        "reduce steroid exposure when safe",
        "dopaminergic therapy evaluation",
        "bisphosphonate evaluation",
        "calcium and vitamin d optimization",
        "diabetes control",
    },

    "topical_dermatologic": {
        "emollients",
        "topical corticosteroid",
        "topical corticosteroid if needed",
        "topical corticosteroids",
        "vitamin d analogs",
        "permethrin treatment",
        "wound care",
    },

    "lifestyle_modification": {
        "diet modification",
        "weight management",
        "salt restriction",
        "trigger avoidance",
        "sleep hygiene",
        "exercise therapy",
        "mobility counseling",
        "avoid exposure to high-risk contacts",
        "treat close contacts",
        "wash bedding",
        "compression therapy if appropriate",
    },

    "procedural_surgical": {
        "joint drainage",
        "appendectomy if confirmed",
        "surgical excision if confirmed",
    },

    "safety_contraindication_adjustment": {
        "avoid nsaids",
        "avoid nsaids or aspirin unless specialist-approved",
        "avoid penicillin-class antibiotics",
        "use contrast precautions or alternative imaging",
        "use pediatric weight-based dosing",
        "monitor geriatric adverse effects",
        "adjust renally cleared medications",
        "confirm pregnancy-safe medication choices",
        "avoid nephrotoxins",
    },

    "gi_treatment": {
        "proton pump inhibitor trial",
        "acid suppression",
        "h. pylori eradication if positive",
        "anti-inflammatory therapy",
    },

    "miscellaneous_management": {
        "public health notification",
        "isolation",
        "isolation precautions",
        "source control",
        "treat underlying cause",
        "stress-dose education",
        "urate-lowering discussion after flare",
        "physical therapy",
        "rehabilitation",
        "nutritional rehabilitation",
        "dose adjustment by labs",
        "thyroid monitoring",
        "sleep support",
        "monitor end-organ damage",
        "monitor medical stability",
        "optimize heart failure medications",
        "follow culture results",
        "electrolyte correction",
        "elevation of affected limb",
        "hospitalization if severe",
        "staging if malignant",
    },

    "safety_risk_treatment": {
        "safety assessment",
        "safety counseling",
        "safety planning if needed",
        "fall prevention",
    },

    "rate_control": {
        "rate control",
        "heart rate control",
        "beta blocker",
        "metoprolol",
        "atenolol",
        "bisoprolol",
        "diltiazem",
        "verapamil",
        "digoxin"
    }
}

TEST_CLASSES = {
    "cbc": {
        "complete blood count",
        "cbc",
    },

    "chest xray": {
        "chest x ray",
        "chest radiograph",
        "cxr",
        "chest x-ray",
    },

    "spirometry": {
        "spirometry",
        "pulmonary function test",
        "pft",
        "peak flow",
    },

    "pulse oximetry": {
        "oxygen saturation monitoring",
        "spo2",
    },

    "ecg": {
        "electrocardiogram",
        "ekg",
        "ecg",
    },

    "troponin": {
        "cardiac troponin",
    },

    "mri brain": {
        "brain mri",
    },

    "ct head": {
        "head ct",
        "noncontrast ct head",
    },

    "blood cultures": {
        "culture",
        "blood culture",
        "blood culture if severe",
    },

    "urinalysis": {
        "ua",
    },

    "abdominal imaging": {
        "abdominal ultrasound",
        "ct abdomen",
        "ct abdomen if needed",
        "noncontrast ct abdomen",
        "abdominal ct",
    },

    "renal pelvic ultrasound": {
        "renal ultrasound",
        "leg ultrasound",
        "venous duplex ultrasound",
        "venous ultrasound",
        "pelvic ultrasound",
    },

    "ct angiography": {
        "ct pulmonary angiography",
        "ctpa",
        "cta",
    },

    "arterial blood gas": {
        "abg",
        "blood gas",
    },

    "basic metabolic panel": {
        "electrolytes",
        "bmp",
        "basic metabolic panel",
        "chem panel",
        "comprehensive metabolic panel",
        "cmp",
    },

    "glucose testing": {
        "blood glucose",
        "glucose test",
        "fingerstick glucose",
        "blood sugar",
    },

    "ketone testing": {
        "ketones",
        "urine ketones",
        "blood ketones",
    },

    "renal function panel": {
        "creatinine",
        "egfr",
        "renal function",
        "bun",
        "kidney function tests",
    },

    "inflammatory markers": {
        "esr",
        "crp",
        "c-reactive protein",
        "erythrocyte sedimentation rate",
    },

    "d dimer": {
        "d-dimer",
        "ddimer",
    },

    "natriuretic peptide": {
        "bnp",
        "nt-probnp",
        "brain natriuretic peptide",
    },

    "lipid panel": {
        "lipid panel",
        "cholesterol panel",
    },

    "liver function tests": {
        "liver function tests",
        "lft",
        "lfts",
        "hepatic panel",
    },

    "thyroid panel": {
        "tsh",
        "tsh if indicated",
        "free t4",
        "t3",
        "thyroid antibodies",
        "thyroid function tests",
        "thyroid function tests if indicated",
        "thyroid tests",
    },

    "adrenal cortisol panel": {
        "morning cortisol",
        "acth",
        "acth stimulation",
        "late-night salivary cortisol",
        "dexamethasone suppression",
        "cortisol level",
    },

    "autoimmune rheumatologic panel": {
        "rheumatoid factor",
        "anti-ccp",
        "ana",
        "antinuclear antibody",
    },

    "joint aspiration": {
        "joint aspiration",
        "joint aspiration if uncertain",
        "synovial fluid analysis",
    },

    "biopsy dermatologic exam": {
        "skin biopsy",
        "skin biopsy if uncertain",
        "excisional biopsy",
        "dermoscopy",
        "skin scraping",
        "pcr from lesion if uncertain",
    },

    "infectious disease workup": {
        "sputum afb",
        "sputum culture",
        "tb culture",
        "h. pylori test",
        "rapid influenza test",
        "rapid antigen test",
        "sars-cov-2 pcr",
        "viral pcr",
        "stool studies",
    },

    "mental health screening tools": {
        "phq-9",
        "gad-7",
        "mood disorder questionnaire",
        "ptsd checklist",
        "suicide risk assessment",
        "substance screening",
        "substance use screening",
        "depression screening",
    },

    "neurological workup": {
        "neurologic exam",
        "eeg",
        "lumbar puncture",
    },

    "cardiac imaging": {
        "echocardiogram",
        "echo",
    },

    "bone density": {
        "dexa scan",
        "bone density scan",
    },

    "urine studies": {
        "urine culture",
        "urine albumin",
        "urine protein",
        "pregnancy test",
        "pregnancy test if relevant",
    },

    "nutrition vitamin panel": {
        "nutritional assessment",
        "vitamin d level",
        "calcium level",
    },

    "misc serum studies": {
        "serum albumin",
        "serum uric acid",
        "uric acid",
    },

    "clinical assessment": {
        "clinical exam",
        "clinical evaluation",
        "medication review",
        "allergy evaluation",
        "allergy evaluation if severe",
        "serial blood pressure",
        "imaging if red flags",
        "x-ray if needed",
    },

    "metabolic gi enzymes": {
        "lactate",
        "lipase",
        "upper endoscopy if alarm symptoms",
        "upper endoscopy if indicated",
    },
}

MONITORING_CLASSES = {
    "vital signs": {
        "heart rate",
        "blood pressure",
        "temperature",
        "vitals",
    },

    "oxygen monitoring": {
        "spo2",
        "pulse oximetry",
        "oxygen saturation",
    },

    "symptom monitoring": {
        "symptom diary",
        "monitor symptoms",
        "symptom tracking",
    },

    "medication monitoring": {
        "adverse effects",
        "side effects",
        "drug toxicity",
    },

    "follow up": {
        "follow-up",
        "follow up appointment",
        "reassessment",
    },
    
    "safety risk monitoring": {
        "suicide risk assessment",
        "safety assessment",
        "safety planning",
        "safety planning if needed",
        "safety counseling",
        "fall prevention",
    },

    "special population monitoring": {
        "monitor geriatric adverse effects",
        "use pediatric weight-based dosing",
        "confirm pregnancy-safe medication choices",
        "adjust renally cleared medications",
    },

    "organ function monitoring": {
        "monitor end-organ damage",
        "monitor medical stability",
        "renal function monitoring",
        "thyroid monitoring",
        "dose adjustment by labs",
    },

    "contraindication monitoring": {
        "avoid nsaids",
        "avoid nsaids or aspirin unless specialist-approved",
        "avoid penicillin-class antibiotics",
        "avoid nephrotoxins",
        "allergy monitoring",
    },
}

def normalize_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    text = " ".join(text.split())

    return text

def canonicalize(term, dictionary):
    term = normalize_text(term)

    for canonical, synonyms in dictionary.items():
        if normalize_text(canonical) == term:
            return canonical
        for synonym in synonyms:
            if normalize_text(synonym) == term:
                return canonical

    return term

def build_reverse_map(dictionary):
    reverse = {}
    for canonical, synonyms in dictionary.items():
        reverse[normalize_text(canonical)] = canonical
        for synonym in synonyms:
            reverse[normalize_text(synonym)] = canonical

    return reverse

def get_disease_category(disease):
    disease = normalize_text(disease)
    for category, diseases in DISEASE_CATEGORIES.items():
        for known in diseases:
            if known in disease:
                return category
            if disease in known:
                return category

    return "unknown"

DIAGNOSIS_MAP = build_reverse_map(DIAGNOSIS_SYNONYMS)
TREATMENT_MAP = build_reverse_map(TREATMENT_CLASSES)
TEST_MAP = build_reverse_map(TEST_CLASSES)
MONITORING_MAP = build_reverse_map(MONITORING_CLASSES)