#!/bin/bash

# LaTeX Resume Validation Script
# This script performs syntax checks and compilation tests

set -e

echo "🔍 LaTeX Resume Validation Script"
echo "================================="
echo

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success") echo -e "${GREEN}✓${NC} $message" ;;
        "error") echo -e "${RED}✗${NC} $message" ;;
        "warning") echo -e "${YELLOW}⚠${NC} $message" ;;
        "info") echo -e "${BLUE}ℹ${NC} $message" ;;
    esac
}

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to root directory
cd "$ROOT_DIR"

echo "📂 Working directory: $ROOT_DIR"
echo

# Check if files exist
echo "1. Checking file existence..."
files_found=0
for file in latex/resume_*.tex; do
    if [[ -f "$file" ]]; then
        print_status "success" "Found: $file"
        ((files_found++))
    fi
done

if [[ $files_found -eq 0 ]]; then
    print_status "error" "No resume files found!"
    exit 1
fi
echo

# Syntax validation
echo "2. Performing syntax validation..."
validation_passed=true

for file in latex/resume_*.tex; do
    [[ -f "$file" ]] || continue
    echo "   Checking $file:"
    
    # Check for \end{document}
    if ! grep -q "\\\\end{document}" "$file"; then
        print_status "error" "Missing \\end{document} in $file"
        validation_passed=false
    else
        print_status "success" "\\end{document} found"
    fi
    
    # Check balanced itemize environments
    begin_count=$(grep -c "\\\\begin{itemize}" "$file" || echo 0)
    end_count=$(grep -c "\\\\end{itemize}" "$file" || echo 0)
    
    if [[ $begin_count -ne $end_count ]]; then
        print_status "error" "Unbalanced itemize environments in $file (begin: $begin_count, end: $end_count)"
        validation_passed=false
    else
        print_status "success" "Itemize environments balanced ($begin_count pairs)"
    fi
    
    # Check for common syntax errors
    if grep -q "\\\\end{document>" "$file"; then
        print_status "error" "Found malformed \\end{document> in $file"
        validation_passed=false
    fi
    
    if grep -q "\\\\end{itemize>" "$file"; then
        print_status "error" "Found malformed \\end{itemize> in $file"
        validation_passed=false
    fi
    
    # Check for content after \end{document}
    if grep -A 10 "\\\\end{document}" "$file" | grep -q "\\\\section"; then
        print_status "warning" "Content found after \\end{document} in $file"
    fi
    
    echo
done

if [[ "$validation_passed" == false ]]; then
    print_status "error" "Syntax validation failed!"
    exit 1
else
    print_status "success" "All syntax checks passed!"
fi
echo

# Test compilation if LaTeX is available
echo "3. Testing compilation..."
if command -v pdflatex &> /dev/null; then
    print_status "info" "pdflatex found, testing compilation..."
    
    for file in latex/resume_*.tex; do
        [[ -f "$file" ]] || continue
        echo "   Compiling $file..."
        
        if pdflatex -interaction=nonstopmode -output-directory=/tmp "$file" > /dev/null 2>&1; then
            print_status "success" "$file compiled successfully"
            # Clean up
            rm -f /tmp/"${file%.tex}".{aux,log,out,fdb_latexmk,fls,synctex.gz}
        else
            print_status "error" "$file failed to compile"
            validation_passed=false
        fi
    done
    
elif command -v docker &> /dev/null; then
    print_status "info" "LaTeX not found locally, but Docker is available"
    print_status "info" "To test compilation with Docker, run:"
    echo "   docker run --rm -v \"\$(pwd)\":/workspace -w /workspace texlive/texlive bash -c \"cd latex && for f in resume_*.tex; do pdflatex \\\$f; done\""
    
else
    print_status "warning" "Neither pdflatex nor Docker found - skipping compilation test"
    print_status "info" "To install LaTeX:"
    print_status "info" "  macOS: brew install --cask mactex"
    print_status "info" "  Ubuntu: sudo apt-get install texlive-full"
fi

echo
if [[ "$validation_passed" == true ]]; then
    print_status "success" "🎉 All validations passed! Your LaTeX files are ready for compilation."
    exit 0
else
    print_status "error" "❌ Some validations failed. Please fix the issues above."
    exit 1
fi
