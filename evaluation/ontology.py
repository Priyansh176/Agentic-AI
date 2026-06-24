import re

DISEASE_CATEGORIES = {

    "respiratory": {
        "asthma exacerbation",
        "community acquired pneumonia",
        "copd exacerbation",
        "pulmonary embolism",
        "tuberculosis",
        "influenza",
        "covid-19"
    },

    "cardiovascular": {
        "acute coronary syndrome",
        "heart failure exacerbation",
        "atrial fibrillation",
        "hypertensive emergency",
        "deep vein thrombosis"
    },

    "neurological": {
        "ischemic stroke",
        "migraine",
        "seizure disorder",
        "meningitis",
        "parkinson disease"
    },

    "endocrine": {
        "diabetic ketoacidosis",
        "hypothyroidism",
        "hyperthyroidism",
        "addison disease",
        "cushing syndrome"
    },

    "infectious": {
        "sepsis",
        "urinary tract infection",
        "cellulitis"
    },

    "gastrointestinal": {
        "acute appendicitis",
        "gastroesophageal reflux disease",
        "peptic ulcer disease",
        "acute pancreatitis",
        "inflammatory bowel disease flare"
    },

    "dermatological": {
        "atopic dermatitis",
        "psoriasis",
        "herpes zoster"
    },

    "psychiatric": {
        "major depressive disorder",
        "generalized anxiety disorder",
        "bipolar disorder",
        "post traumatic stress disorder",
        "anorexia nervosa"
    },

    "renal": {
        "acute kidney injury",
        "chronic kidney disease",
        "kidney stone",
        "pyelonephritis",
        "nephrotic syndrome"
    },

    "musculoskeletal": {
        "osteoarthritis",
        "rheumatoid arthritis",
        "gout",
        "osteoporosis",
        "septic arthritis"
    }
}

DIAGNOSIS_SYNONYMS = {

    "asthma exacerbation": {
        "acute asthma exacerbation",
        "asthma attack",
        "asthma flare",
        "acute asthma"
    },

    "community acquired pneumonia": {
        "cap",
        "pneumonia",
        "bacterial pneumonia"
    },

    "copd exacerbation": {
        "acute copd exacerbation",
        "copd flare",
        "copd attack"
    },

    "pulmonary embolism": {
        "pe",
        "lung embolism"
    },

    "tuberculosis": {
        "tb",
        "pulmonary tuberculosis"
    },

    "acute coronary syndrome": {
        "acs",
        "heart attack",
        "myocardial infarction",
        "mi",
        "stemi",
        "nstemi"
    },

    "heart failure exacerbation": {
        "heart failure",
        "congestive heart failure",
        "chf",
        "acute decompensated heart failure"
    },

    "atrial fibrillation": {
        "af",
        "afib",
        "a fib"
    },

    "hypertensive emergency": {
        "malignant hypertension"
    },

    "deep vein thrombosis": {
        "dvt"
    },

    "ischemic stroke": {
        "stroke",
        "cerebral infarction",
        "brain infarction"
    },

    "migraine": {
        "migraine headache"
    },

    "seizure disorder": {
        "epilepsy",
        "seizure"
    },

    "meningitis": {
        "bacterial meningitis",
        "viral meningitis"
    },

    "parkinson disease": {
        "parkinsons disease",
        "pd"
    },

    "diabetic ketoacidosis": {
        "dka"
    },

    "hypothyroidism": {
        "underactive thyroid"
    },

    "hyperthyroidism": {
        "overactive thyroid",
        "thyrotoxicosis"
    },

    "addison disease": {
        "primary adrenal insufficiency"
    },

    "cushing syndrome": {
        "cushings syndrome"
    },

    "influenza": {
        "flu"
    },

    "covid-19": {
        "covid",
        "coronavirus infection",
        "sars cov 2 infection"
    },

    "sepsis": {
        "septicemia",
        "bloodstream infection"
    },

    "urinary tract infection": {
        "uti"
    },

    "cellulitis": {
        "skin infection"
    },

    "acute appendicitis": {
        "appendicitis"
    },

    "gastroesophageal reflux disease": {
        "gerd",
        "acid reflux"
    },

    "peptic ulcer disease": {
        "pud",
        "gastric ulcer"
    },

    "acute pancreatitis": {
        "pancreatitis"
    },

    "inflammatory bowel disease flare": {
        "ibd flare",
        "crohn flare",
        "ulcerative colitis flare"
    },

    "atopic dermatitis": {
        "eczema"
    },

    "psoriasis": {
        "plaque psoriasis"
    },

    "herpes zoster": {
        "shingles"
    },

    "major depressive disorder": {
        "depression",
        "mdd"
    },

    "generalized anxiety disorder": {
        "gad",
        "anxiety disorder"
    },

    "bipolar disorder": {
        "bipolar"
    },

    "post traumatic stress disorder": {
        "ptsd"
    },

    "anorexia nervosa": {
        "anorexia"
    },

    "acute kidney injury": {
        "aki"
    },

    "chronic kidney disease": {
        "ckd"
    },

    "kidney stone": {
        "renal stone",
        "nephrolithiasis"
    },

    "pyelonephritis": {
        "kidney infection"
    },

    "nephrotic syndrome": {
        "nephrosis"
    },

    "osteoarthritis": {
        "oa"
    },

    "rheumatoid arthritis": {
        "ra"
    },

    "gout": {
        "gout flare"
    },

    "osteoporosis": {
        "bone loss disease"
    },

    "septic arthritis": {
        "joint infection"
    }
}

