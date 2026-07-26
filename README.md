# Contador de Produção Não-Intrusivo

## Identificação do Candidato

- **Nome completo:** Caio Juan da Natividade Santos
- **GitHub:** [CaioNatividade](https://github.com/CaioNatividade)

## Visão Geral da Solução

Este projeto implementa um contador de produção para linhas de montagem sem
CLP. Um sensor óptico LDR identifica a passagem de peças pela interrupção da
luz, e o ESP32 registra cada passagem concluída.

Além da contagem, o sistema identifica bloqueios prolongados como
micro-paradas e permite que o operador zere o turno por meio de um botão
físico. As contagens, os alertas e as confirmações são enviados pelo monitor
serial.

## Arquitetura do Sistema Embarcado

O firmware em `src/main.py` inicializa as entradas do LDR e do botão e, em
seguida, executa continuamente um loop com intervalo de 10 ms.

O fluxo principal pode ser resumido da seguinte forma:

```text
Leitura do LDR
   |
   +-- linha livre -> aguarda uma obstrução
   |
   +-- luz bloqueada -> inicia/acompanha o temporizador
   |                     |
   |                     +-- bloqueio >= 5 s -> alerta de micro-parada
   |
   +-- luz restabelecida -> incrementa a contagem, caso não tenha ocorrido
                            uma micro-parada

Leitura do botão -> debounce de 50 ms -> reset dos contadores
```

A variável `objeto_bloqueando` representa o estado do sensor. A peça só é
contabilizada quando o sinal retorna ao estado de linha livre, evitando
múltiplas contagens enquanto o mesmo objeto permanece diante do sensor.

As temporizações usam `ticks_ms()` e `ticks_diff()`. Dessa forma, tanto o
tempo de bloqueio quanto o debounce são controlados sem pausas longas que
impeçam a leitura dos demais componentes.

## Componentes Utilizados na Simulação

- **ESP32 DevKit C v4 (`esp`):** executa o firmware MicroPython e coordena as
  entradas e a comunicação serial.
- **Sensor fotorresistor/LDR (`ldr1`):** conectado ao GPIO 34 pela saída
  digital `DO`; detecta a interrupção e o restabelecimento da luz.
- **Botão (`btn1`):** conectado ao GPIO 27 e ao GND; utiliza o resistor
  pull-up interno do ESP32 para realizar o reset do turno.
- **Monitor serial (UART):** recebe as mensagens de inicialização, contagem,
  micro-parada e reset.

## Decisões Técnicas Relevantes

- Os números dos pinos e os tempos de controle foram definidos como
  constantes, facilitando ajustes e manutenção.
- A detecção de peças utiliza transições de estado: o bloqueio inicia o ciclo
  e o retorno da luz confirma que a peça passou completamente.
- Cada bloqueio pode emitir somente um alerta de micro-parada.
- Um bloqueio classificado como micro-parada não é contabilizado como peça ao
  ser liberado.
- O botão possui debounce de 50 ms e é processado uma única vez por
  acionamento.
- O loop usa apenas uma espera curta de 10 ms; os controles de tempo
  importantes são não bloqueantes.
- As mensagens seriais seguem exatamente as strings definidas no cenário,
  incluindo pontuação, letras maiúsculas e acentuação.

## Resultados Obtidos

O sistema implementa os comportamentos solicitados para o cenário:

- exibe `Contador de Producao Inicializado` ao iniciar;
- reconhece a sequência de luminosidade alta, baixa e alta como a passagem
  completa de uma peça;
- incrementa o total e exibe `Peca detectada! Total: X`;
- identifica uma obstrução contínua de pelo menos 5 segundos e exibe
  `Alerta: Micro-parada detectada!`;
- trata o acionamento do botão com debounce, zera o turno e exibe
  `Turno resetado com sucesso. Contadores zerados.`;
- mantém o processamento responsivo para acompanhar as alterações de sensor
  realizadas pelos testes automatizados no Wokwi CI.

## Comentários Adicionais

A solução foi mantida enxuta e orientada a estados para reduzir falsos
eventos e facilitar a leitura do firmware. Como evolução, seria possível
adicionar indicadores visuais, persistência da produção e métricas como tempo
médio de ciclo e disponibilidade da linha.
