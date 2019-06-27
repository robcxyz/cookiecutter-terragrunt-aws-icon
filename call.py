from cookiecutter.main import cookiecutter
import os


template_dir = os.path.join(os.path.curdir)

cookiecutter(
    template_dir,
    extra_context={"environment": "dev"}
)

