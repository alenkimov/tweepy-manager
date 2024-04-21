# TWEEPY MANAGER
[![Telegram channel](https://img.shields.io/endpoint?url=https://runkit.io/damiankrawczyk/telegram-badge/branches/master?url=https://t.me/cum_insider)](https://t.me/cum_insider)

- [Running on Windows](#running-on-windows)
- [Running on Ubuntu](#running-on-ubuntu)

## Running on Windows
- Install [Python 3.11+](https://www.python.org/downloads/windows/). Don't forget to check "Add Python to PATH".
- Install [Poetry](https://python-poetry.org/docs/): [instruction in russian](https://teletype.in/@alenkimov/poetry).
- Install [git](https://git-scm.com/download/win). This will make it easy to get updates to the script with the `git pull` command
- Open the console in a convenient location...
  - Clone (or [download](https://github.com/alenkimov/tweepy-manager/archive/refs/heads/main.zip)) this repository:
    ```bash
    git clone https://github.com/alenkimov/tweepy-manager
    ```
  - Go to the project folder:
    ```bash
    cd tweepy-manager
    ```
  - Install the required dependencies and create the database using alembic with the following command or by running the `INSTALL.bat` file:
    ```bash
    poetry install
    poetry run alembic upgrade head
      ```
  - Start the script with the following command or by running the `START.bat`:
    ```bash
    poetry run python main.py
    ```

## Running on Ubuntu
- Update your system:
```bash
sudo apt update && sudo apt upgrade -y
```
- Install [git](https://git-scm.com/download/linux) and screen:
```bash
sudo apt install screen git -y
```
- Install Python 3.11+:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.12 python3.12-dev -y
ln -s /usr/bin/python3.12/usr/bin/python
```
- Install [Poetry](https://python-poetry.org/docs/):
```bash
curl -sSL https://install.python-poetry.org | python -
export PATH="/root/.local/bin:$PATH"
```
- Clone this repository and go to the folder:
```bash
git clone https://github.com/alenkimov/tweepy-manager
cd tweepy-manager
```
- Install the required dependencies and create the database using alembic:
```bash
poetry install
poetry run alembic upgrade head
```
- Run the script:
```bash
poetry run python main.py
```