TREATMENT_CLASSES = {

    "bronchodilator": {
        "albuterol",
        "salbutamol",
        "ipratropium",
        "tiotropium",
        "inhaled bronchodilator",
        "bronchodilator therapy"
    },

    "corticosteroid": {
        "prednisone",
        "prednisolone",
        "dexamethasone",
        "methylprednisolone",
        "inhaled corticosteroid",
        "systemic corticosteroid",
        "steroid"
    },

    "antibiotic": {
        "amoxicillin",
        "azithromycin",
        "ceftriaxone",
        "doxycycline",
        "penicillin",
        "antibiotics"
    },

    "oxygen therapy": {
        "oxygen support",
        "supplemental oxygen",
        "oxygen if hypoxic"
    },

    "anticoagulation": {
        "heparin",
        "warfarin",
        "apixaban",
        "anticoagulation"
    },

    "iv fluids": {
        "fluid resuscitation",
        "intravenous fluids",
        "hydration"
    },

    "insulin therapy": {
        "insulin",
        "insulin infusion"
    },

    "diuretic": {
        "furosemide",
        "loop diuretic"
    },

    "antiviral": {
        "oseltamivir",
        "antiviral therapy"
    },

    "pain control": {
        "analgesia",
        "pain management",
        "acetaminophen"
    },

    "psychotherapy": {
        "cognitive behavioral therapy",
        "cbt",
        "therapy"
    }
}

TEST_CLASSES = {

    "cbc": {
        "complete blood count",
        "cbc"
    },

    "chest xray": {
        "chest x ray",
        "chest radiograph",
        "cxr"
    },

    "spirometry": {
        "spirometry",
        "pulmonary function test",
        "pft"
    },

    "pulse oximetry": {
        "oxygen saturation monitoring",
        "spo2"
    },

    "ecg": {
        "electrocardiogram",
        "ekg",
        "ecg"
    },

    "troponin": {
        "cardiac troponin"
    },

    "mri brain": {
        "brain mri"
    },

    "ct head": {
        "head ct",
        "noncontrast ct head"
    },

    "blood cultures": {
        "culture",
        "blood culture"
    },

    "urinalysis": {
        "ua"
    }
}

MONITORING_CLASSES = {

    "vital signs": {
        "heart rate",
        "blood pressure",
        "temperature",
        "vitals"
    },

    "oxygen monitoring": {
        "spo2",
        "pulse oximetry",
        "oxygen saturation"
    },

    "symptom monitoring": {
        "symptom diary",
        "monitor symptoms",
        "symptom tracking"
    },

    "medication monitoring": {
        "adverse effects",
        "side effects",
        "drug toxicity"
    },

    "follow up": {
        "follow-up",
        "follow up appointment",
        "reassessment"
    }
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