-------------------------
Форк baranchuk/geiger — изменения относительно diyruz/geiger
-------------------------

Готовая прошивка — в разделе Releases (`DIYRuZ_Geiger.hex` — для SmartRF Flash Programmer / CC Debugger,
`DIYRuZ_Geiger_cclib.hex` — для прошивки через ESP8266, см. ниже). Вариант — роутер (питание от USB), как
`DIYRuZ_Geiger.hex` оригинала. Совместима с конвертером DIYRuZ_Geiger в zigbee2mqtt.

## Что изменено

- **Бипер.** На плате стоит пассивный пьезоизлучатель Murata PKLCS1212E4001-R1 (12×12 мм, без генератора,
  полярности нет) на транзисторе Q4; база через R14 от вывода **P1.5** модуля E18-MS1PA1-PCB (вывод 10;
  светодиод — P1.4, вывод 11). Тон 3,9 кГц формирует Timer 4 (модуль `Source/buzzer.c`): 1 МГц, счёт по модулю
  до T4CC0 = 124, прерывание по сравнению канала 0 (8 кГц), в прерывании переключается P1.5.
  Важно: в режиме «по модулю» Timer 4 у CC2530 **не выставляет флаг переполнения** — прерывание брать с канала 0.
  - `buzzer_feedback` (атрибут 0xF002, есть в zigbee2mqtt, по умолчанию ВЫКЛ): щелчок 4 мс на каждую частицу.
  - **`buzzer_alarm`** (0xF006, новый, по умолчанию ВКЛ): пока уровень выше `alert_threshold`, сигнал
    250 мс раз в секунду. Не зависит от щелчков.
  - **`boot_indication`** (0xF007, новый, по умолчанию ВКЛ): после старта прошивки светодиод гаснет на 0,5 с
    (во время загрузки он горит от подтяжки выводов), затем две вспышки, каждая с сигналом 80 мс.
- **Исправлен расчёт мкР/ч** для СБМ-20 и СБМ-19 выше 200 имп/с (12 000 имп/мин): в формулах был лишний
  множитель `cps`, при высоком фоне показания завышались в сотни раз.
- `sensors_count = 0` больше не приводит к делению на ноль.
- Настройки хранятся под новым NV-id 0x0402: после перехода с оригинальной прошивки — настройки по умолчанию.

Новые атрибуты пока не в конвертере zigbee2mqtt; читать/писать их общим механизмом z2m
(61446 = `buzzer_alarm`, 61447 = `boot_indication`, тип 16 = boolean):

    mosquitto_pub -t 'zigbee2mqtt/<устройство>/set' -m '{"write":{"cluster":"msIlluminanceLevelSensing","payload":{"61446":{"value":0,"type":16}}}}'
    mosquitto_pub -t 'zigbee2mqtt/<устройство>/set' -m '{"read":{"cluster":"msIlluminanceLevelSensing","attributes":[61446,61447]}}'

Щелчки на частицы включаются штатным переключателем `buzzer_feedback` в z2m.

## Что проверено на железе (2026-10-02)

| Что | Состояние |
|---|---|
| Сборка в IAR (конфигурация `DIYRuZ_Geiger`) | 0 ошибок, 0 предупреждений, ~209 КБ кода |
| Прошивка 4 плат через ESP8266, проверка чтением | все страницы совпадают |
| Старт, две вспышки + два сигнала | работает |
| Бипер на P1.5 (3,9 кГц) | работает |
| Щелчки `buzzer_feedback`, тревога `buzzer_alarm` | собрано, на плате ещё не проверено |
| Расчёт мкР/ч, работа в сети zigbee2mqtt | на плате ещё не проверено |

Замечание по плате: на тестовой плате импульс на INT_1 (коллектор Q3) опускается лишь до ~1,9 В, а не до нуля,
и вход P0.4 может пропускать часть импульсов — стоит проверить R11/R12/R13 и Q3 на своих платах осциллографом.

## Прошивка модуля

Через ESP8266 (Wemos/Lolin D1 mini) вместо CC Debugger — `tools/esp8266-cc-flasher/README.md`
(~18 мин на плату, с проверкой). Через CC Debugger / SmartRF Flash Programmer — `DIYRuZ_Geiger.hex` как обычно.

