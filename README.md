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

And now simply run these service!

```bash
uv sync && uv run startup.py
```
