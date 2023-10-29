from launchers.server import server
import os
import asyncio


def parse_boolean(val: str):
    if val.lower().strip() == "true":
        return True
    elif val.lower().strip() == "false":
        return False
    else:
        return False


async def main():
    open_browser = parse_boolean(os.getenv("open_2d_canvas"))
    autoreload = parse_boolean(os.getenv("autoreload"))
    await server.launch(open_browser=open_browser, autoreload=autoreload)


if __name__ == "__main__":
    asyncio.run(main())
