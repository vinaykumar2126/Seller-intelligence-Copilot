# Seller Intelligence Copilot - Test Data

## Mock Listings

### listing_001 - Poor Performance Profile
**Scenario:** Multiple issues causing low sales

**Metrics:**
- Impressions: 5,000
- Clicks: 50
- CTR: 1% (LOW - benchmark is 3-4%)
- Conversions: 2
- Conversion Rate: 4%

**Search Ranking:**
- Average Rank: 45.5 (page 5)
- Keyword Match Score: 0.3/1.0 (POOR)
- Category: Electronics

**Pricing:**
- Seller Price: $299.99
- Median Competitor: $249.99
- Price Percentile: 85th (EXPENSIVE)
- Difference: +20%

**Fulfillment:**
- Shipping Days: 12 (SLOW)
- Return Policy: "30-day return, buyer pays shipping"
- In Stock: Yes
- Method: FBM (Fulfilled by Merchant)

**Expected Issues:**
1. Poor search visibility (page 5, low keyword score)
2. Overpriced compared to competitors (+20%)
3. Slow shipping (12 days)
4. Low CTR indicates title/image issues

---

### listing_002 - Excellent Performance Profile
**Scenario:** Well-optimized listing performing well

**Metrics:**
- Impressions: 15,000
- Clicks: 600
- CTR: 4% (GOOD)
- Conversions: 120
- Conversion Rate: 20% (EXCELLENT)

**Search Ranking:**
- Average Rank: 3.2 (page 1, top position)
- Keyword Match Score: 0.92/1.0 (EXCELLENT)
- Category: Home & Kitchen

**Pricing:**
- Seller Price: $49.99
- Median Competitor: $52.99
- Price Percentile: 35th (COMPETITIVE)
- Difference: -5.66% (cheaper)

**Fulfillment:**
- Shipping Days: 2 (FAST - likely Prime)
- Return Policy: "Free 30-day return"
- In Stock: Yes
- Method: FBA (Fulfilled by Amazon)

**Expected Analysis:**
- Strong performance across all metrics
- Good search optimization
- Competitive pricing
- Fast, reliable fulfillment

---

### listing_003 - Critical Issue Profile
**Scenario:** Out of stock problem causing zero sales

**Metrics:**
- Impressions: 200 (LOW)
- Clicks: 10
- CTR: 5% (GOOD when visible)
- Conversions: 0 (NONE)
- Conversion Rate: 0%

**Search Ranking:**
- Average Rank: 15.0 (page 2)
- Keyword Match Score: 0.65/1.0 (MODERATE)
- Category: Books

**Pricing:**
- Seller Price: $15.99
- Median Competitor: $12.99
- Price Percentile: 75th (SOMEWHAT EXPENSIVE)
- Difference: +23.1%

**Fulfillment:**
- Shipping Days: 5 (MODERATE)
- Return Policy: "15-day return, buyer pays shipping"
- In Stock: NO ⚠️ CRITICAL ISSUE
- Method: FBM

**Expected Issues:**
1. OUT OF STOCK (critical)
2. Price is 23% higher than competitors
3. Low impressions (possibly due to stock status)

---

## Test Queries

### General Analysis
```json
{
  "listing_id": "listing_001",
  "question": "Why is my product not selling?"
}
```

### Pricing-Specific
```json
{
  "listing_id": "listing_001",
  "question": "Is my pricing competitive?"
}
```

### Shipping-Specific
```json
{
  "listing_id": "listing_001",
  "question": "Are my shipping times affecting sales?"
}
```

### Visibility Question
```json
{
  "listing_id": "listing_001",
  "question": "Why isn't my listing showing up in searches?"
}
```

### Out of Stock
```json
{
  "listing_id": "listing_003",
  "question": "Why am I getting no sales?"
}
```

### Good Performance
```json
{
  "listing_id": "listing_002",
  "question": "Why is my product not selling?"
}
```

---

## Expected LLM Behavior

### For listing_001 (Poor Performance)
The LLM should:
1. Identify low CTR (1%) as a primary issue
2. Note overpricing (+20% above median)
3. Highlight poor search ranking (page 5)
4. Mention slow shipping (12 days)
5. Recommend specific actions for each issue

### For listing_002 (Excellent)
The LLM should:
1. Acknowledge strong performance
2. Note it IS selling well
3. Suggest minor optimizations to maintain position
4. Highlight what's working (fast shipping, good price, SEO)

### For listing_003 (Out of Stock)
The LLM should:
1. IMMEDIATELY flag out-of-stock as critical issue
2. Note this is likely the primary cause of zero conversions
3. Mention pricing as secondary issue
4. Recommend restocking urgently

---

## Tool Selection Logic

### "Why is my product not selling?" (General)
**Expected Tools:** ALL
- get_seller_metrics (to see traffic and conversions)
- get_search_ranking (to check visibility)
- get_pricing_data (to check competitiveness)
- get_fulfillment_data (to check shipping/stock)

### "Is my pricing competitive?" (Specific)
**Expected Tools:** 
- get_pricing_data (primary)
- get_seller_metrics (secondary - to see if price is causing low conversions)

### "Why isn't my listing visible?"
**Expected Tools:**
- get_search_ranking (primary)
- get_seller_metrics (to see impression data)

### "Are my shipping times too slow?"
**Expected Tools:**
- get_fulfillment_data (primary)
- get_seller_metrics (to see if it's affecting conversions)
