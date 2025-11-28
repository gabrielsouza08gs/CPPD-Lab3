Aluno: Gabriel Souza Do Nasciemnto
Matricula: 2215114



Instruções para Execução do Projeto
1. Requisitos
Antes de executar, certifique-se de ter instalado:
Python 3.10+
Biblioteca MQTT:

pip install paho-mqtt

Como Executar o Participante
Este trabalho simula a eleição distribuída de líder via MQTT, com múltiplos participantes se comunicando pelo broker.
Em cada terminal, execute:

py participant.py --broker broker.emqx.io --port 1883

Número de Participantes
A atividade pode ser executada com 2 ou mais participantes.
Recomendado: 2 terminais, para evitar problemas de latência.
Abra 2 janelas do terminal e rode o comando em cada uma.

O que você deve observar
Quando os participantes conectarem:
Cada participante publica sua presença (fase INIT)
Quando todos são descobertos, inicia-se a votação (fase ELECTION)
O maior ID é eleito líder
O líder publica um desafio no tópico MQTT
Os demais recebem o desafio e processam
O programa exibe logs mostrando cada etapa

Encerramento
Para encerrar um participante, utilize:

CTRL + C



Relatório Técnico — Eleição de Líder via MQTT
1. Objetivo
Implementar um sistema distribuído simples para eleição de líder utilizando o protocolo MQTT, simulando comunicação entre processos distribuídos através de tópicos dedicados.

2. Metodologia
Arquitetura
Cada participante é um processo independente executando o arquivo participant.py
A comunicação ocorre via broker MQTT público (broker.emqx.io)
Os tópicos seguem um padrão específico para evitar conflitos entre alunos
Ex.: sd_gabriel.../init, .../election, .../challenge, etc.
Etapas da execução
O sistema trabalha em três fases principais:

2.1. Fase INIT – Descoberta de Participantes
Cada participante publica sua presença no tópico init
Todos registram os IDs recebidos
Após um tempo, o processo assume que não entrarão novos participantes
A fase termina quando o participante sabe quem são todos os outros

2.2. Fase ELECTION – Votação
Cada participante sorteia ou utiliza seu próprio ID único
Todos os IDs recebidos são comparados
O maior ID é eleito líder
O líder anuncia sua eleição publicando no tópico election

2.3. Fase CHALLENGE – Desafio do Líder
O líder envia um desafio para todos os participantes
Os demais recebem o desafio e processam sua resposta
O líder coleta os resultados (processo simplificado)
Finaliza a simulação

3. Testes Realizados
Configuração dos testes
Ambiente Windows 10
Python 3.10
Broker MQTT: broker.emqx.io
Execução simultânea em 2 terminais diferentes
Resultados observados
Participantes foram descobertos corretamente
IDs trocados entre processos sem perda
Eleição determinística: maior ID sempre eleito
Desafio enviado e recebido sem erros pelo MQTT
Logs confirmaram as três fases funcionando conforme esperado

4. Conclusão
O sistema desenvolvido implementa com sucesso um protocolo simples de eleição distribuída de líder utilizando MQTT como meio de comunicação.
Os testes comprovaram:
Comunicação eficiente entre processos
Sincronização satisfatória das fases
Eleição correta e previsível
Desafio distribuído para todos os participantes ao final
O trabalho atende aos requisitos solicitados em relação a:
Comunicação distribuída
Eleição de líder
Organização modular do código e tópicos MQTT
