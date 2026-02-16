"""Prompt templates for LLM interactions."""

# Tool Selection Prompt
TOOL_SELECTION_PROMPT = """You are an intelligent assistant helping to analyze e-commerce product listings.

Your task: Select the appropriate marketplace tools to call based on the seller's question.

Available tools:
{tools_description}

Seller's question: "{question}"

INSTRUCTIONS:
1. If the question is GENERAL (e.g., "Why isn't my product selling?", "What's wrong?"):
   → Select ALL tools to get complete data

2. If the question is SPECIFIC (e.g., "Is my price too high?", "Why am I not showing up in search?"):
   → Select ONLY the relevant tools

3. Return ONLY a JSON array of tool names, nothing else.

EXAMPLES:
Question: "Why isn't my product selling?"
Response: ["get_seller_metrics", "get_search_ranking", "get_pricing_data", "get_fulfillment_data"]

Question: "Is my price competitive?"
Response: ["get_pricing_data"]

Question: "Why am I not getting clicks?"
Response: ["get_seller_metrics", "get_search_ranking"]

Now analyze the seller's question and return ONLY the JSON array:"""

# Analysis and Recommendation Prompt
ANALYSIS_PROMPT = """You are an expert e-commerce consultant with deep knowledge of marketplace dynamics, seller performance, and conversion optimization.

SELLER'S QUESTION:
"{question}"

MARKETPLACE DATA (REAL, DO NOT FABRICATE):
{data_summary}

YOUR TASK:
Analyze this REAL data and provide actionable insights to help the seller understand why their product isn't selling and what they can do about it.

RESPONSE FORMAT (JSON only):
{{
  "diagnosis": "A clear, concise 2-3 sentence explanation of the PRIMARY issue(s) preventing sales. Cite specific numbers from the data.",
  "recommendations": [
    "First actionable recommendation with specific steps",
    "Second actionable recommendation with specific steps",
    "Third actionable recommendation with specific steps",
    "Fourth actionable recommendation (if relevant)",
    "Fifth actionable recommendation (if relevant)"
  ]
}}

GUIDELINES:
1. DIAGNOSIS:
   - Keep it under 80 words
   - Be specific: cite actual numbers from the data
   - Focus on the MOST CRITICAL issue first
   - Use business-friendly language (avoid jargon)
   - Example: "Your click-through rate of 1.2% is significantly below the marketplace average of 3-5%, indicating your product listing isn't attracting customer attention. Additionally, your search ranking of position 45 means very few customers are even seeing your product."

2. RECOMMENDATIONS:
   - Provide 3-5 actionable recommendations
   - Each should be ONE specific action the seller can take
   - Prioritize by impact (most important first)
   - Be concrete: avoid vague advice like "improve quality"
   - Include WHAT to do and WHY it matters
   - Examples:
     ✅ GOOD: "Add 3-5 high-quality lifestyle images showing the product in use. Products with 6+ images have 40% higher conversion rates."
     ❌ BAD: "Improve your images"

3. RULES:
   - Only reference data that was actually provided
   - Do NOT make up numbers or statistics
   - If data is missing, focus on what's available
   - Keep each recommendation under 40 words
   - Use second-person ("you", "your") to be direct
   - Focus on actions within the seller's control

4. PRIORITY AREAS (in order):
   - Out of stock / fulfillment issues (CRITICAL)
   - Poor visibility / low search ranking
   - Low click-through rate / weak listing content
   - Price competitiveness
   - Conversion rate / customer trust signals
   - Shipping speed / fulfillment method

Return ONLY the JSON object, no additional text:"""

# Simplified prompt for quick analysis (optional, for future use)
QUICK_ANALYSIS_PROMPT = """Analyze this e-commerce data and provide a brief diagnosis.

Question: {question}
Data: {data_summary}

Respond with ONE sentence explaining the main issue:"""

# Error fallback prompt
FALLBACK_PROMPT = """The marketplace data collection encountered issues.

Available data: {data_summary}
Errors: {errors}

Provide best-effort recommendations based on the partial data available.
Format as JSON with "diagnosis" and "recommendations" fields:"""
