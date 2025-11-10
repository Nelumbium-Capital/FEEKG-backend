#!/bin/bash

# Start Neo4j locally using Docker
# This script starts a Neo4j instance for FE-EKG development

set -e

echo "============================================================"
echo "Starting Neo4j for FE-EKG"
echo "============================================================"

# Configuration
NEO4J_CONTAINER="feekg-neo4j"
NEO4J_VERSION="5.15"
NEO4J_PORT="7687"
NEO4J_HTTP_PORT="7474"
NEO4J_PASSWORD="feekg2024"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Docker is running"

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${NEO4J_CONTAINER}$"; then
    echo "📦 Container '${NEO4J_CONTAINER}' already exists"

    # Check if it's running
    if docker ps --format '{{.Names}}' | grep -q "^${NEO4J_CONTAINER}$"; then
        echo "✅ Neo4j is already running"
        echo ""
        echo "Neo4j Browser: http://localhost:${NEO4J_HTTP_PORT}"
        echo "Bolt URL: bolt://localhost:${NEO4J_PORT}"
        echo "Username: neo4j"
        echo "Password: ${NEO4J_PASSWORD}"
        exit 0
    else
        echo "🔄 Starting existing container..."
        docker start ${NEO4J_CONTAINER}
    fi
else
    echo "🚀 Creating and starting new Neo4j container..."
    docker run -d \
        --name ${NEO4J_CONTAINER} \
        -p ${NEO4J_PORT}:7687 \
        -p ${NEO4J_HTTP_PORT}:7474 \
        -e NEO4J_AUTH=neo4j/${NEO4J_PASSWORD} \
        -e NEO4J_PLUGINS='["apoc"]' \
        -e NEO4J_dbms_security_procedures_unrestricted='apoc.*' \
        -e NEO4J_dbms_memory_heap_max__size=2G \
        -v neo4j_data:/data \
        -v neo4j_logs:/logs \
        neo4j:${NEO4J_VERSION}
fi

# Wait for Neo4j to be ready
echo ""
echo "⏳ Waiting for Neo4j to be ready..."
sleep 5

# Check if Neo4j is responding
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker logs ${NEO4J_CONTAINER} 2>&1 | grep -q "Started."; then
        echo "✅ Neo4j is ready!"
        break
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -n "."
    sleep 1
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo ""
    echo "⚠️  Neo4j may still be starting. Check logs with:"
    echo "   docker logs ${NEO4J_CONTAINER}"
fi

echo ""
echo "============================================================"
echo "✅ Neo4j Started Successfully!"
echo "============================================================"
echo ""
echo "📊 Connection Details:"
echo "   Neo4j Browser: http://localhost:${NEO4J_HTTP_PORT}"
echo "   Bolt URL: bolt://localhost:${NEO4J_PORT}"
echo "   Username: neo4j"
echo "   Password: ${NEO4J_PASSWORD}"
echo "   Database: neo4j (default)"
echo ""
echo "🔧 Useful Commands:"
echo "   Stop Neo4j:    docker stop ${NEO4J_CONTAINER}"
echo "   Start Neo4j:   docker start ${NEO4J_CONTAINER}"
echo "   View logs:     docker logs ${NEO4J_CONTAINER}"
echo "   Remove:        docker rm -f ${NEO4J_CONTAINER}"
echo "   Shell:         docker exec -it ${NEO4J_CONTAINER} bash"
echo ""
echo "📝 Next Steps:"
echo "   1. Open Neo4j Browser at http://localhost:7474"
echo "   2. Login with neo4j / feekg2024"
echo "   3. Run: python scripts/load_schema.py"
echo ""
