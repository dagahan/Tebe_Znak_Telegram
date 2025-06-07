# Tebe Znak Telegram



Hello! This is a tebe_znak_project. It simply sending to every telegram channel from list a random constructed message. Last {350} messages in every single channel won't repeating.


## How to run

First, clone repo and cd into it

```bash
git clone https://github.com/dagahan/Tebe_Znak_Telegram
cd Tebe_Znak_Telegram
```

Then, install uv to your system

```bash
pip install uv -y
```

create .env file in main directory

```bash
touch .env
```

type into your data, then test data:

```bash
bot_token="your_token7878"
admin_id=your_tg_id
test_id=1
test_tg_id="tg_channel_id_to_test"
test_name="your_test_name"
```

Then simply run these service and get an error:

```bash
uv sync && uv run startup.py

21:20:24 | CRITICAL | core.database:setup:77 - Great! Database of channels now done, please insert your data into it and run program again!
```

It means database of channels has been created at database/database.db
You need to enter your data into it.
To do so, use command:

```bash
sudo apt install sqlite3
sqlite3 database.db "INSERT INTO channels (tg_id, name) VALUES 
('tg_id', 'Jane'),
('tg_id', 'Masha'),
('tg_id', 'Rose');"
```

And finally you can run these service for usage:

```bash
uv sync && uv run startup.py
```