import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import time

COMMASPACE = ', '
# Define params
imgpath = 'GRAPHS/'

mailsender = "correo3.pruebas@gmail.com"
mailreceip = "correo3.pruebas@gmail.com"
mailserver = 'smtp.gmail.com: 587'
password = '542A6Rnl&'

def send_alert_attached(umbrales,minutos):
    """ Envía un correo electrónico adjuntando la imagen en IMG
    """
    subject = "Sobrepasa Umbral línea base: " 
    if umbrales['cpuLoad']:
        subject += " CPULoad, "
    if umbrales['disk']:
        subject += " almacenamiento, "
    if umbrales['ram']:
        subject += "ram, "

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = mailsender
    msg['To'] = mailreceip

    if umbrales['cpuLoad']:
        fp = open(imgpath+'CPULoad.png', 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        msg.attach(img)
    if umbrales['disk']:
        fp = open(imgpath+'DISK.png', 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        msg.attach(img)
    if umbrales['ram']:
        fp = open(imgpath+'RAM.png', 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        msg.attach(img)

    s = smtplib.SMTP(mailserver)

    s.starttls()
    # Login Credentials for sending the mail
    s.login(mailsender, password)

    s.sendmail(mailsender, mailreceip, msg.as_string())
    s.quit()
    time.sleep(minutos*60)