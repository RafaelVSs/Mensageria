from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from dotenv import load_dotenv


env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=env_path,
        env_file_encoding='utf-8',
        extra='ignore'
    )


try:
    settings = Settings()
except Exception as e:
    print(f"ERRO AO CARREGAR CONFIGURAÇÕES: Verifique seu arquivo .env ou variáveis de ambiente.")
    print(f"Detalhes do erro: {e}")
    print(f"Verifique se o arquivo .env está em: {env_path} e se todas as variáveis obrigatórias estão definidas.")
    raise