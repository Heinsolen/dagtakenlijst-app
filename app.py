import json
import mysql.connector

def lees_json(bestandsnaam):
    with open(bestandsnaam, 'r') as file:
        return json.load(file)

def schrijf_json(bestandsnaam, data):
    with open(bestandsnaam, 'w') as file:
        json.dump(data, file, indent=4)

def connect_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="attractiepark"
    )

def haal_taken_op(beroepstype, bevoegdheid, max_fysieke_belasting):
    db = connect_database()
    cursor = db.cursor(dictionary=True)
    
    query = """
    SELECT * FROM onderhoudstaken
    WHERE beroepstype = %s AND bevoegdheid <= %s AND fysieke_belasting <= %s
    ORDER BY relevantie DESC
    """
    cursor.execute(query, (beroepstype, bevoegdheid, max_fysieke_belasting))
    taken = cursor.fetchall()
    
    db.close()
    return taken

def genereer_dagtakenlijst():
    personeelslid = lees_json("personeelsgegevens.json")
    
    max_fysieke_belasting = 30 if personeelslid["leeftijd"] > 24 else 25
    if "verlaagde_fysieke_belasting" in personeelslid:
        max_fysieke_belasting = personeelslid["verlaagde_fysieke_belasting"]
    
    beschikbare_taken = haal_taken_op(
        personeelslid["beroepstype"],
        personeelslid["bevoegdheid"],
        max_fysieke_belasting
    )
    
    werktijd = personeelslid["werktijd"]
    dagtakenlijst = []
    totale_tijd = 0
    
    for taak in beschikbare_taken:
        if totale_tijd + taak["duur"] <= werktijd:
            dagtakenlijst.append(taak)
            totale_tijd += taak["duur"]
        else:
            break
    
    schrijf_json("dagtakenlijst.json", dagtakenlijst)
    print("Dagtakenlijst gegenereerd!")

genereer_dagtakenlijst()
