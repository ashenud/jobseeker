from job_agent.config.settings import Settings
from job_agent.observability.service import MetricRegistry

settings=Settings(); metrics=MetricRegistry()
class SimpleResponse:
    def __init__(self, text:str, status_code:int=200): self.text=text; self.status_code=status_code
    def json(self)->dict[str,str]:
        import json
        return json.loads(self.text)
class SimpleApp:
    def handle(self,path:str)->SimpleResponse:
        if path=="/health/live": return SimpleResponse('{"status":"live"}')
        if path=="/health/ready": return SimpleResponse('{"status":"ready","bind_host":"'+settings.bind_host+'"}')
        if path=="/metrics": return SimpleResponse(metrics.render())
        return SimpleResponse('<!doctype html><h1>Human review queue</h1><p>Local-only dashboard.</p>')
def create_app()->SimpleApp: return SimpleApp()
