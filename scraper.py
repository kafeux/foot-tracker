import json
import re
import requests
from bs4 import BeautifulSoup

URL = "https://matchs.tv/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9"
}

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

    # Matchs.tv organise généralement les rencontres sous forme de lignes / blocs avec du texte
    # On recherche les éléments contenant des heures au format HH:MM ou HHhMM
    time_pattern = re.compile(r'\b([0-2]?[0-9][h:][0-5][0-9])\b')
    
    # Récupération de tous les conteneurs ou lignes de liste/table
    elements = soup.find_all(['tr', 'li', 'div', 'p'])
    
    seen = set()
    for el in elements:
        text = " ".join(el.get_text().split())
        if not text:
            continue
            
        time_match = time_pattern.search(text)
        # On vérifie si la ligne contient une heure et un séparateur d'équipes classique (vs, -, /)
        if time_match and any(sep in text.lower() for sep in [" - ", " vs ", " contre "]):
            if text in seen:
                continue
            seen.add(text)
            
            heure = time_match.group(1).replace('h', ':')
            text_lower = text.lower()
            
            # Extraction sommaire des infos de la ligne
            match_item = {
                "heure": heure,
                "description": text
            }
            
            if any(k in text_lower for k in ["ligue 1", "ligue 2", "coupe de france", "france", "national"]):
                data["France"].append(match_item)
            elif any(k in text_lower for k in ["premier league", "fa cup", "angleterre", "championship", "efl"]):
                data["Angleterre"].append(match_item)
            elif any(k in text_lower for k in ["liga", "espagne", "copa del rey"]):
                data["Espagne"].append(match_item)
            elif any(k in text_lower for k in ["serie a", "italie", "coppa"]):
                data["Italie"].append(match_item)
            elif any(k in text_lower for k in ["bundesliga", "allemagne"]):
                data["Allemagne"].append(match_item)
            elif any(k in text_lower for k in ["champions league", "europa", "conference", "ligue des champions"]):
                data["Europe"].append(match_item)
            else:
                data["Autres"].append(match_item)

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    get_matches()
