if __name__ == '__main__':
    # Import Psyco if available
    try:
        import psyco
        psyco.full()
	#print 'psyco enabled.'
    except ImportError:
        pass

import pygame
from pygame.locals import *
import sys

MYSURFACE = SWSURFACE

PLAYER,GUARD = 1,2	
ALL = 0xff

class tile:
	def __init__(self,agroups,fnc,value,hover,icon):
		self.agroups = agroups
		self.fnc = fnc
		self.value = value
		self.hover = hover
		self.icon = icon
	
def actor_update(g,a):
	pass
def actor_paint(g,s,a):
	pass
		
class actor:
	def __init__(self):
		self.pos = pygame.Rect(0,0,0,0)
		self._pos = pygame.Rect(0,0,0,0)
		self.update = actor_update
		self.groups = 0
		self.paint1 = actor_paint
		self.paint2 = actor_paint
		self.paint3 = actor_paint
		self.alay = 0


def player_new(g,t,v):
	#print 'new player'
	a = actor()
	a.paint1 = light_paint1
	a.paint2 = light_paint2
	a.paint3 = light_paint3
	a.update = player_update
	a.light = 1
	a.light_toggle = 1
	a.light_len = 8
	a.color = (255,255,128)
	a.lcolor = (255,255,255,128)
	a.pos = pygame.Rect(t.tx*g.tw,t.ty*g.th,g.tw,g.th)
	a._pos = a.pos #HACK
	c = g.clayer[t.ty][t.tx+1]&0xf
	cmap = [pi*2/2,pi*0/2,pi*3/2,pi*1/2]
	a.a = cmap[c]
	a.la = a.a
	a.groups = PLAYER
	a.name = 'player'
	a.battery = 100
	a.danger = 0
	a.panic = 100
	a.dead = 0
	g.actors.append(a)
	g.player = a
	
	
from math import *
from random import *
#dark = pygame.image.load("dark.png").convert_alpha()

def myint(v):
	v = int(v*10)
	mod = v%10
	if mod != 0 and game.frame*mod%10<mod: v += 10
	return int(v/10)

def player_update(g,a):
	keys = pygame.key.get_pressed()
	
	if keys[K_LEFT]: a.a += (2*pi)/24
	if keys[K_RIGHT]: a.a -= (2*pi)/24
	
	
	
	v = 0
	mv = 4.0 * 0.80
	if keys[K_UP]: v += mv
	if keys[K_DOWN]: v -= mv
	ang = a.a
	dx,dy = sin(ang),cos(ang)
	a.pos.x += myint(dx*v)
	a.pos.y += myint(dy*v)
	
	a.la = a.a
	
	"""
	g.origin.x = min(g.origin.x,max(0,a.pos.x-100))
	g.origin.x = max(g.origin.x,min(g.w*g.tw-320,a.pos.x+100-320))
	
	g.origin.y = min(g.origin.y,max(0,a.pos.y-60))
	g.origin.y = max(g.origin.y,min(g.h*g.th-240,a.pos.y+60-240))
	"""
	
	
	g.origin.left = min(g.origin.left,a.pos.x-144)
	g.origin.right = max(g.origin.right,a.pos.x+144)
	
	g.origin.top = min(g.origin.top,a.pos.y-88)
	g.origin.bottom = max(g.origin.bottom,a.pos.y+88)
	
	#diminish battery
	if g.frame%3 == 0 and a.light_toggle == 1: a.battery -= 1
	a.battery = max(0,min(100,a.battery))

	#a.battery = 50
	
	#switch on/off light if needed
	a.light = a.light_toggle
	if a.battery == 0: a.light = 0
		
	#calculate danger level
	p1 = a.pos.x/g.tw,a.pos.y/g.th
	d = 0 #gets best max
	for e in g.guards:
		p2 = e.pos.x/g.tw,e.pos.y/g.th
		dt = adist(p1,p2)
		if e.target == a:
			l = dt*2+len(e.path) - 13
			d = max(d,max(0,100-l*2)) #25 is far, 50 is really far
		else: 
			l = dt*4 - 13 #NOTE: no apath, optimization
			d += max(d,max(0,100-l*2)) # 25 is pretty far
	a.danger = d
	a.danger = max(0,min(100,a.danger))
	
	#calculate panic level
	
	"""
	if a.light == 0:
		a.panic += 1
	elif g.frame%2 == 0:
		a.panic -= 1
	"""
	if g.frame%20 == 0: a.panic -= 1
	a.panic = max(0,min(100,a.panic))
	
	if a.panic == 0:
		g.dead = 1
		g.death = state_death_panic
	#a.panic = 50
	
		
	
