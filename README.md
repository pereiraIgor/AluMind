# AluMind

AluMind é uma startup que oferece um aplicativo focado em bem-estar e saúde mental. Nosso objetivo é proporcionar aos usuários acesso a meditações guiadas, sessões de terapia e conteúdos educativos sobre saúde mental. Com o crescimento acelerado da base de usuários, enfrentamos desafios para analisar feedbacks recebidos em diferentes plataformas, como canais de atendimento ao cliente, comunidades no Discord e redes sociais. Este projeto visa criar uma aplicação para analisar esses feedbacks, classificá-los por sentimento e identificar possíveis melhorias.

## Pré-requisitos

Certifique-se de ter os seguintes itens instalados:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

Além disso, obtenha uma chave de API do [OpenRouter](https://openrouter.ai/) para habilitar o uso do LLM. Após obter a chave, adicione-a ao arquivo `.env` no seguinte formato:

```env
OPENROUTER_API_KEY=sua_chave_aqui
```

## Como executar o projeto

1. Clone o repositório:

    ```bash
    git clone https://github.com/pereiraIgor/AluMind.git
    ```

2. Acesse o diretório do projeto:

    ```bash
    cd AluMind/
    ```

3. Copie as Variaveis de Ambiente e Configure as variáveis de ambiente:

    ```bash
    cp .env.example .env
    ```

4. Execute o projeto com Docker Compose:

    ```bash
    docker compose up --build
    ```

O projeto estará disponível assim que os containers forem inicializados.

## Endpoints disponíveis

A documentação completa dos endpoints está disponível no link abaixo:

[Documentação dos Endpoints](https://documenter.getpostman.com/view/8557249/2sB2cPkRMJ)
