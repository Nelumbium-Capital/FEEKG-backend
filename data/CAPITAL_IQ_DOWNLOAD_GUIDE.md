# Capital IQ Bulk Download Guide

## What to Download

### Recommended Dataset: Financial Crisis Events (2007-2009)

**Scope:**
- **Time Period**: January 2007 - December 2009 (3 years)
- **Industries**: Financial Services, Banks, Investment Banking
- **Geography**: United States + Major International
- **Event Types**: All

**Expected Size:**
- Events: 500-2,000 rows
- File size: 50-200 MB
- Format: Excel (.xlsx) or CSV

---

## Step-by-Step Download Instructions

### Step 1: Access Capital IQ

1. Go to your university library portal
2. Find "Capital IQ" in databases
3. Login with university credentials
4. You'll be at: https://www.capitaliq.com

### Step 2: Navigate to Key Developments

```
Capital IQ Home
→ Screening & List Building
→ Key Developments Search
```

Or:
```
Top Menu → Companies
→ Key Developments
→ Advanced Search
```

### Step 3: Set Search Criteria

**Company Criteria:**
```
Industry:
☑ Banks
☑ Investment Banking & Brokerage
☑ Financial Services
☑ Insurance

Company Status:
☑ Public
☑ Private
☑ Delisted (IMPORTANT - includes Lehman!)

Geography:
☑ United States
☑ Europe (major markets)
☑ Asia (major markets)

Market Cap: All (or >$1B to focus on large institutions)
```

**Event Criteria:**
```
Date Range: 2007-01-01 to 2009-12-31

Event Types: (Select ALL or key ones)
☑ Bankruptcy/Restructuring
☑ Credit Rating Actions
☑ Earnings/Guidance
☑ M&A Announcements
☑ Stock Price Movements
☑ Management Changes
☑ Regulatory Actions
☑ Capital Raising
☑ Strategic Initiatives
```

### Step 4: Export Data

1. **Run Search** - Click "Search" or "Get Results"

2. **Select All Results**
   - Check box at top to select all
   - Or limit to 2,000 most relevant

3. **Export**
   ```
   Click "Export" button
   → Choose format: Excel (recommended) or CSV
   → Select columns (see below)
   → Download
   ```

4. **Required Columns:**
   ```
   ☑ Company Name
   ☑ Company ID (Capital IQ ID)
   ☑ Event Date
   ☑ Event Type
   ☑ Event Headline
   ☑ Event Description/Summary
   ☑ Key Parties Involved
   ☑ Event Impact/Significance
   ☑ Source
   ☑ Industry
   ☑ Geography
   ```

---

## After Download: File Organization

### Save File As:

```bash
# Put your downloaded file here:
feekg/data/capital_iq_raw/financial_crisis_2007_2009.xlsx

# Or if CSV:
feekg/data/capital_iq_raw/financial_crisis_2007_2009.csv
```

### File Naming Convention:

```
Format: [source]_[topic]_[startdate]_[enddate].[ext]

Examples:
✅ capitaliq_financial_crisis_2007_2009.xlsx
✅ capitaliq_banks_events_2007_2009.csv
✅ capitaliq_lehman_related_2007_2009.xlsx
```

---

## Alternative: Smaller Focused Download

If bulk download is too large, try:

### Option A: Lehman Brothers + Key Players Only

**Companies to include:**
```
- Lehman Brothers Holdings Inc.
- Bear Stearns Companies Inc.
- Merrill Lynch & Co Inc.
- American International Group (AIG)
- JPMorgan Chase & Co.
- Bank of America Corporation
- Citigroup Inc.
- Goldman Sachs Group Inc.
- Morgan Stanley
- Washington Mutual Inc.
```

**Filter:** Events mentioning these companies (2007-2009)
**Expected size:** 200-500 events

### Option B: Event Type Focused

**Download only critical event types:**
```
☑ Bankruptcy/Chapter 11
☑ Credit Rating Downgrades
☑ Major M&A
☑ Government Interventions
☑ Major Losses/Write-downs
```

