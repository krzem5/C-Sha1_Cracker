def _gen_sha1_check_code(il):
	TYPE_CONST=0
	TYPE_REF=1
	TYPE_OUTPUT=2
	TYPE_INPUT=3
	TYPE_ROT_LEFT=4
	TYPE_SHIFT_LEFT=5
	TYPE_SUM=6
	TYPE_XOR=7
	TYPE_AND=8
	TYPE_OR=9
	def _set_or(l):
		o=set()
		for k in l:
			o|=k
		return o
	def _shorten(eq,ig=set()):
		def _op(a,b,t):
			if (t==TYPE_SUM):
				return (a+b)&0xffffffff
			if (t==TYPE_XOR):
				return (a^b)&0xffffffff
			if (t==TYPE_AND):
				return (a&b)&0xffffffff
			return (a|b)&0xffffffff
		if ("_vc" not in eq):
			eq["_vc"]=({eq["i"]} if eq["t"]==TYPE_OUTPUT else ((VARS[eq["i"]]["_vc"] if eq["i"] not in ig and VARS[eq["i"]] is not None else {eq["i"]}) if eq["t"]==TYPE_REF else set()))
		if (eq["t"] in [TYPE_REF,TYPE_OUTPUT] and eq["i"] not in ig and VARS[eq["i"]] is not None):
			return _shorten(VARS[eq["i"]],ig)
		elif (eq["t"]==TYPE_ROT_LEFT):
			eq["v"]=_shorten(eq["v"],ig)
			eq["_vc"]=eq["v"]["_vc"]
			if (eq["v"]["t"]==TYPE_CONST):
				return {"t":TYPE_CONST,"v":((eq["v"]["v"]<<eq["i"])|(eq["v"]["v"]>>(32-eq["i"])))&0xffffffff,"_vc":set()}
			elif (eq["v"]["t"]==TYPE_ROT_LEFT):
				eq={"t":TYPE_ROT_LEFT,"i":(eq["i"]+eq["v"]["i"])%32,"v":eq["v"]["v"],"_vc":eq["_vc"]}
			elif (eq["v"]["t"] in [TYPE_XOR,TYPE_AND,TYPE_OR]):
				return _shorten({"t":eq["v"]["t"],"l":[{"t":TYPE_ROT_LEFT,"i":eq["i"],"v":k} for k in eq["v"]["l"]],"_vc":_set_or([k["_vc"] for k in eq["v"]["l"]])},ig)
			return eq
		elif (eq["t"]==TYPE_SHIFT_LEFT):
			eq["v"]=_shorten(eq["v"],ig)
			eq["_vc"]=eq["v"]["_vc"]
			return eq
		elif (eq["t"]==TYPE_SUM):
			l=[]
			cv=-1
			i=0
			while (i<len(eq["l"])):
				k=_shorten(eq["l"][i],ig)
				if (k["t"]==TYPE_CONST):
					if (cv==-1):
						cv=k["v"]
					else:
						cv=_op(cv,k["v"],eq["t"])
				elif (k["t"]==TYPE_SUM):
					eq["l"].extend(k["l"])
				else:
					l.append(k)
				i+=1
			if (len(l)==0):
				return {"t":TYPE_CONST,"v":cv,"_vc":set()}
			if (len(l)==1 and cv<=0):
				return l[0]
			return {"t":TYPE_SUM,"l":l+([{"t":TYPE_CONST,"v":cv,"_vc":set()}] if cv>0 else []),"_vc":_set_or([e["_vc"] for e in l])}
		elif (eq["t"]==TYPE_XOR):
			l=[]
			hl=[]
			cv=-1
			i=0
			while (i<len(eq["l"])):
				k=_shorten(eq["l"][i],ig)
				if (k["t"]==TYPE_CONST):
					if (cv==-1):
						cv=k["v"]
					else:
						cv=_op(cv,k["v"],eq["t"])
				elif (k["t"]==TYPE_XOR):
					eq["l"].extend(k["l"])
				else:
					h=hash(_print(k))
					if (h not in hl):
						hl.append(h)
						l.append(k)
					else:
						del l[hl.index(h)]
						hl.remove(h)
				i+=1
			if (len(l)==0):
				return {"t":TYPE_CONST,"v":cv,"_vc":set()}
			if (len(l)==1 and cv<=0):
				return l[0]
			return {"t":TYPE_XOR,"l":l+([{"t":TYPE_CONST,"v":cv,"_vc":set()}] if cv>0 else []),"_vc":_set_or([e["_vc"] for e in l])}
		elif (eq["t"] in [TYPE_AND,TYPE_OR]):
			l=[]
			hl=[]
			cv=-1
			i=0
			while (i<len(eq["l"])):
				k=_shorten(eq["l"][i],ig)
				if (k["t"]==TYPE_CONST):
					if (cv==-1):
						cv=k["v"]
					else:
						cv=_op(cv,k["v"],eq["t"])
				elif (k["t"]==eq["t"]):
					eq["l"].extend(k["l"])
				else:
					h=hash(_print(k))
					if (h not in hl):
						hl.append(h)
						l.append(k)
				i+=1
			if (len(l)==0 or (cv==0 and eq["t"]==TYPE_AND)):
				return {"t":TYPE_CONST,"v":cv,"_vc":set()}
			if (len(l)==1 and cv<=0):
				return l[0]
			if (cv!=-1):
				l.append({"t":TYPE_CONST,"v":cv,"_vc":set()})
			if (eq["t"]==TYPE_AND and len(l)==2):
				if (l[0]["t"]==TYPE_XOR and l[1]["t"]!=TYPE_XOR):
					l=[l[1],l[0]]
				if (l[0]["t"]!=TYPE_XOR and l[1]["t"]==TYPE_XOR):
					return {"t":TYPE_XOR,"l":[{"t":TYPE_AND,"l":[l[0],e],"_vc":l[0]["_vc"]|e["_vc"]} for e in l[1]["l"]],"_vc":l[0]["_vc"]|l[1]["_vc"]}
			return {"t":eq["t"],"l":l,"_vc":_set_or([e["_vc"] for e in l])}
		return eq
	def _print(eq,q=0):
		def _o(s,q,t):
			return (f"({s})" if q==1 or (q==2 and t not in [TYPE_SUM,TYPE_SUB]) else s)
		if (eq["t"]==TYPE_CONST):
			return str(eq["v"])
		if (eq["t"] in [TYPE_REF,TYPE_OUTPUT,TYPE_INPUT]):
			return eq['i']
		if (eq["t"]==TYPE_ROT_LEFT):
			return f"l{eq['i']}({_print(eq['v'],q=0)})"
		if (eq["t"]==TYPE_SHIFT_LEFT):
			return f"({_print(eq['v'],q=1)}<<{eq['i']})"
		if (eq["t"]==TYPE_SUM):
			return _o("+".join([_print(k,q=1) for k in eq["l"]]),q,eq["t"])
		if (eq["t"]==TYPE_XOR):
			return _o("^".join([_print(k,q=1) for k in eq["l"]]),q,eq["t"])
		if (eq["t"]==TYPE_AND):
			return _o("&".join([_print(k,q=1) for k in eq["l"]]),q,eq["t"])
		return _o("|".join([_print(k,q=1) for k in eq["l"]]),q,eq["t"])
	def _basic_solve(v,eq):
		eq0,eq1=eq
		if (v in eq1["_vc"]):
			eq0,eq1=eq1,eq0
		while (eq0["t"]!=TYPE_REF):
			if (eq0["t"]==TYPE_ROT_LEFT):
				eq1={"t":TYPE_ROT_LEFT,"i":32-eq0["i"],"v":eq1,"_vc":eq1["_vc"]}
				eq0=eq0["v"]
			elif (eq0["t"]==TYPE_SHIFT_LEFT):
				print("Basic Solve: TYPE_SHIFT_LEFT")
				break
			elif (eq0["t"]==TYPE_SUM and eq0["l"][-1]["t"]==TYPE_CONST):
				if (eq1["t"]==TYPE_CONST):
					eq1["v"]=(eq1["v"]-eq0["l"][-1]["v"]+1+0xffffffff)&0xffffffff
					eq0["l"]=eq0["l"][:-1]
					if (len(eq0["l"])==1):
						eq0=eq0["l"][0]
				else:
					break
			elif (eq0["t"]==TYPE_XOR):
				print("Basic Solve: TYPE_XOR")
				break
			elif (eq0["t"]==TYPE_AND):
				print("Basic Solve: TYPE_AND")
				break
			elif (eq0["t"]==TYPE_OR):
				print("Basic Solve: TYPE_OR")
				break
			elif (eq0["t"]==TYPE_OUTPUT):
				print("Basic Solve: TYPE_OUTPUT")
				break
			else:
				break
		if (eq0["t"]!=TYPE_REF or eq0["i"]!=v):
			return (False,(_shorten(eq0),_shorten(eq1)))
		return (True,(eq0,_shorten(eq1)))
	def _add_eq(eq0,eq1):
		eq0=_shorten(eq0)
		eq1=_shorten(eq1)
		if (len(eq0["_vc"]|eq1["_vc"])==1):
			v=next(iter(eq0["_vc"]|eq1["_vc"]))
			st,o=_basic_solve(v,(eq0,eq1))
			if (st==True):
				VARS[v]=o[1]
				return
			else:
				eq0,eq1=o
		EQL.append((eq0,eq1))
	def _add_eq_v(v,eq,f=False):
		eq=_shorten(eq)
		if (f==True):
			VARS[v]=eq
			return
		v_eq=_shorten({"t":TYPE_REF,"i":v},ig={v})
		if ((eq["t"]==TYPE_REF and eq["i"][0]=="o") or len(eq["_vc"])==1):
			st,o=_basic_solve(v,(v_eq,eq))
			if (st==True):
				VARS[v]=o[1]
			else:
				EQL.append(o)
		else:
			VARS[v]=None
			EQL.append((v_eq,eq))
	def _get_temp(ti):
		VARS[f"t{ti}"]=None
		return ({"t":TYPE_REF,"i":f"t{ti}","_vc":{f"t{ti}"}},ti+1)
	def _divide_equation(b,ti,tv_m):
		if (b["t"] in [TYPE_SUM,TYPE_XOR,TYPE_AND,TYPE_OR]):
			if (len(b["l"])>2):
				dt=_shorten({"t":b["t"],"l":b["l"][1:],"_vc":_set_or([e["_vc"] for e in b["l"][1:]])})
				h=hash(_print(dt))
				if (h not in tv_m):
					dt,ti=_divide_equation(dt,ti,tv_m)
					tv,ti=_get_temp(ti)
					DIV_EQL.append((tv,dt))
					tv_m[h]=tv
				else:
					tv=tv_m[h]
				b["l"]=[b["l"][0],tv]
			for j,k in enumerate(b["l"]):
				if (k["t"] not in [TYPE_CONST,TYPE_REF,TYPE_OUTPUT,TYPE_INPUT]):
					h=hash(_print(k))
					if (h not in tv_m):
						k,ti=_divide_equation(k,ti,tv_m)
						tv,ti=_get_temp(ti)
						DIV_EQL.append((tv,k))
						tv_m[h]=tv
					else:
						tv=tv_m[h]
					b["l"][j]=tv
			if (len(b["l"])==1):
				b=b["l"][0]
			else:
				b["_vc"]=b["l"][0]["_vc"]|b["l"][1]["_vc"]
		elif (b["t"] in [TYPE_ROT_LEFT,TYPE_SHIFT_LEFT] and b["v"]["t"] not in [TYPE_CONST,TYPE_REF,TYPE_OUTPUT,TYPE_INPUT]):
			h=hash(_print(b["v"]))
			if (h not in tv_m):
				dt,ti=_divide_equation(b["v"],ti,tv_m)
				tv,ti=_get_temp(ti)
				DIV_EQL.append((tv,dt))
				tv_m[h]=tv
			else:
				tv=tv_m[h]
			b["v"]=tv
			b["_vc"]={tv["i"]}
		return (b,ti)
	VARS={"a0":_shorten({"t":TYPE_CONST,"v":0x67452301}),"b0":_shorten({"t":TYPE_CONST,"v":0xefcdab89}),"c0":_shorten({"t":TYPE_CONST,"v":0x98badcfe}),"d0":_shorten({"t":TYPE_CONST,"v":0x10325476}),"e0":_shorten({"t":TYPE_CONST,"v":0xc3d2e1f0})}
	EQL=[]
	cl=(il+72)//64
	dt=[None for _ in range(0,il)]+[0x80]+[0 for _ in range(0,(56-(il+1)%64)%64)]+[il>>53,(il>>45)&0xff,(il>>37)&0xff,(il>>29)&0xff,(il>>21)&0xff,(il>>13)&0xff,(il>>5)&0xff,(il<<3)&0xff]
	for i in range(0,cl):
		for j in range(0,16):
			VARS[f"o{i*16+j}"]=None
			if ((dt[i*64+j*4] is not None and dt[i*64+j*4+1] is not None and dt[i*64+j*4+2] is not None and dt[i*64+j*4+3] is not None) or (dt[i*64+j*4] is None and dt[i*64+j*4+1] is None and dt[i*64+j*4+2] is None and dt[i*64+j*4+3] is None)):
				_add_eq_v(f"w{i*80+j}",{"t":TYPE_OUTPUT,"i":f"o{i*16+j}"},True)
			elif (dt[i*64+j*4+1] is not None):
				_add_eq_v(f"w{i*80+j}",{"t":TYPE_OR,"l":[{"t":TYPE_SHIFT_LEFT,"i":24,"v":{"t":TYPE_OUTPUT,"i":f"o{i*16+j}"}},{"t":TYPE_CONST,"v":(dt[i*64+j*4+1]<<16)|(dt[i*64+j*4+2]<<8)|dt[i*64+j*4+3]}]},True)
			elif (dt[i*64+j*4+2] is not None):
				_add_eq_v(f"w{i*80+j}",{"t":TYPE_OR,"l":[{"t":TYPE_SHIFT_LEFT,"i":16,"v":{"t":TYPE_OUTPUT,"i":f"o{i*16+j}"}},{"t":TYPE_CONST,"v":(dt[i*64+j*4+2]<<8)|dt[i*64+j*4+3]}]},True)
			else:
				_add_eq_v(f"w{i*80+j}",{"t":TYPE_OR,"l":[{"t":TYPE_SHIFT_LEFT,"i":8,"v":{"t":TYPE_OUTPUT,"i":f"o{i*16+j}"}},{"t":TYPE_CONST,"v":dt[i*64+j*4+3]}]},True)
		for j in range(16,80):
			_add_eq_v(f"w{i*80+j}",{
				"t": TYPE_XOR,
				"l": [
					{
						"t": TYPE_ROT_LEFT,
						"i": 1,
						"v": {
							"t": TYPE_REF,
							"i": f"w{i*80+j-3}"
						}
					},
					{
						"t": TYPE_ROT_LEFT,
						"i": 1,
						"v": {
							"t": TYPE_REF,
							"i": f"w{i*80+j-8}"
						}
					},
					{
						"t": TYPE_ROT_LEFT,
						"i": 1,
						"v": {
							"t": TYPE_REF,
							"i": f"w{i*80+j-14}"
						}
					},
					{
						"t": TYPE_ROT_LEFT,
						"i": 1,
						"v": {
							"t": TYPE_REF,
							"i": f"w{i*80+j-16}"
						}
					}
				]
			},True)
	for j in range(0,cl):
		for i in range(80):
			if (i<20):
				_add_eq_v(f"a{j*81+i+1}",{
					"t": TYPE_SUM,
					"l": [
						{
							"t": TYPE_ROT_LEFT,
							"i": 5,
							"v": {
								"t": TYPE_REF,
								"i": f"a{j*81+i}"
							}
						},
						{
							"t": TYPE_XOR,
							"l": [
								{
									"t": TYPE_REF,
									"i": f"d{j*81+i}"
								},
								{
									"t": TYPE_AND,
									"l": [
										{
											"t": TYPE_REF,
											"i": f"b{j*81+i}"
										},
										{
											"t": TYPE_REF,
											"i": f"c{j*81+i}"
										}
									]
								},
								{
									"t": TYPE_AND,
									"l": [
										{
											"t": TYPE_REF,
											"i": f"b{j*81+i}"
										},
										{
											"t": TYPE_REF,
											"i": f"d{j*81+i}"
										}
									]
								}
							]
						},
						{
							"t": TYPE_REF,
							"i": f"e{j*81+i}"
						},
						{
							"t": TYPE_CONST,
							"v": 0x5a827999
						},
						{
							"t": TYPE_REF,
							"i": f"w{j*80+i}"
						}
					]})
			elif (i<40):
				_add_eq_v(f"a{j*81+i+1}",{
					"t": TYPE_SUM,
					"l": [
						{
							"t": TYPE_ROT_LEFT,
							"i": 5,
							"v": {
								"t": TYPE_REF,
								"i": f"a{j*81+i}"
							}
						},
						{
							"t": TYPE_XOR,
							"l": [
								{
									"t": TYPE_REF,
									"i": f"b{j*81+i}"
								},
								{
									"t": TYPE_REF,
									"i": f"c{j*81+i}"
								},
								{
									"t": TYPE_REF,
									"i": f"d{j*81+i}"
								}
							]
						},
						{
							"t": TYPE_REF,
							"i": f"e{j*81+i}"
						},
						{
							"t": TYPE_CONST,
							"v": 0x6ed9eba1
						},
						{
							"t": TYPE_REF,
							"i": f"w{j*80+i}"
						}
					]})
			elif (i<60):
				_add_eq_v(f"a{j*81+i+1}",{
					"t": TYPE_SUM,
					"l": [
						{
							"t": TYPE_ROT_LEFT,
							"i": 5,
							"v": {
								"t": TYPE_REF,
								"i": f"a{j*81+i}"
							}
						},
						{
							"t": TYPE_OR,
							"l": [
								{
									"t": TYPE_AND,
									"l": [
										{
											"t": TYPE_REF,
											"i": f"b{j*81+i}"
										},
										{
											"t": TYPE_REF,
											"i": f"c{j*81+i}"
										}
									]
								},
								{
									"t": TYPE_AND,
									"l": [
										{
											"t": TYPE_REF,
											"i": f"b{j*81+i}"
										},
										{
											"t": TYPE_REF,
											"i": f"d{j*81+i}"
										}
									]
								},
								{
									"t": TYPE_AND,
									"l": [
										{
											"t": TYPE_REF,
											"i": f"c{j*81+i}"
										},
										{
											"t": TYPE_REF,
											"i": f"d{j*81+i}"
										}
									]
								}
							]
						},
						{
							"t": TYPE_REF,
							"i": f"e{j*81+i}"
						},
						{
							"t": TYPE_CONST,
							"v": 0x8f1bbcdc
						},
						{
							"t": TYPE_REF,
							"i": f"w{j*80+i}"
						}
					]})
			else:
				_add_eq_v(f"a{j*81+i+1}",{
					"t": TYPE_SUM,
					"l": [
						{
							"t": TYPE_ROT_LEFT,
							"i": 5,
							"v": {
								"t": TYPE_REF,
								"i": f"a{j*81+i}"
							}
						},
						{
							"t": TYPE_XOR,
							"l": [
								{
									"t": TYPE_REF,
									"i": f"b{j*81+i}"
								},
								{
									"t": TYPE_REF,
									"i": f"c{j*81+i}"
								},
								{
									"t": TYPE_REF,
									"i": f"d{j*81+i}"
								}
							]
						},
						{
							"t": TYPE_REF,
							"i": f"e{j*81+i}"
						},
						{
							"t": TYPE_CONST,
							"v": 0xca62c1d6
						},
						{
							"t": TYPE_REF,
							"i": f"w{j*80+i}"
						}
					]})
			_add_eq_v(f"b{j*81+i+1}",{"t":TYPE_REF,"i":f"a{j*81+i}"},True)
			_add_eq_v(f"c{j*81+i+1}",{"t":TYPE_ROT_LEFT,"i":30,"v":{"t":TYPE_REF,"i":f"b{j*81+i}"}},True)
			_add_eq_v(f"d{j*81+i+1}",{"t":TYPE_REF,"i":f"c{j*81+i}"},True)
			_add_eq_v(f"e{j*81+i+1}",{"t":TYPE_REF,"i":f"d{j*81+i}"},True)
		_add_eq_v(f"a{(j+1)*81}",{"t":TYPE_SUM,"l":[{"t":TYPE_REF,"i":f"a{j*81}"},{"t":TYPE_REF,"i":f"a{(j+1)*81-1}"}]})
		_add_eq_v(f"b{(j+1)*81}",{"t":TYPE_SUM,"l":[{"t":TYPE_REF,"i":f"b{j*81}"},{"t":TYPE_REF,"i":f"b{(j+1)*81-1}"}]})
		_add_eq_v(f"c{(j+1)*81}",{"t":TYPE_SUM,"l":[{"t":TYPE_REF,"i":f"c{j*81}"},{"t":TYPE_REF,"i":f"c{(j+1)*81-1}"}]})
		_add_eq_v(f"d{(j+1)*81}",{"t":TYPE_SUM,"l":[{"t":TYPE_REF,"i":f"d{j*81}"},{"t":TYPE_REF,"i":f"d{(j+1)*81-1}"}]})
		_add_eq_v(f"e{(j+1)*81}",{"t":TYPE_SUM,"l":[{"t":TYPE_REF,"i":f"e{j*81}"},{"t":TYPE_REF,"i":f"e{(j+1)*81-1}"}]})
	_add_eq({"t":TYPE_INPUT,"v":"__h[0]"},{"t":TYPE_REF,"i":f"a{cl*81}"})
	_add_eq({"t":TYPE_INPUT,"v":"__h[1]"},{"t":TYPE_REF,"i":f"b{cl*81}"})
	_add_eq({"t":TYPE_INPUT,"v":"__h[2]"},{"t":TYPE_REF,"i":f"c{cl*81}"})
	_add_eq({"t":TYPE_INPUT,"v":"__h[3]"},{"t":TYPE_REF,"i":f"d{cl*81}"})
	_add_eq({"t":TYPE_INPUT,"v":"__h[4]"},{"t":TYPE_REF,"i":f"e{cl*81}"})
	rv=cl*16
	for i in range(0,cl*64,4):
		if (dt[i] is not None and dt[i+1] is not None and dt[i+2] is not None and dt[i+3] is not None):
			VARS[f"o{i//4}"]=_shorten({"t":TYPE_CONST,"v":(dt[i]<<24)|(dt[i+1]<<16)|(dt[i+2]<<8)|dt[i+3]})
			rv-=1
	while (True):
		e=True
		t_eql=[]
		for eq0,eq1 in EQL:
			eq0=_shorten(eq0)
			eq1=_shorten(eq1)
			if (eq1["t"] in [TYPE_CONST,TYPE_REF,TYPE_OUTPUT,TYPE_INPUT]):
				eq0,eq1=eq1,eq0
			vc=eq0["_vc"]|eq1["_vc"]
			if (len(vc)==1):
				v=vc.pop()
				st,o=_basic_solve(v,(eq0,eq1))
				if (st==True):
					VARS[v]=o[1]
					e=False
					continue
				eq0,eq1=o
			t_eql.append((eq0,eq1))
			i+=1
		EQL=t_eql
		if (e):
			break
	ti=0
	tv_m={}
	DIV_EQL=[]
	for a,b in EQL:
		a=_shorten(a)
		b=_shorten(b)
		if (b["t"] in [TYPE_CONST,TYPE_REF,TYPE_OUTPUT,TYPE_INPUT]):
			a,b=b,a
		b,ti=_divide_equation(b,ti,tv_m)
		DIV_EQL.append((a,b))
	v_rm={}
	for i,(a,b) in enumerate(DIV_EQL):
		if (a["t"] not in [TYPE_CONST,TYPE_OUTPUT,TYPE_INPUT]):
			if (a["i"] not in v_rm):
				v_rm[a["i"]]=[i,i]
			v_rm[a["i"]][1]=i
		if (b["t"] in [TYPE_ROT_LEFT,TYPE_SHIFT_LEFT]):
			if (b["v"]["i"] not in v_rm):
				v_rm[b["v"]["i"]]=[i,i]
			v_rm[b["v"]["i"]][1]=i
		else:
			for k in b["l"]:
				if (k["t"]!=TYPE_CONST):
					if (k["i"] not in v_rm):
						v_rm[k["i"]]=[i,i]
					v_rm[k["i"]][1]=i
	vc=0
	vl=[]
	vm={f"o{i}":f"o{i}" for i in range(0,rv)}
	rm={}
	for i in range(0,rv):
		v=v_rm[f"o{i}"]
		if (v[1] not in rm):
			rm[v[1]]=[]
		rm[v[1]].append(f"o{i}")
	o=""
	for i,(a,b) in enumerate(DIV_EQL):
		if (i in rm):
			vl.extend(rm[i])
			del rm[i]
		o+="\t"
		if (a["t"] not in [TYPE_CONST,TYPE_INPUT]):
			k=a["i"]
			if (len(vl)==0):
				vl.append(f"v{vc}")
				vc+=1
				o+="uint32_t "
			vm[k]=vl.pop(0)
			v=v_rm[k]
			if (v[1] not in rm):
				rm[v[1]]=[]
			rm[v[1]].append(vm[k])
			o+=f"{vm[k]}="
		else:
			o+=f"if ({a['v']}!="
		if (b["t"]==TYPE_ROT_LEFT):
			o+=f"BIT_ROT_FUNC({vm[b['v']['i']]},{b['i']})"
		elif (b["t"]==TYPE_SHIFT_LEFT):
			o+=f"{vm[b['v']['i']]}<<{b['i']}"
		elif (b["t"]==TYPE_SUM):
			if (b["l"][0]["t"]==TYPE_CONST):
				o+=f"{vm[b['l'][1]['i']]}+{b['l'][0]['v']}"
			elif (b["l"][1]["t"]==TYPE_CONST):
				o+=f"{vm[b['l'][0]['i']]}+{b['l'][1]['v']}"
			else:
				o+=f"{vm[b['l'][0]['i']]}+{vm[b['l'][1]['i']]}"
		elif (b["t"]==TYPE_XOR):
			if (b["l"][0]["t"]==TYPE_CONST):
				o+=f"{vm[b['l'][1]['i']]}^{b['l'][0]['v']}"
			elif (b["l"][1]["t"]==TYPE_CONST):
				o+=f"{vm[b['l'][0]['i']]}^{b['l'][1]['v']}"
			else:
				o+=f"{vm[b['l'][0]['i']]}^{vm[b['l'][1]['i']]}"
		elif (b["t"]==TYPE_AND):
			if (b["l"][0]["t"]==TYPE_CONST):
				o+=f"{vm[b['l'][1]['i']]}&{b['l'][0]['v']}"
			elif (b["l"][1]["t"]==TYPE_CONST):
				o+=f"{vm[b['l'][0]['i']]}&{b['l'][1]['v']}"
			else:
				o+=f"{vm[b['l'][0]['i']]}&{vm[b['l'][1]['i']]}"
		elif (b["t"]==TYPE_OR):
			if (b["l"][0]["t"]==TYPE_CONST):
				o+=f"{vm[b['l'][1]['i']]}|{b['l'][0]['v']}"
			elif (b["l"][1]["t"]==TYPE_CONST):
				o+=f"{vm[b['l'][0]['i']]}|{b['l'][1]['v']}"
			else:
				o+=f"{vm[b['l'][0]['i']]}|{vm[b['l'][1]['i']]}"
		if (a["t"] not in [TYPE_CONST,TYPE_INPUT]):
			o+=";\n"
		else:
			o+="){return 0;}\n"
	return o



