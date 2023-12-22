# Librairies utilisées :
# - requests pour récupérer le XML
# - xmltodict pour parser le XML
# - json pour convertir le XML en JSON

import requests
import xmltodict
import json as _json
import datetime
from bs4 import BeautifulSoup

CRENEAUX = {
    "1": { "debut": "8h30", "fin": "10h00" },
    "2": { "debut": "10h30", "fin": "12h00" },
    "3": { "debut": "12h00", "fin": "13h30" },
    "4": { "debut": "13h30", "fin": "15h00" },
    "5": { "debut": "15h15", "fin": "16h45" },
    "6": { "debut": "17h00", "fin": "18h30" }
}

def get_xml_from_url(url):
    response = requests.get(url)
    xml = response.content
    return xml

def get_json_from_xml(xml):
    jsonXML = _json.dumps(xmltodict.parse(xml))
    json = _json.loads(jsonXML)
    return json

# On récupère les cours du jour correspondant à la date du jour récupérée précédemment
def get_json_cours(date, classe="B3 Groupe 3 DLW-FA.xml"):
    # transforme le classe en url valide avec des %20 à la place des espaces
    classe = classe.replace(" ", "%20")
    # Pour chaque semaine de cours
    APIUrl = "https://eleves.groupe3il.fr/edt_eleves/" + classe
    xml = get_xml_from_url(APIUrl)
    json = get_json_from_xml(xml)
    for semaine in json['DOCUMENT']['GROUPE']['PLAGES']['SEMAINE']:
        # Pour chaque jour de cours
        for jour in semaine['JOUR']:
            # Si le jour correspond à la date du jour
            if jour['Date'] == date:
                # On récupère les cours de la journée
                return jour['CRENEAU']
            

def get_cours_for_date(date, classe="B3 Groupe 3 DLW-FA.xml"):
    emploi_du_temps = get_json_cours(date, classe)
    # On stocke tout les cours dans une liste
    cours_du_jour = []
    for i in emploi_du_temps:
        cours = []
        # i = {'Creneau': '1', 'Activite': 'ELT. GESTION C', 'Id': '24088', 'Couleur': '#FFFFFF;', 'Horaire': None, 'Salles': '305'}
        # On récupère le creneau
        creneau = i['Creneau']
        # Si l'activité (donc le cours) n'est pas set c'est qu'il n'y à pas cours
        plage_horaire = f"{CRENEAUX[creneau]['debut']} à {CRENEAUX[creneau]['fin']}"
        cours.append({"horaire": plage_horaire})
        if 'Activite' not in i:
            # Si c'est le créneau de la pause dej
            if creneau == '3':
                cours.append({"intitule": "Pause déjeuner"})
            else:
                cours.append({"intitule": "Pas de cours prévu"})
            cours.append({"salle": ""})
        else:
            activite = i['Activite']
            salle = i['Salles']
            # On construit le message
            cours.append({"intitule": activite})
            cours.append({"salle": salle})
        cours_du_jour.append(cours)
    return cours_du_jour

def get_classes():
    # Obtenez le contenu de la page Web
    url = "https://eleves.groupe3il.fr/edt_eleves/00_index.php"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Trouvez l'élément select par son id
    select = soup.find('select', {'id': 'idGroupe'})

    # Obtenez toutes les options dans le select
    options = select.find_all('option')

    # Créez une liste de tuples contenant les valeurs affichées et non affichées
    values = [(option.text, option['value']) for option in options]

    # Imprimez les valeurs
    for displayed, not_displayed in values:
        print(f"Affiché: {displayed}, Non affiché: {not_displayed}")

    return values

def get_class_schedule(values):
    # Créez un dictionnaire pour mapper les numéros de classe aux noms de classe
    class_dict = {i+1: (displayed, not_displayed) for i, (displayed, not_displayed) in enumerate(values)}

    # Affichez les options de classe
    for num, (displayed, _) in class_dict.items():
        print(f"Tapez {num} pour {displayed}")

    # Demandez à l'utilisateur de choisir une classe
    while True:
        class_num = input("Veuillez entrer le numéro de la classe dont vous souhaitez voir l'emploi du temps : ")
        if class_num.isdigit() and int(class_num) in class_dict:
            break
        else:
            print("Numéro de classe non valide. Veuillez réessayer.")

    # Récupérez l'emploi du temps de la classe choisie
    displayed, not_displayed = class_dict[int(class_num)]
    date = "22/12/2023"
    schedule = get_cours_for_date(date, not_displayed)
    print(f"L'emploi du temps pour la classe {displayed} le {date} est : {schedule}")


if __name__ == "__main__":
    values = get_classes()
    get_class_schedule(values)
