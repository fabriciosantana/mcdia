import os.path
import base64
import sys
import logging
import traceback
import warnings
from email.message import EmailMessage

# Silenciar avisos do Google
warnings.filterwarnings("ignore", category=FutureWarning)

# Configuração de log para arquivo (para não interferir no stdio)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="mcp_server.log",
    filemode="a",
)
logger = logging.getLogger("gmail-mcp")

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mcp.server.fastmcp import FastMCP

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Initialize FastMCP server
# Usar host="0.0.0.0" permite que o Dify rodando em Docker mande requisições
# usando a URL http://host.docker.internal:8000
mcp = FastMCP("Gmail Server", host="0.0.0.0")

def get_gmail_service():
    """Gets an authorized Gmail service instance."""
    creds = None
    try:
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists("credentials.json"):
                    raise FileNotFoundError(
                        "credentials.json not found. Please follow the instructions to "
                        "download it from the Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

    except Exception as e:
        logger.error(f"Erro ao obter serviço Gmail: {e}")
        raise

    return build("gmail", "v1", credentials=creds)

@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """
    Sends an email using the Gmail API.

    Args:
        to: The email address of the recipient.
        subject: The subject of the email.
        body: The body content of the email.
    """
    try:
        service = get_gmail_service()
        message = EmailMessage()

        message.set_content(body)
        message["To"] = to
        message["From"] = "me"
        message["Subject"] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        
        # pylint: disable=no-member
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        return f'Email sent successfully. Message ID: {send_message["id"]}'
    except HttpError as error:
        logger.error(f"Erro na API do Gmail: {error}")
        return f"An error occurred: {error}"
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return f"Unexpected error: {str(e)}"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "auth":
            print("Iniciando fluxo de autenticação do Google...")
            try:
                get_gmail_service()
                print("✅ Autenticação concluída com sucesso! (token.json gerado)")
            except Exception as e:
                print(f"❌ Erro na autenticação: {e}")
            sys.exit(0)
        elif sys.argv[1] == "sse":
            mcp.run(transport='sse')
            sys.exit(0)
            
    # Default: stdio (para Claude Desktop / Cursor)
    mcp.run(transport='stdio')
