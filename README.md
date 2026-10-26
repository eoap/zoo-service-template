# zoo-service-template

ZOO Project template for deploying Application Packages

This template is used in https://github.com/eoap/ogc-api-processes-with-zoo/ and targets simplicity over functionality to show how ZOO Project OGC API Processes Part-2 DRU is customized.

## Install Python dependencies securely

Use a supported Python release and an updated OS certificate store. Create a
virtual environment, then bootstrap pip from the hash-verified wheel before
contacting the package index:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade "pip @ https://files.pythonhosted.org/packages/3f/06/3e4420302363fbb71be3c7f35ce042f54bfca330e3e66b3a2e3c4cca579f/pip-26.2.2-py3-none-any.whl#sha256=fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70"
.venv/bin/python -m pip install -r requirements.txt
```

Existing virtual environments also need the pip upgrade and a reinstall with
these requirements. See the [Python incident guidance](https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576).
