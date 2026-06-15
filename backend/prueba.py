
def prueba():
    cartas = [
        {
            "set": "pi",
            "numero": "1",
            "edicion": "primera",
        },
        {
            "set": "pi2",
            "numero": "2",
            "edicion": "segunda",
        }     
    ]
    for carta in cartas:
        print(carta["set"])

prueba()