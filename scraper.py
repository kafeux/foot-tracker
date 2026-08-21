import json
import re
import requests
from bs4 import BeautifulSoup

URL = "https://matchs.tv/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9"
}

def clean_text(text):
    return " ".join(text.split()).strip()

def get_matches():
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    data = {
        "France": [],
        "Angleterre": [],
        "Espagne": [],
        "Italie": [],
        "Allemagne": [],
        "Europe": [],
        "Autres": []
    }

    full_text = soup.get_text(separator=" ")
    
    # Regex pour repérer les changements de jour (ex: "vendredi 21 août", "samedi 22 août", etc.)
    days_regex = r'\b(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+\d{1,2}\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\b'
    
    # Découpage par morceaux avec date ou heure
    pattern = re.compile(rf'({days_regex})|([0-2]?[0-9][h:][0-5][0-9])\s+([A-Za-z0-9À-ÿ\.\s]+?\s*-\s*[A-Za-z0-9À-ÿ\.\s]+?)(?=(?:{days_regex}|[0-2]?[0-9][h:][0-5][0-9]|$|,|\bJournée\b))', re.IGNORECASE)
    
    current_date = "Aujourd'hui"
    seen = set()

    for match in pattern.finditer(full_text):
        text_match = match.group(0).strip()
        
        # Si c'est un en-tête de date
        if re.match(rf'^{days_regex}$', text_match, re.IGNORECASE):
            current_date = text_match.capitalize()
            continue
            
        heure_match = re.search(r'([0-2]?[0-9][h:][0-5][0-9])', text_match)
        if not heure_match or " - " not in text_match:
            continue
            
        heure = heure_match.group(1).replace('h', ':').strip()
        affiche = clean_text(text_match[heure_match.end():])
        
        if len(affiche) < 5 or len(affiche) > 80:
            continue
            
        key = f"{current_date}_{heure}_{affiche}"
        if key in seen:
            continue
        seen.add(key)
        
        item = {
            "date": current_date,
            "heure": heure,
            "affiche": affiche
        }
        
        text_lower = affiche.lower()
        if any(k in text_lower for k in ["ligue 1", "ligue 2", "coupe de france", "france", "national", "paris", "marseille", "lyon", "toulouse", "monaco", "nantes", "rennes", "lens", "lille", "nice", "saint-étienne", "strasbourg", "dunkerque", "boulogne", "pau", "sochaux", "red star"]):
            data["France"].append(item)
        elif any(k in text_lower for k in ["premier league", "championship", "fa cup", "arsenal", "chelsea", "liverpool", "manchester", "city", "united", "tottenham", "everton", "newcastle", "villa", "leeds"]):
            data["Angleterre"].append(item)
        elif any(k in text_lower for k in ["liga", "copa del rey", "real madrid", "barcelon", "madrid", "séville", "athletic", "betis", "valence", "espanyol", "villarreal"]):
            data["Espagne"].append(item)
        elif any(k in text_lower for k in ["serie a", "coppa", "juventus", "milan", "inter", "roma", "naples", "lazio", "atalanta", "fiorentina", "torino"]):
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
