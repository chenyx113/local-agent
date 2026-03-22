import os
from typing import Dict, Any, List
from tavily import TavilyClient
import time


def tavily_search(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs real-time web search using Tavily API to gather up-to-date information.
    
    Args:
        parameters: Dictionary containing:
            - query (str): The search query to perform
            - search_depth (str, optional): Search depth level ('basic' or 'advanced', default: 'advanced')
            - max_results (int, optional): Maximum number of results to return (default: 5)
            - include_images (bool, optional): Whether to include images in results (default: False)
            - include_raw_content (bool, optional): Whether to include raw content in results (default: False)
    
    Returns:
        Dictionary containing:
            - success (bool): Whether the search was successful
            - results (list): List of search result items
            - total_results (int): Total number of results returned
            - search_time (float): Time taken for the search in seconds
            - message (str): Human-readable status message
    """
    try:
        # Extract parameters with defaults
        query = parameters.get('query', '')
        search_depth = parameters.get('search_depth', 'advanced')
        max_results = parameters.get('max_results', 5)
        include_images = parameters.get('include_images', False)
        include_raw_content = parameters.get('include_raw_content', False)
        
        # Validate required parameters
        if not query:
            return {
                "success": False,
                "results": [],
                "total_results": 0,
                "search_time": 0,
                "message": "No search query provided"
            }
        
        # Validate search depth
        if search_depth not in ['basic', 'advanced']:
            search_depth = 'advanced'
        
        # Get Tavily API key
        tavily_api_key = os.getenv('TAVILY_API_KEY')
        if not tavily_api_key:
            return {
                "success": False,
                "results": [],
                "total_results": 0,
                "search_time": 0,
                "message": "TAVILY_API_KEY environment variable not set"
            }
        
        # Initialize Tavily client
        try:
            tavily_client = TavilyClient(api_key=tavily_api_key)
        except Exception as e:
            return {
                "success": False,
                "results": [],
                "total_results": 0,
                "search_time": 0,
                "message": f"Failed to initialize Tavily client: {str(e)}"
            }
        
        # Perform search
        start_time = time.time()
        
        try:
            search_result = tavily_client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_images=include_images,
                include_raw_content=include_raw_content
            )
            
            search_time = time.time() - start_time
            
            # Process results
            results = []
            if search_result and 'results' in search_result:
                for item in search_result['results']:
                    result_item = {
                        "title": item.get('title', 'No title'),
                        "url": item.get('url', 'No URL'),
                        "content": item.get('content', 'No content'),
                        "score": item.get('score', 0.0)
                    }
                    results.append(result_item)
            
            total_results = len(results)
            
            return {
                "success": True,
                "results": results,
                "total_results": total_results,
                "search_time": search_time,
                "message": f"Successfully performed search with {total_results} results in {search_time:.2f} seconds"
            }
            
        except Exception as e:
            search_time = time.time() - start_time
            return {
                "success": False,
                "results": [],
                "total_results": 0,
                "search_time": search_time,
                "message": f"Search failed: {str(e)}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "results": [],
            "total_results": 0,
            "search_time": 0,
            "message": f"Error performing Tavily search: {str(e)}"
        }