def light_paint1(g,screen,a):
	#print 'painting player'

	lmax = g.tw*a.light_len
	lmax1 = lmax + g.tw*1
	lmax2 = lmax + g.tw*2
		
	#a.a += (2*pi)/30.0
	if a.light:
		w = (2*pi)/4.0
		
		ledge = 3
		
		rays = a.light_len*4 #36#72 #36 #NOTE: shaved down to about 1/4 for speed
		
		tw,th = g.tw,g.th
		
		o = a.pos.x,a.pos.y
		points = [o]
		for n in range(0,rays):
			ang = a.la + (n-rays/2)*w/rays
			d = sin(ang),cos(ang)
			
			#test along y			
			if d[1] != 0:
				llen = 0
				x,y = o
				if d[1] < 0:
					dy,y = -g.th,int(y/g.th)*g.th-1-ledge
				else: 
					dy,y = g.th,int(y/g.th)*g.th+g.th+ledge
				dx = d[0]*dy/d[1]
				ladd = hypot(dx,dy)
				x = x + (y-o[1])*d[0]/d[1]
				while llen < lmax2:
					tx,ty = int(x/tw),int(y/th)
					if tx < 0 or ty < 0 or tx >= g.w or ty >= g.h: break;
					#g.alayer[ty][tx] = 1
					n = g.qlayer[ty][tx]
					if n == 1: break;
					x,y = x+dx,y+dy
					llen += ladd
				p1 = x,y	

			#test along x			
			if d[0] != 0:
				llen = 0
				x,y = o
				if d[0] < 0:
					dx,x = -g.tw,int(x/g.tw)*g.tw-1-ledge
				else: 
					dx,x = g.tw,int(x/g.tw)*g.tw+g.tw+ledge
				dy = d[1]*dx/d[0]
				ladd = hypot(dx,dy)
				y = y + (x-o[0])*d[1]/d[0]
				while llen < lmax2:
					tx,ty = int(x/tw),int(y/th)
					if tx < 0 or ty < 0 or tx >= g.w or ty >= g.h: break;
					#g.alayer[ty][tx] = 1
					n = g.qlayer[ty][tx]
					if n == 1: break;
					x,y = x+dx,y+dy
					llen += ladd
				p2 = x,y

			if d[0] != 0 and d[1] != 0:
				if adist(o,p1) < adist(o,p2): p = p1
				else: p = p2
			elif d[0] != 0: p = p2
			else: p = p1
			
			
			lp = hypot(o[0]-p[0],o[1]-p[1])
			if lp > lmax:
				p = o[0] + d[0]*lmax,o[1] + d[1]*lmax
			lp = min(lp,lmax)
				
			points.append(p)

			#draw lighting on tiles	
			x,y = o
			ladd = 12
			dx,dy = d[0]*ladd,d[1]*ladd
			llen = 0
			while llen < lp:
				tx,ty = int(x/tw),int(y/th)
				g.alayer[ty][tx] = 1
				x,y,llen = x+dx,y+dy,llen+ladd
			
		a.points = points

		
def light_paint2(g,screen,a):
	if a.light:
		ps = []
		for p in a.points: ps.append((p[0]-g.origin.x,p[1]-g.origin.y))

		pygame.draw.polygon(screen,a.lcolor,ps,0)
		
		"""
		method here works pretty well... with an alpha overlay
		
		c = (255,255,255,24)	
		pygame.draw.polygon(screen,c,ps,72)
		for p in ps:
			pygame.draw.circle(screen,c,p,36)
		
		
		c = (255,255,255,48)	
		pygame.draw.polygon(screen,c,ps,36)
		for p in ps:
			pygame.draw.circle(screen,c,p,18)
			
		
		c = (255,255,255,128)	
		pygame.draw.polygon(screen,c,ps,0)
		"""
			


	
		
p_trans = {}
		
def light_paint3(g,screen,a):
	name = a.name
	n = (g.frame/6)%2
	tx,ty = a.pos.x/g.tw,a.pos.y/g.th
	if a.light == 0 and a.alay != 1: n += 2
	
	ang = a.la
	if ang < 0: ang += (2*pi)
	ang = int(ang * 360 / (2*pi) + 7) / 15 * 15 
	ang = (ang+180) % 360
	
	iname = '%s.%d.%d'%(name,n,ang)
	
	if iname not in p_trans:
		p_trans[iname] = pygame.transform.rotate(images['%s.%d'%(name,n)],ang)
		
	img = p_trans[iname]
	
	screen.blit(img,(a.pos.x-img.get_width()/2-g.origin.x,a.pos.y-img.get_height()/2-g.origin.y))
	
	
	
	
	"""
	pygame.draw.circle(screen,a.color,(a.pos.x-g.origin.x,a.pos.y-g.origin.y),8)
	
	
	ang = a.la
	i = 4
	dx,dy = int(i*sin(ang)),int(i*cos(ang))
	pygame.draw.circle(screen,(255,255,255),
		(a.pos.x-g.origin.x+dx,a.pos.y-g.origin.y+dy),4)
	"""
	
	"""
	if hasattr(a,'path'):
		for p in a.path:
			pygame.draw.circle(screen,(0,255,0),(p[0]*g.tw+g.tw/2-g.origin.x,p[1]*g.th+g.th/2-g.origin.y),4)
	"""
	
def spos_new(g,t,v): #guard stations
	g.spos.append((t.tx,t.ty))

def guard_new(g,t,v):
	#print 'new guard'
	a = actor()
	a.paint1 = light_paint1
	a.paint2 = light_paint2
	a.paint3 = light_paint3
	a.update = guard_update
	a.glow = 1
	a.light = 1
	a.light_len = 6
	a.color = (255,128,128)
	a.lcolor = (255,255,255)
	a.pos = pygame.Rect(t.tx*g.tw,t.ty*g.th,g.tw,g.th)
	a.ipos = (t.tx,t.ty)
	a._pos = a.pos #HACK
	a.a = 0
	a.la = 0
	a.groups = GUARD
	a.name = 'guard'
	a.target = None
	g.actors.append(a)
	g.guards.append(a)
	
	
def light_paint4(g,s,a):
	g.alayer[a.ty][a.tx] = 1
	g.alayer[a.ty+1][a.tx] = 1
	g.alayer[a.ty-1][a.tx] = 1
	g.alayer[a.ty][a.tx+1] = 1
	g.alayer[a.ty][a.tx-1] = 1
	
