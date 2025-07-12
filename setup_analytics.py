#!/usr/bin/env python
"""
Script to help setup the analytics chat ID for the Password Tool Bot.
This will fetch recent updates from your analytics bot and extract chat IDs.

Usage:
    python setup_analytics.py
"""
import os
import json
import logging
import argparse
import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def setup_analytics_chat_id():
    # Load environment variables
    load_dotenv()
    
    # Get analytics bot token
    analytics_bot_token = os.getenv("ANALYTICS_BOT_TOKEN")
    if not analytics_bot_token:
        logger.error("ANALYTICS_BOT_TOKEN not found in .env file!")
        logger.info("Please set ANALYTICS_BOT_TOKEN in your .env file first.")
        return False
    
    # Check current analytics chat ID
    current_chat_id = os.getenv("ANALYTICS_CHAT_ID")
    if current_chat_id and current_chat_id != "YOUR_CHAT_ID":
        logger.info(f"Current ANALYTICS_CHAT_ID: {current_chat_id}")
        confirm = input("Would you like to update it? (y/n): ").lower()
        if confirm != 'y':
            logger.info("Setup canceled. Keeping current chat ID.")
            return False
    
    # Instructions
    print("\n" + "="*80)
    print("ANALYTICS CHAT ID SETUP")
    print("="*80)
    print("\nTo set up your analytics chat ID:")
    print("1. Open Telegram and search for your analytics bot")
    print("2. Start a chat with the bot and send a message (e.g., 'Hello')")
    print("3. This script will now try to fetch your chat ID\n")
    input("Press Enter to continue...")
    
    # Fetch updates from the bot
    url = f"https://api.telegram.org/bot{analytics_bot_token}/getUpdates"
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data.get('ok'):
            logger.error(f"API Error: {data.get('description', 'Unknown error')}")
            return False
        
        updates = data.get('result', [])
        if not updates:
            logger.warning("No updates found. Make sure you've sent a message to your analytics bot.")
            return False
        
        # Extract chat IDs
        chat_ids = []
        for update in updates:
            if 'message' in update and 'chat' in update['message']:
                chat_id = update['message']['chat']['id']
                chat_type = update['message']['chat']['type']
                chat_title = update['message']['chat'].get('title')
                chat_username = update['message']['chat'].get('username')
                chat_first_name = update['message']['chat'].get('first_name')
                
                chat_name = chat_title or chat_username or f"{chat_first_name or 'Unknown'}"
                
                chat_ids.append({
                    'id': chat_id,
                    'type': chat_type,
                    'name': chat_name
                })
        
        if not chat_ids:
            logger.warning("No chat IDs found in updates.")
            return False
        
        # Remove duplicates
        unique_chats = []
        seen = set()
        for chat in chat_ids:
            if chat['id'] not in seen:
                unique_chats.append(chat)
                seen.add(chat['id'])
        
        # Display found chat IDs
        print("\nFound the following chats:")
        for i, chat in enumerate(unique_chats):
            print(f"{i+1}. ID: {chat['id']} - Type: {chat['type']} - Name: {chat['name']}")
        
        # Let user select a chat ID
        if len(unique_chats) == 1:
            # If only one chat ID found, use it
            selected_chat = unique_chats[0]
            confirm = input(f"\nUse chat ID {selected_chat['id']} for analytics? (y/n): ").lower()
            if confirm != 'y':
                logger.info("Setup canceled.")
                return False
        else:
            # If multiple chat IDs found, let user select one
            while True:
                try:
                    selection = int(input("\nSelect a chat ID by number: "))
                    if 1 <= selection <= len(unique_chats):
                        selected_chat = unique_chats[selection-1]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(unique_chats)}")
                except ValueError:
                    print("Please enter a valid number")
        
        # Update .env file
        env_file = ".env"
        new_chat_id = str(selected_chat['id'])
        
        with open(env_file, 'r') as file:
            lines = file.readlines()
        
        with open(env_file, 'w') as file:
            chat_id_found = False
            for line in lines:
                if line.startswith("ANALYTICS_CHAT_ID="):
                    file.write(f"ANALYTICS_CHAT_ID={new_chat_id}\n")
                    chat_id_found = True
                else:
                    file.write(line)
            
            # If ANALYTICS_CHAT_ID line not found, add it
            if not chat_id_found:
                file.write(f"\nANALYTICS_CHAT_ID={new_chat_id}\n")
        
        logger.info(f"Successfully updated ANALYTICS_CHAT_ID to {new_chat_id} in .env file")
        logger.info("Restart your bot for the changes to take effect.")
        return True
        
    except Exception as e:
        logger.error(f"Error fetching updates: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set up analytics chat ID for Password Tool Bot")
    args = parser.parse_args()
    
    if setup_analytics_chat_id():
        logger.info("Analytics chat ID setup completed successfully!")
    else:
        logger.info("Analytics chat ID setup failed or was cancelled.")
        logger.info("You can try again or set ANALYTICS_CHAT_ID manually in your .env file.") 