**Expected size:** 100-300 events

---

## What If Capital IQ Won't Let You Bulk Download?

Some Capital IQ licenses limit exports. If you hit limits:

### Workaround 1: Multiple Smaller Exports

```
Split by year:
1. 2007 events only → export → save as capitaliq_2007.csv
2. 2008 events only → export → save as capitaliq_2008.csv
3. 2009 events only → export → save as capitaliq_2009.csv

I'll write code to merge them.
```

### Workaround 2: Query by Company

```
For each major company:
1. Search Lehman Brothers → export events
2. Search Bear Stearns → export events
3. Search AIG → export events
... etc

Save as:
- capitaliq_lehman.csv
- capitaliq_bear_stearns.csv
- capitaliq_aig.csv

I'll merge them all.
```

### Workaround 3: Use Capital IQ Excel Plugin

If available:
```
1. Open Excel
2. Capital IQ Excel Plugin → Login
3. Use formulas to pull data:
   =CIQ("IQ12345", "IQ_KEY_DEVELOPMENTS", "2007-01-01", "2009-12-31")
4. Can pull more data this way
```

---

## What Columns Do We Really Need?

**Minimum required columns:**
```
1. date           - Event date
2. company        - Company name
3. event_type     - Type of event
4. headline       - Short headline
5. description    - Longer description
```

**Nice to have columns:**
```
6. entities       - Related companies/people
7. impact         - Significance level
8. source         - News source
9. company_id     - Capital IQ ID
10. industry      - Industry classification
```

**We can work with anything!** Even if you only get 3-4 columns, I can process it.

---

## After You Download

### Next Steps:

1. **Save file to:**
   ```
   feekg/data/capital_iq_raw/[your_filename].xlsx
   ```

2. **Tell me:**
   ```
   - Filename
   - How many rows
   - What columns you have
   ```

3. **I will:**
   ```
   - Build processing pipeline
   - Extract Lehman Brothers case study
   - Create filtering tools
   - Generate visualizations
   ```

---

## Expected Dataset Statistics

### If you download full crisis data:

```
Time span: 3 years (2007-2009)
Events: ~500-2,000
Companies: ~100-300
Size: 50-200 MB

Lehman-related events: ~30-50
Bear Stearns events: ~20-30
AIG events: ~25-40
Other major events: ~400-1,800
```

### File will look like:

```
| Date       | Company        | Type              | Headline                          |
|------------|----------------|-------------------|-----------------------------------|
| 2007-06-15 | Bear Stearns   | Hedge Fund Loss   | Bear Stearns hedge funds collapse |
| 2008-03-14 | Bear Stearns   | Acquisition       | JPMorgan to acquire Bear Stearns  |
| 2008-09-15 | Lehman Brothers| Bankruptcy        | Lehman files for bankruptcy       |
| 2008-09-16 | AIG            | Government Bailout| Fed provides $85B to AIG          |
... (hundreds more rows)
```

---

## Troubleshooting

### Problem: "Export limit reached"

**Solution:** Export in smaller batches (by year, by company, or by event type)

### Problem: "Too many results to display"

**Solution:** Add more filters to narrow down, or export in chunks

### Problem: "Don't have access to Capital IQ"

**Solutions:**
1. Check WRDS (might have Capital IQ data)
2. Use Compustat (similar database)
3. I can create dataset from public sources

### Problem: "Columns don't match the template"

**Solution:** No problem! Just export whatever columns you have. I'll adapt the processing code.

---

## Ready to Process

Once you have the file, we'll build a pipeline that can:

✅ Load bulk Capital IQ data
✅ Clean and normalize events
✅ Filter for Lehman Brothers case study
✅ Extract event evolution chains
✅ Generate RDF triples
✅ Create visualizations
✅ Support multiple case studies

---

**Bottom line:** Download as much as you can get from Capital IQ (aim for 500+ events), save to `data/capital_iq_raw/`, and I'll handle the rest!
