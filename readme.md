# Telegram Adventure Bot

## Initial Setup

### Creating a virtual environment

Basically, I think this step is important because if we need to deploy or host this service, best that the installation is light-weight. Meaning the Python installation doesn't contain all the other python library junk on our computers i.e.

-   pandas
-   numpy
-   scipy
-   other junk, etc...

I've named my virtual environment <b>tele_bot</b> and added it to the gitignore so it won't get published to the repo and make this entire file huge and hard to sync.

Open terminal input: (tele_bot will be set as the name of the venv)

```bash
python3 -m venv tele_bot
```

### Installing package(s)

Run:

```bash
pip3 install -r requirements.txt
```
