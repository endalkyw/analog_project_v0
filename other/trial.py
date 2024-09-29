from LUT.read import lut
from LUT.fetch_ import *
import matplotlib.pyplot as plt

tb = fetch_data_1()
markers = [
    'o-',  # circle marker
    's-',  # square marker
    '*-',  # star marker
    'd-',  # thin_diamond marker
    'v-',  # triangle_down marker
    '^-',  # triangle_up marker
    'x-',  # x marker
    '+-',  # plus marker
    '>-',  # triangle_right marker
    '<-',  # triangle_left marker
]

nature_colors = [
    '#E69F00',  # Orange
    '#56B4E9',  # Sky Blue
    '#009E73',  # Bluish Green
    '#F0E442',  # Yellow
    '#0072B2',  # Blue
    '#D55E00',  # Vermilion
    '#CC79A7',  # Reddish Purple
    '#000000',  # Black
]


def gm_id_fin_effect():
  id = tb.lookup("id",1,5,"n",vds_val=0.5)
  gm = tb.lookup("gm",1,5,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, 'o-', color= nature_colors[0], label="fins: 5")

  id = tb.lookup("id",1,10,"n",vds_val=0.5)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, 'x-', color= nature_colors[1],label="fins: 10")

  id = tb.lookup("id",1,15,"n",vds_val=0.5)
  gm = tb.lookup("gm",1,15,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, '*-', color= nature_colors[2], label="fins: 15")

  id = tb.lookup("id",1,40,"n",vds_val=0.5)
  gm = tb.lookup("gm",1,40,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, '--', color= nature_colors[3], label="fins: 20")

  plt.xlabel("$V_{GS},\ V$")
  plt.ylabel("$g_m/I_D,\ S/A$")
  plt.title("$g_m/I_D$ Plots")
  plt.legend()
  plt.savefig("gm_id_fins.png")

def gm_id_stack_effect():
  id = tb.lookup("id",1,10,"n",vds_val=0.5)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, 'o-', color= nature_colors[0], label="stack: 1")

  id = tb.lookup("id",2,10,"n",vds_val=0.5)
  gm = tb.lookup("gm",2,10,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, 'x-', color= nature_colors[1],label="stack: 2")

  id = tb.lookup("id",3,10,"n",vds_val=0.5)
  gm = tb.lookup("gm",3,10,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, '*-', color= nature_colors[2], label="stack: 3")

  id = tb.lookup("id",4,10,"n",vds_val=0.5)
  gm = tb.lookup("gm",4,10,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, '--', color= nature_colors[3], label="stack: 4")

  plt.xlabel("$V_{GS},\ V$")
  plt.ylabel("$g_m/I_D,\ S/A$")
  plt.title("$g_m/I_D$ Plots")
  plt.legend()
  plt.savefig("gm_id_stack.png")

def gm_id_vds_effect():
  id = tb.lookup("id",1,10,"n",vds_val=0.2)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.2)
  plt.plot(tb.vgs, gm/id, 'o-', color= nature_colors[0], label="$v_{ds}:\ 0.2$")

  id = tb.lookup("id",1,10,"n",vds_val=0.4)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.4)
  plt.plot(tb.vgs, gm/id, 'x-', color= nature_colors[1],label="$v_{ds}:\ 0.4$")

  id = tb.lookup("id",1,10,"n",vds_val=0.6)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.6)
  plt.plot(tb.vgs, gm/id, '*-', color= nature_colors[2], label="$v_{ds}:\ 0.6$")

  id = tb.lookup("id",1,10,"n",vds_val=0.8)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.8)
  plt.plot(tb.vgs, gm/id, '--', color= nature_colors[3], label="$v_{ds}:\ 0.8$")

  plt.xlabel("$V_{GS},\ V$")
  plt.ylabel("$g_m/I_D,\ S/A$")
  plt.title("$g_m/I_D$ Plots")
  plt.legend()
  plt.savefig("gm_id_vds.png")






def gm_id():

  plt.figure(figsize=(10,3))


  plt.subplot(1,3,1)
  id = tb.lookup("id",1,5,"n",vds_val=0.5)
  gm = tb.lookup("gm",1,5,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, 'o-', color= nature_colors[0], label="fins: 5")

  id = tb.lookup("id",1,10,"n",vds_val=0.5)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, 'x-', color= nature_colors[1],label="fins: 10")

  id = tb.lookup("id",1,15,"n",vds_val=0.5)
  gm = tb.lookup("gm",1,15,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, '*-', color= nature_colors[2], label="fins: 15")

  id = tb.lookup("id",1,40,"n",vds_val=0.5)
  gm = tb.lookup("gm",1,40,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, '--', color= nature_colors[3], label="fins: 20")
  plt.ylabel("$g_m/I_D,\ S/A$")
  plt.title("$g_m/I_D$ vs $fins$")
  plt.legend()



  plt.subplot(1,3,2)
  id = tb.lookup("id",1,10,"n",vds_val=0.5)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, 'o-', color= nature_colors[0], label="stack: 1")

  id = tb.lookup("id",2,10,"n",vds_val=0.5)
  gm = tb.lookup("gm",2,10,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, 'x-', color= nature_colors[1],label="stack: 2")

  id = tb.lookup("id",3,10,"n",vds_val=0.5)
  gm = tb.lookup("gm",3,10,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, '*-', color= nature_colors[2], label="stack: 3")

  id = tb.lookup("id",4,10,"n",vds_val=0.5)
  gm = tb.lookup("gm",4,10,"n",vds_val=0.5)
  plt.plot(tb.vgs, gm/id, '--', color= nature_colors[3], label="stack: 4")
  plt.xlabel("$V_{GS},\ V$")
  plt.title("$g_m/I_D$ vs $stack$")
  plt.legend()



  plt.subplot(1,3,3)
  id = tb.lookup("id",1,10,"n",vds_val=0.2)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.2)
  plt.plot(tb.vgs, gm/id, 'o-', color= nature_colors[0], label="$v_{ds}:\ 0.2$")

  id = tb.lookup("id",1,10,"n",vds_val=0.4)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.4)
  plt.plot(tb.vgs, gm/id, 'x-', color= nature_colors[1],label="$v_{ds}:\ 0.4$")

  id = tb.lookup("id",1,10,"n",vds_val=0.6)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.6)
  plt.plot(tb.vgs, gm/id, '*-', color= nature_colors[2], label="$v_{ds}:\ 0.6$")

  id = tb.lookup("id",1,10,"n",vds_val=0.8)
  gm = tb.lookup("gm",1,10,"n",vds_val=0.8)
  plt.plot(tb.vgs, gm/id, '--', color= nature_colors[3], label="$v_{ds}:\ 0.8$")


  plt.legend()
  plt.tight_layout()
  plt.title("$g_m/I_D$ vs $v_{ds}$")
  plt.savefig("gm_id.png", dpi=300)




# gm_id_fin_effect()
# gm_id_stack_effect()
# gm_id_vds_effect()
gm_id()