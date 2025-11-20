# Como funcionan las contraseñas de Tiny Toons Buster hidden treasures? 
El juego, cada vez que completás un nivel, guarda el estado del mapa
en la ram (desde FBF0 a FBF7, 8 bytes).
Cada nibble (4 bits) representa en su mayoría el estado de completitud
de un nivel, aunque los primeros 4 bytes son los niveles y los 4 bytes
restantes son los caminos alternativos. Estos 8 bytes son el llamado
payload. 

## Payload (en RAM FBF0-FBF7)

0123 4567 89ab cdef <- nombre del nibble

FFFF FF3F FFFF FF1F <- payload del juego completo

Esto es lo que representa cada bit de cada nibble en el payload, siendo 3 el nivel 3 y A3 el nivel 3 alternativo:

| Nibble | Bit 1 | Bit 2 | Bit 3 | Bit 4 |
|------|-------|-------|-------|-------|
| 0    | A7    | 6     | 5     | 4     |
| 1    | A3    | 3     | 2     | 1     |
| 2    | 12    | A11   | 11    | 10    |
| 3    | 9     | 8     | 7     | A8    |
| 4    | 19    | 18    | 17    | 16    |
| 5    | A15   | 15    | 14    | 13    |
| 6    | X     | X     | 24    | 23    |
| 7    | 22    | A21   | 21    | 20    |
| 8    | X     | X     | X     | X     |
| 9    | A3    | 3     | X     | X     |
| a    | X     | A11   | 11    | X     |
| b    | X     | 8     | X     | A8    |
| c    | X     | X     | X     | X     |
| d    | 15    | A15   | X     | X     |
| e    | X     | X     | X     | X     |
| f    | X     | A21   | 21    | X     |

Cada posicion es un bit. Si está prendido, debería de estar habilitado el nivel (aunque hay restricciones si no hay niveles al rededor, ya que un nivel no puede estar solo en el aire a excepción del primero que está siempre presente)

Por ejemplo, el payload mínimo para todo el mapa desbloqueado es:

FFFF FF3F 0C65 0C06
y el máximo posible es:

FFFF FFFF FFFF FFFF

El que el juego reconoce como el estado completo es:

FFFF FF3F FFFF FF1F

Ya que lo que hace el juego es ir prendiendo bits específicos según lo que comepletes.

Por ejemplo, los primeros niveles son:

0100 0000 0000 0000  Nivel 1

0300 0000 0100 0000  Nivel 2

0700 0000 0300 0000  Nivel 3

1700 0000 0700 0000

3700 0000 1700 0000

7700 0000 3700 0000

F700 0000 7700 0000

F701 0000 F700 0000

F709 0000 F701 0000

F719 0000 F701 0000

F739 0000 F711 0000

F7B9 0000 F731 0000

F7B9 0100 F731 0000

... ETC. (en realidad no estoy seguro de saber que niveles son los Alternativos y cuales no, yo me basé en que los ALTER son los que toman rutas más raras exceptuando el A7 vs 7 que ahi el de la cueva lo tome como el A7... error? igual para este ejemplo use A7 en vez de mi A7)

## Construcción de contraseña

### Cuerpo
Por ejemplo, para el siguiente payload:

**F7B9 0100 F731 0000**

Si quisiésemos crear una Password tenemos que calcular tres pedazos de ella a partir del payload, estas tres partes siendo:

BODY, CHECKSUM HEADER, CHECKSUM FOOTER.

El cuerpo/body es básicamente pasar el payload a letras usando la siguiente tabla de conversión (encontrada en los binarios del juego):

`
|  0: D/L  |  4: V  |  8: R  |  C: J   |
`

`
|  1: G    |  5: Y  |  9: H  |  D: X   |
`

`
|  2: P    |  6: M  |  A: N  |  E: T   |
`

`
|  3: K    |  7: B  |  B: Z  |  F: Q/W |
`

Todas las demás letras tienen internamente el valor "FF" o indefinido, aunque hay un truco. Estas letras (A E I O U S F C) se pueden usar como valor F si se usan como el lado derecho del par, DU por ejemplo sería lo mismo que 0F)

Entonces tenemos el payload separado en pares

**F7 B9 01 00 F7 31 00 00**