## Сборка

IAR Embedded Workbench for 8051 + Z-Stack 3.0.2 (бесплатно у TI: https://www.ti.com/tool/Z-STACK).
Проект кладётся в `Z-Stack 3.0.2\Projects\zstack\HomeAutomation\geiger`, открыть `CC2530DB/GenericApp.eww`,
конфигурация `DIYRuZ_Geiger`. Перед сборкой IAR запускает `python ver.py` — Python должен быть в PATH.
Проверено на IAR из Embedded Workbench 8.3. Новые версии IAR не находят `?B`/`?IE` при компоновке — добавить в конец
`Projects\zstack\Tools\CC2530DB\f8w2530.xcl`:

    -D?B=0xF0
    -D?IE=0xA8

Из командной строки:

    IarBuild.exe GenericApp.ewp -make DIYRuZ_Geiger -log warnings

Результат: `firmwares\DIYRuZ_Geiger.hex`.


-------------------------
Индикатор радиоактивности Zigbee

https://modkam.ru/?p=1591

https://github.com/diyruz/geiger
-------------------------


Сброс устройства для подключения к сети:
- Обесточить устройство (лучше всего кабель от источника питания отключать).
- Подать питание и дождаться, пока не загорится светодиод, тут же питание отключить на секунду и подать вновь.
- Повторить цикл подачи питания 5 раз. 
- Через некоторое время устройство начнет сопряжение с сетью ZigBee (на координаторе также нужно включить режим сопряжения).
  
-------------------------

Настройки:

# Тип трубки (0: СБМ-20/СТС-5/BOI-33; 1: СБМ-19/СТС-6; 3: все остальное):
mosquitto_pub -h mqtt_server -u mqtt_user -P mqtt_password -t 'zigbee2mqtt/0x00124b001ec7777e/1/set/sensors_type' -m '0' -d

# Кол-во трубок:
mosquitto_pub -h mqtt_server -u mqtt_user -P mqtt_password -t 'zigbee2mqtt/0x00124b001ec7777e/1/set/sensors_count' -m '2' -d
# Когда трубки две - показания меньше плавают, чем с одной. Но, мне кажется, показания несколько завышаются при этом.

# Число милирентген для аларма:
mosquitto_pub -h mqtt_server -u mqtt_user -P mqtt_password -t 'zigbee2mqtt/0x00124b001ec7777e/1/set/alert_threshold' -m '60' -d

# Мигание диодом на события радиации:
mosquitto_pub -h mqtt_server -u mqtt_user -P mqtt_password -t 'zigbee2mqtt/0x00124b001ec7777e/1/set/led_feedback' -m 'ON' -d

# НЕ ПОДДЕРДИВАЕТСЯ: Пищание на события радиации:

mosquitto_pub -h mqtt_server -u mqtt_user -P mqtt_password -t 'zigbee2mqtt/0x00124b001ec7777e/1/set/buzzer_feedback' -m 'ON' -d

# Удаление из сети:
mosquitto_pub -h mqtt_server -u mqtt_user -P mqtt_password -t 'zigbee2mqtt/bridge/config/remove' -m '0x00124b001ec7777e' -d

0x00124b001ec7777e - адрес или friendly name индикатора радиоактивности, поменять на свое значение

Не проверял:
Sensitivity: mosquitto_pub -t "zigbee2mqtt/FN/BUTTON_NUM/set/sensitivity" -m '100' This attribute will be used on reporting, pulsesCount * sensitivity. You can use this attribute to setup reporting in your prefered units radiationDosePerHour = pulsesCount * sensitivity

-------------------------

alert_threshold — выставляем уровень в мкР/ч при превышении которого сработает сигнализация

buzzer — встроенный зуммер (поддержка пока не реализована)

Led — включаем/выключаем светодиод отображающий регистрацию частиц

rph — регистрируемое значение в мкР/ч

rpm — регистрируемое значение частиц в минуту

sensitivity — чувствительность счетчика (используется если выбран пункт 3 в sensor_type)

sensor_type — выбор типа счетчика:

0) СБМ-20/СТС-5/BOI-33
1) СБМ-19/СТС-6
3) все остальное

sensors_count — количество установленных счетчиков


