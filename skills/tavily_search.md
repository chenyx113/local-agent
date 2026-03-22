# Tavily Search Skill

## Description
Performs real-time web search using Tavily API to gather up-to-date information.

## Purpose
This skill allows the AI assistant to search for current information on the web when needed. It's useful for:
- Getting latest news and updates
- Researching current events
- Finding up-to-date statistics and data
- Accessing recent publications and reports
- Gathering current weather information
- Checking stock prices and financial data

## Input Parameters
- **query** (string): The search query to perform
- **search_depth** (string, optional): Search depth level ('basic' or 'advanced', default: 'advanced')
- **max_results** (integer, optional): Maximum number of results to return (default: 5)
- **include_images** (boolean, optional): Whether to include images in results (default: false)
- **include_raw_content** (boolean, optional): Whether to include raw content in results (default: false)

## Output
Returns a dictionary containing:
- **success** (boolean): Whether the search was successful
- **results** (list): List of search result items, each containing:
  - **title** (string): Title of the result
  - **url** (string): URL of the result
  - **content** (string): Content/snippet of the result
  - **score** (float): Relevance score of the result
- **total_results** (integer): Total number of results returned
- **search_time** (float): Time taken for the search in seconds
- **message** (string): Human-readable status message

## Examples
```
User: "What are the latest developments in AI?"
Assistant: Uses tavily_search skill with query="latest developments in AI"

User: "What's the current weather in New York?"
Assistant: Uses tavily_search skill with query="current weather New York"

User: "Find recent news about climate change"
Assistant: Uses tavily_search skill with query="recent news climate change" and search_depth="advanced"
```

## Implementation Notes
- Requires TAVILY_API_KEY environment variable to be set
- Uses Tavily's advanced search for better results
- Limits results to prevent information overload
- Includes error handling for API failures
- Supports both basic and advanced search modes
- Returns structured data that can be easily processed by the AI