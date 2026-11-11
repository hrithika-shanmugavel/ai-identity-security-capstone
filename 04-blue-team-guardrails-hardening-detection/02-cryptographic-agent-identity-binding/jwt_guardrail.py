import re

# Custom JWT regex pattern
JWT_PATTERN = re.compile(
    r'(?<![A-Za-z0-9_-])'
    r'eyJ[A-Za-z0-9_-]*'
    r'\.[A-Za-z0-9_-]+'
    r'\.[A-Za-z0-9_-]+'
    r'(?![A-Za-z0-9_-])'
)


# Custom output guardrail
def redact_jwt_tokens(text):
 
    redacted_text, count = JWT_PATTERN.subn(
        "[REDACTED]",
        text
    )

    if count > 0:
        print(
            f"\n[JWT OUTPUT GUARDRAIL] "
            f"Detected and redacted {count} JWT token(s)."
        )

    return redacted_text