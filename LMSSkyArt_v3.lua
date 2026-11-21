--[[
	Modules.LMSSkyArt  v3                                                        (SKY 2026-11-21)

	Every killer's Last Man Standing world. Built from the killer's reference painting:
	  * a full 360-degree skybox: the reference itself in front, extended all the way round from its own
	    painted scenery (seam-cut, centrepieces kept unique), with its own zenith
	  * the painting's light: Atmosphere, fog, ambient and grade measured from the panorama's horizon / mid-sky
	  * life: the sky turns, Terrain clouds drift in the killer's colours, a mist ring rolls round the horizon, and
	    each killer has their own animated set pieces (chains, cages, crystals, eyes, butterflies, searchlights...)
	    built around the camera and animated at the controller's 20 Hz tick.

	LMSSkyArt.spec(key) -> the sky spec SkyCtl (LMSCinema) runs. If a killer's v3 faces are not uploaded yet the
	previous painted faces are used, so nothing ever shows a blank sky.
	Pre-v3 version: ServerStorage.SKY_Backups_20261121.LMSSkyArt_preV3
]]
local Art = {}
local Lighting = game:GetService("Lighting")
local c3 = Color3.fromRGB
local function id(n) return (n and n ~= "" and n ~= 0) and ("rbxassetid://" .. tostring(n)) or nil end
local DN = "rbxassetid://119513369754836"
local MIST = "rbxassetid://117668972455896"

-- =============================================================================================================
-- ASSETS (filled in by the v3 upload; empty entries fall back to the pre-v3 faces)
-- =============================================================================================================
local IDS = {
	faces = {
		guest666 = { Ft = "110092140226298", Bk = "118558823512714", Lf = "114353190904757", Rt = "136437593872576", Up = "72097579801159" },
		sanic = { Ft = "128831454039767", Bk = "91216895979219", Lf = "129670222652459", Rt = "130145655108792", Up = "126126224418765" },
		["1x1x1x1"] = { Ft = "110358109424516", Bk = "120440170453519", Lf = "118918960744889", Rt = "110923847803757", Up = "72769561915234" },
		bloxwatch = { Ft = "91445115063644", Bk = "133845523603104", Lf = "74367740308094", Rt = "91108324087895", Up = "122550294031745" },
		doombringer = { Ft = "125963030480971", Bk = "70903754557306", Lf = "130746258368102", Rt = "72532810616900", Up = "93504045854474" },
		ellernate = { Ft = "102233239689207", Bk = "102980894916348", Lf = "126923503970084", Rt = "108972570763820", Up = "104873759928982" },
		herobrine = { Ft = "95093738511106", Bk = "96046777122812", Lf = "85378076014425", Rt = "121741944982311", Up = "88689017138567" },
		itrapped = { Ft = "72825678110864", Bk = "75714696319902", Lf = "138863085166138", Rt = "92048970884050", Up = "80821340280086" },
		johndoe = { Ft = "100888665472346", Bk = "84419391156396", Lf = "85572948406672", Rt = "139742571340647", Up = "99604494072077" },
		slasher = { Ft = "81348681625335", Bk = "130049941153652", Lf = "96411191252188", Rt = "77745224697436", Up = "133536515896935" },
		rake = { Ft = "94238071552445", Bk = "137757040998630", Lf = "72205907440446", Rt = "74023214280466", Up = "88540215554673" },
		flowers = { Ft = "87367581778203", Bk = "87014117342694", Lf = "85794393515341", Rt = "78823226260748", Up = "73638714874438" },
		noli = { Ft = "81558971713707", Bk = "98959295212333", Lf = "106749027038952", Rt = "98320567310819", Up = "126488526895277" },
		solemn = { Ft = "80273940139861", Bk = "118389924017133", Lf = "127531642094200", Rt = "137267810942151", Up = "104828211250826" },
		stalker = { Ft = "140369025711769", Bk = "126494475171626", Lf = "134055000574990", Rt = "119600790503580", Up = "104277543186354" },
		zerix = { Ft = "83355074078786", Bk = "73330060399492", Lf = "134847128551231", Rt = "138487596120896", Up = "132318885040196" },
		c00lkidd = { Ft = "128995836722262", Bk = "130843590456573", Lf = "85612987949928", Rt = "80897100187274", Up = "88054488631389" },
	},
	util = {
		chain = "127499333348695",
		glow = "110921642897447",
		butterfly = "80689384889134",
		petal = "99934078586565",
		eyes = "96591555451088",
		star4 = "110806362832765",
		beam = "72180540565792",
		square = "91022842869158",
		doodles = "120387189852826",
	},
}
Art.IDS = IDS
-- pre-v3 painted faces (Ft, Bk, Lf, Rt, Up): the fallback
local OLD = {
	guest666 = { "107525310689183", "104759547132883", "76724182347846", "135099793749608", "94584873206583" },
	johndoe = { "71328485622248", "102209457641931", "133727008121267", "94840160075861", "98647109647272" },
	noli = { "102476898780719", "77559486684164", "127605982249112", "139547956943438", "117676165946926" },
	doombringer = { "83794435097899", "111734363663389", "127780774529522", "82464205632880", "137400356843548" },
	["1x1x1x1"] = { "112919799358440", "137528803093140", "70579142021847", "94692806801873", "84182551421176" },
	c00lkidd = { "112533226302902", "127662941720298", "125112095382272", "121241098599246", "108701820606755" },
	herobrine = { "102466562431339", "91707959131168", "122869471474619", "74355494034763", "80086932498647" },
	slasher = { "88929855767349", "102733317417488", "98217333903630", "73585349098156", "100022310908329" },
	flowers = { "138650984908061", "129233006810528", "78368488765163", "75652776258359", "80090931414787" },
	itrapped = { "98548507918147", "122632295254672", "85651068720745", "122761138443590", "80999664258090" },
	stalker = { "130561237626434", "85991042664314", "136629712733820", "117072955951965", "136705527978882" },
	rake = { "118046232934238", "140578347027968", "109992778893935", "76710542143166", "129408360222917" },
	sanic = { "102184382564991", "86354947201956", "111501914710818", "83130541935219", "91677136009704" },
	ellernate = { "126227829016931", "71508645446243", "92086252048955", "93044972793172", "121379902020087" },
	solemn = { "85808606701897", "134127813251210", "95037639869206", "121143749473205", "86236117455054" },
	bloxwatch = { "90133521607745", "129621068124027", "100669757081871", "80918792738215", "123592752059847" },
	default = { "113335640418905", "117194276218721", "96884207080687", "97054680271302", "137450131705280" },
}
local function facesFor(key)
	local f = IDS.faces[key]
	if f and f.Ft and f.Ft ~= "" then
		return { Ft = id(f.Ft), Bk = id(f.Bk), Lf = id(f.Lf), Rt = id(f.Rt), Up = id(f.Up), Dn = DN }, true
	end
	local o = OLD[key]
	if not o then return nil, false end
	return { Ft = id(o[1]), Bk = id(o[2]), Lf = id(o[3]), Rt = id(o[4]), Up = id(o[5]), Dn = DN }, false
end
local function U(name) return id(IDS.util[name]) end

-- calibration, measured in Studio with the labelled test sky: world azimuth (degrees, clockwise from -Z) of
-- SkyboxFt's centre at SkyboxOrientation 0, and which way +SkyboxOrientation.Y turns the painting
local CAL = { frontAz = 0, spinSign = -1 }
Art.CAL = CAL