Cada par tenemos que convertirlo a letras con la tabla, pero la conversión se hace primero con la letra del lado derecho (nibble bajo) y luego su lado izquierdo (nibble alto)
Entonces F7 que sería QB ó WB (da lo mismo) nos quedaría BQ ó BW

**BQ HZ GL DL BW GK LL DL**

Este es nuestro cuerpo, o como se vería en la password

**BQ HZGL DLBW GKLL DL**

Ahora nos queda la parte fundamental de la contraseña, el checksum. Esto define si una contraseña es válida, se utiliza como medida de seguridad y validador a la hora de poner contraseñas en el juego.

El header y el pie se calculan usando el cuerpo. El algoritmo del juego elige
aleatoriamente las L/D y las Q/W del cuerpo para generar variedad por lo que el Header cambia según esta aleatoriedad, aunque haya un patrón de fondo
relacionado con la cantidad de una letra respecto a la otra. Esto no pasa con el FOOTER ya que esta cuenta (ver más adelante) se realiza sin tener en cuenta
el valor de las letras.

### Header
Para obtenerlo, primero sumamos los valores intrínsecos de cada letra del cuerpo creado,
Siendo estos:

`
A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7, I=8
`

`
J=9, K=10, L=11, M=12, N=13, O=14, P=15, Q=16, R=17,
`

`
S=18, T=19, U=20, V=21, W=22, X=23, Y=24, Z=25.
`

Nuestro cuerpo era:

**B Q H Z G L D L B W G K L L D L**

BQ = 1 + 16 = 17

HZGL = 7 + 25 + 6 + 11 = 49

DLBW = 3 + 11 + 1 + 22 = 37

GKLL = 6 + 10 + 11 + 11 = 38

DL = 3 + 11 = 14


17 + 49 + 37 + 38 + 14 = 155.

Ahora este número lo pasamos a hexadecimal.
155 es 0x9B en hexadecimal.
En caso de pasarnos de 0xFF nos quedaríamos
con la parte baja del número, (0x2D9 -> 0xD9, se explica en el FOOTER)

Convertimos a letras con la tabla de conversión (Recordar que se convierte de derecha a izquierda):

**0x9B = ZH**

### Footer

Como primer paso, sumamos todos los pares (bytes) hexadecimales del payload:

**F7+B9+01+00+F7+31+00+00: 0x2D9**

Ahora nos quedamos con el byte bajo del número, es decir, borramos todo lo que está adelante y nos quedamos con los últimos dos dígitos, en este caso **0xD9**.
Si hubiésemos hecho la cuenta en decimal, esto es equivalente a tomar módulo 255, o algorítmicamente es hacer `& 0xFF`

Este resultado es nuestro checksum, pero se debemos convertirlo a letras con la tabla, de forma invertida:

**0xD9 = HX**

Contraseña final:

**ZHBQ HZGL DLBW GKLL DLHX**

Esta password corresponde a los niveles 1 al 13 sin caminos bifurcaciones.

## Glitches posibles

La contraseña puede contener los caracteres inválidos "A C E F I O S U" en cualquier parte, siempre y cuando los checksums den correctos (o el cuerpo esté adecuado al checksum)

Por ejemplo, si quisiésemos tener en el header **"_I"** (siendo _ cualquier cosa e I la letra invalida) el checksum debería ser **0xF0** y para tener **"I_"** el checksum debería ser **0xFF** ya que sin importar que sea lo segundo, el `0xFF | <byte>` siempre dará **0xFF**.

Para tener en el cuerpo letras inválidas sucede lo mismo, si tenemos algo como **"I_"** habrá que sumar 0xFF para el pie y si tenemos **"_I"** habrá que sumar 0xF0 al pie. Para el header
debemos de sumar lo que valen las letras con su valor intrínseco.

Para tener **"I_"** en el pie letras inválidas, tenemos que hacer que la suma del cuerpo de **0xFF** (por ejemplo, *QQ DDDD DDDD DDDD DD*) y para **"_I"** nos alcanza con que la suma de **0x0F**

Ejemplos de passwords inválidas que funcionan dentro del juego:

`
DPSS SSSS SSSS SSSS SSRQ
`

`
DPAC EFIO SUAC EFIO SURQ
`

`
YREF AOSC FEFI OOQI AQRW
`

`
NVQQ DDDD DDDD DDDD DDSS
`

`
LUKW WWWW WKJL YMJL BLVZ
`
