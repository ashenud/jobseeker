import html
import re

SECRET_RE=re.compile(r"(?i)(api[_-]?key|token|password|secret)=([^\s]+)")
def redact(text:str)->str: return SECRET_RE.sub(lambda m: f"{m.group(1)}=[REDACTED]", text)
def sanitize_html(text:str)->str:
    cleaned = re.sub(r"(?is)<script.*?</script>", "", text)
    return html.escape(cleaned, quote=False).replace("&lt;p&gt;", "<p>").replace("&lt;/p&gt;", "</p>")
def neutralize_prompt_injection(text:str)->str: return re.sub(r"(?i)ignore (all )?(previous|system|developer) instructions", "[removed instruction override]", text)
