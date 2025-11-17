# Browphish 🎣

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-YELLOW.svg)
![Status](https://img.shields.io/badge/Status-Alpha-orange.svg)

Un toolkit modulare e open-source per simulazioni di phishing e campagne di social engineering, interamente gestibile da riga di comando (CLI).

---

## 🚨 Disclaimer Etico

**Browphish è stato creato esclusivamente per scopi educativi e per essere utilizzato da professionisti della sicurezza informatica in contesti autorizzati.** L'uso di questo strumento per attività illegali o non etiche è severamente proibito. Gli autori non si assumono alcuna responsabilità per l'uso improprio del software. L'utente finale è l'unico responsabile delle proprie azioni.

---

## 📝 Descrizione

Browphish è un framework di simulazione per phishing e social engineering, progettato per professionisti della sicurezza informatica. 
Permette di creare campagne controllate, clonare pagine web di login e tracciare i risultati attraverso un'interfaccia CLI intuitiva e completamente automatizzata.

---

## 🔑 Funzionalità Principali

- **Gestione Campagne Phishing**: Crea, monitora e gestisci molteplici campagne phishing con tracciamento completo dei risultati
- **Clonazione Dinamica di Pagine Web**: Clona automaticamente pagine di login, riscrivendo CSS/JS per il rendering corretto
- **Server Integrato**: Avvia server Flask in background per servire pagine clonate e catturare credenziali
- **Riconoscimento Intelligente**: Identificazione automatica di campi username, email e password dai form
- **Statistiche Campagne**: Visualizzazione in tempo reale di accessi, credenziali catturate e metriche per campagna
- **Database Centralizzato**: SQLite per persistenza completa di tutte le operazioni

- **Email Campaign Support**: Integrazione per inviare email phishing via SMTP (TODO)


---

## 🛠️ Installazione


### Startup

1. **Clona il repository:**
```bash
git clone https://github.com/gianlucabassani/browphish.git
cd browphish
```

2. **Crea e attiva l'ambiente virtuale:**
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

3. **Installa le dipendenze:**
```bash
pip install -r requirements.txt
```

---

## Utilizzo

Avvia l'interfaccia a riga di comando:

```bash
python3 src/main.py
```

### Flusso Tipico
1. **Gestione Campagne** → Crea una nuova campagna phishing
2. **Gestione Pagine Web** → Clona una pagina di login target e associa alla campagna 
3. **Avvia Campagna** → Esegui il server in background su una porta specifica
4. **Gestione Email** → (Opzionale) Invia email phishing ai target con link alle pagine clonate (TODO)
5. **Visualizza Risultati** → Monitora credenziali catturate e metriche

---

## 📊 Menu Principale

- **Gestione Campagne**: Creare, modificare, eliminare campagne
- **Gestione Pagine Web**: Clonare e gestire pagine phishing
- **Gestione Email**: Configurare e inviare campagne email
- **Dati Catturati**: Visualizzare credenziali e log di accesso
- **Report**: Analisi e statistiche per campagna
- **Opzioni di Sistema**: Backup, import/export, API keys

---

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file [LICENSE](LICENSE) per dettagli.
