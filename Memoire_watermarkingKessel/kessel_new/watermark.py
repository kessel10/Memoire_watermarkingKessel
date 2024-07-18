import cv2
import numpy as np

class Watermark:
    sig_size = 100

    @staticmethod
    def __gene_signature(wm, size):
        wm = cv2.resize(wm, (size, size))
        wm = np.where(wm < np.mean(wm), 0, 1)
        return wm

    def inner_embed(self, B, signature):
        pass

    def inner_extract(self, B):
        pass

    
    def isprem(self, n):
        if n == 1 or n == 2:	
            return True
            
        if n%2 == 0:		
            return False
            
        r = n**0.5
        
        if r == int(r):
            
            return False
        
        for x in range(3, int(r), 2):

            if n % x == 0:
                
                return False	
        
        return True
        
        
    def coupcoup(self,k, long):
        
        d , f = 0 , long
        l = []
        
        while f <= len(k):
            
            l.append(k[d:f])
            
            d , f = f , f + long
            
        
        m = len(k)%long
        
        if m != 0:
            
            l.append(k[len(k)-m:])
        
        return l


    def pgcd(self,a,b):
            
        while (b>0):
            
            r=a%b
            
            a,b=b,r
            
        return a
        
        
        
    def pgcde(self,a, b):
        
        r, u, v = a, 1, 0
        rp, up, vp = b, 0, 1
        
        while rp != 0:
            q = r//rp
            rs, us, vs = r, u, v
            r, u, v = rp, up, vp
            rp, up, vp = (rs - q*rp), (us - q*up), (vs - q*vp)
        
        return (r, u, v)

    def key(self):
        
        #choix au hasard de deux entiers premiers (n et q)
        p = np.random.choice(1000,1)
        q = np.random.choice(1000,1)
        
        while self.isprem(p) is False:
            p = np.random.choice(1000,1)
            
        while self.isprem(q) is False:
            q = np.random.choice(1000,1)
            
        #calcul de n et m
        n = p*q
        m = (p-1)*(q-1)
        
        #recherche de c premier de m (c'est a dire tel que pgcd(m,c)=1 ) et de d = pgcde(m,c) tel que 2 < d < m
        r = 10
        d = 0
        while r != 1 or d <= 2 or d >= m:
            c = np.random.choice(1000,1)
            r, d, v = self.pgcde(c,m)
            
        n, c, d = int(n), int(c), int(d)
        

        return {"priv":(n,c), "pub":(n,d)}


    def enregistrerCle(self):
        dic = self.key()
        with open("clePrivePublique.txt", "w+") as cle :
            cle.write("Cle privee : "+ str(dic['priv'])+"\n")
            cle.write("Cle publique : "+ str(dic['pub']))
        cle.close()

    def cryptage(self,img, key=34) :
        self.enregistrerCle()
        fin = open(img, 'rb')
        val = key
        image = fin.read()
        fin.close()
        
    
        #image = bytearray(image)
    
    
        #for index, values in enumerate(image):
            #image[index] = values ^ val
    
    
        #fin = open(img, 'wb')
        
        #fin.write(image)
        #fin.close()
        print('Cryptage effectuee avec succes...')
 
    def extract(self, wmimg):
        B = None
        print(wmimg)
        print(type(wmimg))
        if len(wmimg.shape) > 2:
            (B, G, R) = cv2.split(cv2.cvtColor(wmimg, cv2.COLOR_BGR2YUV))
        else:
            B = wmimg
        ext_sig = self.inner_extract(B)[0]
        ext_sig = np.array(ext_sig).reshape((self.sig_size, self.sig_size))
        ext_sig = np.where(ext_sig == 1, 255, 0)
        return ext_sig

    def drecryptage(self,img, key=34) :
        self.enregistrerCle()
        fin = open(img, 'rb')
        image = fin.read()
        val = key
        fin.close()
     
        image = bytearray(image)

        for index, values in enumerate(image):
            image[index] = values ^ val
    
        fin = open(img, 'wb')
        
        fin.write(image)
        fin.close()
        print('Decryptage effectué avec succes...')


    def embed(self, cover, wm):
        print(cover.shape)
        self.enregistrerCle()
        B = None
        img = None
        signature = None
        if len(cover.shape) > 2:
            img = cv2.cvtColor(cover, cv2.COLOR_BGR2YUV)
            signature = self.__gene_signature(wm, self.sig_size).flatten()
            B = img[:, :, 0]

        if len(cover.shape) > 2:
            img[:, :, 0] = self.inner_embed(B, signature)
            cover = cv2.cvtColor(img, cv2.COLOR_YUV2BGR)
        else:
            cover = B
        return cover
