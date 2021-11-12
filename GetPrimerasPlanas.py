#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import urllib.request
import img2pdf
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from PyPDF2 import PdfFileMerger


# In[ ]:


#Folder donde se guardan las imagenes
#MODIFICAR CON LA DIRECCION EN LA CUAL SE QUIERA GUARDAR LA INFORMACIÓN
curren_folder = os.getcwd()
folder_imagenes = f'{curren_folder}\\img'


# In[ ]:


def get_date():
    '''
    Return the current day and month
    '''
    return datetime.today().strftime('%d-%b')


# In[ ]:


def loop_list(input_lis: list, target_list: list):
    '''
    Append item of a list into another list
    '''
    for img in input_lis:
        img_src = img.find("img")
        target_list.append(img_src['src'])


# In[ ]:


def get_images_mx():
    '''
    return a list with the src of the images of a section
    '''
    url = "https://es.kiosko.net/mx/"
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    prensas = soup.find_all("div", {"class": "expo"})[0].find_all("div", {"class": "line"})
    img_prensa_info_gral = prensas[0].find_all("a", {"class": "thcover"})
    img_prensa_economia = prensas[2].find_all("a", {"class": "thcover"})
    
    images = []
    loop_list(img_prensa_info_gral, images)
    loop_list(img_prensa_economia, images)
    return images


# In[ ]:


def get_pdf_images_mx(file_name: str):
    '''
    Save a PDf with is downloaded from a goverment page
    '''
    
    url = 'http://comunicacion.diputados.gob.mx/sintesis/notas/whats/001.pdf'
    req = requests.get(url, allow_redirects=True)
    with open(f'{curren_folder}\\{file_name}.pdf', "wb") as documento:
        documento.write(req.content)


# In[ ]:


def get_images_us():
    '''
    return a list with the src of the images of a section
    '''
    url = "https://es.kiosko.net/us/"
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    prensas = soup.find_all("div", {"class": "expo"})[0].find_all("div", {"class": "line"})
    img_prensa_info_gral = prensas[0].find_all("a", {"class": "thcover"})
    img_prensa_economia = prensas[1].find_all("a", {"class": "thcover"})
    
    images = []
    loop_list(img_prensa_info_gral, images)
    loop_list(img_prensa_economia, images)
    return images


# In[ ]:


def map_name(name: str):
    '''
    Map the name of the newspaper to its position in the pdf file 
    '''
    valor = name.split('_')[-1]
    switch_periodico = {
        'financiero': '0',
        'eleconomista': '01',
        'wsj': '02',
        'us': '03',
        'reforma': '04',
        'universal': '05',
        'milenio': '06',
        'jornada': '07',
        'excelsior': '08',
        'times': '09',
        'post': '10',
        'globe': '11',
        'latimes': '12',
        'today': '13'    
    }
    
    return switch_periodico.get(valor)


# In[ ]:


def download_img(url: str, country: str):
    '''
    Download a img from its url
    '''
    url_temp = url.replace('200','750').replace('//','http://')
    if country == 'mx':
        #######Get the name of the img
        date_start = url.find('net/') + len('net/')
        date_end = url.find('/mx')
        date = url[date_start : date_end]

        paper_start = url.find('mx_') + len('mx_')
        paper_end = url.find('.200')
        paper_name = url[paper_start : paper_end]
        fullname = date.replace('/','-') + '_' + paper_name
        
    else:
        #######Get the name of the img
        date_start = url.find('net/') + len('net/')
        date_end = url.find('/mx')
        date = url[date_start : date_end]

        paper_start = url.find('us/') + len('us/')
        paper_end = url.find('.200')
        paper_name = url[paper_start : paper_end]
        fullname = date.replace('/','-') + '_' + paper_name
        
    ############map the name of the file
    
    ######Download the img
    paper_fullname =  f'{fullname}'
    urllib.request.urlretrieve(url_temp, f'{folder_imagenes}\\{map_name(paper_fullname)}.jpg')
    #urllib.request.urlretrieve(url_temp, f'{folder_imagenes}\\{paper_fullname}.jpg')


# In[ ]:


def convert_img2pdf(file_name: str):
    '''
    Convert a list with img paths to a pdf
    '''
    imagenes_jpg = [folder_imagenes + '\\' + archivo for archivo in os.listdir(folder_imagenes) if archivo.endswith(".jpg")]
    with open(f'{curren_folder}\\{file_name}.pdf', "wb") as documento:
        documento.write(img2pdf.convert(imagenes_jpg))


# In[ ]:

def merge_pdfs(pdfs: list,pdf_name: str):
    '''
    Return a single pdf merging the list of pdfs
    '''
    
    fusionador = PdfFileMerger()
    
    for pdf in pdfs:
        fusionador.append(open(f'{curren_folder}\\{pdf}', 'rb'))
    
    print(type(fusionador))
    with open(f'{curren_folder}\\{pdf_name}.pdf', 'wb') as salida:
        fusionador.write(salida)


# In[ ]:


def send_mail(destinatarios : list,file_name: str):

    # Iniciamos los parámetros del script
    remitente = 'actinverdc@gmail.com'
    asunto = 'Primeras planas Nacionales y de USA'
    cuerpo = ''
    ruta_adjunto = f'{curren_folder}\\{file_name}.pdf'
    nombre_adjunto = f'{file_name}.pdf'

    # Creamos el objeto mensaje
    mensaje = MIMEMultipart()

    # Establecemos los atributos del mensaje
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = asunto

    # Agregamos el cuerpo del mensaje como objeto MIME de tipo texto
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Abrimos el archivo que vamos a adjuntar
    archivo_adjunto = open(ruta_adjunto, 'rb')

    # Creamos un objeto MIME base
    adjunto_MIME = MIMEBase('application', 'octet-stream')
    # Y le cargamos el archivo adjunto
    adjunto_MIME.set_payload((archivo_adjunto).read())
    # Codificamos el objeto en BASE64
    encoders.encode_base64(adjunto_MIME)
    # Agregamos una cabecera al objeto
    adjunto_MIME.add_header('Content-Disposition', 'attachment', filename=nombre_adjunto)
    # Y finalmente lo agregamos al mensaje
    mensaje.attach(adjunto_MIME)

    # Creamos la conexión con el servidor
    sesion_smtp = smtplib.SMTP('smtp.gmail.com', 587)

    # Ciframos la conexión
    sesion_smtp.starttls()

    # Iniciamos sesión en el servidor
    sesion_smtp.login('actinverdc@gmail.com','Actinver2021**')

    # Convertimos el objeto mensaje a texto
    texto = mensaje.as_string()

    # Enviamos el mensaje
    sesion_smtp.sendmail(remitente, destinatarios, texto)

    # Cerramos la conexión
    sesion_smtp.quit()


# In[ ]:


def main():
    '''
    main funtion
    '''
    mx_img = get_images_mx()
    us_img = get_images_us()
    
    #Download the images
    '''for item in mx_img:
        download_img(item, 'mx')
    '''
    get_pdf_images_mx('MX')
    
    for item in us_img:
        download_img(item, 'us')
    
    #save the images into a pdf
    convert_img2pdf('USA')
    
    #Merge PDF
    pdfs = ['MX.pdf','USA.pdf']
    merge_pdfs(pdfs, 'news')
    
    #Sent pdf file
    #destinatarios = ['314159735@pcpuma.acatlan.unam.mx','enlopezn@actinver.com.mx','agaliciad@actinver.com.mx','ecovarrubias@actinver.com.mx']
    destinatarios = ['314159735@pcpuma.acatlan.unam.mx']
    send_mail(destinatarios,'news')


# In[ ]:


main()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




