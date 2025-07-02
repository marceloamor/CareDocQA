#!/bin/bash

# 🔄 CareDocQA Quick Demo Reset
# Clears database and uploads sample documents for consistent demos

echo "🔄 Resetting CareDocQA for fresh demo..."

# Clear database without prompting
echo "🗑️  Clearing database and files..."
python -c "
from pathlib import Path
import sqlite3
import shutil

# Clear database
db_path = Path('data/documents.db')
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM documents')
    cursor.execute('DELETE FROM sqlite_sequence WHERE name=\"documents\"')
    conn.commit()
    conn.close()

# Clear files
docs_dir = Path('data/documents')
if docs_dir.exists():
    for file_path in docs_dir.glob('*'):
        if file_path.is_file():
            file_path.unlink()

print('✅ Database and files cleared')
"

# Upload sample documents via API
echo "📁 Uploading sample documents..."

# Check if API Gateway is running
if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "❌ API Gateway not running. Please start services first:"
    echo "   ./start_careDocQA.sh"
    exit 1
fi

# Upload each sample document
for file in sample_documents/*.txt; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "📄 Uploading $filename..."
        curl -s -X POST "http://localhost:8000/upload" \
             -H "Content-Type: multipart/form-data" \
             -F "file=@$file" >/dev/null
    fi
done

echo "✅ Demo reset complete!"
echo "🎯 Ready for fresh demo session"
echo ""
echo "📋 Sample documents uploaded:"
echo "• care_plan_mrs_wilson.txt - Ask about medications"
echo "• emergency_procedures.txt - Ask about fire safety"  
echo "• dementia_care_guidelines.txt - Ask about communication"
echo "• safeguarding_policy.txt - Ask about abuse reporting"
echo "• care_guidelines.txt - Ask about general care"
echo "• shift_notes.txt - Ask about patient status" 