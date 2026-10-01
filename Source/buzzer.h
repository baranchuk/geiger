#ifndef BUZZER_H
#define BUZZER_H

/*
 * Passive piezo buzzer (BUZZER1 = PKLCS1212E4001, resonance 4 kHz) driven by Q4 from P1.5
 * (E18-MS1PA1-PCB pin 10, through R14). The tone is made by Timer 4: an 8 kHz overflow
 * interrupt toggles the pin, giving a 4 kHz square wave for the requested time.
 */

#define BUZZER_CLICK_MS 4    // per detected particle: a short "tick"
#define BUZZER_ALARM_MS 250  // alarm beep length, repeated every APP_ALARM_PERIOD
#define BUZZER_BOOT_MS 80    // boot indication: two beeps of this length

extern void buzzer_init(void);
extern void buzzer_beep(uint16 ms); // safe from an ISR; only ever lengthens an ongoing beep
extern void buzzer_stop(void);

#endif
