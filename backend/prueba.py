
import hashlib

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

    palabra = []

    #if palabra is None:
    #    print("es nulo")
    
    hash_conocido="cbf06754df2f70dd1f853bdccaec98cc6d8ba861a2a91d357540b9d561b6ceb7"
    hash = hashing_api_key("default123")
    if (hash_conocido ==hashing_api_key("default123")):
        print("es igual")
    
    print(hash)

    #for carta in cartas:
    #   print(carta["set"])

def hashing_api_key(API_key: str):
        """Hashea el API key utilizando SHA-256."""
        return hashlib.sha256(API_key.encode()).hexdigest()

prueba()

prueba1_dict={
  "API_key": "default123",
  "lista_cartas_consultar": [
    {"set_name": "SM1", "numero": "12", "edicion": "1st", "idioma": "es", "acabado": "Holo"},
    {"set_name": "futbol", "numero": "123456", "edicion": "limitada", "idioma": "es", "acabado": "bacano"},
    {"set_name": "beisbol", "numero": "654321", "edicion": "", "idioma": "", "acabado": ""}
  ]
}