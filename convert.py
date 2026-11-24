from httpx import __name
from typing import Literal
import asyncio
from ultralytics.data.converter import convert_ndjson_to_yolo
async def main():
    await convert_ndjson_to_yolo("dataset/construction-ppe.ndjson","dataset")

if __name__ == "__main__":
    asyncio.run(main())