-- =============================================================================================================
-- MEASURED from each panorama: horizon / mid-sky / zenith-band / low-horizon colours, and where (azimuth,
-- elevation in degrees, relative to the painting's front) its centrepieces sit
-- =============================================================================================================
local M = {
	guest666 = { hz = c3(38, 10, 11), mid = c3(62, 13, 15), top = c3(17, 1, 2), low = c3(41, 11, 12), anchors = { moon = { 32.2, 40.8 } } },
	sanic = { hz = c3(22, 1, 10), mid = c3(33, 0, 1), top = c3(14, 0, 0), low = c3(16, 1, 10), anchors = { moon = { 41.9, 32.0 }, eyeL = { 2.5, 42.6 }, eyeR = { 14.3, 41.0 } } },
	["1x1x1x1"] = { hz = c3(6, 36, 3), mid = c3(4, 28, 1), top = c3(3, 17, 2), low = c3(5, 24, 2), anchors = { one = { 17.0, 40.4 } } },
	bloxwatch = { hz = c3(48, 38, 25), mid = c3(20, 16, 13), top = c3(20, 14, 7), low = c3(43, 33, 22), anchors = { star = { 31.8, 54.3 } } },
	doombringer = { hz = c3(31, 27, 33), mid = c3(37, 35, 42), top = c3(39, 32, 38), low = c3(26, 22, 27), anchors = { moon = { 23.3, 51.3 }, beam = { -29.2, 53.8 } } },
	ellernate = { hz = c3(99, 66, 46), mid = c3(157, 110, 76), top = c3(187, 142, 100), low = c3(95, 63, 44), anchors = { crown = { -0.2, 67.2 }, pillar = { 1.6, 46.1 } } },
	herobrine = { hz = c3(24, 25, 34), mid = c3(34, 36, 48), top = c3(13, 14, 20), low = c3(20, 21, 30), anchors = { eyeL = { -10.1, 44.7 }, eyeR = { 9.1, 42.5 }, moon = { 39.6, 46.7 }, window = { 33.6, 14.4 } } },
	itrapped = { hz = c3(19, 31, 69), mid = c3(18, 28, 64), top = c3(12, 19, 45), low = c3(16, 26, 58), anchors = { crown = { -1.9, 64.5 } } },
	johndoe = { hz = c3(38, 2, 2), mid = c3(64, 5, 6), top = c3(18, 1, 1), low = c3(38, 2, 3), anchors = { sun = { 2.6, 40.5 } } },
	slasher = { hz = c3(16, 15, 16), mid = c3(13, 13, 13), top = c3(11, 10, 11), low = c3(14, 11, 13), anchors = { moon = { 23.9, 44.0 }, window = { -28.8, 12.8 } } },
	rake = { hz = c3(13, 9, 9), mid = c3(16, 14, 14), top = c3(7, 6, 6), low = c3(11, 7, 8), anchors = { moon = { -7.7, 44.1 }, eyes = { 26.7, 35.6 } } },
	flowers = { hz = c3(84, 9, 9), mid = c3(77, 16, 15), top = c3(39, 5, 5), low = c3(70, 9, 8), anchors = { sun = { 25.0, 31.6 } } },
	noli = { hz = c3(4, 9, 52), mid = c3(4, 7, 36), top = c3(1, 2, 14), low = c3(4, 8, 43), anchors = { halo = { 30.8, 54.7 }, face = { 31.8, 44.3 } } },
	solemn = { hz = c3(77, 76, 76), mid = c3(47, 47, 46), top = c3(23, 23, 22), low = c3(68, 68, 67), anchors = { moon = { 34.4, 35.5 } } },
	stalker = { hz = c3(13, 11, 11), mid = c3(10, 5, 5), top = c3(5, 4, 4), low = c3(17, 15, 15), anchors = { lamp1 = { -49.6, 34.6 }, lamp2 = { -12.6, 19.3 }, lamp3 = { 44.5, 25.6 } } },
	zerix = { hz = c3(113, 111, 112), mid = c3(102, 101, 101), top = c3(71, 71, 71), low = c3(110, 108, 109), anchors = { halo = { -0.8, 55.9 } } },
	c00lkidd = { hz = c3(30, 9, 9), mid = c3(31, 11, 10), top = c3(27, 9, 9), low = c3(32, 11, 11), anchors = {  } },}
Art.M = M

-- =============================================================================================================
-- PRIMITIVES (everything lives in ctx.dome, which SkyCtl keeps centred on the camera)
-- =============================================================================================================
local function newPart(ctx, props)
	local p = Instance.new("Part")
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, false
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Size = Vector3.one
	p.Transparency = 1
	for k, v in pairs(props or {}) do p[k] = v end
	p.Parent = ctx.dome
	return p
end
local function origin(ctx) return ctx.center and ctx.center.Position or ctx.dome:GetPivot().Position end
local function dir(az, el) return (CFrame.Angles(0, -math.rad(az), 0) * CFrame.Angles(math.rad(el), 0, 0)).LookVector end
local function NS(t) local k = {} for i = 1, #t, 2 do table.insert(k, NumberSequenceKeypoint.new(t[i], t[i + 1])) end return NumberSequence.new(k) end
local function rnd(rng, a, b) return a + (b - a) * rng:NextNumber() end
local hi = function(ctx) return ctx.q >= 5 end

-- current turn of the painting, so things painted on it (moon, eyes...) can be tracked by sprites and glows
local function skyTurn(ctx)
	local s = ctx.skyInst
	if not (s and s.Parent) then s = Lighting:FindFirstChildOfClass("Sky") ctx.skyInst = s end
	return s and s.SkyboxOrientation.Y or 0
end
local function skyAz(ctx, az) return CAL.frontAz + az + CAL.spinSign * skyTurn(ctx) end

-- a picture in the sky (BillboardGui at R studs, occlusion-tested by SkyCtl through ctx.boards)
local function sprite(ctx, o)
	local p = newPart(ctx, { Name = "SkySprite" })
	local g = Instance.new("BillboardGui")
	g.Size = UDim2.fromScale(o.size * (o.aspect or 1), o.size)
	g.LightInfluence = 0
	g.Brightness = o.bright or 1.4
	g.MaxDistance = math.huge
	g.AlwaysOnTop = true
	g.Adornee = p
	g.Parent = p
	local im = Instance.new("ImageLabel")
	im.BackgroundTransparency = 1
	im.Size = UDim2.fromScale(1, 1)
	im.Image = o.img or ""
	im.ImageColor3 = o.color or Color3.new(1, 1, 1)
	im.ImageTransparency = o.trans or 0
	if o.rect then im.ImageRectSize = o.rect im.ImageRectOffset = o.offset or Vector2.zero end
	im.Rotation = o.rot or 0
	im.Parent = g
	local s = { p = p, g = g, im = im, az = o.az, el = o.el, R = o.R or 900, sky = o.sky, base = o.trans or 0, size = o.size, aspect = o.aspect or 1, ph = o.ph or math.random() * 6.28 }
	table.insert(ctx.boards, { g = g, p = p })
	table.insert(ctx.sprites, s)
	return s
end

-- a chain hung across the sky between two points (a Beam with the chain-link texture, sagging, swaying)
local function chain(ctx, a, b, o)
	o = o or {}
	local R = o.R or 430
	local O = origin(ctx)
	local function anchor(d)
		local p = newPart(ctx, { Name = "ChainEnd", CFrame = CFrame.new(O + dir(d[1], d[2]) * R) })
		local at = Instance.new("Attachment")
		at.CFrame = CFrame.fromMatrix(Vector3.zero, Vector3.new(0, -1, 0), Vector3.new(1, 0, 0))
		at.Parent = p
		return at
	end
	local a0, a1 = anchor(a), anchor(b)
	local bm = Instance.new("Beam")
	bm.Attachment0, bm.Attachment1 = a0, a1
	bm.Texture = U("chain") or ""
	bm.TextureMode = Enum.TextureMode.Static
	bm.TextureLength = o.link or 9
	bm.Width0, bm.Width1 = o.w or 4.5, o.w or 4.5
	bm.Color = ColorSequence.new(o.color or c3(30, 30, 34))
	bm.LightEmission = o.emit or 0
	bm.LightInfluence = o.lit or 0
	bm.Transparency = NumberSequence.new(o.trans or 0)
	bm.FaceCamera = true
	bm.Segments = 30
	bm.CurveSize0, bm.CurveSize1 = o.sag or 60, -(o.sag or 60)
	bm.Parent = a0.Parent
	local c = { beam = bm, sag = o.sag or 60, ph = math.random() * 6.28, amp = o.sway or 6 }
	table.insert(ctx.chains, c)
	return c
end

-- something that floats: rotates, bobs and drifts round the sky (parts moved together with BulkMoveTo)
local function float(ctx, parts, rel, o)
	local f = { parts = parts, rel = rel, az = o.az, el = o.el, R = o.R, spin = o.spin or Vector3.new(0.05, 0.12, 0.03), drift = o.drift or 0.4,
		bob = o.bob or 3, ph = math.random() * 6.28, rot = o.rot or CFrame.Angles(math.random() * 6, math.random() * 6, math.random() * 6), swing = o.swing }
	table.insert(ctx.floaters, f)
	return f
end
local function block(ctx, size, col, mat, o)
	o = o or {}
	local p = newPart(ctx, { Size = size, Color = col, Material = mat or Enum.Material.SmoothPlastic, Transparency = o.trans or 0, Reflectance = o.refl or 0 })
	if o.edge then
		local sb = Instance.new("SelectionBox")
		sb.Adornee = p
		sb.Color3 = o.edge
		sb.LineThickness = o.edgeW or 0.35
		sb.SurfaceTransparency = 1
		sb.Transparency = o.edgeT or 0
		sb.Parent = p
	end
	if o.face then
		local d = Instance.new("Decal")
		d.Texture = o.face
		d.Face = Enum.NormalId.Front
		d.Color3 = o.faceCol or Color3.new(1, 1, 1)
		d.Transparency = o.faceT or 0
		d.Parent = p
	end
	return p
end
-- an open iron cage (bars + rims), returned as parts + offsets from its hanging point
local function cage(ctx, s, col)
	local parts, rel = {}, {}
	local h, r, t = s * 1.5, s * 0.5, s * 0.06
	local function add(size, cf)
		table.insert(parts, newPart(ctx, { Size = size, Color = col, Material = Enum.Material.Metal, Transparency = 0 }))
		table.insert(rel, cf)
	end
	for _, y in ipairs({ -t, -h * 0.5, -h }) do
		for i = 0, 3 do
			local a = i * math.pi / 2
			add(Vector3.new(r * 2 + t, t, t), CFrame.new(0, y, 0) * CFrame.Angles(0, a, 0) * CFrame.new(0, 0, r))
		end
	end
	for i = 0, 11 do
		local a = i / 12 * math.pi * 2
		local x, z = math.cos(a) * r, math.sin(a) * r
		local m = math.max(math.abs(math.cos(a)), math.abs(math.sin(a)))
		add(Vector3.new(t, h, t), CFrame.new(x / m, -h / 2, z / m))
	end
	add(Vector3.new(t * 1.4, h * 0.35, t * 1.4), CFrame.new(0, h * 0.17, 0))   -- hook
	return parts, rel
end
-- a ring of glowing segments (halo / fire ring) around a point overhead, turning
local function ring(ctx, o)
	local parts, rel = {}, {}
	local n = o.segs or (hi(ctx) and 72 or 40)
	local R = o.radius
	for i = 0, n - 1 do
		local a = i / n * math.pi * 2
		local len = 2 * math.pi * R / n * 1.08
		table.insert(parts, newPart(ctx, { Size = Vector3.new(o.thick, o.thick * (o.flat or 0.5), len), Color = o.color, Material = Enum.Material.Neon, Transparency = o.trans or 0 }))
		table.insert(rel, CFrame.Angles(0, a, 0) * CFrame.new(R, 0, 0))
	end
	local r = { parts = parts, rel = rel, h = o.height, tilt = o.tilt or CFrame.identity, speed = o.speed or 0.03, a = math.random() * 6.28, off = o.off or Vector3.zero, flick = o.flicker }
	table.insert(ctx.rings, r)
	return r
end
-- a particle emitter in a box around the camera
local function emitter(ctx, o)
	if ctx.q < 3 then return end
	local box = newPart(ctx, { Name = "SkyEmitter", Size = o.box or Vector3.new(180, 40, 180), CFrame = CFrame.new(origin(ctx) + (o.off or Vector3.new(0, 30, 0))) })
	local e = Instance.new("ParticleEmitter")
	e.Texture = o.tex or ""
	e.Rate = (o.rate or 10) * (ctx.q >= 7 and 1 or 0.6)
	e.Lifetime = o.life or NumberRange.new(6, 10)
	e.Speed = o.speed or NumberRange.new(1, 4)
	e.SpreadAngle = o.spread or Vector2.new(180, 180)
	e.Size = o.size or NumberSequence.new(1)
	e.Color = o.color or ColorSequence.new(Color3.new(1, 1, 1))
	e.Transparency = o.trans or NS({ 0, 1, 0.12, 0.1, 0.85, 0.2, 1, 1 })
	e.LightEmission = o.emit or 0.3
	e.LightInfluence = o.lit or 0
	e.Rotation = o.rotation or NumberRange.new(0, 360)
	e.RotSpeed = o.rotSpeed or NumberRange.new(-30, 30)
	e.Acceleration = o.accel or Vector3.zero
	e.Drag = o.drag or 0
	e.EmissionDirection = o.emitDir or Enum.NormalId.Top
	if o.flip then
		e.FlipbookLayout = Enum.ParticleFlipbookLayout.Grid2x2
		e.FlipbookMode = Enum.ParticleFlipbookMode.Loop
		e.FlipbookFramerate = o.flipRate or NumberRange.new(10, 16)
		e.FlipbookStartRandom = true
	end
	if o.orient then e.Orientation = o.orient end
	e.Parent = box
	return e
end
-- a searchlight: a soft beam from a tower top that sweeps the sky
local function searchlight(ctx, az, el, o)
	local O = origin(ctx)
	local base = newPart(ctx, { Name = "LampBase", CFrame = CFrame.new(O + dir(az, el) * (o.R or 380)) })
	local a0 = Instance.new("Attachment") a0.Parent = base
	local tgt = newPart(ctx, { Name = "LampTarget", CFrame = base.CFrame })
	local a1 = Instance.new("Attachment") a1.Parent = tgt
	local bm = Instance.new("Beam")
	bm.Attachment0, bm.Attachment1 = a0, a1
	bm.Texture = U("beam") or ""
	bm.TextureMode = Enum.TextureMode.Stretch
	bm.Width0, bm.Width1 = o.w0 or 6, o.w1 or 110
	bm.LightEmission = 1
	bm.LightInfluence = 0
	bm.Brightness = 2
	bm.Color = ColorSequence.new(o.color or c3(235, 235, 240))
	bm.Transparency = NS({ 0, 0.25, 0.5, 0.65, 1, 1 })
	bm.FaceCamera = true
	bm.Segments = 2
	bm.Parent = base
	local glow = sprite(ctx, { img = U("glow"), az = az, el = el, R = o.R or 380, size = 30, color = o.color or c3(255, 255, 255), trans = 0.1, bright = 2 })
	local L = { base = base, tgt = tgt, az = az, el = el, sweep = o.sweep or 35, lift = o.lift or { 25, 60 }, speed = o.speed or 0.18, ph = math.random() * 6.28, len = o.len or 700 }
	table.insert(ctx.lamps, L)
	return L
end
-- a lightning bolt: a jagged run of glowing beams from high cloud down toward the horizon, gone in a blink
local function bolt(ctx, az, col)
	local O = origin(ctx)
	local pts = {}
	local el, a = 50 + math.random() * 15, az
	local n = 7
	for i = 0, n do
		table.insert(pts, O + dir(a + (math.random() - 0.5) * (i == 0 and 0 or 7), el - i * (el + 2) / n) * 480)
	end
	local made = {}
	for i = 1, n do
		local p0 = newPart(ctx, { CFrame = CFrame.new(pts[i]) }) local p1 = newPart(ctx, { CFrame = CFrame.new(pts[i + 1]) })
		local a0 = Instance.new("Attachment") a0.Parent = p0 local a1 = Instance.new("Attachment") a1.Parent = p1
		local bm = Instance.new("Beam")
		bm.Attachment0, bm.Attachment1 = a0, a1
		bm.Texture = U("beam") or ""
		bm.TextureMode = Enum.TextureMode.Stretch
		bm.Width0, bm.Width1 = 7 - i * 0.6, 7 - (i + 1) * 0.6
		bm.LightEmission, bm.LightInfluence, bm.Brightness = 1, 0, 6
		bm.Color = ColorSequence.new(col)
		bm.FaceCamera = true
		bm.Parent = p0
		table.insert(made, p0) table.insert(made, p1)
	end
	task.delay(0.09, function() for _, p in ipairs(made) do for _, b in ipairs(p:GetChildren()) do if b:IsA("Beam") then b.Transparency = NumberSequence.new(0.6) end end end end)
	task.delay(0.16, function() for _, p in ipairs(made) do for _, b in ipairs(p:GetChildren()) do if b:IsA("Beam") then b.Transparency = NumberSequence.new(0) end end end end)
	task.delay(0.3, function() for _, p in ipairs(made) do p:Destroy() end end)
end
-- sky flash (lightning light): the grade pops and settles
local function flash(ctx, k)
	local cc = ctx.cc
	if not (cc and cc.Parent) then return end
	local rest = (ctx.sp and ctx.sp.gradeBrightness) or 0.02
	cc.Brightness = rest + (k or 0.22)
	task.delay(0.07, function() if cc.Parent then cc.Brightness = rest end end)
	task.delay(0.15, function() if cc.Parent then cc.Brightness = rest + (k or 0.22) * 0.6 end end)
	task.delay(0.26, function() if cc.Parent then cc.Brightness = rest end end)
end

-- =============================================================================================================
-- THE MIST RING (from v2): a band of mist rolling round the horizon in the killer's fog colour, and high wisps
-- =============================================================================================================
local STEP = math.pi * 2 / 16
local function slotOffset(s)
	local x = (s % 8) * 256
	return (x < 1024 and Vector2.new(x, 0) or Vector2.new(x - 1024, 512)) + Vector2.new(2, 2)
end
local function makeRing(ctx, o)
	local R = o.R
	local yLo, yHi = R * math.tan(math.rad(o.lo)), R * math.tan(math.rad(o.hi))
	local L = { R = R, yMid = (yLo + yHi) / 2, a = o.a0 or 0, speed = math.rad(o.speed or 0), parts = {}, imgs = {}, tr = o.tr or 0, breathe = o.breathe, bf = o.bf or 0.5 }
	local w, h = 2 * R * math.sin(STEP / 2), yHi - yLo
	for i = 0, 15 do
		local p = newPart(ctx, { Name = "Horizon_" .. o.name, Size = Vector3.new(w, h, 0.2) })
		local g = Instance.new("SurfaceGui")
		g.Face = Enum.NormalId.Front
		g.LightInfluence = 0
		g.Brightness = o.bright or 1
		g.SizingMode = Enum.SurfaceGuiSizingMode.FixedSize
		g.CanvasSize = Vector2.new(256, 512)
		g.Parent = p
		local im = Instance.new("ImageLabel")
		im.BackgroundTransparency = 1
		im.Size = UDim2.fromScale(1, 1)
		im.Image = MIST
		im.ImageRectSize = Vector2.new(252, 508)
		im.ImageRectOffset = slotOffset(i + (o.slot0 or 0))
		im.ImageColor3 = o.tint
		im.ImageTransparency = L.tr
		im.Parent = g
		L.parts[i + 1], L.imgs[i + 1] = p, im
	end
	table.insert(ctx.mist, L)
	return L
end
local function mistBuild(ctx, fog, o)
	o = o or {}
	makeRing(ctx, { name = "mist", R = 350, lo = -7, hi = o.mistHi or 9, slot0 = 2, tr = o.mistT or 0.3, tint = fog, speed = -1.1, breathe = 0.18, bf = 0.45 })
	makeRing(ctx, { name = "wisp", R = 460, lo = 10, hi = 46, slot0 = 5, tr = o.wispT or 0.74, tint = Color3.new(1, 1, 1):Lerp(fog, 0.7), speed = 0.7, breathe = 0.12, bf = 0.3 })
end

-- =============================================================================================================
-- THE TICK: sprites follow the painting, floaters drift, chains sway, rings turn, lamps sweep, mist rolls
-- =============================================================================================================
local function tick(ctx, dt, st)
	st.t = (st.t or 0) + dt
	local t = st.t
	local O = origin(ctx)
	local parts, cfs = {}, {}
	for _, s in ipairs(ctx.sprites) do
		local az = s.sky and skyAz(ctx, s.az) or s.az
		table.insert(parts, s.p) table.insert(cfs, CFrame.new(O + dir(az, s.el) * s.R))
	end
	for _, f in ipairs(ctx.floaters) do
		local az = f.az + t * f.drift
		local pos = O + dir(az, f.el + math.sin(t * 0.3 + f.ph) * 0.8) * f.R + Vector3.new(0, math.sin(t * 0.5 + f.ph) * f.bob, 0)
		local cf
		if f.swing then
			cf = CFrame.new(pos) * CFrame.Angles(math.sin(t * f.swing[1] + f.ph) * f.swing[2], t * 0.05, math.cos(t * f.swing[1] * 0.8 + f.ph) * f.swing[2] * 0.6)
		else
			cf = CFrame.new(pos) * f.rot * CFrame.Angles(t * f.spin.X, t * f.spin.Y, t * f.spin.Z)
		end
		for i, p in ipairs(f.parts) do table.insert(parts, p) table.insert(cfs, cf * f.rel[i]) end
	end
	for _, r in ipairs(ctx.rings) do
		r.a += r.speed * dt
		local base = CFrame.new(O + Vector3.new(0, r.h, 0) + r.off) * r.tilt * CFrame.Angles(0, r.a, 0)
		for i, p in ipairs(r.parts) do table.insert(parts, p) table.insert(cfs, base * r.rel[i]) end
	end
	for _, L in ipairs(ctx.lamps) do
		local a = L.az + math.sin(t * L.speed + L.ph) * L.sweep
		local e = L.lift[1] + (L.lift[2] - L.lift[1]) * (0.5 + 0.5 * math.sin(t * L.speed * 0.7 + L.ph * 1.3))
		local b = O + dir(L.az, L.el) * 380
		table.insert(parts, L.base) table.insert(cfs, CFrame.new(b))
		table.insert(parts, L.tgt) table.insert(cfs, CFrame.new(b + dir(a, e) * L.len))
	end
	for _, L in ipairs(ctx.mist) do
		L.a += L.speed * dt
		for i, p in ipairs(L.parts) do
			local a = L.a - (i - 1) * STEP
			table.insert(parts, p) table.insert(cfs, CFrame.new(O) * CFrame.Angles(0, a, 0) * CFrame.new(0, L.yMid, -L.R) * CFrame.Angles(0, math.pi, 0))
			if L.breathe then L.imgs[i].ImageTransparency = math.clamp(L.tr + L.breathe * math.sin(t * L.bf + i * 0.9), 0, 1) end
		end
	end
	if #parts > 0 then workspace:BulkMoveTo(parts, cfs, Enum.BulkMoveMode.FireCFrameChanged) end
	for _, c in ipairs(ctx.chains) do
		local s = c.sag + math.sin(t * 0.35 + c.ph) * c.amp
		c.beam.CurveSize0, c.beam.CurveSize1 = s, -s
	end
	for _, f in ipairs(ctx.fx) do f(ctx, dt, t, st) end
end

-- =============================================================================================================
-- SHARED PIECES
-- =============================================================================================================
local FACE = "rbxasset://textures/face.png"
local function glowAt(ctx, a, size, col, base, amp, speed, o)
	if not a then return end
	local s = sprite(ctx, { img = U("glow"), az = a[1], el = a[2], R = (o and o.R) or 900, size = size, color = col, trans = base, sky = not (o and o.fixed), bright = (o and o.bright) or 1.6 })
	table.insert(ctx.fx, function(_, _, t)
		if s.off then s.im.ImageTransparency = 1 return end
		s.im.ImageTransparency = math.clamp(base + amp * math.sin(t * speed + s.ph) * (o and o.flick and (0.6 + 0.4 * math.sin(t * 13 + s.ph)) or 1), 0, 1)
	end)
	return s
end
local function twinkles(ctx, rng, n, col, el0, el1, s0, s1)
	n = math.floor(n * (hi(ctx) and 1 or 0.6))
	local list = {}
	for _ = 1, n do
		local s = sprite(ctx, { img = U("star4"), az = rnd(rng, -180, 180), el = rnd(rng, el0, el1), R = 900, size = rnd(rng, s0, s1), color = col, trans = 0.3, sky = true, bright = 2 })
		s.sp = rnd(rng, 0.5, 1.8)
		table.insert(list, s)
	end
	table.insert(ctx.fx, function(_, _, t)
		for _, s in ipairs(list) do
			local k = (0.5 + 0.5 * math.sin(t * s.sp + s.ph)) ^ 3
			s.im.ImageTransparency = 0.85 - 0.8 * k
			local z = s.size * (0.7 + 0.45 * k)
			s.g.Size = UDim2.fromScale(z, z)
		end
	end)
	return list
end
local function floaters(ctx, rng, n, mk, o)
	n = math.floor(n * (hi(ctx) and 1 or 0.6))
	for _ = 1, n do
		local parts, rel = mk(rng)
		float(ctx, parts, rel, { az = rnd(rng, -180, 180), el = rnd(rng, o.el[1], o.el[2]), R = rnd(rng, o.R[1], o.R[2]), drift = rnd(rng, -1, 1) * (o.drift or 0.5),
			spin = Vector3.new(rnd(rng, -0.08, 0.08), rnd(rng, -0.15, 0.15), rnd(rng, -0.06, 0.06)) * (o.spin or 1), bob = o.bob or 3 })
	end
end
local function chains(ctx, list, o)
	for i, c in ipairs(list) do
		if i <= 2 or hi(ctx) then chain(ctx, { c[1], c[2] }, { c[3], c[4] }, { color = o.color, w = o.w, sag = c[5] or o.sag, emit = o.emit, link = o.link, sway = o.sway }) end
	end
end
local function glitch(ctx, cols, gap)
	table.insert(ctx.fx, function(c, dt, _, st)
		st.g = (st.g or rnd(Random.new(), gap[1], gap[2])) - dt
		if st.g > 0 or not (c.cc and c.cc.Parent) then return end
		st.g = gap[1] + math.random() * (gap[2] - gap[1])
		local cc, tint0, sat0 = c.cc, c.cc.TintColor, c.cc.Saturation
		for i = 1, math.random(2, 4) do
			task.delay((i - 1) * 0.06, function() if cc.Parent then cc.TintColor = cols[math.random(1, #cols)] cc.Saturation = 0.6 end end)
		end
		task.delay(0.28, function() if cc.Parent then cc.TintColor = tint0 cc.Saturation = sat0 end end)
	end)
end
local function lightning(ctx, col, gap, k)
	table.insert(ctx.fx, function(c, dt, _, st)
		st.l = (st.l or gap[1]) - dt
		if st.l > 0 then return end
		st.l = gap[1] + math.random() * (gap[2] - gap[1])
		bolt(c, math.random() * 360 - 180, col)
		flash(c, k)
		if math.random() < 0.4 then task.delay(0.35, function() if c.dome.Parent then bolt(c, math.random() * 360 - 180, col) end end) end
	end)
end
local function butterflies(ctx, col, rate, size, emit)
	return emitter(ctx, { tex = U("butterfly"), flip = true, box = Vector3.new(240, 70, 240), off = Vector3.new(0, 26, 0), rate = rate,
		life = NumberRange.new(9, 15), speed = NumberRange.new(2, 5), size = NumberSequence.new(size or 2), color = ColorSequence.new(col),
		emit = emit or 0.3, rotSpeed = NumberRange.new(-12, 12), accel = Vector3.new(0.4, 0.15, 0.2), drag = 0.3,
		trans = NS({ 0, 1, 0.1, 0, 0.9, 0, 1, 1 }) })
end
-- big butterflies far off in the sky, flapping (flipbook frames) and drifting with the painting
local function skyButterflies(ctx, rng, n, col)
	n = math.floor(n * (hi(ctx) and 1 or 0.5))
	local list = {}
	for _ = 1, n do
		local s = sprite(ctx, { img = U("butterfly"), az = rnd(rng, -180, 180), el = rnd(rng, 12, 55), R = 650, size = rnd(rng, 22, 44), color = col, sky = false, rect = Vector2.new(256, 256), bright = 1.6 })
		s.fr = rnd(rng, 7, 11) s.dz = rnd(rng, -2.5, 2.5) s.de = rnd(rng, -0.6, 0.6)
		table.insert(list, s)
	end
	table.insert(ctx.fx, function(_, dt, t)
		for _, s in ipairs(list) do
			local f = math.floor(t * s.fr + s.ph * 3) % 4
			s.im.ImageRectOffset = Vector2.new((f % 2) * 256, math.floor(f / 2) * 256)
			s.az += s.dz * dt
			s.el = math.clamp(s.el + s.de * dt * math.sin(t * 0.2 + s.ph), 8, 60)
		end
	end)
end
-- glowing eyes that open, blink and close at their own pace
local function eyes(ctx, rng, n, col, el0, el1, s0, s1)
	n = math.floor(n * (hi(ctx) and 1 or 0.6))
	local list = {}
	for _ = 1, n do
		local s = sprite(ctx, { img = U("eyes"), az = rnd(rng, -180, 180), el = rnd(rng, el0, el1), R = 900, size = rnd(rng, s0, s1), color = col, sky = true, rect = Vector2.new(256, 256), bright = 2.2, rot = rnd(rng, -14, 14) })
		s.next = rnd(rng, 0.5, 6) s.b = -1
		table.insert(list, s)
	end
	local seq = { 1, 2, 2, 3, 0 }
	table.insert(ctx.fx, function(_, dt)
		for _, s in ipairs(list) do
			if s.b < 0 then
				s.next -= dt
				if s.next <= 0 then s.b = 0 end
			else
				s.b += dt
				local i = math.floor(s.b / 0.05) + 1
				local f = seq[math.min(i, #seq)]
				s.im.ImageRectOffset = Vector2.new((f % 2) * 256, math.floor(f / 2) * 256)
				if i > #seq then s.b = -1 s.next = 1.5 + math.random() * 7 end
			end
		end
	end)
end
local function beamColumn(ctx, a, col, w, o)
	if not a then return end
	local O = origin(ctx)
	local top = newPart(ctx, { CFrame = CFrame.new(O + dir(a[1], math.min(a[2] + 30, 85)) * 700) })
	local bot = newPart(ctx, { CFrame = CFrame.new(O + dir(a[1], -2) * 520) })
	local a0 = Instance.new("Attachment") a0.Parent = top local a1 = Instance.new("Attachment") a1.Parent = bot
	local bm = Instance.new("Beam")
	bm.Attachment0, bm.Attachment1 = a0, a1
	bm.Texture = U("beam") or ""
	bm.TextureMode = Enum.TextureMode.Stretch
	bm.Width0, bm.Width1 = w, w * (o and o.taper or 0.6)
	bm.LightEmission, bm.LightInfluence, bm.Brightness = 1, 0, o and o.bright or 3
	bm.Color = ColorSequence.new(col)
	bm.Transparency = NS({ 0, 0.15, 0.7, 0.3, 1, 1 })
	bm.FaceCamera = true
	bm.Parent = top
	table.insert(ctx.fx, function(_, _, t) bm.Brightness = (o and o.bright or 3) * (0.75 + 0.25 * math.sin(t * 1.1)) end)
	return bm
end

-- =============================================================================================================
-- THE KILLERS
-- =============================================================================================================
local KILL = {}

KILL.guest666 = { fog = 0.22, spin = 0.9, clouds = { 0.42, 0.55, c3(150, 34, 34) }, weather = { "ash", c3(255, 120, 100), 20 },
	build = function(ctx, m, rng)
		chains(ctx, { { -70, 34, 30, 50, 80 }, { 10, 22, 125, 38, 60 }, { 150, 42, 250, 28, 90 }, { 205, 20, 300, 46, 70 }, { -150, 30, -95, 52, 50 } }, { color = c3(34, 8, 9), w = 4.6 })
		floaters(ctx, rng, 8, function(r)
			local s = rnd(r, 9, 15)
			return { block(ctx, Vector3.new(s, s * 1.55, s * 0.16), c3(22, 5, 5), Enum.Material.Slate, { face = FACE, faceCol = c3(255, 200, 200), faceT = 0.15 }) }, { CFrame.identity }
		end, { el = { 16, 55 }, R = { 260, 400 }, drift = 0.6, bob = 4 })
		glowAt(ctx, m.anchors.moon, 430, c3(255, 40, 36), 0.55, 0.16, 0.8)
		twinkles(ctx, rng, 10, c3(255, 120, 110), 25, 75, 18, 34)
	end }

KILL.sanic = { fog = 0.2, spin = 0.5, clouds = { 0.35, 0.5, c3(120, 12, 22) }, weather = { "embers", c3(255, 36, 40), 16 },
	build = function(ctx, m, rng)
		glowAt(ctx, m.anchors.eyeL, 80, c3(255, 30, 30), 0.25, 0.35, 1.9, { flick = true })
		glowAt(ctx, m.anchors.eyeR, 80, c3(255, 30, 30), 0.25, 0.35, 1.9, { flick = true })
		glowAt(ctx, m.anchors.moon, 330, c3(255, 34, 44), 0.5, 0.15, 0.7)
		glitch(ctx, { c3(255, 70, 70), c3(90, 140, 255), c3(255, 255, 255) }, { 5, 11 })
	end }

KILL["1x1x1x1"] = { fog = 0.2, spin = 0.6, clouds = { 0.4, 0.6, c3(30, 130, 55) }, weather = { "motes", c3(120, 255, 160), 22 },
	build = function(ctx, m, rng)
		floaters(ctx, rng, 14, function(r)
			local s = rnd(r, 8, 30)
			return { block(ctx, Vector3.new(s, s, s), c3(5, 9, 5), Enum.Material.SmoothPlastic, { edge = c3(50, 255, 120), edgeW = 0.32 }) }, { CFrame.identity }
		end, { el = { 8, 58 }, R = { 220, 420 }, drift = 0.5, bob = 5 })
		chains(ctx, { { -40, 50, 60, 30, 70 }, { 120, 26, 220, 44, 60 }, { -160, 40, -80, 22, 50 } }, { color = c3(14, 45, 18), w = 4.2, emit = 0.15 })
		glowAt(ctx, m.anchors.one, 300, c3(60, 255, 120), 0.6, 0.18, 1.0)
		emitter(ctx, { tex = U("square"), rate = 12, box = Vector3.new(200, 4, 200), off = Vector3.new(0, -10, 0), life = NumberRange.new(5, 8), speed = NumberRange.new(3, 6),
			spread = Vector2.new(10, 10), size = NS({ 0, 0.6, 1, 0 }), color = ColorSequence.new(c3(70, 255, 130)), emit = 1, rotSpeed = NumberRange.new(-60, 60) })
		glitch(ctx, { c3(80, 255, 140), c3(255, 255, 255), c3(20, 60, 30) }, { 4, 9 })
	end }

KILL.bloxwatch = { fog = 0.16, spin = 0.25, clouds = { 0.28, 0.45, c3(210, 170, 90) }, weather = { "motes", c3(255, 210, 120), 18 },
	build = function(ctx, m, rng)
		eyes(ctx, rng, 34, c3(255, 205, 95), 6, 72, 26, 58)
		twinkles(ctx, rng, 24, c3(255, 220, 150), 5, 80, 30, 70)
		glowAt(ctx, m.anchors.star, 400, c3(255, 210, 120), 0.5, 0.15, 0.6)
	end }

KILL.doombringer = { fog = 0.24, spin = 0.3, clouds = { 0.5, 0.65, c3(85, 85, 96) }, weather = { "ash", c3(200, 200, 210), 18 },
	build = function(ctx, m, rng)
		local n = hi(ctx) and 5 or 3
		for i = 1, n do
			local L = rnd(rng, 50, 90)
			local s = rnd(rng, 10, 16)
			local cp, cr = cage(ctx, s, c3(26, 24, 28))
			local anchor = newPart(ctx, { Name = "CageAnchor" })
			local parts, rel = { anchor }, { CFrame.identity }
			for j, p in ipairs(cp) do table.insert(parts, p) table.insert(rel, CFrame.new(0, -L, 0) * cr[j]) end
			float(ctx, parts, rel, { az = (i / n) * 360 + rnd(rng, -20, 20), el = rnd(rng, 40, 58), R = rnd(rng, 240, 330), drift = rnd(rng, -0.3, 0.3), bob = 1, swing = { rnd(rng, 0.35, 0.6), rnd(rng, 0.06, 0.12) } })
			local a0 = Instance.new("Attachment") a0.Parent = anchor
			local a1 = Instance.new("Attachment") a1.Parent = cp[#cp]
			local bm = Instance.new("Beam")
			bm.Attachment0, bm.Attachment1 = a0, a1
			bm.Texture = U("chain") or "" bm.TextureMode = Enum.TextureMode.Static bm.TextureLength = 7
			bm.Width0, bm.Width1 = 3.5, 3.5 bm.Color = ColorSequence.new(c3(30, 28, 32)) bm.LightInfluence = 0 bm.FaceCamera = true
			bm.Parent = anchor
		end
		chains(ctx, { { -60, 30, 40, 48, 60 }, { 100, 36, 200, 24, 70 }, { -170, 44, -110, 26, 50 } }, { color = c3(24, 22, 26), w = 4.6 })
		floaters(ctx, rng, 10, function(r)
			local s = rnd(r, 3, 8)
			return { block(ctx, Vector3.new(s, s, s * 0.6), c3(20, 19, 22), Enum.Material.Slate) }, { CFrame.identity }
		end, { el = { 10, 60 }, R = { 200, 380 }, drift = 0.8, bob = 4, spin = 2 })
		beamColumn(ctx, m.anchors.beam, c3(255, 30, 40), 26, { taper = 0.8, bright = 3 })
		glowAt(ctx, m.anchors.moon, 360, c3(225, 225, 240), 0.6, 0.12, 0.6)
		lightning(ctx, c3(255, 50, 60), { 5, 12 }, 0.14)
	end }

KILL.ellernate = { fog = 0.2, spin = 0.2, clouds = { 0.35, 0.5, c3(255, 205, 150) }, weather = { "embers", c3(255, 190, 90), 40 },
	build = function(ctx, m, rng)
		ring(ctx, { radius = 260, height = 230, thick = 3.2, color = c3(255, 196, 96), speed = 0.025, tilt = CFrame.Angles(math.rad(4), 0, math.rad(-3)) })
		ring(ctx, { radius = 360, height = 170, thick = 3.8, color = c3(255, 170, 70), speed = -0.018, tilt = CFrame.Angles(math.rad(-3), 0, math.rad(2)) })
		if hi(ctx) then ring(ctx, { radius = 460, height = 110, thick = 4.4, color = c3(255, 150, 60), speed = 0.012 }) end
		floaters(ctx, rng, 12, function(r)
			local s = rnd(r, 10, 30)
			return { block(ctx, Vector3.new(s, s, s * 0.5), c3(42, 32, 26), Enum.Material.Slate, { edge = c3(255, 205, 130), edgeW = 0.25, edgeT = 0.45 }) }, { CFrame.identity }
		end, { el = { 6, 55 }, R = { 230, 420 }, drift = 0.3, bob = 4 })
		beamColumn(ctx, m.anchors.pillar, c3(255, 230, 170), 70, { taper = 0.35, bright = 2.5 })
		glowAt(ctx, m.anchors.crown, 520, c3(255, 232, 175), 0.38, 0.15, 0.5)
	end }

KILL.herobrine = { fog = 0.22, spin = 0.15, clouds = { 0.55, 0.7, c3(95, 100, 118) }, weather = { "ash", c3(215, 220, 235), 12 },
	build = function(ctx, m, rng)
		local L = glowAt(ctx, m.anchors.eyeL, 95, c3(235, 242, 255), 0.25, 0.2, 0.9)
		local R = glowAt(ctx, m.anchors.eyeR, 95, c3(235, 242, 255), 0.25, 0.2, 0.9)
		-- now and then the eyes go out, then come back
		table.insert(ctx.fx, function(_, dt, _, st)
			st.e = (st.e or 9) - dt
			if st.e > 0 then return end
			st.e = 8 + math.random() * 10
			for _, s in ipairs({ L, R }) do if s then s.off = true end end
			task.delay(0.35 + math.random() * 0.6, function() for _, s in ipairs({ L, R }) do if s then s.off = false end end end)
		end)
		glowAt(ctx, m.anchors.moon, 260, c3(215, 228, 255), 0.6, 0.1, 0.5)
		glowAt(ctx, m.anchors.window, 46, c3(255, 170, 80), 0.25, 0.25, 3, { flick = true })
		emitter(ctx, { tex = U("square"), rate = 10, box = Vector3.new(200, 4, 200), off = Vector3.new(0, 50, 0), life = NumberRange.new(8, 12), speed = NumberRange.new(1, 3),
			emitDir = Enum.NormalId.Bottom, spread = Vector2.new(25, 25), size = NumberSequence.new(0.35), color = ColorSequence.new(c3(215, 220, 235)), emit = 0.5, accel = Vector3.new(0.6, -0.4, 0.3) })
	end }

KILL.itrapped = { fog = 0.22, spin = 0.35, clouds = { 0.45, 0.6, c3(125, 155, 235) }, weather = { "snow", c3(230, 245, 255), 45 },
	build = function(ctx, m, rng)
		floaters(ctx, rng, 14, function(r)
			local h = rnd(r, 14, 40)
			return { block(ctx, Vector3.new(h * 0.35, h, h * 0.35), c3(120, 190, 255), Enum.Material.ForceField, { trans = 0, edge = c3(200, 235, 255), edgeW = 0.14, edgeT = 0.5 }) }, { CFrame.Angles(0, math.rad(45), math.rad(45)) }
		end, { el = { 8, 60 }, R = { 220, 420 }, drift = 0.35, bob = 4 })
		twinkles(ctx, rng, 20, c3(190, 225, 255), 10, 78, 22, 50)
		glowAt(ctx, m.anchors.crown, 520, c3(150, 205, 255), 0.55, 0.15, 0.5)
	end }

KILL.johndoe = { fog = 0.22, spin = 0.25, clouds = { 0.4, 0.6, c3(160, 22, 22) }, weather = { "embers", c3(255, 50, 50), 20 },
	build = function(ctx, m, rng)
		chains(ctx, { { -80, 24, 20, 44, 70 }, { 40, 30, 150, 22, 60 }, { 170, 40, 260, 30, 80 }, { -140, 20, -60, 40, 50 } }, { color = c3(30, 4, 5), w = 4.4 })
		local sq = {}
		floaters(ctx, rng, 10, function(r)
			local s = rnd(r, 6, 16)
			local p = block(ctx, Vector3.new(s, s, 0.4), c3(255, 32, 44), Enum.Material.Neon, { trans = 0.15 })
			table.insert(sq, p)
			return { p }, { CFrame.identity }
		end, { el = { 15, 60 }, R = { 260, 420 }, drift = 0.4, bob = 3, spin = 0.5 })
		table.insert(ctx.fx, function(_, _, t) for i, p in ipairs(sq) do p.Transparency = ((math.floor(t * 6 + i * 3.7) % 9) == 0) and 1 or 0.15 end end)
		twinkles(ctx, rng, 12, c3(255, 70, 70), 10, 70, 20, 40)
		glowAt(ctx, m.anchors.sun, 360, c3(255, 50, 50), 0.45, 0.2, 0.9)
		glitch(ctx, { c3(255, 40, 40), c3(255, 255, 255), c3(40, 0, 0) }, { 4, 10 })
	end }

KILL.slasher = { fog = 0.26, spin = 0.25, clouds = { 0.6, 0.75, c3(112, 116, 126) }, weather = { "rain", c3(175, 200, 220), 60 }, mistT = 0.15,
	build = function(ctx, m, rng)
		glowAt(ctx, m.anchors.moon, 280, c3(228, 232, 240), 0.6, 0.1, 0.5)
		glowAt(ctx, m.anchors.window, 34, c3(255, 40, 30), 0.2, 0.3, 4, { flick = true })
		lightning(ctx, c3(220, 235, 255), { 7, 15 }, 0.26)
	end }

KILL.rake = { fog = 0.26, spin = 0.12, clouds = { 0.5, 0.7, c3(92, 92, 98) }, weather = { "motes", c3(205, 210, 220), 8 }, mistT = 0.12, wind = Vector3.new(4, 0, 2),
	build = function(ctx, m, rng)
		glowAt(ctx, m.anchors.moon, 260, c3(222, 222, 228), 0.62, 0.1, 0.4)
		-- the creature's eyes catch the light now and then
		local a = m.anchors.eyes
		if a then
			local e = sprite(ctx, { img = U("glow"), az = a[1], el = a[2], R = 900, size = 22, color = c3(255, 255, 255), trans = 1, sky = true, bright = 2.5 })
			table.insert(ctx.fx, function(_, dt, _, st)
				st.r = (st.r or 6) - dt
				if st.r <= 0 then st.r = 6 + math.random() * 8 st.rg = 0.9 end
				st.rg = math.max(0, (st.rg or 0) - dt)
				e.im.ImageTransparency = 1 - math.clamp(st.rg / 0.9, 0, 1) * 0.9
			end)
		end
		glowAt(ctx, { 70, 2 }, 320, c3(150, 20, 20), 0.75, 0.08, 0.3, { fixed = true })
		glowAt(ctx, { 215, 3 }, 280, c3(130, 16, 16), 0.78, 0.08, 0.25, { fixed = true })
	end }

KILL.flowers = { fog = 0.2, spin = 0.3, clouds = { 0.45, 0.6, c3(205, 64, 64) }, wind = Vector3.new(6, 0, 3),
	build = function(ctx, m, rng)
		emitter(ctx, { tex = U("petal"), rate = 22, box = Vector3.new(220, 4, 220), off = Vector3.new(0, 45, 0), life = NumberRange.new(8, 12), speed = NumberRange.new(2, 4),
			emitDir = Enum.NormalId.Bottom, spread = Vector2.new(30, 30), size = NS({ 0, 0.7, 1, 0.9 }), color = ColorSequence.new(c3(120, 14, 20), c3(40, 4, 8)),
			emit = 0.05, lit = 0.3, accel = Vector3.new(2.5, -0.8, 1.2), rotSpeed = NumberRange.new(-90, 90), drag = 0.4 })
		glowAt(ctx, m.anchors.sun, 440, c3(255, 120, 110), 0.38, 0.12, 0.6)
	end }

KILL.noli = { fog = 0.2, spin = 0.0, clouds = { 0.35, 0.55, c3(62, 84, 210) }, weather = { "motes", c3(170, 180, 255), 20 },
	build = function(ctx, m, rng)
		local h = m.anchors.halo
		if h then
			local r = ring(ctx, { radius = 75, height = 0, thick = 5, color = c3(110, 140, 255), speed = 0.18, tilt = CFrame.Angles(math.rad(70), 0, 0), segs = 48 })
			r.offFn = function(c) return dir(skyAz(c, h[1]), h[2]) * 700 end
		end
		glowAt(ctx, m.anchors.face, 400, c3(80, 110, 255), 0.6, 0.15, 0.7)
		twinkles(ctx, rng, 26, c3(170, 190, 255), 10, 80, 24, 56)
	end }

KILL.solemn = { fog = 0.2, spin = 0.15, clouds = { 0.5, 0.6, c3(225, 225, 225) }, weather = { "motes", c3(255, 255, 255), 16 },
	build = function(ctx, m, rng)
		butterflies(ctx, c3(255, 255, 255), 8, 2.2, 0.45)
		butterflies(ctx, c3(14, 14, 16), 3, 2.4, 0)
		skyButterflies(ctx, rng, 10, c3(255, 255, 255))
		glowAt(ctx, m.anchors.moon, 420, c3(255, 255, 255), 0.45, 0.1, 0.5)
	end }

KILL.stalker = { fog = 0.28, spin = 0.0, clouds = { 0.5, 0.75, c3(70, 36, 36) }, weather = { "ash", c3(150, 140, 140), 14 }, mistT = 0.35,
	build = function(ctx, m, rng)
		for _, k in ipairs({ "lamp1", "lamp2", "lamp3" }) do
			local a = m.anchors[k]
			if a then searchlight(ctx, CAL.frontAz + a[1], a[2], { sweep = rnd(rng, 25, 40), lift = { a[2] + 8, a[2] + 45 }, speed = rnd(rng, 0.12, 0.22) }) end
		end
		local reds = {}
		for _ = 1, (hi(ctx) and 8 or 5) do
			table.insert(reds, sprite(ctx, { img = U("glow"), az = rnd(rng, -180, 180), el = rnd(rng, 6, 22), R = 600, size = 14, color = c3(255, 30, 24), trans = 0.2, bright = 2.5 }))
		end
		table.insert(ctx.fx, function(_, _, t) for i, s in ipairs(reds) do s.im.ImageTransparency = ((t * 0.9 + i * 0.37) % 1 < 0.5) and 0.1 or 0.85 end end)
	end }

KILL.zerix = { fog = 0.18, spin = 0.2, clouds = { 0.4, 0.55, c3(205, 205, 205) }, weather = { "motes", c3(255, 255, 255), 14 },
	build = function(ctx, m, rng)
		butterflies(ctx, c3(255, 255, 255), 6, 2, 0.45)
		butterflies(ctx, c3(10, 10, 12), 6, 2, 0)
		chains(ctx, { { -150, 40, -60, 26, 60 }, { -120, 22, -30, 48, 70 } }, { color = c3(235, 235, 240), w = 4.2, emit = 0.25 })
		chains(ctx, { { 30, 48, 120, 24, 70 }, { 60, 26, 150, 44, 60 } }, { color = c3(16, 16, 18), w = 4.6 })
		local h = m.anchors.halo
		if h then
			local r = ring(ctx, { radius = 110, height = 0, thick = 5.5, color = c3(255, 255, 255), speed = 0.12, tilt = CFrame.Angles(math.rad(65), 0, 0), segs = 56 })
			r.offFn = function(c) return dir(skyAz(c, h[1]), h[2]) * 720 end
		end
		twinkles(ctx, rng, 22, c3(255, 255, 255), 10, 75, 24, 60)
	end }

-- c00lkidd: the doodle wall surrounds the map -- walls all the way round and a low ceiling of tiles cut from
-- the reference, slowly turning, tiles flaring red
KILL.c00lkidd = { fog = 0.16, spin = 0, saturation = -0.1, tint = c3(255, 200, 200),
	build = function(ctx, m, rng)
		local atlas = U("doodles")
		if not atlas then return end
		local O = origin(ctx)
		local tiles = {}
		local function tile(cf, s)
			local p = newPart(ctx, { Size = Vector3.new(s, s, 0.2), CFrame = cf })
			local g = Instance.new("SurfaceGui")
			g.Face = Enum.NormalId.Front g.LightInfluence = 0 g.Brightness = 1.3
			g.SizingMode = Enum.SurfaceGuiSizingMode.FixedSize g.CanvasSize = Vector2.new(256, 256)
			g.Parent = p
			local im = Instance.new("ImageLabel")
			im.BackgroundTransparency = 1 im.Size = UDim2.fromScale(1, 1) im.Image = atlas
			local k = rng:NextInteger(0, 15)
			im.ImageRectSize = Vector2.new(252, 252) im.ImageRectOffset = Vector2.new((k % 4) * 256 + 2, math.floor(k / 4) * 256 + 2)
			im.Rotation = rng:NextInteger(-1, 1) * rnd(rng, 0, 6)
			im.Parent = g
			table.insert(tiles, im)
		end
		local R = 240
		local cols = hi(ctx) and 28 or 18
		local rows = hi(ctx) and 4 or 3
		for row = 0, rows - 1 do
			for c = 0, cols - 1 do
				local a = (c + (row % 2) * 0.5) / cols * math.pi * 2 + rnd(rng, -0.02, 0.02)
				local s = 2 * math.pi * R / cols * rnd(rng, 0.95, 1.12)
				local y = -8 + row * s * 0.98 + rnd(rng, -3, 3)
				local pos = O + Vector3.new(math.sin(a) * R, y, math.cos(a) * R)
				tile(CFrame.lookAt(pos, Vector3.new(O.X, pos.Y, O.Z)) * CFrame.Angles(0, 0, math.rad(rnd(rng, -5, 5))), s)
			end
		end
		local n = hi(ctx) and 6 or 4
		local size = (R * 2) / (2 * n + 1)
		for ix = -n, n do
			for iz = -n, n do
				local x, z = ix * size * 1.02, iz * size * 1.02
				local r = math.sqrt(x * x + z * z)
				if r < R * 1.05 then
					local y = 150 - (r / R) ^ 2 * 30 + rnd(rng, -3, 3)
					tile(CFrame.new(O + Vector3.new(x, y, z)) * CFrame.Angles(math.rad(-90), math.rad(rng:NextInteger(0, 3) * 90), 0) * CFrame.Angles(math.rad(rnd(rng, -6, 6)), 0, math.rad(rnd(rng, -6, 6))), size * rnd(rng, 0.96, 1.15))
				end
			end
		end
		table.insert(ctx.fx, function(c, dt, _, st)
			c.yaw = (c.yaw or 0) + dt * 0.01
			st.a = (st.a or 0) + dt
			if st.a < 0.12 then return end
			st.a = 0
			if st.last then st.last.ImageColor3 = Color3.new(1, 1, 1) end
			local im = tiles[math.random(1, #tiles)]
			im.ImageColor3 = c3(255, 110, 110)
			st.last = im
		end)
		glitch(ctx, { c3(255, 60, 60), c3(255, 255, 255) }, { 6, 12 })
	end }
Art.KILL = KILL

-- =============================================================================================================
-- SPEC
-- =============================================================================================================
local function lift(c, k, floor)
	return Color3.new(math.clamp(c.R * k + floor, 0, 1), math.clamp(c.G * k + floor, 0, 1), math.clamp(c.B * k + floor, 0, 1))
end
function Art.spec(key)
	local K = KILL[key]
	local faces, v3 = facesFor(key)
	if not faces then return nil end
	local m = M[key] or M.guest666
	K = K or {}
	local fog = m.hz:Lerp(m.mid, 0.35)
	local amb = lift(m.mid:Lerp(m.hz, 0.5), 1.4, 0.06)
	local build = function(ctx)
		ctx.sprites, ctx.chains, ctx.floaters, ctx.rings, ctx.lamps, ctx.mist, ctx.fx = {}, {}, {}, {}, {}, {}, {}
		ctx.boards = ctx.boards or {}
		local ok, err = pcall(mistBuild, ctx, lift(fog, 2.2, 0.04), { mistT = K.mistT, wispT = K.wispT })
		if not ok then warn("[LMSSkyArt] mist", err) end
		if v3 and K.build then
			local ok2, err2 = pcall(K.build, ctx, m, Random.new(#key * 131))
			if not ok2 then warn("[LMSSkyArt] " .. key, err2) end
		end
	end
	local ev = function(ctx, dt, st)
		if not ctx.sprites then return end
		for _, r in ipairs(ctx.rings) do if r.offFn then r.off = r.offFn(ctx) - Vector3.new(0, r.h, 0) end end
		local ok, err = pcall(tick, ctx, dt, st)
		if not ok and not st.warned then st.warned = true warn("[LMSSkyArt] tick", err) end
	end
	return {
		plain = true,
		faces = faces,
		celestial = false,
		stars = 0,
		density = K.fog or 0.2,
		offset = 0.12,
		haze = 1.3,
		glare = 0,
		atmColor = fog,
		decay = m.mid,
		tint = K.tint or Color3.new(1, 1, 1):Lerp(m.hz, 0.12),
		contrast = 0.12,
		saturation = K.saturation or 0.06,
		gradeBrightness = 0,
		clock = 14,
		brightness = 1.2,
		ambient = amb,
		outdoor = amb,
		exposure = 0,
		shiftTop = m.mid,
		shiftBottom = Color3.new(0, 0, 0),
		envDiffuse = 0.4,
		envSpecular = 0.4,
		spin = (v3 and K.spin) or 0.3,
		yaw0 = 0,
		clouds = v3 and K.clouds or nil,
		wind = K.wind,
		weather = K.weather,
		build = build,
		events = { ev },
	}
end
return Art
