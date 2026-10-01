#include "hal_mcu.h"
#include "hal_types.h"
#include "hal_defs.h"
#include "buzzer.h"

#define BUZZER_BV BV(5)
#define BUZZER_SBIT P1_5

// Timer 4: tick 32 MHz / 32 = 1 MHz, modulo mode up to T4CC0 -> overflow every 125 us (8 kHz)
#define T4_DIV_32 (5 << 5)
#define T4_START BV(4)
#define T4_OVFIM BV(3)
#define T4_CLR BV(2)
#define T4_MODE_MODULO 0x02
#define T4_PERIOD_TICKS 125
#define T4_TOGGLES_PER_MS 8

#define TIMIF_T4OVFIF BV(3)
#define IEN1_T4IE BV(4)

static volatile uint16 buzzerTogglesLeft = 0;

void buzzer_init(void) {
    P1SEL &= ~BUZZER_BV; // GPIO
    P1DIR |= BUZZER_BV;  // output
    BUZZER_SBIT = 0;     // Q4 off: no DC through the piezo

    T4CTL = T4_CLR;      // stopped, counter cleared
    T4CC0 = T4_PERIOD_TICKS - 1;
    TIMIF &= ~TIMIF_T4OVFIF;
    T4IF = 0;
    IEN1 |= IEN1_T4IE;
}

void buzzer_beep(uint16 ms) {
    halIntState_t intState;
    HAL_ENTER_CRITICAL_SECTION(intState);
    uint16 toggles = ms * T4_TOGGLES_PER_MS;
    if (toggles > buzzerTogglesLeft) { // a particle tick must not cut an alarm beep short
        buzzerTogglesLeft = toggles;
    }
    T4CTL = T4_DIV_32 | T4_START | T4_OVFIM | T4_CLR | T4_MODE_MODULO;
    HAL_EXIT_CRITICAL_SECTION(intState);
}

void buzzer_stop(void) {
    halIntState_t intState;
    HAL_ENTER_CRITICAL_SECTION(intState);
    buzzerTogglesLeft = 0;
    T4CTL = T4_CLR;
    BUZZER_SBIT = 0;
    HAL_EXIT_CRITICAL_SECTION(intState);
}

HAL_ISR_FUNCTION(buzzerTimer4Isr, T4_VECTOR) {
    HAL_ENTER_ISR();
    TIMIF &= ~TIMIF_T4OVFIF;
    T4IF = 0;
    if (buzzerTogglesLeft > 0) {
        BUZZER_SBIT = !BUZZER_SBIT;
        buzzerTogglesLeft--;
    } else {
        T4CTL = T4_CLR; // stop the timer, leave the transistor off
        BUZZER_SBIT = 0;
    }
    HAL_EXIT_ISR();
}
