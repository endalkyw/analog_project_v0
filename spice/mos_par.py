import math

class params:
    p = {"name":"mn0", "d_name":"d", "g_name":"g", "s_name":"s", "b_name":"b",
         "type":"nfet", "m":1, "l":14e-9, "nfin": 2, "nf":1, "par":1, "par_nf":1,
         "asej":1e-6, "adej": 1e-6, "psej":2e-6, "pdej": 2e-6, "cpp":78e-9, "fpitch": 48e-9, "nf_pex":1}
    mos = ["x{name} {d_name} {g_name} {s_name} {b_name} {type} m={m} l={l} nfin={nfin} nf={nf} par={par} "
            "par_nf={par_nf} asej={asej} adej={adej} psej={psej} pdej={pdej} pdevdops=1 pdevlgeos=1 pdevwgeos=1 " 
            "psw_acv_sign=1 plnest=1 pldist=1 plorient=0 cpp={cpp} fpitch={fpitch} xpos=-99 ypos=-99 ptwell=0 "
            "sca=0 scb=0 scc=0 pre_layout_local=-1 ngcon=1 p_vta=0 p_la=0 u0mult_fet=1 lle_sa=71e-9 lle_sb=71e-9 " 
            "lle_rxrxa=78e-9 lle_rxrxb=78e-9 lle_rxrxn=192e-9 lle_rxrxs=192e-9 lle_pcrxn=55e-9 lle_pcrxs=55e-9 "
            "lle_nwa=2e-6 lle_nwb=2e-6 lle_nwn=192e-9 lle_nws=192e-9 lle_ctne=0 lle_ctnw=0 lle_ctse=0 lle_ctsw=0 "
            "lle_sctne=0 lle_sctnw=0 lle_sctse=0 lle_sctsw=0 lrsd=27e-9 dtemp=0 l_shape=0 l_shape_s=0 nsig_dop1=0 "
            "nsig_dop2=0 nsig_dibl=0 nsig_pc=0 nsig_rx=0 fc_index=0 fc_sigma=3 analog=-1 nf_pex={nf_pex} "]
    mos = " ".join(mos)

    def get_mos_string(self,name, d, g, s, b, type,fins,nf=1,m=1,sd=[1,1],source_first=True, stack = 1):
        if source_first:
            n_s = int(math.ceil(nf/2) + (nf+1)%2)
            n_d = int(math.ceil(nf/2))
            if n_s == n_d:
                n_s_ext = 1
                n_s_int = n_s-1
                n_d_ext = 1
                n_d_int = n_d-1
            else:
                n_s_ext = 2
                n_s_int = n_s-2
                n_d_ext = 0
                n_d_int = n_d

            self.p["name"] = name
            self.p["nfin"] = fins
            self.p["type"] = type
            self.p["nf"]   = nf
            self.p["m"]    = m
            self.p["par"]  = m
            self.p["nf_pex"] = nf
            self.p["par_nf"] = self.p["m"]*self.p["nf"]

            self.p["d_name"] = d
            self.p["g_name"] = g
            self.p["s_name"] = s
            self.p["b_name"] = b

            # all calculation are based on fin width: 54nm and the height: 11nm
            asej = n_s_ext*(54e-9)*(11e-9)*self.p["nfin"] + (self.p["cpp"]-14e-9-10e-9)*(11e-9)*n_s_int*self.p["nfin"]/sd[0]
            adej = n_d_ext*(54e-9)*(11e-9)*self.p["nfin"] + (self.p["cpp"]-14e-9-10e-9)*(11e-9)*n_d_int*self.p["nfin"]/sd[1]
            psej = n_s_ext*self.p["nfin"]*(2*(54e-9)+11e-9) + self.p["nfin"]*n_s_int*2*(self.p["cpp"]-14e-9-10e-9)/sd[0]
            pdej = n_d_ext*self.p["nfin"]*(2*(54e-9)+11e-9) + self.p["nfin"]*n_d_int*2*(self.p["cpp"]-14e-9-10e-9)/sd[1]

            self.p["asej"] = f"{asej:.2e}"
            self.p["adej"] = f"{adej:.2e}"
            self.p["psej"] = f"{psej:.2e}"
            self.p["pdej"] = f"{pdej:.2e}"


            net_names = []
            for i in range(stack-1):
                net_names.append(f"{name}_{i}")
                net_names.append(f"{name}_{i}")
            

            stacks = []
            if type == "nfet":
                diff_names = [d] + net_names + [s]
                for i in range(stack):
                    self.p["name"]   = f"{name}_{i}"
                    self.p["d_name"] = diff_names[2*i]
                    self.p["s_name"] = diff_names[2*i + 1]
                    stacks.append(self.mos.format(**self.p))

            else:
                diff_names = [s] + net_names + [d]
                for i in range(stack):
                    self.p["name"]   = f"{name}_{i}"
                    self.p["s_name"] = diff_names[2*i]
                    self.p["d_name"] = diff_names[2*i + 1]
                    stacks.append(self.mos.format(**self.p))
        

            mos_str = "\n".join(stacks)

            return mos_str

if __name__ == "__main__":
    p = params()
    str = p.get_mos_string("mn0","d","g","s","b","nfet",10,4,1, stack=3)
    print(str)