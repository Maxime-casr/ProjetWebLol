"""
Script pour rechercher les 6 items les plus joués d'un champion League of Legends
"""
import json
import os
from pathlib import Path


def charger_donnees():
    """Charge les données des champions depuis le JSON"""
    json_path = Path(__file__).parent / 'data' / 'all_champion_builds.json'
    
    if not json_path.exists():
        print(f"❌ Erreur : Le fichier {json_path} n'existe pas!")
        print("Lance d'abord le scraping avec : scrapy crawl champion_builds")
        return None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def afficher_items(champion_data):
    """Affiche les items d'un champion de manière formatée"""
    champion = champion_data['champion']
    items = champion_data['popular_items']
    
    print(f"\n{'='*60}")
    print(f"🏆 Top 6 items pour {champion.upper()}")
    print(f"{'='*60}\n")
    
    if not items:
        print("❌ Aucun item trouvé pour ce champion.")
        return
    
    for i, item in enumerate(items, 1):
        nom_item = item['item']
        pourcentage = item['percentage']
        
        # Barre de progression visuelle
        barre_longueur = int(pourcentage / 2)  # Max 50 caractères
        barre = '█' * barre_longueur + '░' * (50 - barre_longueur)
        
        print(f"{i}. {nom_item:<30} {barre} {pourcentage}%")
    
    print(f"\n{'='*60}\n")


def rechercher_champion(donnees, nom):
    """Recherche un champion par nom (insensible à la casse)"""
    nom_lower = nom.lower().strip()
    
    # Recherche exacte
    if nom_lower in donnees:
        return donnees[nom_lower]
    
    # Recherche partielle (contient le nom)
    resultats = []
    for champ_slug, champ_data in donnees.items():
        if nom_lower in champ_slug:
            resultats.append((champ_slug, champ_data))
    
    if len(resultats) == 1:
        return resultats[0][1]
    elif len(resultats) > 1:
        print(f"\n🔍 Plusieurs champions trouvés : {', '.join([r[0] for r in resultats])}")
        print("Sois plus précis !")
        return None
    
    return None


def lister_champions(donnees):
    """Affiche la liste de tous les champions disponibles"""
    champions = sorted(donnees.keys())
    print(f"\n📋 Liste des {len(champions)} champions disponibles :\n")
    
    # Affichage en colonnes
    colonnes = 4
    for i in range(0, len(champions), colonnes):
        ligne = champions[i:i+colonnes]
        print("  ".join(f"{champ:<20}" for champ in ligne))
    
    print()


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🎮 LEAGUE OF LEGENDS - RECHERCHE D'ITEMS PRO BUILD")
    print("="*60)
    
    # Charger les données
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
        
        choix = input("\n👉 Ton choix : ").strip().lower()
        
        if choix in ['quit', 'q', 'exit', 'quitter']:
            print("\n👋 À bientôt sur la Faille !\n")
            break
        
        elif choix in ['liste', 'list', 'ls']:
            lister_champions(donnees)
        
        elif choix == '':
            continue
        
        else:
            champion_data = rechercher_champion(donnees, choix)
            if champion_data:
                afficher_items(champion_data)
            else:
                print(f"\n❌ Champion '{choix}' non trouvé. Tape 'liste' pour voir tous les champions.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interruption - À bientôt !\n")
    except Exception as e:
        print(f"\n❌ Erreur : {e}\n")
