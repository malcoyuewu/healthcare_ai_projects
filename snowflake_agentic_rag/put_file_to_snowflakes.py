import os
import logging
from pathlib import Path
from config_cortex_search import snowflake_connector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_file_to_snowflake_stage(local_file_path: str, stage_name: str = "medline_xml_stage"):
    """
    Upload a file to Snowflake stage using the existing snowflake_connector
    
    Args:
        local_file_path: Path to the local file to upload
        stage_name: Name of the Snowflake stage to create/use
    """
    
    if not snowflake_connector or not snowflake_connector.session:
        raise RuntimeError("Snowflake connection not available")
    
    try:
        session = snowflake_connector.session
        
        # Ensure we're using the correct database and schema
        logger.info("Setting database and schema context...")
        session.sql("USE DATABASE KNOWLEDGE_DB").collect()
        session.sql("USE SCHEMA RAW_STAGING").collect()
        
        # Verify the file exists
        file_path = Path(local_file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {local_file_path}")
        
        logger.info(f"File found: {file_path.name} ({file_path.stat().st_size} bytes)")
        
        # Create the stage if it doesn't exist (in RAW_STAGING schema)
        create_stage_sql = f"""
        CREATE STAGE IF NOT EXISTS KNOWLEDGE_DB.RAW_STAGING.{stage_name}
        DIRECTORY = (ENABLE = TRUE)
        COMMENT = 'Stage for medical XML files'
        """
        
        logger.info(f"Creating stage: {stage_name}")
        session.sql(create_stage_sql).collect()
        
        # Upload the file using PUT command
        # Convert to absolute path and use proper file:// format
        abs_path = file_path.resolve()
        put_sql = f"PUT file://{abs_path} @KNOWLEDGE_DB.RAW_STAGING.{stage_name} AUTO_COMPRESS=TRUE"
        
        logger.info(f"Uploading file: {abs_path}")
        result = session.sql(put_sql).collect()
        
        if result:
            for row in result:
                logger.info(f"Upload result: {row}")
        
        # Verify the file is there
        logger.info("Verifying upload...")
        list_sql = f"LIST @KNOWLEDGE_DB.RAW_STAGING.{stage_name}"
        files = session.sql(list_sql).collect()
        
        logger.info("Files in stage:")
        for file_info in files:
            logger.info(f"  - {file_info}")
        
        logger.info("✅ Upload successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise

def main():
    """Main function to upload the medical XML file"""
    
    # File to upload
    local_file_path = "/Users/malcowu/Downloads/mplus_topics_2025-12-27.xml"
    
    try:
        logger.info("🏥 Healthcare RAG - File Upload to Snowflake")
        logger.info("=" * 50)
        
        # Upload the file
        upload_file_to_snowflake_stage(local_file_path)
        
        logger.info("=" * 50)
        logger.info("✅ File upload completed successfully!")
        
        # Optional: Show how to process the uploaded file
        logger.info("\n💡 Next steps:")
        logger.info("1. The file is now in Snowflake stage: KNOWLEDGE_DB.RAW_STAGING.medline_xml_stage")
        logger.info("2. You can process it using the data ingestion pipeline")
        logger.info("3. Run: CALL PROCESS_UPLOADED_DOCUMENTS(); to chunk and index the content")
        
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        logger.info("💡 Please check the file path and try again")
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        logger.info("💡 Please check your Snowflake connection and permissions")

if __name__ == "__main__":
    main()
