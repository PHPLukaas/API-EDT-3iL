from fastapi import FastAPI, Response
from datetime import datetime
import json
from emploi_du_temps import get_classes, get_cours_for_date 

app = FastAPI()


@app.get("/classes")
def read_classes():
    classes = get_classes()
    return Response(json.dumps({"status": "success", "data": classes}), media_type='application/json; charset=UTF-8')

@app.get("/edt/{fichier_xml_classe}")
def read_edt(fichier_xml_classe: str, date: str = datetime.today().strftime('%d-%m-%Y')):
    date_obj = datetime.strptime(date, '%d-%m-%Y')
    # On convertit la date en string au format "DD/MM/YYYY"
    date = date_obj.strftime('%d/%m/%Y')
    schedule = get_cours_for_date(date, fichier_xml_classe)
    return Response(json.dumps({"status": "success", "data": schedule}), media_type='application/json; charset=UTF-8')