def light_new(g,t,v):
	a = actor()
	a.tx,a.ty = t.tx,t.ty
	a.paint1 = light_paint4
	g.actors.append(a)
	
def adist(a,b):
	return abs(a[0]-b[0])+abs(a[1]-b[1]) #best algorithm
	#return max(abs(a[0]-b[0]),abs(a[1]-b[1]))
	#dx = abs(a[0]-b[0])
	#dy = abs(a[1]-b[1])
	#return ( (dx+dy) + max(dx,dy) ) / 2

	
class anode:
	def __init__(self,prev,p,dest):
		self.prev = prev
		self.p = p
		if self.prev == None: self.g = 0
		else: self.g = self.prev.g+1
			
		self.h = adist(self.p,dest)
		self.f = self.g+self.h
		
		
	
def apath(a,b):
	dirs = [ (-1,0),(1,0),(0,-1),(0,1) ] 
	#dirs = [ (-1,0),(1,0),(0,-1),(0,1), (-1,-1),(1,1),(1,-1),(-1,1)] 

	ons = []
	on = {}
	cn = {}
	
	cur = anode(None,a,b)
	
	on[cur.p] = cur
	ons.append(cur)
	
	while len(on):
		cur = ons.pop(0)
		if cur.p not in on: continue #HACK: not sure if this is correct, should have deleted it from the ons at **here**
		del on[cur.p]
		cn[cur.p] = cur
		if cur.p == b: break 
		
		for d in dirs:
			p = cur.p[0]+d[0],cur.p[1]+d[1]
			n = game.qlayer[p[1]][p[0]]
			if n != 0: continue
			
			node = anode(cur,p,b)
			ok = 1
			if p in on and node.f >= on[p].f: continue
			if p in cn and node.f >= cn[p].f: continue
			if p in on: del on[p] #HACK, **here**
			if p in cn: del cn[p]
			on[p] = node
			
			lo = 0
			hi = len(ons)
			while lo < hi:
				mid = (lo+hi)/2
				if node.f < ons[mid].f: hi = mid
				else: lo = mid + 1
			ons.insert(lo,node)
			
	#dx,dy = a[0]-b[0],a[1]-b[1]
	#print 'path:',abs(dx),abs(dy),cur.g
			
	path = []
	while cur.prev != None:
		path.append(cur.p)
		cur = cur.prev
	path.reverse()
	return path
	
			
def guard_update(g,a):
	p1 = (a.pos.x/g.tw,a.pos.y/g.th)
	if g.player.light: 
		a.target = g.player
		p2 = (g.player.pos.x/g.tw,g.player.pos.y/g.th)
	else:
		if a.target == g.player:
			if len(a.path) > 12: a.target = a.path.pop(12)
			else: a.target = p1
		p2 = a.target
		if len(a.path) == 0: p2 = p1
		if p1 == p2 and len(g.spos)!=0:
			a.target = choice(g.spos)
			a.path = None
		elif p1 == p2:
			a.target = a.ipos
			a.path = None
		p2 = a.target

		#print p1,p2
	
	if not hasattr(a,'path') or a.path == None or g.frame%8 == 0: #NOTE/HACK: optimization
		a.path = apath(p1,p2)[1:]
	#print len(a.path)
	
	path = a.path
	d = a.pos.x/g.tw,a.pos.y/g.th
	#if len(path) > 1: d = path[1]
	#elif len(path) > 0: d = path[0]
	if len(path): d = path[0]
	x,y = d[0]*g.tw+g.tw/2,d[1]*g.th+g.th/2

	dx,dy = x-a.pos.x,y-a.pos.y
	
	a.a = atan2(dx,dy)
				
	av = (2*pi)/15
	ang = a.la
	dang = a.a
	
	if abs(dang-ang) > pi:
		if ang < dang: ang += (2*pi)
		else: dang += (2*pi)
	if ang < dang: ang += av
	if ang > dang: ang -= av
	a.la = ang
	
	#print ang,dang
	v = 3.0*0.80
	ang = a.a
	dx,dy = sin(ang),cos(ang)
	a.pos.x += myint(dx*v)
	a.pos.y += myint(dy*v)

	p = game.player
	dx,dy = p.pos.x-a.pos.x,p.pos.y-a.pos.y
	ang = a.la
	dang = atan2(dx,dy)
	dist = hypot(dx,dy)
	if abs(dang-ang) > pi:
		if ang < dang: ang += (2*pi)
		else: dang += (2*pi)
	
	#print g.frame
	#if abs(dang-ang) < ((2*pi)/8.0): print 'in cone'
	#if dist < 16*8: print 'close enough'	
	
	kill = 1
	
	if dist > a.light_len*g.tw: kill = 0
	
	if abs(dang-ang) > ((2*pi)/8.0): kill = 0
	 
	dx,dy = sin(dang),cos(dang)
	x,y,l = a.pos.x,a.pos.y,0
	i = g.tw/2
	while l < dist:
		tx,ty = int(x/g.tw),int(y/g.th)
		n = g.qlayer[ty][tx]
		if n == 1: 
			kill = 0
			break
		x,y,l = x+dx*i,y+dy*i,l+i
			
	if kill:
		#print g.frame,'we got him!'
		g.dead = 1
		g.death = state_death_guard
			
		
		
		
	
def tile_corner(g,t,a):
	return tile_wall(g,t,a)
	
