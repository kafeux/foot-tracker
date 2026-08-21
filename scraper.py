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

    # On récupère tout le texte brut du site
    full_text = soup.get_text(separator=" ")
    
    # Regex qui détecte chaque match : (Heure) + (Équipe 1 - Équipe 2) + (Compétition/Détails jusqu'au prochain match ou virgule)
    # Exemple : "20h45 Marseille - Strasbourg Ligue 1"
    pattern = re.compile(r'([0-2]?[0-9][h:][0-5][0-9])\s+([A-Za-z0-9À-ÿ\.\s]+?\s*-\s*[A-Za-z0-9À-ÿ\.\s]+?)(?=(?:[0-2]?[0-9][h:][0-5][0-9]|$|,|\bJournée\b))', re.IGNORECASE)
    
    matches_found = pattern.findall(full_text)
    
    seen = set()
    for heure, affiche in matches_found:
        heure_clean = heure.replace('h', ':').strip()
        affiche_clean = clean_text(affiche)
        
        # Filtre pour éviter les faux positifs ou les textes trop longs/courts
        if len(affiche_clean) < 5 or len(affiche_clean) > 80 or " - " not in affiche_clean:
            continue
            
        key = f"{heure_clean}_{affiche_clean}"
        if key in seen:
            continue
        seen.add(key)
        
        item = {
            "heure": heure_clean,
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
