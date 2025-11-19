1. Payload (en RAM FBF0)

0123 4567 89ab cdef
FFFF FF3F FFFF FF1F

0: A7 6 5 4
1: A3 3 2 1
2: 12 A11 11 10
3: 9 8 7 A8
4: 19 18 17 16
5: A15 15 14 13
6: X X 24 23
7: 22 A21 21 20
8: X X X X
9: A3 3 X X
a: X A11 11 X
b: X 8 X A8
c: X X X X
d: 15 A15 X X
e: X X X X
f: X A21 21 X

Cada posicion es un bit. Si está prendido, debería de estar habilitado el nivel (aunque hay restricciones si no hay niveles al rededor)
Por ejemplo, el payload minimo para todo desbloqueado es 
FFFF FF3F 0C65 0C06
y el máximo
FFFF FFFF FFFF FFFF

El que el juego reconoce es
FFFF FF3F FFFF FF1F

Ya que lo que hace el juego es ir shifteando (o algo así) 

Por ejemplo, los primeros niveles son:
0100 0000 0000 0000
0300 0000 0100 0000
0700 0000 0300 0000
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
... ETC. (en realidad no termino de saber que niveles son Alter y cuales no, yo me basé en que los ALTER son los que toman rutas más raras exceptuando el A7 vs 7 que ahi el de la cueva lo tome como el A7... error? igual para este ejemplo use A7 en vez de mi A7)

Por ejemplo, para el payload
F7B9 0100 F731 0000
Si quisiésemos crear una Password tenemos que calcular
CUERPO, HEADER, PIE.

El cuerpo es básicamente pasar el payload a letras usando la tabla de conversión:
0:DL	4:V		8:R		C:J
1:G		5:Y		9:H		D:X
2:P		6:M		A:N		E:T
3:K		7:B		B:Z		F:QW (* ojo, acá hay un truco, las letras AEIOUSFC se pueden usar como valor F si se usan como el lado derecho del par, DU por ejemplo sería 0-F)

F7 B9 01 00 F7 31 00 00
Pero cada par se lee desde su low nibble y luego su high nibble entonces quedan al revés:
BQ HZ GL DL BW GK LL DL

Este es nuestro cuerpo, o como se vería en la password
BQ HZGL DLBW GKLL DL

El header y el pie se calculan con el cuerpo. El algoritmo del juego pone
aleatoriamente las LD y QW del cuerpo por lo que el HEADER cambia aleatoriamente
según la cantidad de uno y de otro. Esto no pasa con el PIE porque a fines de ese
cálculo, D y L tienen el mismo valor (en realidad el en payload ambos valen 0)

HEADER:
Sumamos los valores intrínsecos de cada letra del cuerpo creado,
siendo estos:

A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7, I=8
J=9, K=10, L=11, M=12, N=13, O=14, P=15, Q=16, R=17,
S=18, T=19, U=20, V=21, W=22, X=23, Y=24, Z=25.

BQ HZGL DLBW GKLL DL

BQ = 1 + 16 = 17
HZGL = 7 + 25 + 6 + 11 = 49
DLBW = 3 + 11 + 1 + 22 = 37
GKLL = 6 + 10 + 11 + 11 = 38
DL = 3 + 11 = 14

17 + 49 + 37 + 38 + 14 = 155

155 en decimal es 0x9B en hexadecimal.
En caso de pasarnos de 0xFF nos quedaríamos
con la parte baja (0x2D9 -> 0xD9, se explica en el PIE)

Convertimos a letras con la tabla
0x9B = ZH (Recordar que se convierte de derecha a izquierda)

PIE:
Sumamos todos los pares hexadecimales del payload:
F7+B9+01+00+F7+31+00+00: 0x2D9

Ahora le tomamos módulo 256 (si lo hubiésemos hecho en DECIMAL) o 
simplemente borramos la parte alta: 0xD9 (se hace un AND 0xFF)

Este resultado es nuestro header, pero se convierte a letras
de nuevo de forma invertida:
0xD9 = HX

PASSWORD ENTERA:
ZHBQ HZGL DLBW GKLL DLHX

Esta password corresponde a los niveles 1 al 13 por un camino recto.