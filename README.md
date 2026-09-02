# Assistente Voz — MVP completo

Um ponto de partida executável para o produto discutido na reunião:
**voz/conversa → interpretação → agenda/tarefas → briefing → plano de estudos**.

## Tecnologias utilizadas

**Backend**
- [Python 3.12](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/) — framework web
- [Uvicorn](https://www.uvicorn.org/) — servidor ASGI
- [Pydantic](https://docs.pydantic.dev/) — validação de dados
- [python-dateutil](https://dateutil.readthedocs.io/) — manipulação de datas
- SQLite — banco de dados

**Frontend**
- HTML5
- CSS3
- JavaScript (vanilla, sem frameworks)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API) — reconhecimento de voz do navegador

**Ferramentas de desenvolvimento**
- Git + GitHub
- VSCode

## O que já existe
- API FastAPI.
- SQLite persistente.
- CRUD de tarefas e eventos.
- Interpretação local de frases em português (sem chave de IA).
- Camada de IA isolada para futura integração com um LLM.
- Endpoint de briefing de reunião a partir de texto transcrito.
- Endpoint de plano de estudos.
- Interface web responsiva.
- Reconhecimento de voz do navegador quando disponível.
- Dashboard diário.

## Arquitetura

```text
[Browser / App]
      |
      v
[FastAPI REST API]
      |
      +--> [Interpretador]
      |       +--> parser local (MVP)
      |       +--> LLM adapter (futuro)
      |
      +--> [Serviço de reuniões]
      +--> [Serviço de estudos]
      |
      v
   [SQLite]
```

## Executar

```bash
cd backend
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Abra `http://127.0.0.1:8001`.

A documentação automática da API fica em `/docs`.

## Exemplos
Digite ou fale:
- `Hoje às 10h tenho reunião com Micael para discutir o projeto.`
- `Amanhã às 9h estudar Python por 1 hora.`
- `Lembrar de ligar para o fornecedor amanhã às 14h.`

## Importante
Este é um MVP de engenharia, não uma aplicação pronta para produção.
Antes de uso comercial, adicione autenticação, autorização, criptografia, política
de retenção, consentimento para gravações, LGPD, logs seguros, testes automatizados,
monitoramento e uma integração de IA/transcrição com credenciais protegidas.

## Próximas versões
1. Login e múltiplos usuários.
2. PostgreSQL.
3. Transcrição de áudio real.
4. Integração de calendário.
5. Notificações push.
6. LLM para entendimento semântico.
7. Memória e preferências.
8. Motor de priorização e recomendações.
