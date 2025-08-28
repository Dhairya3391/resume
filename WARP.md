# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This repository contains a LaTeX-based resume system that generates role-specific resumes from a shared template architecture. The system follows DRY (Don't Repeat Yourself) principles and is optimized for Applicant Tracking Systems (ATS).

## Architecture

### Template Structure
All resume variants share a common LaTeX template foundation with:
- **Unified preamble**: Standard document setup, packages, and formatting
- **Custom commands**: Reusable LaTeX macros for consistent formatting
- **ATS-optimized design**: Black text, standard fonts, minimal graphics for parser compatibility
- **Role-specific content**: Tailored sections while maintaining consistent structure

### File Organization
```
resume_backend_engineer.tex     # Backend/server-side development focus
resume_software_engineer.tex    # General full-stack software engineering
resume_ai_ml_engineer.tex       # AI/Machine Learning specialization
resume_data_scientist.tex       # Data science and analytics focus
resume_devops_engineer.tex      # DevOps and infrastructure focus
```

### Section Architecture
Each resume follows this consistent structure:
1. **Header** - Name, contact information, links
2. **Summary** - Role-specific professional summary
3. **Skills** - Tailored technical skills by domain
4. **Projects** - Key projects with role-relevant emphasis
5. **Experience** - Professional experience (consistent across variants)
6. **Achievements** - Accomplishments and awards
7. **Education** - Academic background
8. **Languages** - Language proficiencies

## Build System

### Prerequisites
Install a LaTeX distribution:

**macOS:**
```bash
# Recommended: TinyTeX (lightweight, ~150MB)
curl -sL "https://yihui.org/tinytex/install-bin-unix.sh" | sh

# Install required packages for TinyTeX
tlmgr install enumitem titlesec xcolor hyperref

# Alternative: BasicTeX (larger but more complete)
brew install --cask basictex

# Full MacTeX (very large, ~4GB)
brew install --cask mactex
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install texlive-full
```

**Docker (any OS):**
```bash
# Build single resume
docker run --rm -v "$(pwd)":/workspace -w /workspace texlive/texlive pdflatex resume_backend_engineer.tex

# Build all resumes
docker run --rm -v "$(pwd)":/workspace -w /workspace texlive/texlive bash -c "for f in resume_*.tex; do pdflatex \$f; done"
```

### Build Commands

**Single resume:**
```bash
pdflatex resume_backend_engineer.tex
# or for better font support:
xelatex resume_backend_engineer.tex
```

**All resumes (using build script):**
```bash
./build_resumes.sh
```

**All resumes (manual):**
```bash
for file in resume_*.tex; do
    pdflatex "$file"
done
```

**Clean build artifacts:**
```bash
rm -f *.aux *.log *.out *.fdb_latexmk *.fls *.synctex.gz
```

## Custom LaTeX Commands

### Key Macros
- **`\resumeSubheading{title}{dates}{company}{location}`** - Formats job/education entries
- **`\resumeItem{text}`** - Creates bullet points with consistent spacing
- **Color definitions** - `primary` (black) and `secondary` (dark gray) for ATS compatibility
- **Hyperlink setup** - Configured for black links to maintain ATS parsing

### Usage Example
```latex
\resumeSubheading
{Software Engineer}{June 2023 -- Present}
{Tech Company}{San Francisco, CA}
\begin{itemize}[leftmargin=*]
\resumeItem{Developed scalable backend services using Node.js and MongoDB}
\resumeItem{Implemented CI/CD pipelines reducing deployment time by 40\%}
\end{itemize}
```

## Role-Specific Customization

### Creating New Role Variants
1. **Copy existing template:**
   ```bash
   cp resume_software_engineer.tex resume_new_role.tex
   ```

2. **Customize key sections:**
   - Update **Summary** with role-specific focus
   - Modify **Skills** section for relevant technologies
   - Emphasize relevant **Projects** and achievements
   - Adjust **ATS Keywords** comment at bottom