def tile_wall(g,t,a):
	#print 'hit wall'
	#a.pos = pygame.Rect(a._pos)
	tx,ty = t.tx,t.ty
	
	px,py = a._pos.x/g.tw,a._pos.y/g.th
	cx,cy = a.pos.x/g.tw,a.pos.y/g.th
	#dx,dy = abs(a.pos.x-a._pos.x),abs(a.pos.y-a._pos.y)
	
	if cx != px and cx == tx:
		a.pos.x = a._pos.x
	if cy != py and cy == ty:
		a.pos.y = a._pos.y
	
def tile_pit(g,t,a):
	g.dead = 1
	g.death = state_death_pit
	
def tile_light(g,t,a):
	a.battery = min(100,a.battery+25)
	game.score += 25
	g.tlayer[t.ty][t.tx] = 0
	sfx['battery'].play()
	
def tile_exit(g,t,a):
	g.win = 1
	
class code:
	def __init__(self,fnc,value):
		self.fnc = fnc
		self.value = value
	

class _game:
	def __init__(self):
		self.tw,self.th = 12,12
		self.origin = pygame.Rect(0,0,0,0)
		self.bounds = pygame.Rect(0,0,0,0)
		
		
		self.actors = []
		self.codes = [
			code(None,None),
			code(player_new,None),
			code(guard_new,None),
			code(spos_new,None),
			
			code(light_new,None),
			code(None,None),
			code(None,None),
			code(None,None),
			
			code(None,None),code(None,None),code(None,None),code(None,None),
			code(None,None),code(None,None),code(None,None),code(None,None),
			
			code(None,None),code(None,None),code(None,None),code(None,None),
			code(None,None),code(None,None),code(None,None),code(None,None),
			code(None,None),code(None,None),code(None,None),code(None,None),
			code(None,None),code(None,None),code(None,None),code(None,None),
			]
		
		BKGR = (0,None,None,0,0)
		HOVER = (0,None,None,1,0)
		WALL = (ALL,tile_wall,None,1,0)
		CORNER = (ALL,tile_corner,None,1,0)
		PIT = (PLAYER,tile_pit,None,1,0)
		LIGHT = (PLAYER,tile_light,None,1,1)
		EXIT = (PLAYER,tile_exit,None,1,1)

		_tiles = [
			#0
			BKGR,WALL,PIT,LIGHT,
			EXIT,EXIT,EXIT,EXIT,
			
			BKGR,BKGR,BKGR,BKGR,
			BKGR,BKGR,BKGR,BKGR,
			
			#1
			CORNER,WALL,CORNER,WALL,
			WALL,WALL,WALL,WALL,
			PIT,PIT,PIT,PIT,
			PIT,PIT,PIT,PIT,
			
			#2
			WALL,WALL,WALL,WALL,
			WALL,WALL,WALL,WALL,
			PIT,PIT,PIT,PIT,
			PIT,PIT,PIT,PIT,
			
			#3
			CORNER,WALL,CORNER,WALL,
			WALL,WALL,WALL,WALL,
			PIT,PIT,PIT,PIT,
			PIT,PIT,PIT,PIT,
			
			
			]
		self.tiles = []
		img = pygame.image.load("tiles.tga").convert_alpha(screen)
		blk = pygame.Surface((self.tw,self.th),MYSURFACE,screen)
		blk.fill((0,0,0))
		alpha = [0,60,120,255]
		n = 0
		for y in range(0,img.get_height()/4,self.th): #HACK: /4, not all are used
			for x in range(0,img.get_width(),self.tw):
				#print n
				if len(_tiles) >= n+1: agroups,fnc,value,hover,icon = _tiles[n]
				else: agroups,fnc,value,hover,icon = 0,None,None,0,0
				t = tile(agroups,fnc,value,hover,icon)
				t.image = img.subsurface((x,y,self.tw,self.th))
				t.images = []
				ck = (255,0,255)
				for i in range(0,4):
					fimg = pygame.Surface((self.tw,self.th),MYSURFACE,screen)
					fimg.set_colorkey(ck)
					fimg.blit(t.image,(0,0))
					blk.set_alpha(alpha[i])
					fimg.blit(blk,(0,0))
					ac = 0
					for yy in xrange(0,self.th):
						for xx in xrange(0,self.tw):
							if t.image.get_at((xx,yy))==(0,0,0,0):
								fimg.set_at((xx,yy),ck)
								ac += 1
					#if ac == 0: fimg = fimg.convert()
					fimg.set_alpha(None,RLEACCEL)
					t.images.append(fimg)
				self.tiles.append(t)
				n += 1
		
	
	def load(self,fname):
		img = pygame.image.load(fname)
		self.w,self.h = img.get_width(),img.get_height()
		self.bounds = pygame.Rect(self.tw*2,self.th*2,(self.w-4)*self.tw,(self.h-4)*self.th)
		self.origin.x,self.origin.y = self.bounds.x,self.bounds.y
		self.frame = 0
		self.guards = []
		self.actors = []
		self.spos = [] #guard positions to walk to..
		
		self.dead = 0
		self.win = 0
		
		self.tlayer = [[0 for x in range(0,self.w)] for y in range(0,self.h)]
		self.clayer = [[0 for x in range(0,self.w)] for y in range(0,self.h)]
		self.alayer = [[0 for x in range(0,self.w)] for y in range(0,self.h)]
		self.qlayer = [[0 for x in range(0,self.w)] for y in range(0,self.h)]

		for y in range(0,self.h):
			for x in range(0,self.w):
				r,g,b,a = img.get_at((x,y))
				self.tlayer[y][x] = r
				self.clayer[y][x] = b
				self.alayer[y][x] = 0

		self.pretty() #prettifiying changes some block values..
		
		for y in range(0,self.h):
			for x in range(0,self.w):
				t = self.tiles[self.tlayer[y][x]]
				q = 0
				if t.fnc == tile_wall: q = 1
				if t.fnc == tile_pit: q = 2
				if t.fnc == tile_corner: q = 3
				self.qlayer[y][x] = q
				
		for y in range(0,self.h):
			for x in range(0,self.w):
				n = self.clayer[y][x]
				c = self.codes[n]
				if c.fnc != None:
					c.tx,c.ty = x,y
					c.fnc(self,c,c.value)
					
		
	def pretty(self):
	
		dirs = [(-1,0),(1,0),(0,-1),(0,1)]
		flips = [(-1,1),(1,1),(1,-1),(-1,-1)]
		
		
		
		
		for v,a in ((1,0),(2,8)):
			l = self.tlayer
			nlayer = [l[y][:] for y in range(0,self.h)]

			for y in range(1,self.h-1):
				for x in range(1,self.w-1):
					n = l[y][x]
					
					#solo
					if n == v and l[y-1][x] != v and l[y+1][x] != v and l[y][x-1] != v and l[y][x+1] != v:
						n = choice([0x33,0x34]) + a
						nlayer[y][x] = n
						continue
						
					#air corner
					if n == 0:
						for f in flips:
							up,down,left,right = -1*f[0],1*f[0],-1*f[1],1*f[1]
							if l[y+up][x] != v and l[y][x+left] != v and l[y][x+right] == v and l[y+down][x] == v:
								n = 0x21 + left + up*16 + a
								nlayer[y][x] = n
								break
					
					#hard corner
					if n == v:
						for f in flips:
							up,down,left,right = -1*f[0],1*f[0],-1*f[1],1*f[1]
							if l[y+up][x] != v and l[y][x+left] != v and (l[y][x+right] == v or l[y+down][x] == v) and l[y+down][x+left] != v and l[y+up][x+right] != v:
								n = 0x15 + (left!=-1) + (up!=-1)*16 + a
								nlayer[y][x] = n
								break
	
					#v-side 
					if n == v:
						for f in flips:
							up,down,left,right = -1*f[0],1*f[0],-1*f[1],1*f[1]
							if l[y+up][x] != v and l[y+down][x] == v and l[y+up][x+left] != v and l[y+up][x+right] != v:
								n = 0x21 + up*16 + a
								nlayer[y][x] = n
								break
								
					#h-side
					if n == v:
						for f in flips:
							up,down,left,right = -1*f[0],1*f[0],-1*f[1],1*f[1]
							if l[y][x+left] != v and l[y][x+right] == v and l[y+up][x+left] != v and l[y+down][x+left] != v:
								n = 0x21 + left + a
								nlayer[y][x] = n
								break
	
												
					#inner corner
					if n == v:
						for f in flips:
							up,down,left,right = -1*f[0],1*f[0],-1*f[1],1*f[1]
							if l[y+up][x+left] != v  and (l[y][x+left] != v or l[y+up][x] != v):
								n = 0x13 + (left!=-1) + (up!=-1)*16 + a
								nlayer[y][x] = n
								break
								#and l[y+down][x+right] == v
					
					#inner
					if n == v: 
						n = 0x21 + a
					
					nlayer[y][x] = n
					
			self.tlayer = nlayer
				
				
				
				
				
		
		

	
	def paint(self,screen):
		sblit = screen.blit
		sfill = screen.fill
		
		tw,th = self.tw,self.th
		
		sw,sh = screen.get_width(),screen.get_height()
			
		self.origin.w,self.origin.h= sw,sh
		self.origin.clamp_ip(self.bounds)

		sw,sh = screen.get_width()+tw-1,screen.get_height()+th-1
				
		ox,oy = self.origin.x,self.origin.y
		ix,iy = ox/tw*tw,oy/th*th
		tlayer = self.tlayer
		tiles = self.tiles
		alayer = self.alayer
		
		for a in self.actors:
			a.paint1(self,screen,a)
		
		nlayer = [ alayer[ty][:] for ty in range(0,self.h) ]
		for ty in range(iy/th,(iy+sh)/th):
			for tx in range(ix/tw,(ix+sw)/tw):
				a = alayer[ty][tx]
				if a == 0 and (alayer[ty-1][tx] != 0 and alayer[ty+1][tx] != 0) or (alayer[ty][tx-1] != 0 and alayer[ty][tx+1] != 0):
					nlayer[ty][tx] = 1
		alayer = self.alayer = nlayer
			
		nlayer = [ alayer[ty][:] for ty in range(0,self.h) ]
		for ty in range(iy/th,(iy+sh)/th):
			for tx in range(ix/tw,(ix+sw)/tw):
				a = alayer[ty][tx]
				if a == 0 and (alayer[ty-1][tx] != 0 or alayer[ty+1][tx] != 0 or alayer[ty][tx-1] != 0 or alayer[ty][tx+1] != 0):
					nlayer[ty][tx] = 2
		alayer = self.alayer = nlayer
		
		nlayer = [ alayer[ty][:] for ty in range(0,self.h) ]
		for ty in range(iy/th,(iy+sh)/th):
			for tx in range(ix/tw,(ix+sw)/tw):
				a = alayer[ty][tx]
				if not a and (alayer[ty-1][tx] != 0 or alayer[ty+1][tx] != 0 or alayer[ty][tx-1] != 0 or alayer[ty][tx+1] != 0):
					nlayer[ty][tx] = 3
		alayer = self.alayer = nlayer
		
		for a in self.actors:
			tx,ty = a.pos.x/tw,a.pos.y/th
			a.alay = alayer[ty][tx]
		
		bkgr = tiles[0]	
		
		for y in range(iy,iy+sh,th):
			ty = y/th
			trow = tlayer[ty]
			arow = alayer[ty]
			for x in range(ix,ix+sw,tw):
				tx = x/tw
				n = trow[tx]
				a = arow[tx]
				t = tiles[n]
				if a and not t.hover:
					sblit(t.images[a-1],(x-ox,y-oy))
					arow[tx] = 0
				elif a and t.hover:
					sblit(bkgr.images[a-1],(x-ox,y-oy))
				else: sfill((0,0,0),(x-ox,y-oy,tw,th))

		if not hasattr(self,'overlay'):
			self.overlay = pygame.Surface((screen.get_width(),screen.get_height()),MYSURFACE,screen)
			self.overlay.set_alpha(128)
			self.overlay.set_colorkey((0,0,0))

		self.overlay.fill((0,0,0))
		for a in self.actors:
			a.paint2(self,self.overlay,a)
		screen.blit(self.overlay,(0,0))

		for y in range(iy,iy+sh,th):
			ty = y/th
			trow = tlayer[ty]
			arow = alayer[ty]
			for x in range(ix,ix+sw,tw):
				tx = x/tw
				n = trow[tx]
				a = arow[tx]
				t = tiles[n]
				if a or t.icon:
					if t.icon: a = 1
					sblit(t.images[a-1],(x-ox,y-oy))
					arow[tx] = 0
		
		for a in self.actors:
			a.paint3(self,screen,a)

		#reset the alayer for good measure		
		self.alayer = [[0 for x in xrange(0,self.w)] for y in xrange(0,self.h)]
			
		#p = game.player
		#screen.blit(dark,(p.pos.x-110,p.pos.y-110))

		
	def paint_frills(self,screen):		
		screen.fill((0,0,0),(0,208,320,32))
		
		p = game.player
		
		t = 2
		
		c = (0,0,255)
		if p.battery < 20 and self.frame/t%2: c = (255,255,255)
		screen.fill(c,(60,210,p.battery*200/100,8))
		myprint(screen,fntg,(0,208),(255,255,255),"battery")
		
		c = (255,0,0)
		if p.danger > 80 and self.frame/t%2: c = (255,255,255)
		screen.fill(c,(60,220,p.danger*200/100,8))
		myprint(screen,fntg,(0,218),(255,255,255),"danger")
		
		c = (255,255,0)
		if p.panic < 20 and self.frame/t%2: c = (255,255,255)
		screen.fill(c,(60,230,p.panic*200/100,8))
		myprint(screen,fntg,(0,228),(255,255,255),"time")
		
		myprint(screen,fntg,(262,208),(255,255,255),"score:")
		myprint(screen,fntg,(262,218),(255,255,255),"%04d"%game.score)
		
		myprint(screen,fntg,(262,228),(255,255,255),"level:%d"%(game.level+1))
		
		
	def tilehits(self,a):
		tw,th= self.tw,self.th
		dx,dy = a.pos.x-a._pos.x,a.pos.y-a._pos.y
		
		a.pos.x,a.pos.y = a._pos.x,a._pos.y
		a.pos.x += dx
		tx,ty = a.pos.x/tw,a.pos.y/th
		n = self.tlayer[ty][tx]
		t = self.tiles[n]
		t.tx,t.ty = tx,ty
		if t.agroups & a.groups:
			t.fnc(self,t,a)
		x = a.pos.x
			
		a.pos.x,a.pos.y = a._pos.x,a._pos.y
		a.pos.y += dy
		tx,ty = a.pos.x/tw,a.pos.y/th
		n = self.tlayer[ty][tx]
		t = self.tiles[n]
		t.tx,t.ty = tx,ty
		if t.agroups & a.groups:
			t.fnc(self,t,a)
		y = a.pos.y
		
		a.pos.x,a.pos.y = x,y

	def tick_init(self):		
		self.wait = 33
		self.nt = pygame.time.get_ticks()
		
	def tick_delay(self):
		self.ct = pygame.time.get_ticks()
		if self.ct < self.nt:
			pygame.time.wait(self.nt-self.ct)
			self.nt+=self.wait
		else: 
			#print self.frame,'ack!'
			self.nt = pygame.time.get_ticks()+self.wait
		

			
	
