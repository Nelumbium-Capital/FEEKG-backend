#!/usr/bin/env python3
"""
Setup Event_risk repository in AllegroGraph
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from franz.openrdf.connect import ag_connect

def main():
    ag_url = os.getenv('AG_URL', 'https://qa-agraph.nelumbium.ai/')
    ag_user = os.getenv('AG_USER', 'sadmin')
    ag_pass = os.getenv('AG_PASS')
    ag_repo = os.getenv('AG_REPO', 'Event_risk')
    ag_catalog = os.getenv('AG_CATALOG', 'mycatalog')

    print(f"Connecting to AllegroGraph...")
    print(f"  URL: {ag_url}")
    print(f"  User: {ag_user}")
    print(f"  Catalog: {ag_catalog}")
    print(f"  Repository: {ag_repo}")

    try:
        # ag_connect with create=True will create the repository if it doesn't exist
        conn = ag_connect(
            repo=ag_repo,
            catalog=ag_catalog,
            host=ag_url,
            user=ag_user,
            password=ag_pass,
            create=True,  # Create if doesn't exist
            clear=False   # Don't clear existing data
        )

        # Check size
        size = conn.size()
        print(f"\n✅ Successfully connected to repository '{ag_repo}'")
        print(f"   Current triple count: {size}")

        conn.close()
        print(f"\n✅ Repository is ready for use!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
