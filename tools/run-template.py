import os
import sys

from reanatempl import TemplateSpec
from reanatempl.engine.alternate import AlternateTemplateEngine


template_file = sys.argv[1]
template_spec = TemplateSpec.load(template_file)

arguments = template_spec.read()

print(arguments)

engine = AlternateTemplateEngine(
    server_url=os.getenv('REANA_SERVER_URL'),
    access_token=os.getenv('REANA_ACCESS_TOKEN')
)

identifier = engine.run(template_spec, arguments, '')

print(identifier)