def run(fnc,value):
	while fnc != None:
		fnc,value = fnc(value)
		
def state_quit(value):
	return None,None
	
	
def loop():
	#print game.frame
	for a in game.actors: 
		a.update(game,a)
		game.tilehits(a)
		a._pos = pygame.Rect(a.pos)
	
	game.paint(screen.subsurface((0,0,320,13*16)))
	#game.paint(screen.subsurface((0,0,640,13*16*2)))
	game.paint_frills(screen)
	game.frame += 1
	
	

def state_restart(value):

	game.score = 0
	return state_play,None
	
def state_death_pit(value):
	sfx['pit'].play()

	s = screen.subsurface((0,0,320,13*16))
	sw,sh = s.get_width(),s.get_height()
	c = (255,0,0)
	
	for i in range(0,45):
		img = pygame.transform.rotozoom(s,15,0.92)
		s.fill((0,0,0))
		s.blit(img,((sw-img.get_width())/2,(sh-img.get_height())/2))
		pygame.display.flip()
		game.tick_delay()
	return state_again,None

		
def state_death_panic(value):
	sfx['pause'].play()
	
	s = screen.subsurface((0,0,320,13*16))
	sw,sh = s.get_width(),s.get_height()
	
	img = pygame.Surface((sw,sh),MYSURFACE,s)
	img.fill((0,0,0))
	img.blit(s,(0,0))
	
	for i in range(0,15):
		w = sw/((i+1)**2)
		w = max(w,1)
		h = sh * w / sw
		h = max(h,1)
		
		img2 = pygame.transform.scale(img,(w,h))
		img2 = pygame.transform.scale(img2,(sw,sh))
		s.blit(img2,(0,0))
		
		pygame.display.flip()
		game.tick_delay()
	s.fill((0,0,0))
	pygame.display.flip()
		
	return state_again,None

