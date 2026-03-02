# SCF Claude Lab – Student Starter Kit

## Objective
Learn how AI (Claude) is used responsibly in compliance and control engineering.

You will:
- Use governed prompts
- Validate prompts locally
- Review and improve AI-generated drafts
- Produce audit-ready control artifacts

You will NOT:
- Chat randomly with AI
- Treat AI output as final truth
- Use private or sensitive data

---

## Setup Instructions

### 1. Clone or unzip this kit
```bash
cd scf-claude-lab
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate   # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Validate prompts
```bash
python tools/validate_prompts.py
```

Expected output:
All prompts valid
