import csv
import io
import base64
import os
from jobspy import scrape_jobs
from linkedin_api import Linkedin
import sendgrid
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from datetime import datetime
from requests.cookies import RequestsCookieJar
from dotenv import load_dotenv

load_dotenv()

# Configuración de cookies para LinkedIn
cookies = RequestsCookieJar()
cookies.set("li_at", os.getenv("li_at"))
cookies.set("JSESSIONID", os.getenv("JSESSIONID"))

linkedin_api = Linkedin(os.getenv("LINKEDIN_MAIL"), os.getenv("LINKEDIN_PASSWORD"), cookies=cookies)

hours_old=24 # En horas.
search_term="programador junior trainee argentina"
location="Argentina"
sendgrid_api_key = os.getenv("SENDGRID_API_KEY")


# Scraping de trabajos en sitios especificados
jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
    search_term=search_term,
    location=location,
    results_wanted=100,
    hours_old=hours_old
)
print(f"Found {len(jobs)} jobs")

# Scraping de publicaciones en LinkedIn
search_term = search_term
publicaciones = linkedin_api.search({"keywords": search_term, "geoId": "100446943", "location": location, "postedWithin": str(hours_old) + "h"}, limit=50)


# Procesar resultados de publicaciones
publicaciones_data = []
for publicacion in publicaciones:
    job_url = publicacion.get("navigationUrl", "")
    if not job_url.startswith("https://www.linkedin.com/in/"):
        publicaciones_data.append({
            "sitio": "linkedin",
            "titulo": publicacion.get("title", {}).get("text", ""),
            "company": publicacion.get("primarySubtitle", {}).get("text", ""),
            "job_url": job_url,
            "location": publicacion.get("secondarySubtitle", {}).get("text", ""),
            "tipo_trabajo": "",
            "fecha_publicacion": "No disponible",
        })

print(f"Found {len(publicaciones)} posts")

# Crear archivo CSV en memoria, unificando campos
csv_buffer = io.StringIO()
fieldnames = ["sitio", "titulo", "company", "job_url", "location", "tipo_trabajo", "fecha_publicacion"]
writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
writer.writeheader()

# Escribir trabajos en el archivo CSV
for job in jobs.to_dict(orient="records"):
    writer.writerow({
        "sitio": job.get("site"),
        "titulo": job.get("title"),
        "company": job.get("company"),
        "job_url": job.get("job_url"),
        "location": job.get("location"),
        "tipo_trabajo": job.get("job_type"),
        "fecha_publicacion": job.get("date_posted"),
    })

# Escribir publicaciones en el archivo CSV
for publicacion in publicaciones_data:
    writer.writerow(publicacion)

csv_buffer.seek(0)

# Configurar SendGrid
if not sendgrid_api_key:
    print("Falta la clave de API de SendGrid")
    exit()

sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
today = datetime.now().strftime("%d %b")

# Mensaje base del correo
base_message = Mail(
    from_email='programadoresargentina@gmail.com',
    subject=f'Ofertas Laborales Junior Argentina {today}',
    plain_text_content='Buenas tardes, aquí están las últimas ofertas laborales y publicaciones de LinkedIn sobre el rol de desarrollador junior en Argentina.'
)

# Codificar CSV en base64
csv_data = base64.b64encode(csv_buffer.getvalue().encode('utf-8')).decode('utf-8')
attachment = Attachment(
    FileContent(csv_data),
    FileName('jobs_and_posts.csv'),
    FileType('text/csv'),
    Disposition('attachment')
)
base_message.attachment = attachment

# Download jobs in local
with open("jobs.csv", "w", newline='', encoding='utf-8') as f:
    f.write(csv_buffer.getvalue())

# Confirmación para enviar correos
send_emails = input("¿Quieres enviar los correos? (sí/no): ").strip().lower()
if send_emails not in ["sí", "s", "si", "y", "yes"]:
    print("Envío de correos cancelado.")
    exit()
else:
    try:
        email_list = []
        with open("emails.csv", mode="r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'EMAIL' in row:  # Asegurarse de que la columna 'EMAIL' exista en cada fila
                    email_list.append(row['EMAIL'])

        # Verificar si se obtuvieron correos electrónicos
        if not email_list:
            print("No se encontraron correos electrónicos en el archivo emails.csv.")
            exit()
            
        for email in email_list:
            try:
                if not email:
                    print("La variable 'email' está vacía o no contiene un valor válido. Deteniendo el programa.")
                    exit()
                # Crear una nueva instancia de Mail para cada destinatario
                message = Mail(
                    from_email='programadoresargentina@gmail.com',
                    to_emails=email,
                    subject=f'Ofertas Laborales Junior Argentina {today}',
                    plain_text_content='Buenas tardes, aquí están las últimas ofertas laborales y publicaciones de LinkedIn sobre el rol de desarrollador junior en Argentina.'
                )
                message.attachment = attachment  # Agregar el archivo adjunto

                # Enviar el correo
                responsePost = sg.client.mail.send.post(request_body=message.get())
                if responsePost.status_code == 202:
                    print(f"Email sent successfully to {email}.")
                else:
                    print(f"Failed to send email to {email}: {responsePost.status_code} - {responsePost.body.decode('utf-8')}")
            except Exception as e:
                print(f"Error al enviar el correo a {email}: {str(e)}")

    except Exception as e:
        print(f"Error al obtener contactos: {str(e)}")