def state_death_guard(value):
	sfx['guard'].play()

	s = screen.subsurface((0,0,320,13*16))
	sw,sh = s.get_width(),s.get_height()
	c = (255,0,0)
	
	"""
	w = game.tw
	
	gore = []
	for i in range(0,40):
		if i < 10:
			x,y,r = randrange(w,sw-w),randrange(w,(sh-w*2)),randrange(10,14)
			gore.append((x,y,r-5))
			pygame.draw.circle(s,c,(x,y),r)
			for n in range(0,r):
				xx,yy,rr = x+randrange(-20,20),y+randrange(-20,20),randrange(1,4)
				pygame.draw.circle(s,c,(xx,yy),rr)
				
		for n in range(0,len(gore)):
			x,y,r = gore[n]
			dy = randrange(2,5)
			if randrange(0,5) == 0: r -= 1
			if r>0: 
				while dy: 
					pygame.draw.circle(s,c,(x,y),max(2,r))
					y, dy = y+1, dy-1
			gore[n] = x,y,r
		
		pygame.display.flip()
		game.tick_delay()
	"""

	hole = pygame.image.load("hole.tga")
	w = 24
	holes = []
	for i in range(0,10):
		d = 0
		while d < w*2:
			x = randrange(w,sw-w*2)
			y = randrange(w,sh-w*2)
			d = w*2
			for (xx,yy) in holes: d = min(d,hypot(xx-x,yy-y))
		s.blit(pygame.transform.rotate(hole,randrange(0,360)),(x,y))
		holes.append((x,y))
		pygame.display.flip()
		game.tick_delay()
		
	for i in range(0,30):
		#pygame.display.flip()
		game.tick_delay()

			
	return state_again,None
		
