import pandas as pd
import re


MEASURE_PATTERNS = [
    r"\d+MM", r"\d+CM", r"\d+M", r"\d+V", r"\d+W",
    r"\d+AH", r"\d+PCS?", r"\d+PZS?", r"\d+PK",
    r"\d+KG", r"\d+G", r"\d+ML", r"\d+L"
]

NOISE_WORDS = {
    "TOTAL","SUPER","INDUSTRIAL","USO","AGRICOLA",
    "INCL","INCLUYE","SET","KIT","PACK","PAQUETE",
    "CON","PARA","DE","DEL","LOS","LAS","THE",
    "AND","WITH"
}


KEY_TERMS = {
    "DESTORNILLADOR": "SCREWDRIVER",
    "DISCO": "DISC",
    "CARGADOR": "CHARGER",
    "BOMBA": "PUMP",
    "MOTOSIERRA": "CHAINSAW",
    "TALADRO": "DRILL",
    "REACTIVO": "LAB REAGENT",
    "VITAMINA": "VITAMIN",
    "FORMULA": "FORMULA",
    "SIMILAC": "INFANT FORMULA",
}


def remove_measurements(text: str) -> str:
    for pat in MEASURE_PATTERNS:
        text = re.sub(pat, " ", text)
    return text


def normalize_terms(words):
    out = []
    for w in words:
        if w in KEY_TERMS:
            out.append(KEY_TERMS[w])
        elif w not in NOISE_WORDS and len(w) > 2:
            out.append(w)
    return out


def shorten_product(text: str):

    if not isinstance(text, str):
        return text

    t = text.upper()
    t = re.sub(r"[^\w\s]", " ", t)

    t = remove_measurements(t)

    words = t.split()
    words = normalize_terms(words)

    return " ".join(words[:5])


def normalize_product_details(series: pd.Series) -> pd.Series:
    return series.apply(shorten_product)