3. **Maintain consistency:**
   - Keep header, experience, education, and languages identical
   - Preserve all LaTeX commands and formatting
   - Follow existing section ordering

### Current Role Variations
- **Backend Engineer**: Server-side technologies, APIs, databases, performance
- **Software Engineer**: Full-stack development, general programming skills
- **AI/ML Engineer**: Machine learning, neural networks, data science libraries
- **Data Scientist**: Statistical analysis, business intelligence, data visualization  
- **DevOps Engineer**: Infrastructure, containerization, CI/CD, monitoring

## File Management

### Naming Convention
- Pattern: `resume_{role_name}.tex`
- Use underscores for multi-word roles
- Keep role names descriptive but concise

### Output Organization
The repository includes a `build_resumes.sh` script that automatically:
- Creates a `build/` directory
- Compiles all resume variants
- Organizes PDFs in the build directory
- Cleans up auxiliary files
- Provides colored output and summary

```bash
# Automated build (recommended)
./build_resumes.sh

# Manual build with organization
mkdir -p build/
for file in resume_*.tex; do
    pdflatex -output-directory=build/ "$file"
done
```

## ATS Optimization Features

### Design Choices
- **Standard fonts**: Uses LaTeX default sans-serif fonts
- **Black text**: Primary color set to RGB(0,0,0) for maximum compatibility
- **Simple formatting**: Minimal graphics, standard bullet points
- **Clear sections**: Bold headers with horizontal rules
- **Consistent spacing**: Uniform margins and line spacing

### Keywords Integration
Each resume includes role-specific ATS keywords in comments:
- Backend: "Backend Development, REST API, Node.js, Database Design"
- AI/ML: "Machine Learning, Artificial Intelligence, Deep Learning, Neural Networks"
- DevOps: "DevOps, Docker, Kubernetes, CI/CD, Infrastructure Automation"

## Content Management

### Shared Information
The following sections remain consistent across all variants:
- Personal header information
- Core experience entries
- Education details
- Language proficiencies
- Major achievements and awards

### Variable Content
Role-specific sections that should be customized:
- Professional summary paragraph
- Technical skills lists
- Project descriptions and emphasis
- Specialized achievements
- Relevant coursework mentions

## Quality Assurance

### Pre-build Checklist
- [ ] Personal information updated in header
- [ ] Role-specific summary written
- [ ] Skills section tailored to target role
- [ ] Project descriptions emphasize relevant technologies
- [ ] ATS keywords comment updated
- [ ] No LaTeX compilation errors
- [ ] PDF renders correctly

### Testing Build
```bash
# Test compilation of all resumes
for file in resume_*.tex; do
    echo "Building $file..."
    if ! pdflatex "$file" > /dev/null 2>&1; then
        echo "ERROR: Failed to build $file"
    else
        echo "SUCCESS: Built $file"
    fi
done
```

### Validation Script
The repository includes a comprehensive validation script that checks LaTeX syntax and tests compilation:

```bash
# Run validation script
./validate_latex.sh
```

The script performs:
- File existence checks
- LaTeX syntax validation
- Balanced environment checking
- Compilation testing (if LaTeX is available)
- Docker-based compilation suggestions

## LaTeX Issues Fixed

The following LaTeX syntax issues have been resolved:

### Common Issues Addressed
1. **Malformed document endings**: Fixed `\end{document>` → `\end{document}`
2. **Missing closing braces**: Fixed `\end{itemize>` → `\end{itemize}`
3. **Content after document end**: Moved content before `\end{document}`
4. **Unbalanced environments**: Ensured all `\begin{itemize}` have matching `\end{itemize}`

### File-Specific Fixes
- **AI/ML Engineer resume**: Fixed document termination and relocated Languages section
- **Data Scientist resume**: Fixed missing brace and document structure
- **All files**: Validated consistent preamble and section structure