def state_again(value):
	mycprint(screen,fntm,(255,255,255),"Try Again? y/n")
	pygame.display.flip()
	v = getch()
	if v == K_y: 
		return state_restart,None
	return state_title,None
			

	
def state_play(value):
	if game.sound == 1 and game.music != 'play':
		game.music = 'play'
		pygame.mixer.music.load("play.ogg")
		pygame.mixer.music.play(-1)

	if len(sys.argv) > 1:
		game.load(sys.argv[1])
	else: 
		game.load(levels[game.level])
	

	game.tick_init()
	
	loop()
	loop()
	
	mycprint(screen,fntm,(255,255,255),"Get Ready!")
	pygame.display.flip()
	sfx['getready'].play()
	getch()
	
	while 1:
		pause = 0
		quit = 0
		for e in pygame.event.get():
			if e.type is KEYDOWN and e.key == K_f:
				pygame.display.toggle_fullscreen()
			if e.type is KEYDOWN and e.key in (K_q,K_ESCAPE):
				quit = 1
			if e.type is KEYDOWN and e.key in (K_SPACE,K_RETURN,K_p):
				pause = 1
			if e.type is KEYDOWN and e.key in (K_LCTRL,K_RCTRL,K_LALT,K_RALT,K_LSHIFT,K_RSHIFT):
				game.player.light_toggle ^= 1
				#print 'light click'
				if game.player.light_toggle: sfx['light_on'].play()
				else: sfx['light_off'].play()
		
		if pause:
			mycprint(screen,fntm,(255,255,255),"Pause")
			pygame.display.flip()
			sfx['pause'].play()
			getch()
			
		if quit:
			mycprint(screen,fntm,(255,255,255),"Quit? y/n")
			pygame.display.flip()
			sfx['pause'].play()
			v = getch()
			if v == K_y:
				return state_title,None
			
				
		#if not game.pause: loop()
		loop()
		pygame.display.flip()
		
		if game.score > game.high: game.high = game.score #keep track of high scores, auto
		
		game.tick_delay()
		
		if game.dead: 
			return game.death,None
			
		if game.win: 
			bonus = game.player.battery+game.player.panic
			game.score += bonus
			if game.score > game.high: game.high = game.score #keep track of high scores, auto
			
			mycprint(screen,fntm,(255,255,255),"Bonus: %04d"%bonus)
			pygame.display.flip()
			sfx['win'].play()
			getch()
			
			game.level += 1
			if game.level == len(levels):
				game.level = 0
				return state_win,None
			return state_play,None
			
		
		
	return state_quit,None

def state_win(value):
	bkgr = pygame.image.load("win.jpg")
	
	screen.blit(bkgr,(0,0))
	x,y = 16,16
	
	c1 = (255,255,255)
	c2 = (255,255,255)
	
	myprint(screen,fntm,(x,y),c1,"you're free")
	y += 40
	
	help = [
		"you've",
		"escaped",
		"the anathema",
		"mines!",
		"",
		"good job.",
		"",
		"take a nap.",
		"buy a candy bar.",
		"",
		"rent a goat.",
		]
		
	for txt in help:
		myprint(screen,fnts,(x,y),c2,txt)
		y += 16
		
	pygame.display.flip()
	
	getch()
	
	return state_title,None

