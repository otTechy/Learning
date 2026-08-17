import chainlit as cl
import requests

@cl.on_message
async def main(message: cl.Message):
    if message.elements:
        for element in message.elements:
            if element.mime == "application/pdf":
                with open(element.path, "rb") as f:
                    files = {"file": (element.name, f, "application/pdf")}
                    response = requests.post(
                        "http://localhost:8000/extract",
                        files=files,
                        data={"output_format": "json"}
                    )
                    if response.ok:
                        result = response.json().get("result")
                        await cl.Message(content=f"Extracted Data:\n{result}").send()
                    else:
                        await cl.Message(content="Failed to extract data from PDF.").send()
    else:
        await cl.Message(content="Please upload a PDF file.").send()
