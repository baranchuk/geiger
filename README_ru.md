-------------------------
Форк baranchuk/geiger — изменения относительно diyruz/geiger
-------------------------

Прошивка (Source/):
- **Бипер.** На плате стоит пассивный пьезоизлучатель PKLCS1212E4001 (4 кГц) на Q4; база через R14 от вывода
  **P1.5** модуля (E18-MS1PA1-PCB, вывод 10; светодиод — P1.4, вывод 11). Звук формируется Timer 4
  (прерывание 8 кГц, меандр 4 кГц на P1.5), модуль `buzzer.c`.
  - `buzzer_feedback` (атрибут 0xF002, уже есть в zigbee2mqtt): короткий щелчок на каждую частицу.
  - Новый атрибут **`buzzer_alarm`** (0xF006, по умолчанию ВКЛ): пока уровень выше `alert_threshold`,
    сигнал тревоги 250 мс раз в секунду. Работает независимо от щелчков.
- **Исправлен расчёт мкР/ч** для СБМ-20 и СБМ-19 выше 200 имп/с (12 000 имп/мин): в формулах был лишний
  множитель `cps`, и при высоком фоне показания завышались в сотни раз.
- `sensors_count = 0` больше не приводит к делению на ноль.
- Настройки хранятся под новым NV-id (0x0402): после обновления с оригинальной прошивки устройство
  стартует с настройками по умолчанию.

`buzzer_alarm` пока нет в конвертере zigbee2mqtt; читать/писать можно общим механизмом z2m:

    mosquitto_pub -t 'zigbee2mqtt/<устройство>/set' -m '{"write":{"cluster":"msIlluminanceLevelSensing","payload":{"61446":{"value":0,"type":16}}}}'
    mosquitto_pub -t 'zigbee2mqtt/<устройство>/set' -m '{"read":{"cluster":"msIlluminanceLevelSensing","attributes":[61446]}}'

Прошивка модуля через ESP8266 (D1 mini) вместо CC Debugger: `tools/esp8266-cc-flasher/README.md`.

Сборка: IAR Embedded Workbench for 8051 + Z-Stack 3.0.2 (проект `CC2530DB/GenericApp.eww`, перед сборкой
`python ver.py`; Python должен быть в PATH). Проект кладётся в `Z-Stack 3.0.2\Projects\zstack\HomeAutomation\geiger`.
Собирается в IAR EW8051 из Embedded Workbench 8.3 (конфигурация `DIYRuZ_Geiger`: 0 ошибок, 0 предупреждений в коде
приложения, ~209 КБ кода). Новые версии IAR не находят `?B`/`?IE` при компоновке — добавить в конец
`Projects\zstack\Tools\CC2530DB\f8w2530.xcl` две строки:

    -D?B=0xF0
    -D?IE=0xA8

Сборка из командной строки:

    IarBuild.exe GenericApp.ewp -make DIYRuZ_Geiger -log warnings

Изменения форка собраны, на железе ещё не проверены.


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


