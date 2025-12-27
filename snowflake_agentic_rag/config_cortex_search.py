import os
import logging
from typing import Optional, Dict, Any
from snowflake.snowpark import Session
from snowflake.core import Root
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SnowflakeConnector:
    """Manages Snowflake connection and Cortex Search operations"""
    
    def __init__(self):
        self.session: Optional[Session] = None
        self.root: Optional[Root] = None
        self._connect()
    
    def _connect(self):
        """Initialize Snowflake connection using environment variables"""
        try:
            # connection_parameters = {
            #     "account": os.getenv("UPONRequest"),
            #     "user": os.getenv("UPONRequest"),
            #     "password": os.getenv("UPONRequest"),
            #     "role": os.getenv("SNOWFLAKE_ROLE", "SYSADMIN"),
            #     "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            #     "database": os.getenv("SNOWFLAKE_DATABASE", "KNOWLEDGE_DB"),
            #     "schema": os.getenv("SNOWFLAKE_SCHEMA", "AI_SERVICES")
            # }
            connection_parameters = {
                "account": "UPONRequest",
                "user": "UPONRequest",
                "password": "UPONRequest",
                "role": "SYSADMIN",
                "warehouse": "COMPUTE_WH",
                "database": "KNOWLEDGE_DB",
                "schema": "AI_SERVICES"
            }
            
            # Validate required parameters
            required_params = ["account", "user", "password"]
            missing_params = [param for param in required_params if not connection_parameters[param]]
            if missing_params:
                raise ValueError(f"Missing required Snowflake parameters: {missing_params}")
            
            self.session = Session.builder.configs(connection_parameters).create()
            self.root = Root(self.session)
            logger.info("Successfully connected to Snowflake")
            
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            raise
    
    def search_documents(self, query: str, limit: int = 5) -> str:
        """
        Search medical documents using Cortex Search Service.
        Returns formatted results for LLM consumption.
        """
        try:
            if not self.session or not self.root:
                raise RuntimeError("Snowflake connection not established")
            
            # Use the document search service from your existing setup
            escaped_query = query.replace("'", "''")
            search_sql = f"""
            SELECT 
                chunk_id,
                document_name,
                chunk_text,
                category,
                department,
                relevance_score
            FROM TABLE(
                KNOWLEDGE_DB.AI_SERVICES.DOCUMENT_SEARCH_SERVICE(
                    query => '{escaped_query}',
                    limit => {limit}
                )
            )
            ORDER BY relevance_score DESC
            """
            
            results = self.session.sql(search_sql).collect()
            
            if not results:
                return "No relevant medical information found for this query."
            
            # Format results for LLM
            context = "Retrieved Medical Information:\n\n"
            for i, row in enumerate(results, 1):
                context += f"{i}. **{row['DOCUMENT_NAME']}** (Score: {row['RELEVANCE_SCORE']:.3f})\n"
                context += f"   Category: {row['CATEGORY']} | Department: {row['DEPARTMENT']}\n"
                context += f"   Content: {row['CHUNK_TEXT'][:500]}...\n\n"
            
            return context
            
        except Exception as e:
            logger.error(f"Error in document search: {e}")
            return f"Error searching medical documents: {str(e)}"
    
    def query_structured_data(self, question: str) -> str:
        """
        Query structured healthcare data using Cortex Analyst.
        """
        try:
            if not self.session:
                raise RuntimeError("Snowflake connection not established")
            
            # Use the structured data query function from your setup
            escaped_question = question.replace("'", "''")
            query_sql = f"CALL TOOL_QUERY_STRUCTURED_DATA('{escaped_question}');"
            result = self.session.sql(query_sql).collect()
            
            if result and len(result) > 0:
                return str(result[0][0])  # Return the result from the stored procedure
            else:
                return "No structured data results found for this query."
                
        except Exception as e:
            logger.error(f"Error in structured data query: {e}")
            return f"Error querying structured data: {str(e)}"
    
    def close(self):
        """Close Snowflake connection"""
        if self.session:
            self.session.close()
            logger.info("Snowflake connection closed")

# Global connector instance
snowflake_connector = SnowflakeConnector()

# Functions for AutoGen registration
def medical_document_search(query: str) -> str:
    """
    Search medical documents and guidelines in Snowflake.
    Use this for questions about medical procedures, policies, guidelines, and documentation.
    """
    return snowflake_connector.search_documents(query)

def medical_data_analysis(question: str) -> str:
    """
    Analyze structured medical data (metrics, statistics, trends).
    Use this for questions about patient statistics, treatment outcomes, and numerical analysis.
    """
    return snowflake_connector.query_structured_data(question)
