-- ChessSceneClient: Touka and James playing an endless game of chess in the cabin.
--
-- Everything here runs on each client and is driven by the shared server clock (workspace:GetServerTimeNow()),
-- so every player sees the same move at the same moment, and someone who walks in mid-game sees the board
-- exactly as it stands. Nothing replicates: the server only holds the scene (ChessScene model) and the two rigs.
--
-- The game: ChessScene.Loop (ModuleScript) holds a middlegame position and a sequence of legal, capture-free
-- maneuvering moves that brings the position back to itself, so the match runs forever without ever resetting.
--
-- The animation is fully procedural:
--   * body  : lean from the hips, twist, roll and a little slide, each on its own critically damped spring,
--             plus breathing; legs stay planted on the chair whatever the torso does
--   * head  : looks at whatever matters (the piece being moved, the board, the opponent, the clock, a nearby
--             player) on a spring, with small saccades
--   * arms  : rest poses (hands on the table edge, on the lap, arms folded) are springs; reaching, lifting,
--             carrying, setting down and pressing the clock are minimum-jerk paths solved with arm IK, and the
--             torso leans / twists to make every square reachable. A held piece rides the actual hand.
-- Turn structure: think (scan the board, sometimes reach for a piece and change one's mind) -> reach -> grasp
-- -> lift -> carry in an arc -> set down -> let go -> press the clock -> settle back. The opponent watches,
-- shifts in their chair, folds their arms or leans in while waiting.

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local LP = Players.LocalPlayer
local camera = workspace.CurrentCamera

local V3, CF = Vector3.new, CFrame.new
local sin, cos, abs, min, max, clamp, sqrt, rad, pi = math.sin, math.cos, math.abs, math.min, math.max, math.clamp, math.sqrt, math.rad, math.pi

-- ---------------------------------------------------------------------------------------------------------------
-- scene
-- ---------------------------------------------------------------------------------------------------------------
local function findScene()
	for _ = 1, 600 do
		local s = workspace:FindFirstChild("ChessScene", true)
		if s and s:IsA("Model") then return s end
		task.wait(0.5)
	end
	return nil
end
local scene = findScene()
if not scene then return end

local Loop = require(scene:WaitForChild("Loop") :: ModuleScript)
local base = (scene:WaitForChild("Base") :: BasePart).CFrame -- floor point under the table centre; +Z = white's side
local SQ: number = scene:GetAttribute("SQ") or 0.21
local BOARD_Y: number = scene:GetAttribute("BoardY") or 2.56 -- tile top, scene local
local piecesFolder = scene:WaitForChild("Pieces")

local function L(x: number, y: number, z: number): Vector3 return base:PointToWorldSpace(V3(x, y, z)) end
local UP = base.UpVector

-- square "e4" -> scene-local point on the tile top
local function sqLocal(sq: string): Vector3
	local f = string.byte(sq, 1) - 97
	local r = tonumber(string.sub(sq, 2, 2)) :: number - 1
	return V3((f - 3.5) * SQ, BOARD_Y, -(r - 3.5) * SQ)
end
local function sqWorld(sq: string): Vector3 return base:PointToWorldSpace(sqLocal(sq)) end

-- ---------------------------------------------------------------------------------------------------------------
-- deterministic hashing (integer, so every client agrees)
-- ---------------------------------------------------------------------------------------------------------------
local function hash(n: number): number
	local x = bit32.band(math.floor(n) * 2654435761 + 1013904223, 0xFFFFFFFF)
	x = bit32.bxor(x, bit32.rshift(x, 15))
	x = bit32.band(x * 2246822519, 0xFFFFFFFF)
	x = bit32.bxor(x, bit32.rshift(x, 13))
	x = bit32.band(x * 3266489917, 0xFFFFFFFF)
	x = bit32.bxor(x, bit32.rshift(x, 16))
	return x / 4294967296
end

-- ---------------------------------------------------------------------------------------------------------------
-- curves
-- ---------------------------------------------------------------------------------------------------------------
local function mj(t: number): number -- minimum jerk 0..1
	t = clamp(t, 0, 1)
	return t * t * t * (10 + t * (-15 + 6 * t))
end
local function seg(t: number, a: number, b: number): number return mj((t - a) / (b - a)) end

-- ---------------------------------------------------------------------------------------------------------------
-- pieces & game replay
-- ---------------------------------------------------------------------------------------------------------------
type Piece = { part: BasePart, kind: string, color: string, h: number, offset: CFrame, sq: string }
local pieces: { [string]: Piece } = {} -- keyed by starting square
for _, p in ipairs(piecesFolder:GetChildren()) do
	if p:IsA("BasePart") then
		local sq = p:GetAttribute("Square") :: string
		local kind = p:GetAttribute("Kind") :: string
		local color = p:GetAttribute("Color") :: string
		-- the piece's own placement relative to its square point (mesh centre offset + facing), captured once
		local off = CF(sqWorld(sq)):ToObjectSpace(p.CFrame)
		pieces[sq] = { part = p, kind = kind, color = color, h = p:GetAttribute("Height") :: number or 0.2, offset = off, sq = sq }
	end
end

-- replay: board[k] = map square -> piece id (the piece's starting square) before ply k
local moves: { string } = Loop.moves
local N = #moves
local boards: { { [string]: string } } = {}
do
	local b: { [string]: string } = {}
	for sq in pairs(pieces) do b[sq] = sq end
	for k = 1, N do
		local snap = table.clone(b)
		boards[k] = snap
		local m = moves[k]
		local from, to = string.sub(m, 1, 2), string.sub(m, 3, 4)
		b[to] = b[from]
		b[from] = nil
	end
	boards[N + 1] = b
end

-- per-ply timing (fixed for every lap of the loop, so the loop period is constant)
local T_ACTION_BASE = 0.95 + 1.15 + 0.12 + 0.35 + 1.75 + 0.45 -- reach/grasp, (carry varies), release, retreat, clock, settle
type Ply = { t0: number, think: number, carry: number, dur: number, from: string, to: string, white: boolean,
	hes: boolean, hesAt: number, hesSq: string?, idleSeed: number }
local plies: { Ply } = {}
local period = 0
for k = 1, N do
	local m = moves[k]
	local from, to = string.sub(m, 1, 2), string.sub(m, 3, 4)
	local df = abs(string.byte(from, 1) - string.byte(to, 1))
	local dr = abs(tonumber(string.sub(from, 2, 2)) :: number - (tonumber(string.sub(to, 2, 2)) :: number))
	local dist = sqrt(df * df + dr * dr)
	local think = 2.6 + 6.2 * hash(k * 7 + 1) + (hash(k * 13 + 5) < 0.15 and 4 or 0)
	local carry = clamp(0.55 + 0.17 * dist, 0.6, 1.4)
	local hes = think > 5.2 and hash(k * 31 + 2) < 0.5
	local white = (k % 2 == 1) -- the loop starts with white to move
	-- a piece of the mover's own to hesitate over (not the one they end up moving)
	local hesSq: string? = nil
	if hes then
		local own = {}
		for sq, id in pairs(boards[k]) do
			if pieces[id].color == (white and "w" or "b") and sq ~= from and pieces[id].kind ~= "K" and pieces[id].kind ~= "P" then table.insert(own, sq) end
		end
		table.sort(own)
		if #own > 0 then hesSq = own[1 + math.floor(hash(k * 53 + 9) * #own)] else hes = false end
	end
	local dur = think + T_ACTION_BASE + carry
	plies[k] = { t0 = period, think = think, carry = carry, dur = dur, from = from, to = to, white = white,
		hes = hes, hesAt = think * (0.25 + 0.2 * hash(k * 17 + 3)), hesSq = hesSq, idleSeed = k }
	period += dur
end

-- ---------------------------------------------------------------------------------------------------------------
-- springs
-- ---------------------------------------------------------------------------------------------------------------
type Spring = { x: number, v: number, w: number }
local function spring(x: number, w: number): Spring return { x = x, v = 0, w = w } end
local function step(s: Spring, target: number, dt: number)
	local w = s.w
	local a = w * w * (target - s.x) - 2 * w * s.v
	s.v += a * dt
	s.x += s.v * dt
end
type VSpring = { x: Vector3, v: Vector3, w: number }
local function vstep(s: VSpring, target: Vector3, dt: number)
	local w = s.w
	local a = (target - s.x) * (w * w) - s.v * (2 * w)
	s.v += a * dt
	s.x += s.v * dt
end

-- ---------------------------------------------------------------------------------------------------------------
-- characters
-- ---------------------------------------------------------------------------------------------------------------
type Arm = { side: number, motor: Motor6D, part: BasePart, pivotL: Vector3, tipL: Vector3, u: Vector3,
	p: VSpring, stretch: Spring, driven: boolean, drivenPrev: Vector3?, held: Piece?, heldOff: Vector3 }
type Char = {
	model: Model, white: boolean, seat: CFrame, torso: BasePart, head: BasePart,
	root: Motor6D, neck: Motor6D, hipR: Motor6D, hipL: Motor6D, legR: BasePart, legL: BasePart,
	armR: Arm, armL: Arm, clockArm: Arm,
	lean: Spring, twist: Spring, roll: Spring, slide: Spring, rise: Spring,
	yaw: Spring, pitch: Spring, tilt: Spring,
	phase: number,
}

local function motorOf(model: Model, name: string): Motor6D
	local m = model:FindFirstChild(name, true)
	assert(m and m:IsA("Motor6D"), "missing motor " .. name)
	return m
end

local function makeArm(model: Model, side: number): Arm
	local motor = motorOf(model, side > 0 and "Right Shoulder" or "Left Shoulder")
	local part = motor.Part1 :: BasePart
	local pivotL = V3(-0.5 * side, 0.5, 0)
	local tipL = V3(0, -1, 0)
	return { side = side, motor = motor, part = part, pivotL = pivotL, tipL = tipL, u = tipL - pivotL,
		p = { x = Vector3.zero, v = Vector3.zero, w = 7 }, stretch = spring(0, 14), driven = false, drivenPrev = nil, held = nil, heldOff = Vector3.zero }
end

local function makeChar(model: Model, white: boolean, seat: CFrame): Char
	local torso = model:WaitForChild("Torso") :: BasePart
	local head = model:WaitForChild("Head") :: BasePart
	local root = motorOf(model, "RootJoint")
	local c: Char = {
		model = model, white = white, seat = seat, torso = torso, head = head,
		root = root, neck = motorOf(model, "Neck"), hipR = motorOf(model, "Right Hip"), hipL = motorOf(model, "Left Hip"),
		legR = motorOf(model, "Right Hip").Part1 :: BasePart, legL = motorOf(model, "Left Hip").Part1 :: BasePart,
		armR = makeArm(model, 1), armL = makeArm(model, -1), clockArm = nil :: any,
		lean = spring(0.12, 6), twist = spring(0, 6), roll = spring(0, 5), slide = spring(0, 6), rise = spring(0, 6),
		yaw = spring(0, 9), pitch = spring(-0.3, 9), tilt = spring(0, 5),
		phase = white and 0 or 1.7,
	}
	-- the clock sits at scene +X: white (facing -Z) reaches it with the right hand, black with the left
	c.clockArm = white and c.armR or c.armL
	return c
end

-- pose model ------------------------------------------------------------------------------------------------
local function torsoCF(c: Char): CFrame
	return c.seat * CF(0, c.rise.x, -c.slide.x) * CFrame.Angles(0, c.twist.x, 0) * CFrame.Angles(-c.lean.x, 0, c.roll.x) * CF(0, 1, 0)
end
local function shoulderPos(c: Char, a: Arm, tcf: CFrame): Vector3
	return tcf:PointToWorldSpace(V3(a.side, 0.5, 0))
end

-- the body pose that lets arm `a` put its hand on world point T: twist toward the far shoulder, lean from the hips
local LEAN_MIN, LEAN_MAX = rad(-4), rad(34)
local function solveBody(c: Char, a: Arm, T: Vector3): (number, number)
	local lp = c.seat:PointToObjectSpace(T)
	local fwd = -lp.Z
	local lateral = lp.X * a.side -- + = toward this arm's side
	local tw = a.side * clamp((fwd - 1.1) * 0.22 + clamp(-lateral, -0.6, 0.6) * 0.25, -0.05, 0.36)
	local L = a.u.Magnitude
	local lo, hi = LEAN_MIN, LEAN_MAX
	local function dist(l: number): number
		local tcf = c.seat * CFrame.Angles(0, tw, 0) * CFrame.Angles(-l, 0, 0) * CF(0, 1, 0)
		return (T - tcf:PointToWorldSpace(V3(a.side, 0.5, 0))).Magnitude
	end
	if dist(lo) <= L then return lo, tw end
	if dist(hi) >= L then return hi, tw end
	for _ = 1, 14 do
		local m = (lo + hi) / 2
		if dist(m) > L then lo = m else hi = m end
	end
	return (lo + hi) / 2, tw
end

-- arm world CFrame pointing pivot->tip at world point P, with `stretch` slid along the arm
local function armCF(c: Char, a: Arm, tcf: CFrame, P: Vector3, stretch: number): CFrame
	local S = shoulderPos(c, a, tcf)
	local d = P - S
	if d.Magnitude < 1e-3 then d = -tcf.UpVector end
	d = d.Unit
	local R0 = tcf.Rotation -- hanging: arm axes = torso axes
	local u0 = R0:VectorToWorldSpace(a.u.Unit)
	local axis = u0:Cross(d)
	local s = axis.Magnitude
	local R = R0
	if s > 1e-5 then
		local ang = math.atan2(s, u0:Dot(d))
		R = CFrame.fromAxisAngle(axis / s, ang) * R0
	elseif u0:Dot(d) < 0 then
		R = CFrame.fromAxisAngle(tcf.RightVector, pi) * R0
	end
	return CF(S + d * stretch) * R * CF(-a.pivotL)
end

local function tipOf(a: Arm, acf: CFrame): Vector3 return acf:PointToWorldSpace(a.tipL) end

-- motor: make Part1 sit at world cframe W given Part0 at world cframe P0
local function drive(m: Motor6D, P0: CFrame, W: CFrame)
	m.Transform = (P0 * m.C0):Inverse() * W * m.C1
end

-- rest poses ----------------------------------------------------------------------------------------------
-- returns world targets for both hands (+ body offsets) for a named idle pose
type Rest = { r: Vector3, l: Vector3, lean: number, roll: number, slide: number }
local function restPose(c: Char, name: string, tcf: CFrame): Rest
	local seat = c.seat
	if name == "table" then
		-- forearms-free R6: hands rest on the table edge in front of them
		return { r = seat:PointToWorldSpace(V3(0.62, 0.66, -1.12)), l = seat:PointToWorldSpace(V3(-0.62, 0.66, -1.12)), lean = rad(9), roll = 0, slide = 0.05 }
	elseif name == "focus" then
		return { r = seat:PointToWorldSpace(V3(0.55, 0.67, -1.16)), l = seat:PointToWorldSpace(V3(-0.6, 0.66, -1.1)), lean = rad(15), roll = 0, slide = 0.08 }
	elseif name == "lap" then
		return { r = tcf:PointToWorldSpace(V3(0.62, -0.5, -1.05)), l = tcf:PointToWorldSpace(V3(-0.62, -0.5, -1.05)), lean = rad(3), roll = 0, slide = 0 }
	elseif name == "folded" then
		return { r = tcf:PointToWorldSpace(V3(-0.45, -0.35, -0.95)), l = tcf:PointToWorldSpace(V3(0.45, -0.22, -1.0)), lean = rad(-3), roll = rad(1.5), slide = -0.02 }
	elseif name == "mixed" then
		return { r = seat:PointToWorldSpace(V3(0.6, 0.66, -1.1)), l = tcf:PointToWorldSpace(V3(-0.6, -0.5, -1.0)), lean = rad(7), roll = rad(-2), slide = 0.03 }
	end
	return { r = tcf:PointToWorldSpace(V3(0.62, -0.5, -1.05)), l = tcf:PointToWorldSpace(V3(-0.62, -0.5, -1.05)), lean = rad(3), roll = 0, slide = 0 }
end

-- ---------------------------------------------------------------------------------------------------------------
-- build characters
-- ---------------------------------------------------------------------------------------------------------------
local function seatCF(name: string): CFrame
	return (scene:WaitForChild(name) :: BasePart).CFrame
end
local whiteModel = scene:GetAttribute("White") and workspace:WaitForChild(scene:GetAttribute("White") :: string, 30) :: Model
local blackModel = scene:GetAttribute("Black") and workspace:WaitForChild(scene:GetAttribute("Black") :: string, 30) :: Model
if not (whiteModel and blackModel) then return end
local W = makeChar(whiteModel, true, seatCF("SeatW"))
local B = makeChar(blackModel, false, seatCF("SeatB"))
local chars = { W, B }

-- clock
local clock = scene:FindFirstChild("Clock")
local btnW = scene:FindFirstChild("ClockBtnW") :: BasePart?
local btnB = scene:FindFirstChild("ClockBtnB") :: BasePart?
local btnWRest = btnW and btnW.CFrame
local btnBRest = btnB and btnB.CFrame
local handsW = { scene:FindFirstChild("HandMinW") :: BasePart?, scene:FindFirstChild("HandHrW") :: BasePart? }
local handsB = { scene:FindFirstChild("HandMinB") :: BasePart?, scene:FindFirstChild("HandHrB") :: BasePart? }
local dialW = scene:FindFirstChild("DialW") :: BasePart?
local dialB = scene:FindFirstChild("DialB") :: BasePart?
local BTN_TRAVEL = 0.028
local function btnTop(white: boolean): Vector3
	local b = white and btnW or btnB
	if not b then return L(1.1, 2.84, white and 0.14 or -0.14) end
	return (white and btnWRest or btnBRest :: CFrame).Position + UP * (b.Size.Y / 2)
end

-- think-time accounting for the clock faces: seconds each side has spent thinking up to time t (absolute)
local thinkW, thinkB = 0, 0
for k = 1, N do if plies[k].white then thinkW += plies[k].dur else thinkB += plies[k].dur end end
local function clockSpent(t: number, white: boolean): number
	local lap = math.floor(t / period)
	local u = t - lap * period
	local total = lap * (white and thinkW or thinkB)
	for k = 1, N do
		local p = plies[k]
		if p.white == white then
			if u >= p.t0 + p.dur then total += p.dur
			elseif u > p.t0 then total += u - p.t0 end
		end
	end
	return total
end

-- ---------------------------------------------------------------------------------------------------------------
-- per-frame evaluation
-- ---------------------------------------------------------------------------------------------------------------
local function pieceTop(id: string): number return pieces[id].h end

-- where should each hand be, and what is it holding, at play time u inside ply k?
type ArmCmd = { arm: Arm, P: Vector3, hold: string? }
local captured: { [string]: Vector3 } = {} -- segment start points (continuity), keyed by segment id

local function restTip(c: Char, a: Arm, rest: Rest): Vector3 return a.side > 0 and rest.r or rest.l end

local function evaluate(t: number, dt: number)
	local lap = math.floor(t / period)
	local u = t - lap * period
	local k = 1
	for i = 1, N do
		if u < plies[i].t0 + plies[i].dur then k = i break end
	end
	local ply = plies[k]
	local lt = u - ply.t0 -- time inside this ply
	local board = boards[k]
	local mover = ply.white and W or B
	local other = ply.white and B or W
	local moverId = board[ply.from]
	local mp = pieces[moverId]

	-- ---- idle pose choice (deterministic per ~7 s window, per character)
	local function idleName(c: Char): string
		local win = math.floor((t + c.phase * 3) / 7.5)
		local h = hash(win * 97 + (c.white and 11 or 23))
		if c == mover and lt < ply.think then return h < 0.55 and "focus" or (h < 0.85 and "table" or "mixed") end
		if h < 0.28 then return "folded" elseif h < 0.55 then return "lap" elseif h < 0.8 then return "table" end
		return "mixed"
	end

	-- ---- board pieces: everything at its square for this ply, except the one in hand
	local A = ply.think
	local tReachEnd = A + 0.95          -- hand above / at the piece
	local tGrasp = A + 1.12             -- fingers close (piece follows the hand from here)
	local tLiftEnd = tGrasp + 0.05
	local tCarryEnd = tLiftEnd + 1.1 + ply.carry -- lift + carry + lower
	local tRelease = tCarryEnd + 0.06
	local tRetreatEnd = tRelease + 0.4
	local tClock0 = tRetreatEnd - 0.1
	local tPress = tClock0 + 0.62
	local tClockUp = tPress + 0.14
	local tClockEnd = tClockUp + 0.9
	local tMoveArmHome = tRetreatEnd + 0.95

	for sq, id in pairs(board) do
		if id ~= moverId then
			local pc = pieces[id]
			pc.part.CFrame = CF(sqWorld(sq)) * pc.offset
		end
	end

	-- ---- which arm moves the piece (the one on the side of the move)
	local function sideOf(c: Char, sq: string): number
		local lp = c.seat:PointToObjectSpace(sqWorld(sq))
		return lp.X
	end
	local lat = (sideOf(mover, ply.from) + sideOf(mover, ply.to)) / 2
	local moveArm = lat >= -0.05 and mover.armR or mover.armL
	local cmds: { ArmCmd } = {}
	local srcTop = sqWorld(ply.from) + UP * pieceTop(moverId)
	local dstTop = sqWorld(ply.to) + UP * pieceTop(moverId)
	local inHand = false

	local function start(id: string, fallback: Vector3): Vector3
		local s = captured[id]
		if not s then s = fallback captured[id] = s end
		return s
	end

	local moverRest = restPose(mover, idleName(mover), torsoCF(mover))
	local moveRest = restTip(mover, moveArm, moverRest)

	if lt < A then
		-- thinking; maybe a hesitant reach toward another piece
		if ply.hes and ply.hesSq then
			local h0 = ply.hesAt
			local hs = lt - h0
			if hs >= 0 and hs < 2.5 then
				local hid = board[ply.hesSq]
				local over = sqWorld(ply.hesSq) + UP * (pieceTop(hid) + 0.16)
				local arm = (sideOf(mover, ply.hesSq) >= -0.05) and mover.armR or mover.armL
				local p0 = start("hes" .. k .. lap, arm.p.x)
				local P
				if hs < 1.0 then
					local s = mj(hs / 1.0)
					P = p0:Lerp(over, s) + UP * (0.12 * sin(pi * s))
				elseif hs < 1.5 then
					P = over + UP * (0.012 * sin((hs - 1.0) * 19)) -- a moment's hover
				else
					local rest = restTip(mover, arm, moverRest)
					local s = mj((hs - 1.5) / 1.0)
					P = over:Lerp(rest, s) + UP * (0.06 * sin(pi * s))
				end
				table.insert(cmds, { arm = arm, P = P })
			end
		end
	elseif lt < tRetreatEnd + 0.95 then
		-- reach -> grasp
		local P: Vector3
		if lt < tGrasp then
			local p0 = start("reach" .. k .. lap, moveArm.p.x)
			local tt = (lt - A) / (tGrasp - A)
			local hz = mj(tt / 0.82)
			local horiz = p0:Lerp(srcTop, hz)
			local hTarget = srcTop.Y + 0.2
			local y = p0.Y + (hTarget - p0.Y) * mj(tt / 0.72) - 0.2 * seg(tt, 0.62, 1.0)
			P = V3(horiz.X, y, horiz.Z)
			-- (scene floors are level, so Y works as "up")
		elseif lt < tCarryEnd then
			-- lift, carry in an arc, lower
			local tt = (lt - tGrasp) / (tCarryEnd - tGrasp)
			local horiz = srcTop:Lerp(dstTop, seg(tt, 0.16, 0.86))
			local lift = 0.2 + 0.05 * clamp(ply.carry - 0.6, 0, 1)
			local up = mj(tt / 0.3) * (1 - seg(tt, 0.72, 1.0))
			P = horiz + UP * (lift * up)
			inHand = true
		elseif lt < tRelease then
			P = dstTop
			inHand = true
		elseif lt < tRetreatEnd then
			local s = mj((lt - tRelease) / (tRetreatEnd - tRelease))
			local back = (mover.seat.Position - dstTop) * V3(1, 0, 1)
			P = dstTop + UP * (0.18 * s) + (back.Magnitude > 0 and back.Unit * (0.1 * s) or Vector3.zero)
		else
			local p0 = dstTop + UP * 0.18 + ((mover.seat.Position - dstTop) * V3(1, 0, 1)).Unit * 0.1
			local s = mj((lt - tRetreatEnd) / 0.95)
			P = p0:Lerp(moveRest, s) + UP * (0.05 * sin(pi * s))
		end
		if not (moveArm == mover.clockArm and lt >= tClock0) then
			table.insert(cmds, { arm = moveArm, P = P, hold = inHand and moverId or nil })
		end
	end

	-- the clock press (after the move), with the clock-side hand
	local pressed = false
	if lt >= tClock0 and lt < tClockEnd then
		local arm = mover.clockArm
		local top = btnTop(mover.white)
		local above = top + UP * 0.12
		local p0
		if arm == moveArm then
			p0 = dstTop + UP * 0.18
		else
			p0 = start("clk" .. k .. lap, arm.p.x)
		end
		local P
		if lt < tPress - 0.12 then
			local s = mj((lt - tClock0) / (tPress - 0.12 - tClock0))
			P = p0:Lerp(above, s) + UP * (0.08 * sin(pi * s))
		elseif lt < tPress then
			P = above:Lerp(top - UP * BTN_TRAVEL, mj((lt - (tPress - 0.12)) / 0.12))
		elseif lt < tClockUp then
			P = (top - UP * BTN_TRAVEL):Lerp(above, mj((lt - tPress) / (tClockUp - tPress)))
		else
			local rest = restTip(mover, arm, moverRest)
			local s = mj((lt - tClockUp) / (tClockEnd - tClockUp))
			P = above:Lerp(rest, s) + UP * (0.05 * sin(pi * s))
		end
		table.insert(cmds, { arm = arm, P = P })
		pressed = lt >= tPress - 0.02
	end

	-- the moving piece
	if not inHand then
		local done = lt >= tRelease
		mp.part.CFrame = CF(sqWorld(done and ply.to or ply.from)) * mp.offset
	end

	-- clock buttons: the side that has just moved has its button down
	if btnW and btnB and btnWRest and btnBRest then
		local wDown: number
		if ply.white then
			-- white to move: black's button is down until white presses
			wDown = pressed and mj((lt - (tPress - 0.02)) / 0.06) or 0
		else
			wDown = pressed and 1 - mj((lt - (tPress - 0.02)) / 0.06) or 1
		end
		btnW.CFrame = btnWRest - UP * (BTN_TRAVEL * wDown)
		btnB.CFrame = btnBRest - UP * (BTN_TRAVEL * (1 - wDown))
	end
	-- clock hands
	for _, side in ipairs({ true, false }) do
		local hands = side and handsW or handsB
		local dial = side and dialW or dialB
		if dial and hands[1] then
			local spent = clockSpent(t, side) + 18 * 60 * (side and 1 or 1.13)
			local minA = -(spent / 3600) * 2 * pi
			local hrA = -(spent / 43200) * 2 * pi
			local dcf = dial.CFrame
			-- dial: LookVector = face normal, UpVector = 12 o'clock
			hands[1].CFrame = dcf * CFrame.Angles(0, 0, minA) * CF(0, hands[1].Size.Y * 0.4, -0.006)
			if hands[2] then hands[2].CFrame = dcf * CFrame.Angles(0, 0, hrA) * CF(0, hands[2].Size.Y * 0.4, -0.004) end
		end
	end

	-- ---- per character: body, head, arms
	local now = t
	for _, c in ipairs(chars) do
		local isMover = c == mover
		local tcfNow = torsoCF(c)
		local rest = restPose(c, idleName(c), tcfNow)
		-- which arms are driven this frame
		local drivenR, drivenL = nil :: ArmCmd?, nil :: ArmCmd?
		if isMover then
			for _, cmd in ipairs(cmds) do
				if cmd.arm == c.armR then drivenR = cmd elseif cmd.arm == c.armL then drivenL = cmd end
			end
		end
		-- body targets
		local leanT, twistT = rest.lean, 0
		local rollT, slideT = rest.roll, rest.slide
		local reachCmd = drivenR or drivenL
		if reachCmd then
			local l, tw = solveBody(c, reachCmd.arm, reachCmd.P)
			leanT, twistT = max(l, rad(4)), tw
			slideT = 0.06 + 0.1 * clamp((l - rad(10)) / rad(20), 0, 1)
			rollT = 0
		elseif not isMover then
			-- waiting: small weight shifts
			twistT = 0.05 * sin(now * 0.31 + c.phase) + 0.03 * sin(now * 0.17 + 2)
			rollT += 0.02 * sin(now * 0.23 + c.phase * 2)
		else
			-- thinking: lean in a little more, slow sway
			twistT = 0.06 * sin(now * 0.4 + c.phase)
		end
		-- breathing
		local br = sin(now * (2 * pi / 3.9) + c.phase)
		c.lean.w = reachCmd and 9 or 4.5
		c.twist.w = reachCmd and 8 or 4
		step(c.lean, leanT + 0.012 * br, dt)
		step(c.twist, twistT, dt)
		step(c.roll, rollT, dt)
		step(c.slide, slideT, dt)
		step(c.rise, 0.012 * br, dt)

		local tcf = torsoCF(c)

		-- head: look target
		local look: Vector3
		if isMover then
			if reachCmd then
				look = reachCmd.P - UP * 0.05
			elseif lt < A then
				-- scan the board: pick squares on a short rhythm, glance at the opponent now and then
				local win = math.floor(lt / 1.35)
				local h = hash(k * 131 + win * 7 + (c.white and 1 or 2))
				if h < 0.12 then
					look = other.head.Position
				elseif h < 0.18 and btnW then
					look = btnTop(c.white) - UP * 0.1
				else
					local f = math.floor(hash(win * 19 + k) * 8)
					local r = math.floor(hash(win * 23 + k * 3) * 6) + (c.white and 0 or 2)
					look = sqWorld(string.char(97 + f) .. tostring(1 + r)) + UP * 0.1
				end
			else
				look = sqWorld(ply.to)
			end
		else
			-- the opponent follows the hand while the mover acts, otherwise rests their eyes on the board / looks around
			local otherCmd = cmds[1]
			if otherCmd and lt >= A - 0.3 then
				look = otherCmd.P - UP * 0.05
			else
				local win = math.floor((now + c.phase) / 2.6)
				local h = hash(win * 41 + (c.white and 5 or 9))
				if h < 0.22 then
					look = mover.head.Position
				elseif h < 0.32 then
					-- a nearby player catches their eye
					local cam = camera.CFrame.Position
					if (cam - c.head.Position).Magnitude < 22 then look = cam else look = L(0, BOARD_Y, 0) end
				else
					local f = math.floor(hash(win * 3 + 1) * 8)
					local r = math.floor(hash(win * 5 + 2) * 8)
					look = sqWorld(string.char(97 + f) .. tostring(1 + r))
				end
			end
		end
		-- head yaw / pitch relative to the torso
		local neckCF = tcf * CF(0, 1, 0)
		local d = neckCF:VectorToObjectSpace(look - (neckCF * CF(0, 0.5, 0)).Position)
		local yawT = clamp(math.atan2(-d.X, -d.Z), -1.1, 1.1)
		local pitchT = clamp(math.atan2(d.Y, sqrt(d.X * d.X + d.Z * d.Z)), -0.85, 0.45)
		step(c.yaw, yawT, dt)
		step(c.pitch, pitchT, dt)
		step(c.tilt, 0.04 * sin(now * 0.37 + c.phase) + (isMover and lt < A and 0.05 or 0), dt)
		local headCF = neckCF * CFrame.Angles(0, c.yaw.x, 0) * CFrame.Angles(c.pitch.x, 0, c.tilt.x) * CF(0, 0.5, 0)

		-- arms
		for _, a in ipairs({ c.armR, c.armL }) do
			local cmd = (a == c.armR) and drivenR or drivenL
			if cmd then
				local P = cmd.P
				a.p.v = dt > 0 and (P - a.p.x) / dt or Vector3.zero
				a.p.x = P
				a.driven = true
			else
				local target = restTip(c, a, rest)
				-- tapping fingers when hands rest on the table
				if not isMover and (idleName(c) == "table") then
					target += UP * (0.02 * max(0, sin(now * 6.5 + a.side)) ^ 6)
				end
				a.p.w = a.driven and 9 or 5
				vstep(a.p, target, dt)
				a.driven = false
			end
			local S = shoulderPos(c, a, tcf)
			local need = (a.p.x - S).Magnitude - a.u.Magnitude
			step(a.stretch, cmd and clamp(need, -0.38, 0.32) or 0, dt)
			if cmd then a.stretch.x = clamp(need, -0.38, 0.32) a.stretch.v = 0 end
			local acf = armCF(c, a, tcf, a.p.x, a.stretch.x)
			drive(a.motor, tcf, acf)
			if cmd and cmd.hold then
				local pc = pieces[cmd.hold]
				local tip = tipOf(a, acf)
				pc.part.CFrame = CF(tip - UP * pc.h) * pc.offset
			end
		end

		-- torso, head, legs
		drive(c.root, c.seat * CF(0, 1, 0), tcf)
		drive(c.neck, tcf, headCF)
		local legsBase = c.seat * CFrame.Angles(pi / 2, 0, 0)
		local sway = 0.025 * sin(now * 0.5 + c.phase)
		drive(c.hipR, tcf, CF(c.seat:PointToWorldSpace(V3(0.5, 0, -1))) * legsBase.Rotation * CFrame.Angles(0, 0, sway))
		drive(c.hipL, tcf, CF(c.seat:PointToWorldSpace(V3(-0.5, 0, -1))) * legsBase.Rotation * CFrame.Angles(0, 0, -sway * 0.7))
	end

	-- forget stale continuity points
	if hash(math.floor(t)) < 0.02 then
		for key in pairs(captured) do
			if not string.find(key, tostring(k) .. tostring(lap), 1, true) then captured[key] = nil end
		end
	end
end

-- ---------------------------------------------------------------------------------------------------------------
-- run
-- ---------------------------------------------------------------------------------------------------------------
-- seed the springs at the current pose so nothing snaps on the first frame
do
	local t0 = workspace:GetServerTimeNow()
	for _, c in ipairs(chars) do
		local tcf = torsoCF(c)
		local r = restPose(c, "table", tcf)
		c.armR.p.x = r.r
		c.armL.p.x = r.l
	end
	for _ = 1, 90 do evaluate(t0, 1 / 30) end
end

local ACTIVE_RANGE = 160
local lastT = workspace:GetServerTimeNow()
RunService:BindToRenderStep("ChessScene", Enum.RenderPriority.Character.Value + 1, function(dt)
	local t = workspace:GetServerTimeNow()
	local cam = camera.CFrame.Position
	if (cam - base.Position).Magnitude > ACTIVE_RANGE then lastT = t return end
	dt = clamp(t - lastT, 0, 1 / 20)
	lastT = t
	local ok, err = pcall(evaluate, t, max(dt, 1 / 240))
	if not ok then warn("[ChessScene]", err) end
end)
