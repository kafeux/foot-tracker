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

    # On cherche les éléments spécifiques de chaque ligne de match
    # On évite les conteneurs globaux (div/p trop longs)
    match_items = []
    
    for row in soup.find_all(['tr', 'li', 'div']):
        # Ignore les blocs trop longs (paragraphes entiers ou descriptions de page)
        text = " ".join(row.get_text().split())
        if len(text) > 150 or len(text) < 10:
            continue
        
        # Format d'heure type 20h45 ou 20:45
        time_match = re.search(r'\b([0-2]?[0-9][h:][0-5][0-9])\b', text)
        if time_match and any(sep in text.lower() for sep in [" - ", " vs ", " contre "]):
            # On vérifie qu'on ne prend pas un conteneur parent qui englobe plusieurs sous-éléments
            if len(row.find_all(['tr', 'li'])) > 0:
                continue
            
            heure = time_match.group(1).replace('h', ':')
            match_items.append((heure, text))

    seen = set()
    for heure, text in match_items:
        if text in seen:
            continue
        seen.add(text)
        
        item = {
            "heure": heure,
            "description": text
        }
        
        text_lower = text.lower()
        if any(k in text_lower for k in ["ligue 1", "ligue 2", "coupe de france", "france", "national", "paris", "marseille", "lyon", "toulouse"]):
            data["France"].append(item)
        elif any(k in text_lower for k in ["premier league", "fa cup", "championship", "arsenal", "chelsea", "liverpool", "city", "united"]):
            data["Angleterre"].append(item)
        elif any(k in text_lower for k in ["liga", "copa del rey", "real madrid", "barcelon", "madrid", "séville", "athletic"]):
            data["Espagne"].append(item)
        elif any(k in text_lower for k in ["serie a", "coppa", "juventus", "milan", "inter", "roma", "naples"]):
            data["Italie"].append(item)
        elif any(k in text_lower for k in ["bundesliga", "bayern", "dortmund", "leverkusen", "leipzig"]):
            data["Allemagne"].append(item)
        elif any(k in text_lower for k in ["champions league", "europa", "conference", "ligue des champions"]):
            data["Europe"].append(item)
        else:
            data["Autres"].append(item)

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    get_matches()
