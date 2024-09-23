

#coinfigurancion de

#Clase que va a tomar los datos y encapcularlos
class POM ():
    pass

#funcion que va a escribir en el formulario y mandar los dartos
def writer_form():
    pass

import requests

# URL del formulario (reemplaza FORM_ID con tu ID real)
url = "https://docs.google.com/forms/d/e/1FAIpQLSfNe4krjpaC7I_9FA7Do3MAuQr7eC9wF5zVHIgOV2XeqzAAnA/formResponse"


# Datos que quieres enviar (reemplaza los IDs con los correctos)
data = {
    'entry.1234567890': 'John Doe',  # ID del campo de nombre
    'entry.0987654321': 'johndoe@example.com',  # ID del campo de email
}

# Enviar la solicitud POST
response = requests.post(url, data=data)

# Verificar el resultado
if response.status_code == 200:
    print("Formulario enviado con éxito")
else:
    print("Error al enviar el formulario, código de estado:", response.status_code)
