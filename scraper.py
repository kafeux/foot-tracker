import json
import requests
from bs4 import BeautifulSoup

URL = "https://matchs.tv/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_text(text):
    return " ".join(text.split()).strip() if text else ""

def get_matches():
    response = requests.get(URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Structure de sortie classée par pays
    data = {
        "France": [],
        "Angleterre": [],
        "Espagne": [],
        "Italie": [],
        "Allemagne": [],
        "Europe": [],
        "Autres": []
    }

    # Sélecteur des lignes de matchs sur matchs.tv
    rows = soup.select(".match, tr.match, li.match, div[class*='match']")
    
    for row in rows:
        heure_el = row.select_one(".heure, .time, [class*='hour']")
        equipes_el = row.select_one(".affiche, .teams, [class*='title'], [class*='teams']")
        chaine_el = row.select_one(".chaine, .tv, [class*='channel']")
        compet_el = row.select_one(".competition, [class*='compet']")
        
        heure = clean_text(heure_el.text) if heure_el else ""
        affiche = clean_text(equipes_el.text) if equipes_el else clean_text(row.text)
        chaine = clean_text(chaine_el.text) if chaine_el else "Non renseigné"
        compet = clean_text(compet_el.text).lower() if compet_el else ""
        
        if not affiche or not heure:
            continue
            
        match_item = {
            "heure": heure,
            "affiche": affiche,
            "chaine": chaine,
            "competition": compet_el.text.strip() if compet_el else ""
        }
        
        # Tri automatique par pays
        compet_lower = compet.lower()
        if any(k in compet_lower for k in ["ligue 1", "ligue 2", "coupe de france", "france"]):
            data["France"].append(match_item)
        elif any(k in compet_lower for k in ["premier league", "fa cup", "angleterre", "championship"]):
            data["Angleterre"].append(match_item)
        elif any(k in compet_lower for k in ["liga", "espagne", "copa del rey"]):
            data["Espagne"].append(match_item)
        elif any(k in compet_lower for k in ["serie a", "italie", "coppa"]):
            data["Italie"].append(match_item)
        elif any(k in compet_lower for k in ["bundesliga", "allemagne"]):
            data["Allemagne"].append(match_item)
        elif any(k in compet_lower for k in ["champions league", "europa", "conference", "ligue des champions"]):
            data["Europe"].append(match_item)
        else:
            data["Autres"].append(match_item)

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    get_matches()
