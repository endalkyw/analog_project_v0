*********************************************
.LIB "/project/ssstudents/TAPO_downloads/GF12_V1.0_4.1/12LP/V1.0_4.1/Models/HSPICE/models/12LP_Hspice.lib" TT
.option post = 2
.option ingold = 1
.PARAM wireopt=3 pre_layout_sw=0


.subckt five_transistor_ota vin_m vin_p nx1 is vdd g 
 xm0_0 is is g g nfet m=1 l=1.4e-08 nfin=12 nf=1 par=1 par_nf=1 asej=7.13e-15 adej=7.13e-15 psej=1.43e-06 pdej=1.43e-06 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1 
xm1_0 ny is g g nfet m=1 l=1.4e-08 nfin=12 nf=1 par=1 par_nf=1 asej=7.13e-15 adej=7.13e-15 psej=1.43e-06 pdej=1.43e-06 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1 
xm2_0 nx0 vin_p ny g nfet m=1 l=1.4e-08 nfin=23 nf=1 par=1 par_nf=1 asej=1.37e-14 adej=1.37e-14 psej=2.74e-06 pdej=2.74e-06 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1 
xm3_0 nx1 vin_m ny g nfet m=1 l=1.4e-08 nfin=23 nf=1 par=1 par_nf=1 asej=1.37e-14 adej=1.37e-14 psej=2.74e-06 pdej=2.74e-06 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1 
xm4_0 nx0 nx0 vdd vdd pfet m=1 l=1.4e-08 nfin=15 nf=1 par=1 par_nf=1 asej=8.91e-15 adej=8.91e-15 psej=1.78e-06 pdej=1.78e-06 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1 
xm5_0 nx1 nx0 vdd vdd pfet m=1 l=1.4e-08 nfin=15 nf=1 par=1 par_nf=1 asej=8.91e-15 adej=8.91e-15 psej=1.78e-06 pdej=1.78e-06 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1  
 .ends


.param v1=0.15v v2=-0.15v td=50ns tr=1ns tf=1ns pw=200ns per=400ns
xota vout vin_p vout is vdd 0 five_transistor_ota
C vout 0 2e-11
Vdd vdd 0 1.2
Is 0 is 7e-05
Vcm c 0 0.6
vpulse vin_p c pulse( v1 v2 td tr tf pw per )

* ---- Analysis part ----- 
.tran 1n 1000n
.measure tran max_v max v(vout)
.measure tran min_v min v(vout)
.measure tran del param = 'max_v - min_v'
.measure tran vout10 param = '0.1*del + min_v'
.measure tran vout90 param = '0.9*del + min_v'
.measure tran t10 when v(vout) = 'vout10' rise=1
.measure tran t90 when v(vout) = 'vout90' rise=1
.measure tran slew_rate param = '(vout90-vout10)/(t90-t10)'


.end