#!/usr/bin/env python3
"""
BROWPHISH - Complete Workflow Test Script
Simulates every function available in the CLI
"""

import sys
from pathlib import Path
from colorama import Fore, Style, init

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Initialize colorama
init(autoreset=True)

from db.manager import DatabaseManager
from modules.campaign_managers import campaign_manager
from modules.web_pages.page_generator import (
    clone_webpage, 
    save_phishing_page_to_db,
    get_phishing_page_by_name,
    create_phishing_campaign
)


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.db = DatabaseManager.get_instance("data/test_workflow.db")
        self.current_section = ""
    
    def header(self, text):
        """Print section header"""
        self.current_section = text
        print(f"\n{Fore.LIGHTRED_EX}{'='*60}")
        print(f"█ {Fore.WHITE}{text:^56}{Fore.LIGHTRED_EX} █")
        print(f"{'='*60}{Style.RESET_ALL}\n")
    
    def test(self, description, condition, error_msg=""):
        """Test a condition"""
        if condition:
            print(f"{Fore.GREEN}✅ {description}{Style.RESET_ALL}")
            self.passed += 1
            return True
        else:
            print(f"{Fore.RED}❌ {description}")
            if error_msg:
                print(f"   Error: {error_msg}{Style.RESET_ALL}")
            self.failed += 1
            return False
    
    def run_all_tests(self):
        """Execute all test scenarios"""
        try:
            # Initialize
            self.test_database_initialization()
            
            # Campaign operations
            self.test_campaign_creation()
            self.test_campaign_retrieval()
            self.test_campaign_update()
            self.test_campaign_association()
            self.test_campaign_statistics()
            self.test_campaign_termination()
            
            # Page operations
            self.test_page_creation()
            self.test_page_retrieval()
            
            # Data operations
            self.test_database_methods()
            
            # Utilities
            self.test_utilities()
            
            # Print summary
            self.print_summary()
            
        except Exception as e:
            print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()
            return False
        
        return self.failed == 0
    
    def test_database_initialization(self):
        """Test 1: Database Initialization"""
        self.header("TEST 1: Database Initialization")
        
        try:
            self.db.init_schema()
            self.test("Database connection established", self.db.connection is not None)
            self.test("Database file created", Path("data/test_workflow.db").exists())
            self.test("Tables exist", len(self.db.get_tables()) > 0)
        except Exception as e:
            self.test("Database initialization", False, str(e))
    
    def test_campaign_creation(self):
        """Test 2: Campaign Creation"""
        self.header("TEST 2: Campaign Creation")
        
        try:
            # Create entity first
            entity_id = self.db.get_or_create_entity("test.example.com", "domain")
            self.test("Entity created", entity_id is not None)
            
            # Create campaign
            campaign_id = campaign_manager.create_campaign(
                "Test Campaign 1",
                "Testing campaign creation",
                entity_id,
                self.db
            )
            self.test("Campaign created", campaign_id is not None and campaign_id > 0)
            self.campaign_id = campaign_id
            
            # Verify stored
            campaign = campaign_manager.get_campaign_by_id(campaign_id, self.db)
            self.test("Campaign stored correctly", campaign is not None)
            self.test("Campaign name correct", campaign['name'] == "Test Campaign 1")
            self.test("Campaign status is active", campaign['status'] == 'active')
            
        except Exception as e:
            self.test("Campaign creation workflow", False, str(e))
    
    def test_campaign_retrieval(self):
        """Test 3: Campaign Retrieval"""
        self.header("TEST 3: Campaign Retrieval")
        
        try:
            campaigns = campaign_manager.get_campaigns(self.db)
            self.test("Get all campaigns", campaigns is not None)
            self.test("At least one campaign exists", len(campaigns) > 0)
            
            if hasattr(self, 'campaign_id'):
                campaign = campaign_manager.get_campaign_by_id(self.campaign_id, self.db)
                self.test("Get campaign by ID", campaign is not None)
                self.test("Retrieved campaign is correct", 
                         campaign['id'] == self.campaign_id)
            
        except Exception as e:
            self.test("Campaign retrieval", False, str(e))
    
    def test_campaign_update(self):
        """Test 4: Campaign Update"""
        self.header("TEST 4: Campaign Update")
        
        try:
            if not hasattr(self, 'campaign_id'):
                print(f"{Fore.YELLOW}Skipping: No campaign ID from previous test{Style.RESET_ALL}")
                return
            
            new_name = "Updated Test Campaign"
            new_desc = "Updated description"
            
            ok = campaign_manager.update_campaign(
                self.campaign_id,
                new_name,
                new_desc,
                self.db
            )
            
            self.test("Campaign update executed", ok)
            
            # Verify update
            campaign = campaign_manager.get_campaign_by_id(self.campaign_id, self.db)
            self.test("Campaign name updated", campaign['name'] == new_name)
            self.test("Campaign description updated", campaign['description'] == new_desc)
            
        except Exception as e:
            self.test("Campaign update", False, str(e))
    
    def test_campaign_association(self):
        """Test 5: Campaign Association"""
        self.header("TEST 5: Campaign Association with Pages")
        
        try:
            if not hasattr(self, 'campaign_id'):
                print(f"{Fore.YELLOW}Skipping: No campaign ID{Style.RESET_ALL}")
                return
            
            # Create a test page first
            page_entity_id = self.db.get_or_create_entity("google_login_phish", "email")
            domain_entity_id = self.db.get_or_create_entity("accounts.google.com", "domain")
            
            # Insert page manually
            with self.db.transaction() as cursor:
                cursor.execute("""
                    INSERT INTO phishing_pages 
                    (campaign_entity_id, page_entity_id, domain_entity_id, 
                     name, original_url, cloned_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    self.campaign_id,
                    page_entity_id,
                    domain_entity_id,
                    "google_login_phish",
                    "https://accounts.google.com/signin",
                    "/tmp/google_phish.html"
                ))
                page_id = cursor.lastrowid
            
            self.test("Page created for association", page_id is not None and page_id > 0)
            
            # Get campaign pages
            pages = campaign_manager.get_campaign_pages(self.campaign_id, self.db)
            self.test("Campaign pages retrieved", pages is not None)
            self.test("Page associated with campaign", len(pages) > 0)
            
        except Exception as e:
            self.test("Campaign association", False, str(e))
    
    def test_campaign_statistics(self):
        """Test 6: Campaign Statistics"""
        self.header("TEST 6: Campaign Statistics")
        
        try:
            if not hasattr(self, 'campaign_id'):
                print(f"{Fore.YELLOW}Skipping: No campaign ID{Style.RESET_ALL}")
                return
            
            stats = campaign_manager.get_campaign_stats(self.campaign_id, self.db)
            self.test("Campaign stats retrieved", stats is not None)
            self.test("Stats has total_credentials", 'total_credentials' in stats)
            self.test("Stats has unique_ips", 'unique_ips' in stats)
            self.test("Stats has today_credentials", 'today_credentials' in stats)
            
            print(f"\n   Stats: {stats}")
            
        except Exception as e:
            self.test("Campaign statistics", False, str(e))
    
    def test_campaign_termination(self):
        """Test 7: Campaign Termination"""
        self.header("TEST 7: Campaign Termination")
        
        try:
            if not hasattr(self, 'campaign_id'):
                print(f"{Fore.YELLOW}Skipping: No campaign ID{Style.RESET_ALL}")
                return
            
            # Create another campaign for termination test
            entity_id = self.db.get_or_create_entity("terminate.test.com", "domain")
            term_campaign_id = campaign_manager.create_campaign(
                "Campaign to Terminate",
                "This will be terminated",
                entity_id,
                self.db
            )
            
            # Terminate
            ok = campaign_manager.terminate_campaign(term_campaign_id, self.db)
            self.test("Campaign termination executed", ok)
            
            # Verify
            campaign = campaign_manager.get_campaign_by_id(term_campaign_id, self.db)
            self.test("Campaign status is terminated", campaign['status'] == 'terminated')
            
            # Delete
            ok = campaign_manager.delete_campaign(term_campaign_id, self.db)
            self.test("Campaign deletion executed", ok)
            
            # Verify deleted
            campaign = campaign_manager.get_campaign_by_id(term_campaign_id, self.db)
            self.test("Campaign deleted from database", campaign is None)
            
        except Exception as e:
            self.test("Campaign termination", False, str(e))
    
    def test_page_creation(self):
        """Test 8: Page Creation (without actual cloning)"""
        self.header("TEST 8: Page Creation & Metadata Storage")
        
        try:
            # Get or create entities
            page_entity_id = self.db.get_or_create_entity("test_phishing_page", "email")
            domain_entity_id = self.db.get_or_create_entity("test.example.com", "domain")
            
            self.test("Page entity created", page_entity_id is not None)
            self.test("Domain entity created", domain_entity_id is not None)
            
            # Simulate page storage (without actual cloning from web)
            with self.db.transaction() as cursor:
                cursor.execute("""
                    INSERT INTO phishing_pages 
                    (page_entity_id, domain_entity_id, name, original_url, cloned_path)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    page_entity_id,
                    domain_entity_id,
                    "test_page",
                    "https://test.example.com/login",
                    "/tmp/test_page.html"
                ))
                page_id = cursor.lastrowid
            
            self.test("Page metadata stored", page_id is not None and page_id > 0)
            self.page_id = page_id
            
        except Exception as e:
            self.test("Page creation", False, str(e))
    
    def test_page_retrieval(self):
        """Test 9: Page Retrieval"""
        self.header("TEST 9: Page Retrieval")
        
        try:
            pages_query = "SELECT * FROM phishing_pages"
            pages = self.db.execute_query(pages_query)
            self.test("Pages retrieved", pages is not None)
            self.test("At least one page exists", len(pages) > 0 if pages else False)
            
            if pages:
                print(f"   Found {len(pages)} page(s)")
            
        except Exception as e:
            self.test("Page retrieval", False, str(e))
    
    def test_database_methods(self):
        """Test 10: Database Manager Methods"""
        self.header("TEST 10: Database Manager Methods")
        
        try:
            # Test table checking
            table_exists = self.db.table_exists("phishing_campaigns")
            self.test("Table existence check", table_exists)
            
            # Test get tables
            tables = self.db.get_tables()
            self.test("Get all tables", tables is not None)
            self.test("Multiple tables exist", len(tables) > 0 if tables else False)
            
            if tables:
                print(f"   Tables: {', '.join(tables)}")
            
            # Test entity operations
            test_entity_id = self.db.get_or_create_entity("duplicate.test.com", "domain")
            test_entity_id_2 = self.db.get_or_create_entity("duplicate.test.com", "domain")
            self.test("Entity deduplication works", test_entity_id == test_entity_id_2)
            
        except Exception as e:
            self.test("Database methods", False, str(e))
    
    def test_utilities(self):
        """Test 11: CLI Utilities"""
        self.header("TEST 11: CLI Utilities")
        
        try:
            from cli.utils import clear_screen, prompt_for_input
            
            # Test imports
            self.test("CLI utils imported", True)
            self.test("clear_screen function exists", callable(clear_screen))
            self.test("prompt_for_input function exists", callable(prompt_for_input))
            
        except Exception as e:
            self.test("CLI utilities", False, str(e))
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n{Fore.LIGHTRED_EX}{'='*60}")
        print(f"█ {Fore.WHITE}{'TEST SUMMARY':^56}{Fore.LIGHTRED_EX} █")
        print(f"{'='*60}{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}✅ Passed: {self.passed}{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ Failed: {self.failed}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Total:  {total}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📈 Success Rate: {success_rate:.1f}%{Style.RESET_ALL}")
        
        print(f"\n{Fore.LIGHTRED_EX}{'='*60}{Style.RESET_ALL}\n")
        
        if self.failed == 0:
            print(f"{Fore.GREEN}{'🎉 ALL TESTS PASSED! 🎉':^60}{Style.RESET_ALL}\n")
            return True
        else:
            print(f"{Fore.RED}{'⚠️  SOME TESTS FAILED ⚠️':^60}{Style.RESET_ALL}\n")
            return False


def main():
    """Main entry point"""
    print(f"\n{Fore.LIGHTRED_EX}")
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   BROWPHISH - COMPLETE WORKFLOW TEST SIMULATION           ║
    ║   Testing all CLI functions and their integrations        ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    print(f"{Style.RESET_ALL}\n")
    
    runner = TestRunner()
    success = runner.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
