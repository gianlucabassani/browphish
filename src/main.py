import sys
from pathlib import Path
import logging
import colorama

# Aggiungi la directory src al Python path
src_path = str(Path(__file__).parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importa la classe CLI principale
from cli.phish_cli import BrowphishCLI
from cli.utils import clear_screen
from db.manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("browphish.main")

def main():
    clear_screen()
    colorama.init(autoreset=True)
    print("Avvio Browphish...")
    db = DatabaseManager.get_instance()
    db.init_schema()
    cli = BrowphishCLI()
    try:
        cli.run()
        
    except KeyboardInterrupt:
        print("\n\ Chiusura di Browphish in corso...")
        db.disconnect()
        sys.exit(0)

if __name__ == "__main__":
    main()
