# Lehman Brothers Pipeline - Quick Start

## 3-Step Pipeline (After You Download Capital IQ Data)

### Step 1: Process Capital IQ Data
```bash
./venv/bin/python ingestion/process_capital_iq.py \
    --input data/capital_iq_raw/your_file.xlsx \
    --filter lehman
```

**Output:** `data/capital_iq_processed/lehman_case_study.json`

---

### Step 2: Load into Neo4j + Run Evolution
```bash
./venv/bin/python ingestion/load_lehman.py
```

**Creates:**
- Entities (financial institutions, regulators)
- Events (chronological timeline)
- Risks (credit, systemic, market)
- Evolution links (21+ connections with causality scores)

---

### Step 3: Convert to RDF Triples
```bash
./venv/bin/python scripts/convert_lehman_to_rdf.py
```

**Output:**
- `results/lehman_graph.ttl` (Turtle format)
- `results/lehman_graph.xml` (RDF/XML format)
- `results/lehman_graph.nt` (N-Triples format)

**Optional: Upload to AllegroGraph**
```bash
./venv/bin/python scripts/convert_lehman_to_rdf.py --upload
```

---

## Alternative Commands

### Process All Capital IQ Data (Not Just Lehman)
```bash
./venv/bin/python ingestion/process_capital_iq.py \
    --input data/capital_iq_raw/financial_crisis_2007_2009.xlsx \
    --filter all \
    --output data/capital_iq_processed/all_events.json
```

### Process Specific Companies
```bash
./venv/bin/python ingestion/process_capital_iq.py \
    --input data/capital_iq_raw/financial_crisis_2007_2009.xlsx \
    --companies "Lehman Brothers,Bear Stearns,AIG,Merrill Lynch"
```

### Custom Output File
```bash
./venv/bin/python ingestion/load_lehman.py \
    --input data/capital_iq_processed/custom_case_study.json
```

---

## What You Need to Download

**From Capital IQ (via university library):**

1. Time Period: 2007-01-01 to 2009-12-31
2. Industries: Financial Services, Banks, Investment Banking
3. Event Types: All
4. Target Size: 500-2,000 events
5. Save As: `data/capital_iq_raw/financial_crisis_2007_2009.xlsx`

**Detailed instructions:** See `data/CAPITAL_IQ_DOWNLOAD_GUIDE.md`

---

## Current Status with Template Data

**Input:** 7 events from Lehman crisis template

**Output:**
- ✅ 12 entities (Lehman Brothers, Bear Stearns, AIG, JPMorgan, etc.)
- ✅ 7 events (Jan 2008 - Sep 2008)
- ✅ 4 risks (credit, systemic, market)
- ✅ 21 evolution links (temporal, causal, semantic)
- ✅ 278 RDF triples

**Processing time:** < 10 seconds end-to-end

---

## Troubleshooting

### "File not found"
Make sure you saved Capital IQ data to:
```
data/capital_iq_raw/your_file.xlsx
```

### "Cannot connect to Neo4j"
Start Neo4j first:
```bash
./scripts/start_neo4j.sh
```

### "No events found for Lehman"
Check if Capital IQ data contains Lehman Brothers events:
- Search for "Lehman" or "Lehman Brothers"
- Verify date range includes 2008
- Try `--filter all` to see all events

### "Column names don't match"
The processor handles various Capital IQ formats automatically.
It normalizes:
- "Company Name" → "company"
- "Event Date" → "date"
- "Event Type" → "event_type"

---

## Generated Files Location

```
data/
├── capital_iq_processed/
│   └── lehman_case_study.json  ← FE-EKG format

results/
├── lehman_graph.ttl            ← Turtle RDF (human-readable)
├── lehman_graph.xml            ← RDF/XML
└── lehman_graph.nt             ← N-Triples
```

---

## RDF Triple Example

```turtle
@prefix feekg: <http://feekg.org/ontology#> .
@prefix lehman: <http://feekg.org/lehman/> .

# Lehman Brothers bankruptcy event
lehman:evt_004 a feekg:Event ;
    feekg:date "2008-09-15" ;
    feekg:eventType "bankruptcy" ;
    feekg:headline "Lehman Brothers files for bankruptcy" ;
    feekg:description "Lehman Brothers Holdings Inc filed for Chapter 11..." ;
    feekg:sentiment 0.0 ;
    feekg:triggers lehman:risk_evt_004 .

# Evolution: Failed acquisition → Bankruptcy
lehman:evt_003_to_evt_004 a feekg:EvolutionLink ;
    feekg:fromEvent lehman:evt_003 ;  # BofA backs out
    feekg:toEvent lehman:evt_004 ;    # Lehman bankruptcy
    feekg:score 0.85 ;
    feekg:temporalScore 0.92 ;
    feekg:causalityScore 0.95 .

# Triggered credit risk
lehman:risk_evt_004 a feekg:Risk ;
    feekg:riskType "credit_risk" ;
    feekg:severity "critical" ;
    feekg:likelihood 0.95 .
```

---

## Complete Documentation

- **Architecture:** `LEHMAN_CASE_STUDY_PIPELINE.md`
- **Workflow:** `data/README_WORKFLOW.md`
- **Download Guide:** `data/CAPITAL_IQ_DOWNLOAD_GUIDE.md`

---

**Ready to process your Capital IQ data!**
