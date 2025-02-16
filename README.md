---
description: This repo has scripts to setup ai-agent.
---

# Setup Infrastructure

# Deployment

Click on the Deploy to Azure button to follow the steps to create a resource group and **Azure AI Hub**:

[![Deploy to Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg?sanitize=true)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fctava-msft%2Fai-agents%2Fmain%2Fazuredeploy.json)


# Setup python environment
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
Copy sample.env to .env and enter values for the parameters.

## Scripts

Run agent.py to create agent, thread, upload files and provide Q&A on them.