def state_help(value):
	bkgr = pygame.image.load("bkgr.png")
	
	screen.blit(bkgr,(0,0))
	x,y = 16,16
	
	c1 = (255,255,255)
	c2 = (255,255,255)
	
	myprint(screen,fntm,(x,y),c1,"help")
	y += 40
	
	help = [
		"you've been a slave for too long,",
		"escape the anathema mines!",
		"",
		"left, right - change direction",
		"up, down - run forward / backward",
		"ctrl - turn on/off flashlight",
		"",
		"pick up batteries for more power",
		"turn off flashlight to ",
		" - hide from guards",
		" - conserve battery power",
		]
		
	for txt in help:
		myprint(screen,fnts,(x,y),c2,txt)
		y += 16
		
	pygame.display.flip()
	
	getch()
	
	return value
	
def getch():
	while 1:
		for e in pygame.event.get():
			if e.type is KEYDOWN and e.key in (K_SPACE,K_RETURN,K_ESCAPE,K_y,K_n): return e.key
		pygame.time.wait(100)
		#pygame.display.flip()
	

def myprint(s,fnt,pos,c,txt):
	i = fnt.render(txt,1,(0,0,0))
	si = 2
	if fnt == fnts: si = 1
	s.blit(i,(pos[0]+si,pos[1]+si))
	i = fnt.render(txt,1,c)
	s.blit(i,pos)

def mycprint(s,fnt,c,txt):
	i = fnt.render(txt,1,(0,0,0))
	
	x = (s.get_width()-i.get_width())/2
	y = (s.get_height()-i.get_height())/2
	
	s.blit(i,(x+2,y+2))
	i = fnt.render(txt,1,c)
	s.blit(i,(x,y))

	
def state_title(value):
	title = pygame.image.load("title.png")
	
	c1 = (255,255,255)
	c2 = (128,128,128)
	
	opts = [
		('play < L >',state_restart,None),
		('help',state_help,(state_title,None)),
		('quit',state_quit,None),
		]
		
	nopts = len(opts)
	nlevels = len(levels)
	
	if game.sound == 1 and game.music != 'title':
		pygame.mixer.music.fadeout(2000)
		game.music = 'title'

		
	pos = 0
	#game.level
	
	while 1:
		for e in pygame.event.get():
			if e.type is KEYDOWN:
				sfx['tick'].play()
				if e.key == K_UP: pos = (pos-1+nopts)%nopts
				elif e.key == K_DOWN: pos = (pos+1)%nopts
				elif e.key == K_LEFT: game.level = (game.level-1+nlevels)%nlevels
				elif e.key == K_RIGHT: game.level = (game.level+1)%nlevels
				elif e.key == K_RETURN: return opts[pos][1],opts[pos][2]
		screen.blit(title,(0,0))
		
		x,y = 155,60
		
		myprint(screen,fntm,(x,y),c2,"high: %04d"%game.high)
		y += 48
		
		n = 0
		for o in opts:
			txt,fnc,value = o
			txt = txt.replace('L',str(game.level+1))
			c = c2
			if n == pos: c = c1
			myprint(screen,fntm,(x,y),c,txt)
			y+=32
			n+=1
			
		myprint(screen,fnts,(0,240-16),c1,"04/05 ludum dare - (c) 2005 phil hassey")
		
		pygame.display.flip()
		pygame.time.wait(100)
		
class _sound:
	def play(self):
		pass
		
def state_init(value):
	global screen,game,levels,fnts,fntm,fntg,sfx,images
	
	pygame.font.init()
	#screen = pygame.display.set_mode((640,480),MYSURFACE|FULLSCREEN)
	screen = pygame.display.set_mode((320,240),MYSURFACE|FULLSCREEN)
	#screen = pygame.display.set_mode((320,240),HWSURFACE|DOUBLEBUF|FULLSCREEN)
	pygame.mouse.set_visible(0)
	
	game = _game()

	game.level = 0
	game.high = 0

	try:	
		pygame.mixer.init()
		pygame.mixer.music.set_volume(0.5)
		game.sound = 1
	except: game.sound = 0
	
	game.music = None

	levels = [
		'level1.tga',
		'level2.tga',
		'level2.5.tga',
		'level3.tga',
		'level3.5.tga',
		'level4.tga',
		'level5.tga',
		'level4.5.tga',
		]
	
	fntm = pygame.font.Font("goodtime.ttf",24)
	fnts = pygame.font.Font("goodtime.ttf",12)
	fntg = pygame.font.Font("goodtime.ttf",10)
	
	sfx = {}
	for name in ['battery','getready','guard','light_off','light_on','pause','pit','tick','win']:
		if game.sound: sfx[name] = pygame.mixer.Sound("%s.wav"%name)
		else: sfx[name] = _sound()
		
	images = {}
	for name in ['player','guard']:
		img = pygame.image.load('%s.tga'%name).convert_alpha(screen)
		for i in range(0,4):
			s = img.subsurface((i*24,0,24,16))
			images['%s.%d'%(name,i)] = s

	return state_title,None
	
run(state_init,None)	

#import profile
#profile.run('run(state_init,None)')

#only do apath 1/8 frames per guard (instead of every frame)
#only do about 32 rays per flaslight (instead of 144)

