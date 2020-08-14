from numpy import sqrt, square, divide, inf
from scipy.optimize import curve_fit

def s1_2(q_R,c1_2):
    return c1_2*q_R[0] # q

def t(q_R, c3, c4):
    return c3 + c4*square(q_R[0]) # q

def Rs(q_R): #simulated reflectivity
    return q_R[1] # R

def nb(q_R, i, c1_2, c3, c4, c5):
    return (i*c5*
            t(q_R, c3, c4)*
            square(s1_2(q_R,c1_2)))

def ns(q_R, i, c1_2, c3, c4):
    return i*( Rs(q_R)*
            t(q_R, c3, c4)*
            square(s1_2(q_R,c1_2)) )

def func_dR_R1(q_R, i, c1_2, c3, c4, c5):
    out = divide( sqrt(q_R[1]+2*c5),
                 Rs(q_R)*sqrt(i*t(q_R, c3, c4)*
                             square( s1_2(q_R,c1_2) )) )
    return out

def func_dR_R2(q_R, i, c1_2, c3, c4, c5):
    return ( sqrt( ns(q_R, i, c1_2, c3, c4)+
            2*nb(q_R, i, c1_2, c3, c4, c5) ) /
            ns(q_R, i, c1_2, c3, c4) )

def dR_R_func(q_R, i, c1_2, c3, c4, c5): # difrent
    return divide( sqrt(ns(q_R, i, c1_2, c3, c4)+
            2*c5),
            ns(q_R, i, c1_2, c3, c4) )

# def dR_R_func2(q_R, i, c1_2, c3, c4, c5): # difrent
#     return divide( sqrt(ns(q_R, i, c1_2, c3, c4)+
#             2*c5),
#             ns(q_R, i, c1_2, c3, c4) )

def func_(q_R, i, c1_2, c3, c4, c5):
    pass

def main(sim_q=None, sim_R=None, sim_dR=None, file="SimDataBase_29553_54.dat"):
    # 29553_54.dat
    func = func_dR_R2
#     file = "29553_54.dat"
    import data_in
    data = data_in.data_in(file)
    q = data[0]
    R = data[1]
    dR = data[2]
    q_R = [q,R]
    if sim_q is None:
        sim_q = q
    if sim_R is None:
        sim_R = R
    if sim_dR is None:
        sim_dR = dR
    #[i, c1_2, c3, c4, c5]
    bounds = (0,inf)#[(0,inf),(0,inf),(0,inf),(0,inf),(0,inf)]# 
    dR_R = divide(dR, R)
    out_opt, out_covar = curve_fit(func, q_R, dR_R,bounds=bounds)
    print("out ",out_opt,"\nvar: ", out_covar)
    sim_dR_R = func([sim_q, sim_R], *out_opt)
    #print(q,R,dR)
    return sim_dR_R*sim_R



class tester:
    def __init__(self,ins=False,q=[],R=[],dR=[], cs=[]):
        import numpy as np
        if not ins:
            q = [1.,2.,3.,4.]
            R = [2*x for x in q]
            dR = [x/2 for x in q]
            cs = [1.5,2.5,3.5,4.5,5.5]
        self.q = np.array(q)
        #self.q = []
        self.R = np.array(R)
        self.q_R = np.array([q,R])
        self.dR = np.array(dR)
        self.cs = np.array(cs)
        
    def __call__(self, func=None):
        q_R, i, c1_2, c3, c4, c5 = self.q_R, self.cs[0], self.cs[1], self.cs[2], self.cs[3], self.cs[4]
        if func is None:
            func = [self.s1_2, self.t, self.Rs, self.nb, self.ns, self.func_dR_Rs]
        if not hasattr(func, '__iter__'):
            #q_R, c1_2, c3, c4, c5
            func = [func]
        outs = [f(q_R, i, c1_2, c3, c4, c5) for f in func]
        print(outs)
        self.printout(outs)

    def printout(self,outs):
        if hasattr(outs, '__iter__'):
            outs = all(outs)
        print("results: ", outs)
        
    def s1_2(self, q_R, i, c1_2, c3, c4, c5):
        reqs = [c1_2*x==s for x,s in zip(self.q,s1_2(q_R, c1_2))]
        return all(reqs)

    def t(self, q_R, i, c1_2, c3, c4, c5):
        outs = [(c3+c4*(x**2))==ts for x,ts in zip(self.q,t(q_R, c3, c4))]
        return all(outs)

    def Rs(self, q_R, i, c1_2, c3, c4, c5):
        outs = [x==r for x,r in zip(Rs(q_R),self.R)]
        return all(outs)

    def nb(self, q_R, i, c1_2, c3, c4, c5):
        outs = [i*c5*( (c3+c4*(x**2))*
                      ((c1_2*x)**2) )==n for x,n in zip(self.q,
                           nb(q_R, i, c1_2, c3, c4, c5))]
        return all(outs)
    
    def ns(self, q_R, i, c1_2, c3, c4, c5):
        comp = [i*rs*( (c3+c4*(x**2))*
                      ((c1_2*x)**2) ) for x,rs in zip(self.q,self.R)]
        outs = [x==n for x,n in zip(comp,
                           ns(q_R, i, c1_2, c3, c4))]
        return all(outs)
    
    def func_dR_Rs(self, q_R, i, c1_2, c3, c4, c5):
        result1 = [self.aprox_equal(out1,out2) for out1,out2 in zip( func_dR_R1(q_R, i, c1_2, c3, c4, c5),
                                          func_dR_R2(q_R, i, c1_2, c3, c4, c5) )]
        result2 = [out1==out2 for out1,out2 in zip( func_dR_R1(q_R, i, c1_2, c3, c4, c5), # will not be equal
                                          dR_R_func(q_R, i, c1_2, c3, c4, c5) )]
        result3 = [out1==out2 for out1,out2 in zip( func_dR_R2(q_R, i, c1_2, c3, c4, c5), # will not be equal
                                          dR_R_func(q_R, i, c1_2, c3, c4, c5) )]
        print(result1)
        return ( all(result1) and# all(result2), all(result3),
               self.nb(q_R, i, c1_2, c3, c4, c5) and
               self.ns(q_R, i, c1_2, c3, c4, c5) )

    def aprox_equal(self,one,two,aprox=0.00005):
        return two<=one+aprox and two >=one-aprox


if __name__ == '__main__':
    if False:
        import numpy as np
        a = np.linspace(1,5,num=5) # 1,2,3,4,5
        b = np.linspace(6,10,num=5) # 6,7,8,9,10
        c = np.array([a,b]) # [1,2,3,4,5],[6,7,8,9,10]
        d = np.transpose(c)# [1,6],[2,7],[3,8],[4,9],[5,10]
        print(a,b,c,c[1],c[1,:],d, d[1,:]) #c[1], c[1,:] = [6,7,8,9,10]
        file = "29553_54.dat"
        import data_in
        data = data_in.data_in(file)
        print(data[0],data[:,0])
    elif True:
        print("testing...")
        test = tester()
        test()
    else:
        main()
    
    