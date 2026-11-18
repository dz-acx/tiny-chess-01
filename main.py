import json,os,urllib.request as U;E=os.environ["MAKEFUN_ENV_URL"]
def post(p,b):return json.load(U.urlopen(U.Request(E+p,json.dumps(b).encode())))
VAL=dict(P=100,N=320,B=330,R=500,Q=900,K=20000);B,R=(-17,-15,15,17),(-16,-1,1,16);N=(-33,-31,-18,-14,14,18,31,33);D=dict(N=N,B=B,R=R,Q=B+R,K=B+R)
PST_S="555555676789789b12333577468824553444466646774655556745564556788934554667567745667864454222201110";to_uci=lambda m:f"{chr(97+(m[0]&7))}{m[0]//16+1}{chr(97+(m[1]&7))}{m[1]//16+1}{m[2]}"
def parse_fen(f):
 p,b,r,i=f.split(),["."]*128,7,0
 for c in p[0]:
  if c=="/":r-=1;i=0
  elif c.isdigit():i+=int(c)
  else:b[r*16+i]=c;i+=1
 return b,p[1],p[2],ord(p[3][0])+int(p[3][1])*16-113 if len(p)>3 and p[3]!="-"else None
def attacked(b,sq,w):
 for ds,p in(((-17,-15)if w else(15,17),"P"if w else"p"),(N,"N"if w else"n"),(B+R,"K"if w else"k")):
  for d in ds:
   if not(sq+d)&0x88 and b[sq+d]==p:return True
 for dr,pcs in((B,"BQ"if w else"bq"),(R,"RQ"if w else"rq")):
  for d in dr:
   t=sq+d
   while not t&0x88:
    if(p:=b[t])!=".":
     if p in pcs:return True
     break
    t+=d
 return False
in_chk=lambda b,s:(k:="K"if s=="w"else"k")in b and attacked(b,b.index(k),s!="w")
def gen_m(st,cp=0):
 b,s,cs,e=st;w=s=="w";f=w*32-16
 for q,p in enumerate(b):
  if q&0x88 or p=="."or p.isupper()!=w:continue
  u=p.upper()
  if u=="P":
   for d,c in((f,0),(f-1,1),(f+1,1)):
    t=q+d
    if not t&0x88 and(b[t]=="."if not c else b[t]!="."and b[t].isupper()!=w or t==e):
     for r in("q",)if t>>4 in(0,7)else("",):
      if c or r or not cp:yield q,t,r
     if not(c or cp)and q>>4==(6-5*w)and b[q+2*f]==".":yield q,q+2*f,""
  else:
   for d in D[u]:
    t=q+d
    while not t&0x88:
     if(x:=b[t])!=".":
      if x.isupper()!=w:yield q,t,""
      break
     if not cp:yield q,t,""
     if u not in"BRQ":break
     t+=d
   if u=="K"and not(cp or attacked(b,q,not w)):
    for c,d in(("kK"[w],2),("qQ"[w],-2)):
     if c in cs and not attacked(b,q+d//2,not w)and b[q+d//2]==b[q+d]=="."and(d>0 or b[q-3]=="."):yield q,q+d,""
def make_m(s,m):
 b,u,c,e=s;f,t,x=m;n,p,w=list(b),b[f],u=="w";n[f],n[t]=".",x.upper()if w and x else(x or p)
 if p in"Pp"and t==e:n[t+16-w*32]="."
 elif p in"Kk"and abs(t-f)==2:n[f+(3 if t>f else -4)],n[f+(1 if t>f else -1)]=".","rR"[w]
 if p in"Kk":c=c.replace("kK"[w],"").replace("qQ"[w],"")
 for q,k in zip((0,7,112,119),"QKqk"):c=c.replace(k,"")if q in(f,t)else c
 return n,"wb"[w],c,(f+t)//2 if p in"Pp"and abs(t-f)==32 else None
I=lambda q,w:((q>>4 if w else 7-(q>>4))//2)*4+min(q&7,7-(q&7))
def evaluate(st):
 b,s=st[:2];tot,K=0,[0,0];P=lambda i:(int(PST_S[i],16)-5)*10
 for sq,p in enumerate(b):
  if sq&0x88 or p==".":continue
  u,w=p.upper(),p.isupper()
  if u=="K":K[w]=sq;continue
  v=VAL[u]+P("PNBRQK".index(u)*16+I(sq,w));tot+=v if w else-v
 return(tot+P(80+I(K[1],1))-P(80+I(K[0],0)))*((s=="w")*2-1)
def order(s,m,v=None):
 b,e=s[0],s[3]
 def c(x):
  if x==v:return 9000000
  f,t,p=x;q="p"if b[t]=="."and b[f]in"Pp"and t==e else b[t];return((10000+VAL[q.upper()]*10-VAL[b[f].upper()])if q!="."else 0)+VAL.get(p.upper(),0)
 return sorted(m,key=c,reverse=1)
M=100000
def qsearch(s,a,b,n):
 if n[0]>=M:return evaluate(s)
 n[0]+=1;p=evaluate(s)
 if p>=b:return b
 a=max(a,p)
 for m in order(s,gen_m(s,1)):
  x=make_m(s,m)
  if in_chk(x[0],s[1]):continue
  v=-qsearch(x,-b,-a,n)
  if v>=b:return b
  a=max(a,v)
 return a
def negamax(s,d,a,b,p,n,v=None):
 if n[0]>=M:return 0,None
 n[0]+=1;c=in_chk(s[0],s[1])
 if d<=0:
  if not c:return qsearch(s,a,b,n),None
  d=1
 l,k=0,None
 for m in order(s,gen_m(s,0),v):
  x=make_m(s,m)
  if in_chk(x[0],s[1]):continue
  l+=1;r=-negamax(x,d-1,-b,-a,p+1,n)[0]
  if n[0]>=M and l>1:break
  if r>a:
   a,k=r,m
   if a>=b:return b,k
 return(a,k)if l else(-30000+p if c else 0,None)
def choose(f,l):
 s=parse_fen(f);n,k=[0],None
 for d in range(1,64):
  if n[0]>=M:break
  _,m=negamax(s,d,-M,M,0,n,k)
  if m and n[0]<M:k=m
 u=to_uci(k)if k else"";return u if u in l else l[0]
while(g:=post("/game",{}))["status"]!="done":
 while g["status"]=="your_move":g=post("/move",{"game":g["game"],"move":choose(g["fen"],g["legal_moves"])})
