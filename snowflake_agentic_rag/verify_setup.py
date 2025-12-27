#!/usr/bin/env python3
"""
Healthcare Agentic RAG System - Setup Verification
Verifies that all components are properly configured and working
"""

import os
import sys
import importlib
from pathlib import Path
from dotenv import load_dotenv

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_environment_vars():
    """Check required environment variables"""
    print("\n🔍 Checking Environment Variables...")
    
    required_vars = {
        "SNOWFLAKE_ACCOUNT": "Snowflake account identifier",
        "SNOWFLAKE_USER": "Snowflake username", 
        "SNOWFLAKE_PASSWORD": "Snowflake password"
    }
    
    optional_vars = {
        "OPENAI_API_KEY": "OpenAI API key",
        "GOOGLE_API_KEY": "Google API key",
        "DEEPSEEK_API_KEY": "DeepSeek API key"
    }
    
    missing_required = []
    missing_optional = []
    
    for var, desc in required_vars.items():
        if os.getenv(var):
            print(f"✅ {desc}: Set")
        else:
            print(f"❌ {desc}: Missing")
            missing_required.append(var)
    
    for var, desc in optional_vars.items():
        if os.getenv(var):
            print(f"✅ {desc}: Set")
        else:
            print(f"⚠️  {desc}: Not set")
            missing_optional.append(var)
    
    if missing_required:
        print(f"\n❌ Missing required variables: {missing_required}")
        return False
    
    if len(missing_optional) == len(optional_vars):
        print(f"\n⚠️  No LLM API keys configured. At least one is required.")
        return False
    
    return True

def check_python_dependencies():
    """Check if required Python packages are installed"""
    print("\n📦 Checking Python Dependencies...")
    
    required_packages = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("streamlit", "Streamlit web framework"),
        ("snowflake.snowpark", "Snowflake Snowpark"),
        ("autogen", "AutoGen framework"),
        ("dotenv", "Environment variables"),
        ("pydantic", "Data validation")
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {description}: Installed")
        except ImportError:
            print(f"❌ {description}: Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {missing_packages}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def check_project_files():
    """Check if all required project files exist"""
    print("\n📁 Checking Project Files...")
    
    required_files = [
        ("requirements.txt", "Python dependencies"),
        ("config_cortex_search.py", "Snowflake connector"),
        ("autogen_configs.py", "AutoGen configuration"),
        ("api.py", "FastAPI application"),
        ("streamlit_app.py", "Streamlit application"),
        ("streamlit_healthcare_system.py", "Streamlit healthcare system"),
        ("demo.py", "Demo script"),
        ("run.py", "Main launcher"),
        ("web_demo.html", "Web interface"),
        (".env.template", "Environment template")
    ]
    
    sql_files = [
        ("01_database_setup.sql", "Database setup"),
        ("02_cortex_search_service.sql", "Cortex Search setup"),
        ("03_semantic_model.yaml", "Semantic model"),
        ("04_cortex_agent_setup.sql", "Agent setup"),
        ("05_data_ingestion_pipeline.sql", "Data pipeline")
    ]
    
    all_good = True
    
    for filename, description in required_files:
        if not check_file_exists(filename, description):
            all_good = False
    
    for filename, description in sql_files:
        if not check_file_exists(filename, description):
            all_good = False
    
    return all_good

def test_snowflake_connection():
    """Test Snowflake connection"""
    print("\n❄️  Testing Snowflake Connection...")
    
    try:
        from config_cortex_search import SnowflakeConnector
        
        connector = SnowflakeConnector()
        
        # Test simple query
        result = connector.session.sql("SELECT CURRENT_VERSION()").collect()
        if result:
            print(f"✅ Snowflake connection successful")
            print(f"   Version: {result[0][0]}")
            connector.close()
            return True
        else:
            print("❌ Snowflake connection failed - no results")
            return False
            
    except Exception as e:
        print(f"❌ Snowflake connection failed: {e}")
        return False

def test_autogen_setup():
    """Test AutoGen configuration"""
    print("\n🤖 Testing AutoGen Setup...")
    
    try:
        from autogen_configs import HealthcareAgentConfig
        
        config = HealthcareAgentConfig()
        
        if len(config.config_list) > 0:
            print(f"✅ AutoGen configured with {len(config.config_list)} LLM provider(s)")
            for i, llm_config in enumerate(config.config_list):
                model = llm_config.get('model', 'Unknown')
                print(f"   {i+1}. {model}")
            return True
        else:
            print("❌ No LLM providers configured")
            return False
            
    except Exception as e:
        print(f"❌ AutoGen setup failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🏥 Healthcare Agentic RAG System - Setup Verification")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Run all checks
    checks = [
        ("Project Files", check_project_files),
        ("Environment Variables", check_environment_vars),
        ("Python Dependencies", check_python_dependencies),
        ("AutoGen Setup", test_autogen_setup),
        ("Snowflake Connection", test_snowflake_connection)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ {check_name} check failed with error: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("\nYour Healthcare Agentic RAG System is ready to use!")
        print("\nNext steps:")
        print("  • Run Streamlit app: python run.py streamlit")
        print("  • Run demo: python run.py demo")
        print("  • Start API: python run.py api")
        print("  • Open web interface: web_demo.html")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("\nPlease fix the issues above before proceeding.")
        print("Refer to the README.md for detailed setup instructions.")
        sys.exit(1)

if __name__ == "__main__":
    main()