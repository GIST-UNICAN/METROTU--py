import urllib.request

def convierte(
    access_key="c12140c42b4e132fb0c6d14ed940d70e",
    document_url="https://archivosgist.es/tests/informe.html"
    ):
    
    url = (
        f"http://api.pdflayer.com/api/convert"
        f"?access_key={access_key}"
        f"&document_url={document_url}"
        #"& auth_user = myUsername"
        #"& auth_pass = myPassword"
        )
    urllib.request.urlretrieve(url, "test.pdf")

if __name__ == "__main__":
    convierte()
    


