"""
Healthcare Agentic RAG System Demo
Demonstrates the capabilities of the medical AI system
"""

import os
import asyncio
import logging
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_demo():
    """Run interactive demo of the healthcare agentic system"""
    
    print("=" * 60)
    print("🏥 HEALTHCARE AGENTIC RAG SYSTEM DEMO")
    print("=" * 60)
    print()
    
    try:
        # Import and initialize the system
        from autogen_configs import get_healthcare_system
        
        print("🔄 Initializing healthcare system...")
        healthcare_system = get_healthcare_system()
        print("✅ Healthcare system initialized successfully!")
        print()
        
        # Demo queries
        demo_queries = [
            {
                "question": "What are the current guidelines for diabetes screening in adults?",
                "agent": "clinical",
                "description": "Clinical guidelines query"
            },
            {
                "question": "What is our patient satisfaction rate for diabetes care?",
                "agent": "data_analyst", 
                "description": "Data analysis query"
            },
            {
                "question": "What are the side effects of metformin?",
                "agent": "clinical",
                "description": "Drug information query"
            },
            {
                "question": "Show me the trend in HbA1c levels over the past year",
                "agent": "data_analyst",
                "description": "Trend analysis query"
            }
        ]
        
        print("🧪 Running demo queries...")
        print()
        
        for i, query in enumerate(demo_queries, 1):
            print(f"📋 Query {i}: {query['description']}")
            print(f"❓ Question: {query['question']}")
            print(f"🤖 Agent: {query['agent']}")
            print("-" * 50)
            
            try:
                if query['agent'] == 'clinical':
                    response = healthcare_system.chat_with_clinical_assistant(query['question'])
                else:
                    response = healthcare_system.chat_with_data_analyst(query['question'])
                
                print(f"💬 Response: {response[:300]}...")
                if len(response) > 300:
                    print("   [Response truncated for demo]")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            print()
            print("=" * 60)
            print()
        
        # Interactive mode
        print("🎯 INTERACTIVE MODE")
        print("Enter your medical questions (type 'quit' to exit)")
        print("Prefix with 'data:' for data analysis or 'clinical:' for clinical research")
        print()
        
        while True:
            try:
                user_input = input("🩺 Your question: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input:
                    continue
                
                # Determine agent type
                if user_input.lower().startswith('data:'):
                    question = user_input[5:].strip()
                    agent_type = 'data_analyst'
                elif user_input.lower().startswith('clinical:'):
                    question = user_input[9:].strip()
                    agent_type = 'clinical'
                else:
                    question = user_input
                    agent_type = 'clinical'  # Default
                
                print(f"\n🤖 Processing with {agent_type} agent...")
                
                if agent_type == 'clinical':
                    response = healthcare_system.chat_with_clinical_assistant(question)
                else:
                    response = healthcare_system.chat_with_data_analyst(question)
                
                print(f"\n💬 Response:\n{response}")
                print("\n" + "=" * 60 + "\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}\n")
        
        print("\n👋 Demo completed. Thank you!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ System error: {e}")
        logger.error(f"Demo failed: {e}")

def test_api_endpoints():
    """Test the API endpoints"""
    import requests
    import json
    
    print("🌐 TESTING API ENDPOINTS")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test endpoints
    endpoints = [
        {"method": "GET", "url": "/", "description": "Root endpoint"},
        {"method": "GET", "url": "/health", "description": "Health check"},
        {"method": "GET", "url": "/agents/info", "description": "Agent information"},
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Testing {endpoint['description']}...")
            
            if endpoint["method"] == "GET":
                response = requests.get(f"{base_url}{endpoint['url']}")
            
            if response.status_code == 200:
                print(f"✅ {endpoint['url']} - OK")
                print(f"   Response: {json.dumps(response.json(), indent=2)[:200]}...")
            else:
                print(f"❌ {endpoint['url']} - Status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint['url']} - Connection failed (API not running?)")
        except Exception as e:
            print(f"❌ {endpoint['url']} - Error: {e}")
        
        print()
    
    # Test query endpoint
    try:
        print("Testing medical query endpoint...")
        query_data = {
            "question": "What are the symptoms of diabetes?",
            "agent_type": "clinical",
            "include_sources": True
        }
        
        response = requests.post(
            f"{base_url}/query",
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Query endpoint - OK")
            result = response.json()
            print(f"   Answer: {result.get('answer', 'No answer')[:200]}...")
        else:
            print(f"❌ Query endpoint - Status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Query endpoint - Connection failed (API not running?)")
    except Exception as e:
        print(f"❌ Query endpoint - Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        test_api_endpoints()
    else:
        run_demo()