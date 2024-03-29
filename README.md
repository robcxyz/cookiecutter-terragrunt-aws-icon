
STATUS UPDATE:  This project is going to be split up soon such that the logic that builds the file structure is going 
to be separated from the repo templating logic.  This repo will no longer be maintained with the new project calling 
a more general purpose CLI tool possibly written in Go.  Any feedback would be well appreciated as I plan on submitting 
all this work to Gruntworks as a general purpose scaffolding tool.  Would love thoughts on the templating logic so please 
DM me if you would like to collab. 


## cookiecutter-terragrunt-aws-icon

Cookiecutter template to build a [terragrunt](https://github.com/gruntwork-io/terragrunt) 
folder structure for a [terraform](https://www.terraform.io/) deployment of various stacks. 
Basically this is a higher level configuration file format to build stacks on the cloud 
with a CLI to guide you through a few options.

Terragrunt is [awesome](https://blog.gruntwork.io/a-comprehensive-guide-to-terraform-b3d32832baca)
 for [many](https://medium.com/@anton.babenko/atlantis-terragrunt-689b1aa2bf89), 
 [many](https://blog.gruntwork.io/) [reasons](). Most importantly it allows you to keep your code DRY, 
 as in Don't Repeat Yourself, as in when you change variables, you only change them in one place. 
 There are a lot of ways to structure terraform files, but so far I think 
 [this way](https://github.com/antonbabenko/terragrunt-reference-architecture) is best. 
 As long as you conform to a structure of `environment` / `region` / `rescource group` in your 
 config files as well as how you **refer to the remote state** within the modules, you will have
 a consistent way to reference any object, even if it is within another account. 

### WIP / POC

This is not ready for use and is more to demonstrate some of the coupling issues you have when 
trying to generalize components. Please see the [ttd](#ttd) for what needs to be built.  
This is part a larger project on cookiecutter. Please pm [me](https://github.com/robcxyz) to ask more. 

Status:
- terraform 12 not tested 
- Only `basic-p-rep` working 


### Pre-installation 

This package depends on these requirements 
```
pip install pyhcl boto3 cookiecutter requests prompt_toolkit
```

You will also need the appropriate terraform and terragrunt packages. 
While the terraform 11 / 12 transition is happening, both are supported. 

Terraform Releases - https://releases.hashicorp.com/terraform/
Terragrunt Releases - https://github.com/gruntwork-io/terragrunt/releases


Terraform 0.11
```bash
wget https://releases.hashicorp.com/terraform/0.11.14/terraform_0.11.14_linux_amd64.zip
unzip terraform_0.11.14_linux_amd64.zip
sudo chmod +x terraform 
sudo mv terraform /usr/local/bin/terraform11
sudo ln -s /usr/local/bin/terraform11 /usr/local/bin/terraform
terraform --version 
```
** Unverified ** 
```bash 
wget https://github.com/gruntwork-io/terragrunt/releases/download/v0.18.6/terragrunt_linux_amd64
unzip terragrunt_linux_amd64
sudo chmod +x terragrunt
sudo mv terragrunt /usr/local/bin/terragrunt11
sudo ln -s /usr/local/bin/terragrunt11 /usr/local/bin/terragrunt
terragrunt --version 
```

### Usage 

#### Generate reference architecture

```bash
cookiecutter https://github.com/robcxyz/cookiecutter-terragrunt-aws-icon
cd <env> 
chmod +x init.sh clear-cache.sh 
./init.sh <ACCOUNT_ID> <REMOTE_STATE_REGION> <LOCAL_KEY_FILE> <ROOT_DOMAIN_NAME> <CORPORATE_IP>
```

#### Deploy 

```bash
cd <region>
terragrunt apply-all --terragrunt-source-update
```

#### Move to Prod 
```bash
cd ../.. && cp dev prod & cd prod 
./init.sh <ACCOUNT_ID> <REMOTE_STATE_REGION> <LOCAL_KEY_FILE> <ROOT_DOMAIN_NAME> <CORPORATE_IP>
terragrunt apply-all --terragrunt-source-update
```


### TTD 

This is going to be rebuilt in the near future to incorporate the learnings from this first go. 
Most of this stuff is really going to be done on the next iteration. 

#### Bugs 
- Fix output of network 
    - Rebuild network 
- fix region output 
- Rebuild tests to point to hooks dir and tests dir 
- Read hcl after tests 

#### General 
- Throw better errors to bubble up what exactly is messing with the jinja 
- Upgrade question to [python-prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
- Get headless version working properly 
    - Rip out `ask` logic 
    - Get the stack down to a single json / hcl and be able to make based on that 
    - ask / read -> BL -> make 
- Once headless is working, render copy of pre_gen_hook in main ouptut dir as well as output of config 
- Once questions have been asked, the project can be re-built based on updating one 
generated config file from running copy of pre_gen_hook
- No region questions unless specifically needed 

#### Headless Service 

- Split out logic to generate multi-az configs in headless 
- Need to get AZs dynamic
- Until questions inform stack object for AZs, this part is coupled 
    - Remove AZs
- Render stack in place to account for prior questions 
    - Input config for rendering stack 
    - Num azs to lookup into populating jinja rendering
- Finalize sources 
- Push new versions for 0.12

### Resources 

- [terragrunt-reference-architecture](https://github.com/antonbabenko/terragrunt-reference-architecture
    - Great example of terragrunt strucuture 
