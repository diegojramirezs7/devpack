---
title: Validate and Limit User-Uploaded Files
impact: HIGH
impactDescription: prevents malicious file uploads and resource exhaustion
tags: static-files, uploads, validation, security, file-size
---

## Validate and Limit User-Uploaded Files

Never trust user uploads. Validate file types, sizes, and store them outside of your application code.

**Correct:**

```python
from django.core.validators import FileExtensionValidator

class Document(models.Model):
    file = models.FileField(
        upload_to='documents/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'txt'])],
    )

# In settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
```
