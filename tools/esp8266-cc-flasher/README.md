# Прошивка E18 (CC2530) через ESP8266 (Wemos/Lolin D1 mini)

Проверено 2026-10-01 на плате DIYRuZ Geiger с модулем E18-MS1PA1-PCB (заводской, заблокированный).

## Подключение (разъём J1 на плате, подписи на нижнем слое; квадратная площадка = GND)

| J1         | D1 mini |
|------------|---------|
| GND        | G       |
| P2.1 (DD)  | D5      |
| P2.2 (DC)  | D2      |
| RST        | D1      |
| VCC        | не подключать — плата питается от своего USB |

Питать плату от 3V3 D1 mini можно, но импульсный преобразователь ВВ даёт помехи на общей
шине 3,3 В: в таком режиме запись срывалась. Трубки на время прошивки вынуть.

## Программатор

[CCLib](https://github.com/kirovilya/CCLib) (форк с поддержкой ESP8266), пример `Arduino/CCLib/Examples/CCLib_proxy`,
`platformio.ini` уже есть (`env:d1_mini`). Наложить `CCLib_proxy-d1mini.patch`:

- DD на одном выводе D5 (у ESP 3,3 В, делитель не нужен; библиотека сама переключает направление);
- Wi-Fi выключен (меньше пиков тока);
- `Serial.setRxBufferSize(4096)` — **обязательно**: штатный буфер 256 байт, пакеты по 2 КБ теряются,
  и запись обрывается с «Could not read from the serial port»;
- 115200 бод (страница 2 КБ ≈ 0,2 с вместо 2 с).

`pio run -t upload --upload-port COMx`

## Python-часть

Python 3 + `pyserial`. CCLib написан под Python 2 — наложить `cclib-python3.patch` на `Python/cclib/ccproxy.py`
(bytes вместо chr/ord, 115200 бод, ожидание загрузки ESP 4 с).

Из HEX релиза удалить запись типа 05 (CCLib её не понимает):

    grep -v "^:04000005" DIYRuZ_Geiger.hex > DIYRuZ_Geiger_cclib.hex

Скопировать `flash_e18.py` и `resume_e18.py` в `CCLib/Python/` и запустить:

    python cc_info.py -p COM3                          # видим CC2530, DEBUG_LOCKED у заводского модуля
    python flash_e18.py COM3 DIYRuZ_Geiger_cclib.hex  # стирание + запись + проверка

`flash_e18.py` сначала стирает чип и переподключается (заблокированный чип сообщает размер флеша 16 КБ, после
стирания — 256 КБ), затем пишет с проверкой. Если запись оборвалась, продолжить с адреса страницы:

    python resume_e18.py COM3 DIYRuZ_Geiger_cclib.hex 0x22000

Время при 115200: около 12 с на страницу 2 КБ с проверкой.
