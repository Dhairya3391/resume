#!/bin/bash

# Resume Build Script
# Builds all resume variants and organizes output

set -e

# Ensure TinyTeX is in PATH
export PATH="/Users/dhairya/Library/TinyTeX/bin/universal-darwin:$PATH"

echo "🚀 Building Resume Collection"
echo "============================="
echo

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to root directory
cd "$ROOT_DIR"

# Create build directory
mkdir -p build/

# Track success/failure
success_count=0
total_count=0
failed_files=()

echo "📁 Creating build directory: build/"
echo "📂 Working directory: $ROOT_DIR"
echo

# Build each resume
for file in latex/resume_*.tex; do
    if [[ -f "$file" ]]; then
        total_count=$((total_count + 1))
        base_name=$(basename "$file" .tex)
        
        echo -e "${BLUE}🔨 Building $file...${NC}"
        
        if pdflatex -interaction=nonstopmode -output-directory=build/ "$file" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Successfully built: build/${base_name}.pdf${NC}"
            success_count=$((success_count + 1))
        else
            echo -e "${RED}✗ Failed to build: $file${NC}"
            failed_files+=("$file")
        fi
        echo
    fi
done

# Clean up auxiliary files in build directory
echo "🧹 Cleaning up auxiliary files..."
rm -f build/*.{aux,log,out,fdb_latexmk,fls,synctex.gz} 2>/dev/null || true
echo

# Summary
echo "📊 Build Summary"
echo "================"
echo -e "Total files: $total_count"
echo -e "${GREEN}Successful: $success_count${NC}"
echo -e "${RED}Failed: $((total_count - success_count))${NC}"

if [[ ${#failed_files[@]} -gt 0 ]]; then
    echo -e "\n${YELLOW}Failed files:${NC}"
    for file in "${failed_files[@]}"; do
        echo -e "  - $file"
    done
fi

echo -e "\n📁 Output directory: ${PWD}/build/"
echo

if [[ $success_count -eq $total_count ]]; then
    echo -e "${GREEN}🎉 All resumes built successfully!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some builds failed. Check the output above for details.${NC}"
    exit 1
fi
