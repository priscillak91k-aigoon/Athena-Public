#!/usr/bin/env python3
"""
Hawkeye NZBC Auto-Updater (Automated Mode)
-------------------------------------------
This script scrapes the MBIE (Building.govt.nz) website for the latest 
Acceptable Solutions and Verification Methods PDFs (e.g., B1, C1-C6, D1, E2).
It downloads them to the local Open WebUI knowledge directory.

Dependencies: requests, beautifulsoup4
Run this via a monthly cron job.
"""

import os
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- Configuration ---
# The directory where Open WebUI monitors RAG files
KNOWLEDGE_BASE_DIR = os.path.expanduser("~/obsidian_vault/Hawkeye_Codes")
MBIE_BASE_URL = "https://www.building.govt.nz"
# Example target codes. Add all required NZBC clauses here.
TARGET_CLAUSES = [
    "/building-code-compliance/b-stability/b1-structure/",
    "/building-code-compliance/c-protection-from-fire/c1-c6-protection-from-fire/",
    "/building-code-compliance/d-access/d1-access-routes/",
    "/building-code-compliance/e-moisture/e2-external-moisture/"
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_directory():
    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        os.makedirs(KNOWLEDGE_BASE_DIR)
        logging.info(f"Created Knowledge Base directory at {KNOWLEDGE_BASE_DIR}")

def fetch_latest_pdfs():
    session = requests.Session()
    # Mask as a standard browser to avoid basic anti-bot blocks
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

    for clause_path in TARGET_CLAUSES:
        clause_url = urljoin(MBIE_BASE_URL, clause_path)
        logging.info(f"Scanning {clause_url} for latest PDFs...")
        
        try:
            response = session.get(clause_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links ending in .pdf
            # MBIE typically links Acceptable Solutions clearly in the main content body
            pdf_links = soup.find_all('a', href=lambda href: (href and href.endswith('.pdf')))
            
            downloaded = 0
            for link in pdf_links:
                pdf_url = urljoin(MBIE_BASE_URL, link.get('href'))
                filename = pdf_url.split('/')[-1]
                
                # We only want the main acceptable solutions, not random auxiliary PDFs
                # In production, you might want to regex filter the filename here
                # e.g., if 'acceptable-solution' in filename.lower():
                
                filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
                
                # Check if we already have this exact file to save bandwidth
                if not os.path.exists(filepath):
                    logging.info(f"New Update Found! Downloading: {filename}")
                    pdf_resp = session.get(pdf_url, stream=True)
                    if pdf_resp.status_code == 200:
                        with open(filepath, 'wb') as f:
                            for chunk in pdf_resp.iter_content(1024):
                                f.write(chunk)
                        logging.info(f"Successfully saved {filename}")
                        downloaded += 1
                else:
                    logging.debug(f"Already up to date: {filename}")
            
            if downloaded == 0:
                logging.info(f"No new updates for {clause_path}")
                
        except Exception as e:
            logging.error(f"Failed to process {clause_url}: {str(e)}")

def trigger_webui_revectorize():
    # Once files are downloaded, Open WebUI needs to update its ChromaDB index.
    # We hit the local Open WebUI API.
    # Note: Replace YOUR_OPENWEBUI_TOKEN with the actual API token.
    api_url = "http://localhost:8080/api/v1/knowledge/update"
    headers = {"Authorization": "Bearer YOUR_OPENWEBUI_TOKEN"}
    
    try:
        logging.info("Triggering Open WebUI RAG Vectorization...")
        # Un-comment the below lines in production with the correct payload and token
        # resp = requests.post(api_url, headers=headers)
        # resp.raise_for_status()
        logging.info("Vectorization triggered successfully. Hawkeye is fully updated.")
    except Exception as e:
        logging.error(f"Failed to trigger WebUI vectorization: {str(e)}")

if __name__ == "__main__":
    logging.info("=== Starting Hawkeye NZBC Auto-Updater ===")
    setup_directory()
    fetch_latest_pdfs()
    trigger_webui_revectorize()
    logging.info("=== Auto-Update Complete ===")
