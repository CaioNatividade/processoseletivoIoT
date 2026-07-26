from machine import ADC, Pin
from time import ticks_diff, ticks_ms, sleep_ms


PINO_LDR = 34
PINO_BOTAO = 27

LIMITE_BLOQUEIO = 100
TEMPO_MICRO_PARADA_MS = 5000
TEMPO_DEBOUNCE_MS = 50


ldr = ADC(Pin(PINO_LDR))
ldr.atten(ADC.ATTN_11DB)
ldr.width(ADC.WIDTH_12BIT)

botao = Pin(PINO_BOTAO, Pin.IN, Pin.PULL_UP)


total_pecas = 0

objeto_bloqueando = False
inicio_bloqueio = None
alerta_micro_parada_emitido = False

ultimo_estado_botao = botao.value()
ultimo_instante_mudanca_botao = ticks_ms()
botao_processado = False


print("Contador de Producao Inicializado")


def converter_adc_para_lux(valor_adc):
    return int((valor_adc / 4095) * 1000)


while True:
    agora = ticks_ms()

    valor_adc = ldr.read()
    lux = converter_adc_para_lux(valor_adc)

    bloqueado = lux < LIMITE_BLOQUEIO

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

    estado_atual_botao = botao.value()

    if estado_atual_botao != ultimo_estado_botao:
        ultimo_estado_botao = estado_atual_botao
        ultimo_instante_mudanca_botao = agora

    if ticks_diff(agora, ultimo_instante_mudanca_botao) >= TEMPO_DEBOUNCE_MS:
        if estado_atual_botao == 0 and not botao_processado:
            total_pecas = 0
            objeto_bloqueando = False
            inicio_bloqueio = None
            alerta_micro_parada_emitido = False

            print("Turno resetado com sucesso. Contadores zerados.")
            botao_processado = True

        elif estado_atual_botao == 1:
            botao_processado = False

    sleep_ms(20)
