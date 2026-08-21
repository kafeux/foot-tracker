import json
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

URL = "https://matchs.tv/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9"
}

def get_paris_offset():
    # Détection automatique du décalage France -> Côte d'Ivoire (UTC+2 en été, UTC+1 en hiver)
    now = datetime.now(ZoneInfo("Europe/Paris"))
    return int(now.utcoffset().total_seconds() // 3600)

def convert_to_ci_time(heure_str):
    try:
        h, m = map(int, heure_str.replace('h', ':').split(':'))
        offset = get_paris_offset()
        ci_h = (h - offset) % 24
        return f"{ci_h:02d}:{m:02d}"
    except Exception:
        return heure_str

def clean_text(text):
    return " ".join(text.split()).strip()

def get_matches():
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    full_text = soup.get_text(separator=" ")

    data = {
        "France": [],
        "Angleterre": [],
        "Espagne": [],
        "Italie": [],
        "Allemagne": [],
        "Europe": [],
        "Autres": []
    }

    # Regex de détection des dates
    date_regex = r'(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)'
    parts = re.split(f'({date_regex})', full_text, flags=re.IGNORECASE)
    
    current_date = "Aujourd'hui"
    match_pattern = re.compile(r'([0-2]?[0-9][h:][0-5][0-9])\s+([A-Za-z0-9À-ÿ\.\s\'-]+?\s*-\s*[A-Za-z0-9À-ÿ\.\s\'-]+?)(?=(?:[0-2]?[0-9][h:][0-5][0-9]|$|,|\bJournée\b|\bFinale\b))', re.IGNORECASE)
    
    seen = set()

    for part in parts:
        part_str = part.strip()
        if not part_str:
            continue
        
        # Vérifie s'il s'agit d'une date
        if re.match(f'^{date_regex}$', part_str, re.IGNORECASE):
            current_date = part_str.capitalize()
            continue

        matches_found = match_pattern.findall(part_str)
        for heure, affiche in matches_found:
            affiche_clean = clean_text(affiche)
            affiche_clean = re.sub(r'^[0-2]?[0-9][h:][0-5][0-9]\s*', '', affiche_clean).strip()

            if len(affiche_clean) < 5 or len(affiche_clean) > 80 or " - " not in affiche_clean:
                continue

            heure_ci = convert_to_ci_time(heure)

            key = f"{current_date}_{heure_ci}_{affiche_clean}"
            if key in seen:
                continue
            seen.add(key)

            item = {
                "date": current_date,
                "heure": heure_ci,
                "affiche": affiche_clean
            }

            text_lower = affiche_clean.lower()
            if any(k in text_lower for k in ["ligue 1", "ligue 2", "france", "paris", "marseille", "lyon", "toulouse", "monaco", "nantes", "rennes", "lens", "lille", "nice", "saint-étienne", "strasbourg", "dunkerque", "boulogne", "pau", "sochaux", "red star"]):
                data["France"].append(item)
            elif any(k in text_lower for k in ["premier league", "championship", "fa cup", "arsenal", "chelsea", "liverpool", "manchester", "city", "united", "tottenham", "everton", "newcastle", "villa", "leeds"]):
                data["Angleterre"].append(item)
            elif any(k in text_lower for k in ["liga", "real madrid", "barcelon", "madrid", "séville", "athletic", "betis", "valence", "espanyol", "villarreal"]):
                data["Espagne"].append(item)
            elif any(k in text_lower for k in ["serie a", "juventus", "milan", "inter", "roma", "naples", "lazio", "atalanta", "fiorentina", "torino"]):
                data["Italie"].append(item)
            elif any(k in text_lower for k in ["bundesliga", "bayern", "dortmund", "leverkusen", "leipzig", "stuttgart", "francfort"]):
                data["Allemagne"].append(item)
            elif any(k in text_lower for k in ["champions league", "europa", "conference", "ligue des champions"]):
                data["Europe"].append(item)
            else:
                data["Autres"].append(item)

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    get_matches()
