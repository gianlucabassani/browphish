Roadmap Browphish - Alpha Version

Obiettivo
Rilasciare una versione alpha stabile e minimamente funzionante del toolkit Browphish, con un flusso end-to-end testabile e capacità avanzate per simulazioni di phishing realistiche.

1. Fase 1: Flusso Minimo Funzionante (MVP) & Fondamenta Tecniche
1.1 Collegamento CLI e Moduli (Completato/In Corso):

Assicurarsi che ogni voce del menu CLI richiami una funzione reale (anche stub) dei moduli.

[X] Creazione/Gestione pagine phishing → modules/web_pages/page_generator.py

[X] Gestione campagne email → modules/email/email_sender.py

[X] Visualizzazione dati raccolti → query su DB (captured_data_menu.py)

[X] Avvio server phishing → modules/web_pages/web_server.py (server Flask temporaneo)

[X] Report/statistiche → reports_menu.py (stub/report base)

[X] Opzioni sistema → system_options_menu.py (gestione config/log)

1.2 Flusso End-to-End di Base (Completato/In Corso):

[X] Creazione campagna (inserimento in DB, scelta template).

[ ] Invio email di phishing (a target fittizi/reali): Implementare modules/email/email_sender.py per inviare email realmente (non solo simulate). Loggare l'invio.

[X] Avvio server web per landing page (collegata a campagna).

[X] Cattura credenziali e salvataggio su DB.

[X] Visualizzazione dati raccolti su CLI.

1.3 Logging e Configurazione (Completato/In Corso):

[X] Logging uniforme in tutti i moduli.

[ ] Caricamento e validazione config da .env o file di configurazione all’avvio (per credenziali SMTP, API keys, ecc.).

1.4 Pulizia e Path (Completato/In Corso):

[X] Usare path relativi e centralizzati (no hardcoded).

[X] Unificare gestione template/email/pagine.

2. Fase 2: Realismo e Credibilità dell'Attacco
2.1 Gestione Domini e Sottodomini:

[ ] Integrazione Acquisto/Gestione Domini: Funzionalità per gestire domini di phishing (es. domini look-alike). (Nota: l'acquisto effettivo sarà manuale o tramite integrazione con registrar API, ma il tool deve gestirli).

[ ] Configurazione DNS automatizzata: Assistenza nella configurazione di record DNS (A, CNAME, MX) per i domini di phishing.

2.2 Supporto HTTPS/SSL (Cruciale):

[ ] Integrazione Let's Encrypt: Automatizzare l'ottenimento e il rinnovo di certificati SSL/TLS per i domini di phishing (modules/web_pages/server_manager.py). Questo è vitale per la credibilità.

[ ] Configurazione del server Flask per servire pagine via HTTPS.

2.3 Invio Email Avanzato:

[ ] Configurazione SMTP RobustA: Permettere la configurazione di più server SMTP (con autenticazione, porta, crittografia TLS/SSL).

[ ] Personalizzazione Email Dinamica: Ampliare la gestione dei template email (email_campaign_menu.py) per includere campi dinamici (es. nome destinatario, link unici per il tracciamento).

[ ] Bypass Filtri Email (SPF/DKIM/DMARC): Implementare opzioni per specificare l'envelope sender e header personalizzati per migliorare la deliverability delle email e superare i controlli SPF/DKIM/DMARC.

2.4 Clonazione Pagine Web Avanzata:

[ ] Gestione JavaScript/Risorse Complesse: Migliorare il page_generator.py per gestire meglio pagine con JavaScript complesso, CSS dinamico e risorse esterne, assicurando che tutti i link interni ed esterni siano riscritti correttamente.

[ ] Iniezione Script Custom: Possibilità di iniettare script JavaScript personalizzati nella pagina clonata (es. per fingerprinting, tracciamento avanzato).

3. Fase 3: Gestione Campagne e Analisi Avanzata
3.1 Gestione Target e Liste:

[ ] Importazione Liste Destinatari: Funzionalità per importare massivamente liste di indirizzi email (da CSV/TXT) per le campagne.

[ ] Segmentazione Target: Possibilità di suddividere i destinatari in gruppi per campagne specifiche.

3.2 Campagne Complesse:

[ ] Scenari di Phishing: Definizione di scenari di attacco predefiniti o personalizzabili (es. finto avviso HR, aggiornamento password).

[ ] Workflow Campagna: Gestione del flusso completo di una campagna: selezione template email, selezione pagina di atterraggio, lista target, scheduling invio.

3.3 Reportistica e Statistiche Dettagliate (reports_menu.py):

[ ] Tracking Interazioni in Tempo Reale: Tracciamento preciso di:

Aperture Email (tramite tracking pixel).

Click sui Link (con reindirizzamenti unici).

Invii Credenziali.

Visitatori Unici/Totali.

[ ] Timeline Utente: Visualizzazione della sequenza di azioni di un utente (email aperta, link cliccato, credenziali inserite).

[ ] Reportistica Grafica: Generazione di grafici e visualizzazioni per le metriche chiave (es. percentuale di successo, credenziali catturate per campagna/giorno).

[ ] Esportazione Dati: Funzionalità per esportare i dati catturati e i report in formati comuni (CSV, JSON).

3.4 Evasione e Stealth:

[ ] Anti-Crawler/Anti-Sandbox: Implementare tecniche per rilevare e bloccare l'accesso da parte di bot, crawler e sandbox di sicurezza.

[ ] Modifica dei Parametri URL: Randomizzazione o obfuscazione dei parametri di tracciamento nelle URL generate.

4. Fase 4: Estensioni e Funzionalità Avanzate
4.1 Supporto Multi-Factor Authentication (MFA) Bypass (Complesso):

[ ] Integrazione Reverse Proxy (Evilginx2-like): Esplorare l'integrazione o la compatibilità con strumenti come Evilginx2 per intercettare e inoltrare le credenziali e i token 2FA in tempo reale. Questo richiederebbe una revisione significativa dell'architettura del server.

4.2 Gestione Allegati Malevoli:

[ ] Possibilità di caricare e servire allegati malevoli (es. documenti con macro) e tracciare i download e le interazioni.

4.3 Integrazione API (Opzionale):

[ ] Sviluppare un'API RESTful per consentire l'automazione delle campagne e l'integrazione con altri strumenti di Red Teaming.

4.4 Interfaccia Utente Web (Opzionale - Maggiore Riprogettazione):

[ ] Considerare lo sviluppo di un'interfaccia utente grafica basata sul web per semplificare la gestione delle campagne, simile a Gophish. Questo è un lavoro significativo che potrebbe essere una roadmap a sé stante.