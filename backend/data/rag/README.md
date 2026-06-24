# RAG Data Layout

תיקייה זו מיועדת לידע שה-Agent ישתמש בו כדי לענות על שאלות קורס.

## מבנה

- `raw/course_materials/` – כאן מכניסים קבצי מקור של הקורס (לדוגמה: `.txt`, `.md`, `.pdf`, `.docx`).
- `metadata/` – קבצי מטא-דאטה (לדוגמה: מיפוי קורסים, תגים, קישורים).
- `processed/chunks/` – טקסטים אחרי chunking (נוצר אוטומטית בתהליך ingestion).
- `processed/embeddings/` – ייצוגי embedding (נוצר אוטומטית).
- `indexes/` – אינדקס וקטורי לחיפוש (נוצר אוטומטית).

## מה אתה צריך לעשות עכשיו

1. להכניס את חומרי הקורס אל `raw/course_materials/`.
2. (אופציונלי) לעדכן `metadata/course_catalog.template.json` ולשמור כקובץ חדש עם שם מתאים.

> כרגע הפרויקט כולל placeholder ל-RAG (`backend/services/rag_service.py`) ולכן התיקיות מוכנות לקליטת תוכן ולשלב חיבור ingestion/retrieval.
