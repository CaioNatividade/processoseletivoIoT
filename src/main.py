from machine import Pin
from time import ticks_diff, ticks_ms, sleep_ms


PINO_LDR = 34
PINO_BOTAO = 27

TEMPO_MICRO_PARADA_MS = 5000
TEMPO_DEBOUNCE_MS = 50


ldr = Pin(PINO_LDR, Pin.IN)

botao = Pin(PINO_BOTAO, Pin.IN, Pin.PULL_UP)


total_pecas = 0

objeto_bloqueando = False
inicio_bloqueio = None
alerta_micro_parada_emitido = False

ultimo_estado_lido_botao = botao.value()
estado_estavel_botao = ultimo_estado_lido_botao
instante_mudanca_botao = ticks_ms()
botao_processado = False


print("Contador de Producao Inicializado")


while True:
    agora = ticks_ms()

    bloqueado = ldr.value() == 1

    if bloqueado and not objeto_bloqueando:
        objeto_bloqueando = True
        inicio_bloqueio = agora
        alerta_micro_parada_emitido = False

    elif bloqueado and objeto_bloqueando:
        tempo_bloqueado = ticks_diff(agora, inicio_bloqueio)

        if (
            tempo_bloqueado >= TEMPO_MICRO_PARADA_MS
            and not alerta_micro_parada_emitido
        ):
            print("Alerta: Micro-parada detectada!")
            alerta_micro_parada_emitido = True

    elif not bloqueado and objeto_bloqueando:
        objeto_bloqueando = False
        inicio_bloqueio = None

        if not alerta_micro_parada_emitido:
            total_pecas += 1
            print("Peca detectada! Total: {}".format(total_pecas))

        alerta_micro_parada_emitido = False

    leitura_botao = botao.value()

    if leitura_botao != ultimo_estado_lido_botao:
        ultimo_estado_lido_botao = leitura_botao
        instante_mudanca_botao = agora

    if ticks_diff(agora, instante_mudanca_botao) >= TEMPO_DEBOUNCE_MS:
        if leitura_botao != estado_estavel_botao:
            estado_estavel_botao = leitura_botao

            if estado_estavel_botao == 0 and not botao_processado:
                total_pecas = 0
                objeto_bloqueando = False
                inicio_bloqueio = None
                alerta_micro_parada_emitido = False

                print("Turno resetado com sucesso. Contadores zerados.")
                botao_processado = True

            elif estado_estavel_botao == 1:
                botao_processado = False

    sleep_ms(10)
