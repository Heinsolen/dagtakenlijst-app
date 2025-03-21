import json
import requests
import mysql.connector

# Configuratie voor databaseverbinding
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "attractiepark_db"
}

# API-configuratie voor weergegevens
WEER_API_KEY = "jouw_api_key"
WEER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

def haal_personeelsgegevens_op(json_bestand):
    """Leest personeelsgegevens uit een JSON-bestand."""
    with open(json_bestand, "r", encoding="utf-8") as file:
        return json.load(file)

def haal_geschikte_taken_op(personeelslid):
    """Haalt onderhoudstaken op die passen bij het personeelslid."""
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT * FROM onderhoudstaken
    WHERE functie = %s OR ervaring <= %s
    ORDER BY prioriteit DESC;
    """
    cursor.execute(query, (personeelslid["functie"], personeelslid["ervaring"]))
    taken = cursor.fetchall()
    cursor.close()
    conn.close()
    return taken

def haal_weer_op(stad="Amsterdam"):
    """Haalt actuele weersgegevens op."""
    params = {"q": stad, "appid": WEER_API_KEY, "units": "metric"}
    response = requests.get(WEER_API_URL, params=params)
    return response.json()

def genereer_dagtakenlijst(personeelslid, taken, weer):
    """Genereert een dagtakenlijst met pauzes en werkuren."""
    dagtakenlijst = []
    totaal_uren = 0
    max_werkuren = 8
    
    for taak in taken:
        if totaal_uren + taak["duur"] <= max_werkuren:
            dagtakenlijst.append({
                "taak": taak["naam"],
                "duur": taak["duur"],
                "locatie": taak["locatie"],
                "status": "Ingepland"
            })
            totaal_uren += taak["duur"]
        else:
            break
    
    dagtakenlijst.append({"taak": "Lunchpauze", "duur": 1, "status": "Pauze"})
    
    if weer["weather"][0]["main"] == "Rain":
        dagtakenlijst.append({"taak": "Binnenwerk uitvoeren", "status": "Aangepast vanwege regen"})
    
    return dagtakenlijst

def sla_op_als_json(data, bestandsnaam="dagtakenlijst.json"):
    """Slaat de dagtakenlijst op als JSON-bestand."""
    with open(bestandsnaam, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def main():
    personeelslid = haal_personeelsgegevens_op("personeel.json")
    taken = haal_geschikte_taken_op(personeelslid)
    weer = haal_weer_op(personeelslid.get("locatie", "Amsterdam"))
    dagtakenlijst = genereer_dagtakenlijst(personeelslid, taken, weer)
    sla_op_als_json(dagtakenlijst)
    print("Dagtakenlijst gegenereerd en opgeslagen in dagtakenlijst.json")

if __name__ == "__main__":
    main()
