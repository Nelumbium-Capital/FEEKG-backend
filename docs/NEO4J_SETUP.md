## Neo4j Setup Guide for FE-EKG

### Option 1: Docker (Recommended - Easiest)

**Prerequisites**: Docker Desktop installed and running

```bash
# Start Neo4j
./scripts/start_neo4j.sh

# Access Neo4j Browser
open http://localhost:7474

# Login credentials
Username: neo4j
Password: feekg2024
```

**Stop Neo4j**:
```bash
docker stop feekg-neo4j
```

**Restart Neo4j**:
```bash
docker start feekg-neo4j
```

**Remove Neo4j** (deletes all data):
```bash
docker rm -f feekg-neo4j
docker volume rm neo4j_data neo4j_logs
```

---

### Option 2: Neo4j Desktop (GUI Application)

1. **Download Neo4j Desktop**:
   - Visit: https://neo4j.com/download/
   - Download for macOS
   - Install the application

2. **Create a Project**:
   - Open Neo4j Desktop
   - Click "New Project" → Name it "FE-EKG"

3. **Create a Database**:
   - Click "Add Database" → "Create a Local Database"
   - Name: `feekg_dev`
   - Password: `feekg2024`
   - Version: 5.15+ (latest stable)

4. **Install APOC Plugin**:
   - Click on your database
   - Go to "Plugins" tab
   - Click "Install" on APOC

5. **Start the Database**:
   - Click "Start" button
   - Wait for green "Active" status

6. **Get Connection Details**:
   - Click "..." → "Connection Details"
   - Copy Bolt URL (usually `bolt://localhost:7687`)

7. **Update .env**:
   ```bash
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASS=feekg2024
   NEO4J_DB=neo4j
   ```

---

### Option 3: Homebrew (macOS)

```bash
# Install Neo4j
brew install neo4j

# Set password
neo4j-admin dbms set-initial-password feekg2024

# Start Neo4j
neo4j start

# Stop Neo4j
neo4j stop

# Check status
neo4j status
```

**Data Location**: `/usr/local/var/neo4j/`

---

### Option 4: Cloud (Neo4j Aura Free Tier)

1. Visit: https://neo4j.com/cloud/aura-free/
2. Create free account
3. Create a free instance
4. Download connection credentials
5. Update `.env` with cloud credentials

---

### Verify Installation

Once Neo4j is running, test the connection:

```bash
# Activate virtual environment
source venv/bin/activate

# Test connection
python -c "from config.graph_backend import get_connection; b = get_connection(); print(f'✅ Connected! Nodes: {b.size()}'); b.close()"
```

---

### Load Schema

After Neo4j is running:

```bash
# Ensure GRAPH_BACKEND=neo4j in .env
python scripts/load_schema.py
```

Expected output:
```
✅ Schema loaded successfully
   Risk types created: 12
   Constraints created: 6
```

---

### Access Neo4j Browser

Open in browser: http://localhost:7474

**Useful Cypher Queries**:

```cypher
// List all risk types
MATCH (rt:RiskType) RETURN rt.name, rt.label;

// Count nodes by type
MATCH (n) RETURN labels(n) as Type, count(n) as Count ORDER BY Count DESC;

// Show schema
CALL db.schema.visualization();
```

---

### Troubleshooting

**Issue**: "Connection refused"
- **Solution**: Ensure Neo4j is running (`docker ps` or Neo4j Desktop status)

**Issue**: "Authentication failed"
- **Solution**: Check password in `.env` matches Neo4j password

**Issue**: "Database 'feekg_dev' not found"
- **Solution**: Use default database name `neo4j` in `.env`

**Issue**: Docker not running
- **Solution**: Start Docker Desktop or use Neo4j Desktop instead

---

### Next Steps

Once Neo4j is set up and schema is loaded:

1. Proceed to Stage 3: Load sample Evergrande data
2. Test queries and visualization
3. Build event evolution graph