def generate():
	with open("src/cpu_cracker/include/generated.h","w") as hf_cpu,open("src/cpu_cracker/generated.c","w") as cf_cpu,open("src/gpu_cracker/include/generated.h","w") as f_gpu:
		f1=_gen_sha1_check_code(1)
		f2=_gen_sha1_check_code(2)
		f3=_gen_sha1_check_code(3)
		f4=_gen_sha1_check_code(4)
		hf_cpu.write("#ifndef __GENERATED_H__\n#define __GENERATED_H__ 1\n#include <cpu_cracker.h>\n#include <stdint.h>\n\n\n\n#define _CHECK_HASH_CONCAT(l) _chk_ ## l\n#define CHECK_HASH(l,...) _CHECK_HASH_CONCAT(l)(__VA_ARGS__)\n\n\n\nvoid setup_hash(uint32_t h0,uint32_t h1,uint32_t h2,uint32_t h3,uint32_t h4);\n\n\n\nuint8_t _chk_1(uint32_t o0);\n\n\n\nuint8_t _chk_2(uint32_t o0);\n\n\n\nuint8_t _chk_3(uint32_t o0);\n\n\n\nuint8_t _chk_4(uint32_t o0);\n\n\n\n#endif")
		f_gpu.write(f"#ifndef __GENERATED_H__\n#define __GENERATED_H__ 1\n#include <gpu_cracker.h>\n#include <stdint.h>\n\n\n\n#define _CHECK_HASH_CONCAT(l) _chk_ ## l\n#define CHECK_HASH(l,...) _CHECK_HASH_CONCAT(l)(__VA_ARGS__)\n\n\n\n__device__ uint32_t __h[5];\n\n\n\nvoid setup_hash(sha1_t sha1){{\n\tCUDA_CALL(cudaMemcpyToSymbol(__h,sha1.h,5*sizeof(uint32_t)));\n}}\n\n\n\n__forceinline__ __device__ uint8_t _chk_1(uint32_t o0){{\n\t{f1}\treturn 1;\n}}\n\n\n\n__forceinline__ __device__ uint8_t _chk_2(uint32_t o0){{\n\t{f2}\treturn 1;\n}}\n\n\n\n__forceinline__ __device__ uint8_t _chk_3(uint32_t o0){{\n\t{f3}\treturn 1;\n}}\n\n\n\n__forceinline__ __device__ uint8_t _chk_4(uint32_t o0){{\n\t{f4}\treturn 1;\n}}\n\n\n\n#endif\n")
		cf_cpu.write(f"#include <generated.h>\n#include <cpu_cracker.h>\n#include <stdint.h>\n\n\n\nuint32_t __h[5];\n\n\n\nvoid setup_hash(uint32_t h0,uint32_t h1,uint32_t h2,uint32_t h3,uint32_t h4){{\n\t*__h=h0;\n\t*(__h+1)=h1;\n\t*(__h+2)=h2;\n\t*(__h+3)=h3;\n\t*(__h+4)=h4;\n}}\n\n\n\nuint8_t _chk_1(uint32_t o0){{\n\t{f1}\treturn 1;\n}}\n\n\n\nuint8_t _chk_2(uint32_t o0){{\n\t{f2}\treturn 1;\n}}\n\n\n\nuint8_t _chk_3(uint32_t o0){{\n\t{f3}\treturn 1;\n}}\n\n\n\nuint8_t _chk_4(uint32_t o0){{\n\t{f4}\treturn 1;\n}}\n")
