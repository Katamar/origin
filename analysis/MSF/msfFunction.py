import MDAnalysis
import MDAnalysis.KDTree.NeighborSearch as NS
import MDAnalysis.analysis.align as AL
import numpy as np

def accumulate_positions(lenc, coord, x_avg, y_avg, z_avg, x_a, y_a, z_a):
    for j in range(0,lenc):
        x_avg[j]+=coord[j][0]
        y_avg[j]+=coord[j][1]
        z_avg[j]+=coord[j][2]
        x_a[j]+=coord[j][0]*coord[j][0]
        y_a[j]+=coord[j][1]*coord[j][1]
        z_a[j]+=coord[j][2]*coord[j][2]
    return x_avg, y_avg, z_avg, x_a, y_a, z_a

def average_positions(lenc, fixedWindowWidth, x_avg, y_avg, z_avg, x_a, y_a, z_a):
    finalval=0
    for j in range(0,lenc):
        x_avg[j]=(x_avg[j]/fixedWindowWidth)*(x_avg[j]/fixedWindowWidth)
        y_avg[j]=(y_avg[j]/fixedWindowWidth)*(y_avg[j]/fixedWindowWidth)
        z_avg[j]=(z_avg[j]/fixedWindowWidth)*(z_avg[j]/fixedWindowWidth)
        x_a[j]=x_a[j]/fixedWindowWidth
        y_a[j]=y_a[j]/fixedWindowWidth
        z_a[j]=z_a[j]/fixedWindowWidth
        finalval+=1.0/3.0*(x_a[j]-x_avg[j]+y_a[j]-y_avg[j]+z_a[j]-z_avg[j])
    return finalval

def msf_win(begin, end, ref, trj, fixedWindowWidth, lenH, H_Catoms, u1, u2):
   x_avg=[0]*lenH
   y_avg=[0]*lenH
   z_avg=[0]*lenH
   x_a=[0]*lenH
   y_a=[0]*lenH
   z_a=[0]*lenH
   finalval=0
   for ts in u2.trajectory[begin:end]:
      result=AL.alignto(trj, ref, select="name CA")
      coord=H_Catoms.atoms.coordinates()
      accumulate_positions(len(coord), coord, x_avg, y_avg, z_avg, x_a, y_a, z_a)
   win_avg=average_positions(len(coord), fixedWindowWidth, x_avg, y_avg, z_avg, x_a, y_a, z_a)
   win_avg/=float(len(coord))
   return win_avg 

def blocksum(blocklen, fixedWindowWidth, begin, end, ref, trj, lenH, H_Catoms, u1, u2):
    blocks=0
    count=0
    for i in range(begin, begin+blocklen, fixedWindowWidth):
        count+=1
        begin=i
        end=i+fixedWindowWidth
        #print 'begin end', begin, end
        blocks+=msf_win(begin, end, ref, trj, fixedWindowWidth, lenH, H_Catoms, u1, u2)
    #print 'blocks before division', blocks
    blocks/=float(count)
    #print ' blocks/count', blocks
    return blocks


def main():
    pdb="2lym_wbi.pdb"
    psf="2lym_wbi.psf"
    dcd="1000.dcd"
    
    u1 = MDAnalysis.Universe(pdb)
    u2 = MDAnalysis.Universe(psf, dcd)
    print len(u2.trajectory)
    
    fixedWindowWidth=2
    begin=0
    end=begin+fixedWindowWidth
    blocklen=4

    for i in 'U':
        segment=u2.selectAtoms("segid %s" %(i))
        #print(segment)
        hy = segment.selectAtoms("name H*")
        car = segment.selectAtoms("name C*")
        ns_hy=NS.AtomNeighborSearch(hy)
        H_Catoms=ns_hy.search_list(car, 1.5)
        #coord=H_Catoms.atoms.coordinates()
        #print len(coord), len(coord)
        lenH=len(H_Catoms)
        ref = u1.selectAtoms("segid %s" %(i))
        trj = u2.selectAtoms("segid %s" %(i))
        
        
        #print msf_win(begin, end, ref, trj, fixedWindowWidth, lenH, H_Catoms, u1, u2)
        #print blocksum(blocklen, fixedWindowWidth, begin)
        blocksum(blocklen, fixedWindowWidth, begin, end, ref, trj, lenH, H_Catoms, u1, u2)

if __name__ == "__main__":
    main()
