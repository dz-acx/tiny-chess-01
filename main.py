import os;from json import loads,dumps;from urllib.request import Request,urlopen
ENV=os.environ.get("MAKEFUN_ENV_URL","http://localhost:8000").rstrip("/")
MAX_N=30000;VAL=dict(P=100,N=320,B=330,R=500,Q=900,K=20000)
PST={k:[int(x,16)-5 for x in "555566636545555766686678aaaa55550122135626672577267725671355012278657755433332212110211021102110"[i*32:i*32+32]]for i,k in enumerate("PNK")}
B,R=(-17,-15,15,17),(-16,-1,1,16);D=dict(N=((-33,-31,-18,-14,14,18,31,33),0),B=(B,1),R=(R,1),Q=(B+R,1),K=(B+R,0))
to_uci=lambda m:f"{chr(97+(m[0]&7))}{(m[0]>>4)+1}{chr(97+(m[1]&7))}{(m[1]>>4)+1}{m[2]}"

def parse_fen(f):
 p,b,r,i=f.split(),["."]*128,7,0
 for c in p[0]:
  if c=="/":r,i=r-1,0
  elif c.isdigit():i+=int(c)
  else:b[r*16+i],i=c,i+1
 return b,p[1],p[2],ord(p[3][0])+int(p[3][1])*16-113 if len(p)>3 and p[3]!="-"else None

in_chk=lambda b,s:(k:="kK"[s=="w"])in b and any(m[1]==b.index(k)for m in gen_m((b,"wb"[s=="w"],"",None),True))

def gen_m(st,caps=False):
 b,s,cast,ep=st;w,f=s=="w",16 if s=="w"else -16
 for sq,p in enumerate(b):
  if sq&0x88 or p=="." or p.isupper()!=w:continue
  u=p.upper()
  if u=="P":
   for d,c in((f,0),(f-1,1),(f+1,1)):
    t=sq+d
    if not t&0x88 and((not c and b[t]==".")or(c and((b[t]!="." and b[t].isupper()!=w)or t==ep))):
     for pr in("qrbn" if t>>4 in(0,7)else("",)):
      if c or pr or not caps:yield(sq,t,pr)
     if not c and not caps and sq>>4==(1 if w else 6) and b[sq+2*f]==".":yield(sq,sq+2*f,"")
  else:
   dirs,slide=D[u]
   for d in dirs:
    t=sq+d
    while not t&0x88:
     if b[t]!=".":
      if b[t].isupper()!=w:yield(sq,t,"")
      break
     if not caps:yield(sq,t,"")
     if not slide:break
     t+=d
   if u=="K" and not caps and sq in(4,116) and not in_chk(b,s):
    for tag,off,er in(("kK"[w],2,(1,2)),("qQ"[w],-2,(-1,-2,-3))):
     if tag in cast and all(b[sq+i]=="."for i in er) and not in_chk(make_m(st,(sq,sq+off//2,""))[0],s):yield(sq,sq+off,"")

def make_m(st,m):
 b,s,cast,ep=st;f,t,pr=m;nb,p,w=list(b),b[f],s=="w"
 nb[f],nb[t]=".",pr.upper()if w and pr else(pr or p)
 if p in"Pp" and t==ep:nb[t+(-16 if w else 16)]="."
 elif p in"Kk" and abs(t-f)==2:nb[f+(3 if t>f else -4)],nb[f+(1 if t>f else -1)]=".",("rR"[w])
 nc=cast.replace("K" if p=="K" else "k","").replace("Q" if p=="K" else "q","")if p in"Kk"else cast
 for sq,ch in zip((0,7,112,119),"QKqk"):
  if sq in(f,t):nc=nc.replace(ch,"")
 return nb,"wb"[w],nc,(f+t)//2 if p in"Pp" and abs(t-f)==32 else None

def evaluate(st):
 b,s,tot=st[0],st[1],0
 for sq,p in enumerate(b):
  if not sq&0x88 and p!=".":
   u,r,f,w=p.upper(),sq>>4,sq&7,p.isupper()
   v=VAL[u]+(PST[u][(r if w else 7-r)*4+min(f,7-f)]*10 if u in PST else 0)
   tot+=v if w else -v
 return tot if s=="w"else -tot

v=lambda x:VAL.get(x.upper(),0)
def order(st,ms):
 b,ep=st[0],st[3]
 return sorted(ms,key=lambda m:(v(b[m[1]])*10-v(b[m[0]])if b[m[1]]!="."else(900 if b[m[0]]in"Pp" and m[1]==ep else 0))+v(m[2]),reverse=True)

def negamax(st,d,a,b,ply,nodes,root=False):
 if nodes[0]>=MAX_N:return(None,0)if root else 0
 nodes[0]+=1;chk=in_chk(st[0],st[1])
 if d<=0 and not chk:
  pat=evaluate(st)
  if pat>=b:return b
  if a<pat:a=pat
 legal,best_m=0,None
 for m in order(st,gen_m(st,d<=0 and not chk)):
  nxt=make_m(st,m)
  if in_chk(nxt[0],st[1]):continue
  legal+=1;s=-negamax(nxt,d-1,-b,-a,ply+1,nodes)
  if nodes[0]>=MAX_N and legal>1:break
  if s>a:
   a,best_m=s,m
   if not root and a>=b:return b
 mate=-30000+ply if chk else 0
 return((None,mate)if root else mate)if not legal else((best_m,a)if root else a)

def choose_move(st,ms=None):
 nodes,best=[0],None
 for d in range(1,64):
  if nodes[0]>=MAX_N:break
  m,_=negamax(st,d,-10**6,10**6,0,nodes,root=True)
  if m and nodes[0]<MAX_N:best=m
 u=to_uci(best or next(gen_m(st)))
 return u if not ms or u in ms else ms[0]

post=lambda p,b:loads(urlopen(Request(f"{ENV}{p}",dumps(b).encode(),{"Content-Type":"application/json"})).read())

def main():
 g=post("/game",{})
 while g.get("status")!="done":g=post("/move",{"game":g.get("game",g.get("id")),"move":choose_move(parse_fen(g["fen"]),g.get("legal_moves",[]))})

if __name__=="__main__":main()
