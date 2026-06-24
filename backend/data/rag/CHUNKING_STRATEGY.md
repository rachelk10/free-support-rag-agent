# Semantic Chunking Strategy for Course Materials

## Why Semantic Chunking?
The current regex/paragraph-based chunking loses context. These files should be chunked by **semantic units**, not by headers or paragraph breaks.

## Proposed Chunks & Structure

### CHUNK 1: Course Identity & Overview
**Files**: 01_course_overview.md.md (partially)
**Content**: 
- Title: "קורס Machine Learning"
- Description, goals, main advantages
**Category**: Course Fundamentals
**Metadata**: importance=high, retrievable_by=["מה לומדים?", "תיאור הקורס", "למה קורס זה?"]

### CHUNK 2: Target Audience / Who Should Take
**Files**: 02_target_audience.md
**Content**: 
- Developers, Data People, Students, Entrepreneurs, Career changers
**Category**: Enrollment Decision
**Metadata**: importance=high, retrievable_by=["למי הקורס?", "האם זה בשבילי?", "מי מתאים?", "מפתחים", "מדעני דאטה"]

### CHUNK 3: Prerequisites & Knowledge Requirements
**Files**: 03_prerequisites.md
**Content**:
- Required: Basic coding, Python basics
- Optional: Math, Statistics
- English: Not required
**Category**: Enrollment Decision
**Metadata**: importance=high, retrievable_by=["דרישות קדם", "מה צריך לדעת קודם?", "Python", "תכנות"]

### CHUNK 4: Curriculum Overview & Structure
**Files**: 04_curriculum.md
**Content**:
- All 8 modules with names and main topics
- Projects for each module
**Category**: Curriculum
**Metadata**: importance=very_high, retrievable_by=["סילבוס", "מה לומדים?", "מודולים", "אלגוריתמים", "Machine Learning"]

### CHUNK 5: Core Concepts & Learning Path
**Split from**: 04_curriculum.md
**Content**:
- Module 1: Foundations (NumPy, Pandas, Matplotlib)
- Module 3: Regression algorithms
- Module 5: Classification algorithms
**Category**: Curriculum
**Metadata**: importance=high, retrievable_by=["רגרסיה", "קלסיפיקציה", "NumPy", "Pandas", "אלגוריתמים"]

### CHUNK 6: Projects & Practical Work
**Split from**: 04_curriculum.md
**Content**:
- 8 projects listed (EDA, Price prediction, Customer churn, etc.)
**Category**: Curriculum
**Metadata**: importance=high, retrievable_by=["פרויקטים", "עבודה מעשית", "דאטה אמיתי", "Portfolio"]

### CHUNK 7: Pricing & Value Proposition
**Files**: 07_pricing.md (to be created/consolidated)
**Content**:
- Price information, payment options, value statement
**Category**: Enrollment Decision
**Metadata**: importance=medium, retrievable_by=["מחיר", "עלות", "כמה עולה?"]

### CHUNK 8: Registration & Refund Policy
**Files**: 08_registration_and_refund.md
**Content**:
- How to register, payment methods, refund conditions
**Category**: Enrollment Decision
**Metadata**: importance=medium, retrievable_by=["איך מתחילים?", "חוזר כסף", "הרשמה"]

### CHUNK 9: Learning Platform & Technical Setup
**Files**: 09_learning_platform.md
**Content**:
- Platform features, accessibility, support, video hosting
**Category**: Technical
**Metadata**: importance=medium, retrievable_by=["פלטפורמה", "טכנולוגיה", "תמיכה", "וידאו"]

### CHUNK 10: Certificate & Credentials
**Files**: 10_certificate.md
**Content**:
- Certificate details, recognition, portfolio value
**Category**: Outcomes
**Metadata**: importance=low, retrievable_by=["תעודה", "סרטיפיקט"]

### CHUNK 11: Career Impact & Job Market
**Files**: 11_career_and_job_market.md
**Content**:
- Job opportunities, salary expectations, career paths in AI/ML
**Category**: Enrollment Decision
**Metadata**: importance=high, retrievable_by=["עבודה", "מקום עבודה", "משכורת", "קריירה", "בשוק העבודה"]

### CHUNK 12: Sales Objections & Value Defense
**Files**: 12_sales_objections.md
**Content**:
- "Why ML today?" - relevance of the field
- "Why this course over ChatGPT?" - foundational vs. models
- "Why this specific course?" - differentiation (Hebrew, practical, etc.)
- "Is it for beginners?" - who can take it
**Category**: Enrollment Decision
**Metadata**: importance=high, retrievable_by=["למה ללמוד?", "ChatGPT", "למה קורס זה?", "למתחילים", "הצדקה"]

### CHUNK 13: Lead Collection & Support
**Files**: 13_lead_collection.md
**Content**:
- How to contact, support channels, community
**Category**: Enrollment Decision
**Metadata**: importance=low, retrievable_by=["קשר", "תמיכה", "שאלות", "community"]

### CHUNK 14: Agent Instructions & Internal
**Files**: 14_agent_instructions.md
**Content**:
- Chatbot behavior, tone, guidelines
**Category**: Internal
**Metadata**: importance=system, retrievable_by=[]

---

## Implementation Steps

1. **Keep raw files as-is** (no modifications needed to source files)

2. **Create consolidated chunks** in `backend/data/rag/processed/chunks/` directory:
   - Each chunk = one `.txt` or `.md` file
   - Filename = semantic identifier (e.g., `chunk_01_course_identity.txt`)
   - Include metadata as YAML frontmatter

3. **Update RAGService** to:
   - Load from `processed/chunks/` directory first
   - Apply predefined semantic metadata
   - Skip automatic chunking/embedding if manual chunks exist

4. **Test queries**:
   - "מה לומדים בקורס?" → Should return CHUNK 1 + 4 + 6
   - "מה דרישות קדם?" → Should return CHUNK 3
   - "כמה עולה?" → Should return CHUNK 7
   - "מה עם עבודות?" → Should return CHUNK 6

---

## Example Chunk Format

```yaml
---
id: chunk_01_course_identity
source: course_identity
category: Course Fundamentals
importance: very_high
keywords: [מה לומדים, תיאור הקורס, Machine Learning]
---

# קורס Machine Learning

קורס Machine Learning מקיף בעברית, המלמד את תחום למידת המכונה מהיסודות ועד לפרויקטים מעשיים...

[Full content here]
```

---

## Expected Improvements

- ✅ Queries will find **exactly relevant chunks**, not scattered paragraphs
- ✅ Metadata filtering enables **category-aware searches**
- ✅ LLM gets **complete semantic units** for better answer generation
- ✅ No over-chunking or under-chunking issues
