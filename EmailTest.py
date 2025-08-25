import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()  # se você quiser pegar os dados do .env

# ===== CONFIGURAÇÕES DO BANCO =====
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# ===== CONFIGURAÇÕES DO EMAIL =====
FROM_EMAIL = "xxx"
SENHA = "xxx"
SMTP_SERVER = "smtp.zoho.com"
SMTP_PORT = 587  # porta TLS

# ===== ASSUNTO E CORPO DO EMAIL =====
ASSUNTO = "Assunto do email"
CORPO = """
Olá,

Este é um email de teste enviado automaticamente via script Python.

Atenciosamente,
Sua Empresa
"""

# ===== CONECTAR AO BANCO =====
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = conn.cursor()

# ===== BUSCAR EMAILS =====
cur.execute("SELECT id, email FROM empresas WHERE email IS NOT NULL AND status_envio = 0")
emails = cur.fetchall()  # retorna lista de tuplas (id, email)

# ===== ENVIAR EMAIL =====
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(FROM_EMAIL, SENHA)

for empresa_id, email in emails:
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = email
    msg['Subject'] = ASSUNTO
    msg.attach(MIMEText(CORPO, 'plain'))
    
    try:
        server.send_message(msg)
        print(f" Email enviado para {email}")
        
        # ===== ATUALIZAR STATUS NO BANCO =====
        cur.execute("UPDATE empresas SET status_envio = 1 WHERE id = %s", (empresa_id,))
        conn.commit()
        
    except Exception as e:
        print(f" Falha ao enviar email para {email}: {e}")
        conn.rollback()  # desfaz alterações no caso de erro

server.quit()
cur.close()
conn.close()
