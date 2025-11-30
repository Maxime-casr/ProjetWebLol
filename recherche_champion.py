import json
import os
from pathlib import Path


def charger_donnees():
    json_path = Path(__file__).parent / 'data' / 'all_champion_builds.json'
    
    if not json_path.exists():
        print(f"Erreur : Le fichier {json_path} n'existe pas")
        print("Lance d'abord le scraping avec : scrapy crawl champion_builds")
        return None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def afficher_items(champion_data):
    champion = champion_data['champion']
    items = champion_data['popular_items']
    
    print(f"\n{'='*60}")
    print(f"Top 6 items pour {champion.upper()}")
    print(f"{'='*60}\n")
    
    if not items:
        print("Aucun item trouvé pour ce champion.")
        return
    
    for i, item in enumerate(items, 1):
        nom_item = item['item']
        pourcentage = item['percentage']
        
        print(f"{i}. {nom_item:<30} {pourcentage}%")
    
    print(f"\n{'='*60}\n")


def rechercher_champion(donnees, nom):
    nom_lower = nom.lower().strip()
    
    if nom_lower in donnees:
        return donnees[nom_lower]
    
    resultats = []
    for champ_slug, champ_data in donnees.items():
        if nom_lower in champ_slug:
            resultats.append((champ_slug, champ_data))
    
    if len(resultats) == 1:
        return resultats[0][1]
    elif len(resultats) > 1:
        print(f"\nPlusieurs champions trouvés : {', '.join([r[0] for r in resultats])}")
        print("Sois plus précis !")
        return None
    
    return None


def lister_champions(donnees):
    champions = sorted(donnees.keys())
    print(f"\nListe des {len(champions)} champions disponibles :\n")
    
    colonnes = 4
    for i in range(0, len(champions), colonnes):
        ligne = champions[i:i+colonnes]
        print("  ".join(f"{champ:<20}" for champ in ligne))
    
    print()


def main():
    print("\n" + "="*60)
    print("LEAGUE OF LEGENDS - CHERCHEUR D'ITEMS DE CHAMPIONS")
    print("="*60)
    
    donnees = charger_donnees()
    if donnees is None:
        return
    
    print(f"\n✅ {len(donnees)} champions chargés avec succès!\n")
    
    while True:
        print("\n" + "-"*60)
        print("Options :")
        print("  - Tape le nom d'un champion (ex: jinx, ahri, yasuo)")
        print("  - Tape 'liste' pour voir tous les champions")
        print("  - Tape 'quit' pour quitter")
        print("-"*60)
        
        choix = input("\nTon choix : ").strip().lower()
        
        if choix in ['quit']:
            break
        
        elif choix in ['liste']:
            lister_champions(donnees)
        
        elif choix == '':
            continue
        
        else:
            champion_data = rechercher_champion(donnees, choix)
            if champion_data:
                afficher_items(champion_data)
            else:
                print(f"\nChampion '{choix}' non trouvé. Tape 'liste' pour voir tous les champions.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterruption\n")
    except Exception as e:
        print(f"\nErreur : {e}\n")
