This is a source file		$must have a title line

.LIB "/project/ssstudents/TAPO_downloads/GF12_V1.0_4.1/12LP/V1.0_4.1/Models/HSPICE/models/12LP_Hspice.lib" TT
.option post = 2
.PARAM wireopt=3 pre_layout_sw=0

.include "nmos_cm_0.pex.dspf"
.param vd0_val = 0.8
.param vd1_val = 0.8

xcm d0 d1 0 nmos_cm_0
Vd0 d0 0 DC vd0_val
Vd1 d10 0 DC vd1_val
Vac d1 d10 AC 1

.DC Vd1 LIN 1 vd1_val vd1_val SWEEP DATA=datanm

.AC LIN 1 10k 10k SWEEP DATA=datanm
.measure ac real_v param = 'VR(d1)' 
.measure ac imag_v param = 'VI(d1)' 
.measure ac real_i param = 'IR(Vac)'
.measure ac imag_i param = 'II(Vac)'
.measure dc Idc find i(Vd1) when v(d1)=vd1_val

.DATA datanm
+ vd0_val vd1_val
+ 0.2   0.2
+ 0.3   0.2
+ 0.4   0.2
+ 0.5   0.2
+ 0.6   0.2
+ 0.2   0.3
+ 0.3   0.4
+ 0.4   0.5
+ 0.5   0.6
+ 0.6   0.7
.ENDDATA

.end

