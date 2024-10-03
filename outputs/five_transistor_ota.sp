*********************************************
.LIB "/project/ssstudents/TAPO_downloads/GF12_V1.0_4.1/12LP/V1.0_4.1/Models/HSPICE/models/12LP_Hspice.lib" TT
.option post = 2
.option ingold = 1
.PARAM wireopt=3 pre_layout_sw=0


.subckt five_transistor_ota vin_m vin_p nx1 is vdd g 
 xm0_0 is is g g nfet m=1 l=1.4e-08 nfin=6 nf=1 par=1 par_nf=1 asej=3.56e-15 adej=3.56e-15 psej=7.14e-07 pdej=7.14e-07 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1 
xm1_0 ny is g g nfet m=1 l=1.4e-08 nfin=6 nf=1 par=1 par_nf=1 asej=3.56e-15 adej=3.56e-15 psej=7.14e-07 pdej=7.14e-07 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1 
xm2_0 nx0 vin_p ny g nfet m=1 l=1.4e-08 nfin=16 nf=1 par=1 par_nf=1 asej=9.50e-15 adej=9.50e-15 psej=1.90e-06 pdej=1.90e-06 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1 
xm3_0 nx1 vin_m ny g nfet m=1 l=1.4e-08 nfin=16 nf=1 par=1 par_nf=1 asej=9.50e-15 adej=9.50e-15 psej=1.90e-06 pdej=1.90e-06 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1 
xm4_0 nx0 nx0 vdd vdd pfet m=1 l=1.4e-08 nfin=2 nf=1 par=1 par_nf=1 asej=1.19e-15 adej=1.19e-15 psej=2.38e-07 pdej=2.38e-07 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1 
xm5_0 nx1 nx0 vdd vdd pfet m=1 l=1.4e-08 nfin=2 nf=1 par=1 par_nf=1 asej=1.19e-15 adej=1.19e-15 psej=2.38e-07 pdej=2.38e-07 pdevdops=1 pdevlgeos=1 pdevwgeos=1 psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp=7.8e-08 fpitch=4.8e-08 xpos=-99 ypos=-99 ptwell=0 sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex=1  
 .ends


xota vin_m vin_p vout is vdd 0 five_transistor_ota
C vout 0 4e-12
Vdd vdd 0 1.2
Is 0 is 2.4e-05
Vcm c 0 0.6
Vdm vd 0 AC 1
Ene vin_m c vd 0 -0.5
Epo vin_p c vd 0 0.5

* ---- Analysis part ----- 
.ac dec 5 1 100G    * Frequency sweep from 10 Hz to 100 kHz, 20 points per decade
.noise v(vout) vdm 100
.print ac vdb(vout) vp(vout) * Print the AC magnitude and phase at node 2 (Vout)
.measure ac gain max vdb(vout)
.measure ac bw when vdb(vout) = 'gain - 3'
.measure ac ugf when vdb(vout) = 0 cross=1
.measure ac Phase_at_0db find vp(vout) when vdb(vout)=0
.measure ac Phase_Margin param='180 + Phase_at_0db'


.end