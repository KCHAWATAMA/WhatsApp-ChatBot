import os
from dotenv import load_dotenv
from fastapi import FastAPI
from wa_cloud_py import WhatsApp
from fastapi.responses import PlainTextResponse
from fastapi import Request, HTTPException
from email_sender import send_email
from wa_cloud_py.components.messages import (
    ReplyButton,
)
from wa_cloud_py.messages.types import InteractiveButtonMessage

from wa_cloud_py.components.messages import ReplyButton
from wa_cloud_py.messages.types import (
    TextMessage,
    DocumentMessage,
)
import logging
from datetime import datetime


load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

if not VERIFY_TOKEN:
    raise ValueError("VERIFY_TOKEN environment variable is not set")
if not ACCESS_TOKEN:
    raise ValueError("ACCESS_TOKEN environment variable is not set")
if not PHONE_NUMBER_ID:
    raise ValueError("PHONE_NUMBER_ID environment variable is not set")


app = FastAPI()


whatsapp = WhatsApp(access_token=ACCESS_TOKEN, phone_number_id=PHONE_NUMBER_ID)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/")
async def read_root():
    return {"message": "WhatsApp Webhook is running"}


@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    logger.info("Verifying webhook: mode=%s, token=%s", mode, token)

    if token and token == VERIFY_TOKEN:
        logger.info("Token verified successfully.")
        return PlainTextResponse(content=challenge)

    logger.warning("Invalid verify token: %s", token)
    raise HTTPException(status_code=403, detail="Invalid verify token")


@app.post("/webhook")
async def receive_message(request: Request):
    app_doc_upload = False
    try:
        body = await request.body()
        message = whatsapp.parse(body)

        if isinstance(message, TextMessage):
            whatsapp.send_interactive_buttons(
                to=message.user.phone_number,
                body="Welcome to Our Bank Account Application WhatsApp portal! Please verify by clicking 'Send Application' or 'Cancel'.",
                buttons=[
                    ReplyButton(id="send_application", title="Send Docs"),
                    ReplyButton(id="cancel", title="Cancel"),
                ],
            )

        elif isinstance(message, InteractiveButtonMessage):
            user_choice = message.reply_id
            app_doc_upload = True
            print(app_doc_upload)
            if user_choice == "send_application":
                whatsapp.send_text(
                    to=message.user.phone_number,
                    body="You selected 'Send Application'. Please upload your application document.",
                )

        elif isinstance(message, DocumentMessage):
            app_doc_upload = True
            logger.info("Document received, app_doc_upload set to True")
            print(f"Received document: {message.filename}")
            file_name = message.filename
            print(app_doc_upload)
            if app_doc_upload:
                print("Uploading")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{message.user.phone_number}_{timestamp}_{file_name}"

                whatsapp.download_media(
                    message.media_id, filename=filename, save_path="./assets/"
                )
                full_path = f"assets/{filename}.docx"
                file_extensions = [
                    "docx",
                    "pdf",
                    "txt",
                ]
                full_path = None

                for file_extension in file_extensions:
                    potential_path = f"assets/{filename}.{file_extension}"
                    if os.path.exists(potential_path):
                        full_path = potential_path
                        logger.info("Found existing file: %s", full_path)
                        break

                if full_path is None:
                    logger.warning(
                        "No file found for %s with the specified extensions.", filename
                    )
                else:
                    send_email(full_path)

                    if os.path.exists(full_path):
                        os.remove(full_path)
                        logger.info(
                            "File %s has been removed after sending.", full_path
                        )
                    else:
                        logger.warning(
                            "File %s does not exist, cannot remove.", full_path
                        )

                whatsapp.send_text(
                    to=message.user.phone_number,
                    body="Your application document has been submitted successfuly. Thank you for uploading your application document.",
                )

        logger.info("Current state of app_doc_upload: %s", app_doc_upload)

        return {"status": "processed"}
    except Exception as e:
        logger.error("Error processing message: %s", str(e))
        return {"status": "error", "message": str(e)}
