
# WIP 

## cookiecutter-terragrunt-aws-icon

Cookiecutter template to build a [terragrunt]() folder structure for a terraform deployment of various stacks. 
Basically this is a higher level configuration file format to build stacks on the cloud. 

### Pre-installation 

This package depends on these requirements 
```
pip install pyhcl boto3 cookiecutter prompt_toolkit
```

You will also need the appropriate terraform and terragrunt 


### Usage 

```
cookiecutter https://github.com/robcxyz/cookiecutter-terragrunt-aws-icon
```


### TTD 

- Upgrade question to [python-prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
- Get headless version working properly 
    - Rip out `ask` logic 
    - Get the stack down to a single json / hcl and be able to make based on that 
    - ask / read -> BL -> make 
- Once headless is working, render copy of pre_gen_hook in main ouptut dir as well as output of config 
- Once questions have been asked, the project can be re-built based on updating one 
generated config file from running copy of pre_gen_hook


#### Headless Service 

- Need to get AZs dynamic
- Until questions inform stack object for AZs, this part is coupled 
    - Remove AZs


- Render stack in place to account for prior questions 
    - Num azs to lookup into populating jinja rendering

- Finalize sources 
- Push new 

### Resources 

- [
