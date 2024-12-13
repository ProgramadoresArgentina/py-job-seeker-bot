## Linkedin Scrapper (Jobs & Posts)


Bot creado por [Juanse Mastrangelo](https://github.com/JuanseMastrangelo) para el scrapping de trabajos en indeed, linkedin, zip_recruiter, glassdoor para la comunidad de Programadores Argentina. También hace scrapping de publicaciones de linkedin, para esto es necesario tu usuario, contraseña y cookies.

#### Parametros configurables:
- Fecha desde.
- Texto/Trabajo a buscar.
- Ubicación.
- Total de empleos.

#### Retorna un excel con las siguientes columnas:
- Sitio
- Titulo
- Empresa
- Job Url
- Localización
- Tipo de Trabajo (remoto, hybrido, presencial)
- Fecha Publicacion


#### Setup:
- Tener instalado Python y Pip
- Instalar dependencias con ```pip install -r requirements.txt```
- Agregar valores al .env file. 
  - **JSESSIONID** y **li_at** hacen referencias a cookies de sesion de linkedin. Obtenerlas desde la consola dentro de linkedin una vez logeado.

#### Correr el scrapper:
- Es necesario contar con un csv en api/emails.csv. Usar emails-test.csv para pruebas.
- Correr ```pip api/scrapper.py``` para comenzar el scrapping.
- Obtendras un mensaje de confirmación antes de enviar los mails.


Puedes usar ```pip api/getLists.py``` para obtener listas de usuarios desde sendgrid.