* RC Low-Pass Filter with AC Analysis and Parameter Sweep Using .ALTER and .DATA

* Define the resistor value
.param R1=1k

* Define the circuit with placeholder for capacitor value
Vin 1 0 AC 1        * AC source with amplitude 1V
R1 1 2 R1           * Resistor (1k ohm)
C1 2 0 C1           * Capacitor (value to be swept)

* Using .DATA and .ALTER for sweeping
.data sweep_data
+ C1
+ 1n
+ 10n
+ 100n
.enddata

.alter sweep_data
.ac dec 10 1 1meg
.print ac V(2)

.end