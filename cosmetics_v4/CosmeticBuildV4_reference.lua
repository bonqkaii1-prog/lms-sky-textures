--[[
	Cosmetics v4 builder (CL 2026-11-21): rebuilds the 11 format-2 cosmetics from the Blender meshes
	(ServerStorage.CosmeticMeshLibV4, one MeshPart per piece, sized and textured with baked PBR + emissive maps).
	Every piece is placed from its Blender bounding centre (Roblox axes) inside an item frame, the item frame
	is placed on the limb, and the moving pieces get joints CosmeticFX drives.
]]
return function(F, LIB)
	local rgb, rad = F.rgb, math.rad
	local CF, V3 = CFrame.new, Vector3.new
	local out = {}

	-- clone a piece; `item` = CFrame of the item origin; `s` = uniform item scale
	local function piece(acc, key, item, s, name)
		local src = LIB:FindFirstChild(key)
		assert(src, "missing mesh " .. key)
		local p = src:Clone()
		p.Name = name or key:gsub("^%w+_", "")
		local c = p:GetAttribute("C")
		p.Size = p:GetAttribute("S") * s
		p.CFrame = item * CF(c * s)
		p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.Massless = true, false, false, false, true
		p.Parent = acc
		return p
	end
	local function setup(name, char, concept, view)
		local model, acc = F.cosmetic(name, char, concept)
		model:SetAttribute("RenderView", view)
		model:SetAttribute("Version", 4)
		return model, acc
	end
	local function sparks(part, col, rate, tex)
		return F.emitter(part, { name = "Embers", texture = tex or "rbxasset://textures/particles/sparkles_main.dds", color = ColorSequence.new(col),
			size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.06), NumberSequenceKeypoint.new(1, 0) }),
			transp = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(1, 1) }),
			life = NumberRange.new(0.6, 1.2), rate = rate or 4, speed = NumberRange.new(0.2, 0.6), spread = Vector2.new(180, 180), light = 1,
			accel = V3(0, 0.6, 0) })
	end

	------------------------------------------------------------------------------------------------ Executioner's Burden
	do
		local model, acc = setup("Executioner's Burden", "Doombringer", "Doombringer's colossal war hammer slung across the back: a waffled striking face, a hooked beak, rune panels burning red, a chain wound round the haft and a weighted length swinging free.", "Back")
		local torso = F.anchor(acc, "Torso")
		local s = 0.78
		local item = F.L("Torso", CF(0, -1.75, 0.78) * CFrame.Angles(0, math.pi, 0) * CFrame.Angles(0, 0, rad(-38)))
		local hub = F.hub(acc, "Sway", item)
		F.joint(torso, hub, item * CF(0, 2.2, 0), "Sway", { RotAmp = V3(1.2, 0, 1.6), RotSpeed = 1.1 })
		local body = piece(acc, "doom_HammerBody", item, s, "Hammer") F.weld(hub, body)
		local wound = piece(acc, "doom_ChainWound", item, s, "ChainWound") F.weld(hub, wound)
		local hang = piece(acc, "doom_ChainHang", item, s, "ChainHang")
		local top = item * CF(0, 2.35 * s, 0)
		local hh = F.hub(acc, "HangHub", top)
		F.joint(hub, hh, top, "ChainSwing", { RotAmp = V3(9, 0, 6), RotSpeed = 1.6, Phase = 0.7, MoveBoost = 2 })
		F.weld(hh, hang)
		local heat = F.part(acc, { name = "Heat", size = V3(0.6, 0.5, 0.2), cf = item * CF(0.26 * s, 4.43 * s, 0), transp = 1, shadow = false })
		F.weld(hub, heat)
		F.light(heat, rgb(255, 40, 20), 5, 0.9)
		sparks(heat, rgb(255, 70, 30), 3)
		out[#out + 1] = model
	end

	------------------------------------------------------------------------------------------------ Corrupted Crown
	do
		local model, acc = setup("Corrupted Crown", "1x1x1x1", "A crown of blackened iron split at the front, gothic blades (two snapped), plaques of glowing green code and voxel corruption erupting from the break -- floating above the head.", "Front")
		local head = F.anchor(acc, "Head")
		local s = 1.25
		-- hovers clear of the head: model front is -Y in Blender -> +Z in Roblox, so turn it to face the player's front
		local item = F.L("Head", CF(0, 0.95, 0) * CFrame.Angles(0, math.pi, 0) * CFrame.Angles(rad(-6), 0, 0))
		local hub = F.hub(acc, "Float", item * CF(0, 0.45 * s, 0))
		F.joint(head, hub, item * CF(0, 0.45 * s, 0), "Float", { PosAmp = V3(0, 0.14, 0), PosSpeed = 1.5, RotAmp = V3(5, 10, 5), RotSpeed = 0.7 })
		local body = piece(acc, "crown_CrownBody", item, s, "Crown") F.weld(hub, body)
		local cor = piece(acc, "crown_Corruption", item, s, "Corruption")
		F.joint(hub, cor, cor.CFrame, "Corrupt", { Mode = "Shift", PosAmp = V3(0.03, 0.05, 0.03), PosSpeed = 3, RotAmp = V3(3, 3, 3), RotSpeed = 2.5 })
		cor:SetAttribute("Glitch", true)
		cor:SetAttribute("GlitchColor", rgb(120, 255, 150))
		local glow = F.part(acc, { name = "Glow", size = V3(0.3, 0.3, 0.3), cf = cor.CFrame, transp = 1, shadow = false }) F.weld(hub, glow)
		F.light(glow, rgb(60, 255, 110), 6, 1.2)
		F.emitter(glow, { name = "Bits", texture = "rbxasset://textures/particles/sparkles_main.dds", color = ColorSequence.new(rgb(80, 255, 130)),
			size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.08), NumberSequenceKeypoint.new(1, 0) }), transp = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(1, 1) }),
			life = NumberRange.new(0.5, 1), rate = 6, speed = NumberRange.new(0.3, 0.8), spread = Vector2.new(60, 60), light = 1, accel = V3(0, 1, 0) })
		-- a faint green ring of light under the floating crown
		local under = F.part(acc, { name = "Under", size = V3(0.2, 0.2, 0.2), cf = item * CF(0, -0.05, 0), transp = 1, shadow = false }) F.weld(hub, under)
		F.light(under, rgb(40, 255, 90), 4, 0.6)
		out[#out + 1] = model
	end

	------------------------------------------------------------------------------------------------ Forgotten Relic
	do
		local model, acc = setup("Forgotten Relic", "John Doe", "An ancient eight-pointed sigil of charred iron, embers smouldering in its cracks, a ring of burning runes and a faceted crystal heart, hanging on a snapped chain before the chest.", "Front")
		local torso = F.anchor(acc, "Torso")
		local s = 0.78
		local item = F.L("Torso", CF(0, 0.25, -0.78) * CFrame.Angles(0, math.pi, 0))
		local top = item * CF(0, 1.27 * s, 0)
		local hub = F.hub(acc, "Swing", top)
		F.joint(torso, hub, top, "Swing", { RotAmp = V3(4, 3, 6), RotSpeed = 1.3, MoveBoost = 2 })
		local frame = piece(acc, "relic_SigilFrame", item, s, "Sigil") F.weld(hub, frame)
		local chain = piece(acc, "relic_SigilChain", item, s, "Chain") F.weld(hub, chain)
		local heart = piece(acc, "relic_SigilHeart", item, s, "Heart")
		F.joint(hub, heart, heart.CFrame, "HeartSpin", { RotAmp = V3(0, 0, 25), RotSpeed = 0.8, PosAmp = V3(0, 0, 0.02), PosSpeed = 2 })
		F.light(heart, rgb(255, 90, 30), 6, 1.1)
		sparks(heart, rgb(255, 120, 40), 4)
		out[#out + 1] = model
	end

	------------------------------------------------------------------------------------------------ Fractured Halo
	do
		local model, acc = setup("Fractured Halo", "Ellernate", "A halo of black obsidian shattered into crystal shards with thorns breaking out of them, crimson veins burning through, the pieces drifting apart and back.", "Front")
		local head = F.anchor(acc, "Head")
		local s = 0.82
		local item = F.L("Head", CF(0, 1.0, 0.05) * CFrame.Angles(rad(-10), 0, 0))
		local hub = F.hub(acc, "Hover", item)
		F.joint(head, hub, item, "Hover", { PosAmp = V3(0, 0.1, 0), PosSpeed = 1.2, RotAmp = V3(4, 0, 4), RotSpeed = 0.6 })
		local spin = F.hub(acc, "Spin", item)
		F.joint(hub, spin, item, "Spin", { Spin = V3(0, 14, 0) })
		for i = 1, 3 do
			local p = piece(acc, "halo_Shards" .. i, item, s, "Shards" .. i)
			F.joint(spin, p, p.CFrame, "Drift" .. i, { PosAmp = V3(0.05, 0.06, 0.05), PosSpeed = 0.9 + i * 0.2, Phase = i * 2.1, RotAmp = V3(2, 2, 2), RotSpeed = 0.8 })
		end
		local chips = piece(acc, "halo_Chips", item, s, "Chips")
		F.joint(spin, chips, item, "Chips", { Spin = V3(0, -30, 0) })
		local core = F.part(acc, { name = "Core", size = V3(0.2, 0.2, 0.2), cf = item, transp = 1, shadow = false }) F.weld(hub, core)
		F.light(core, rgb(255, 30, 40), 6, 0.8)
		out[#out + 1] = model
	end

	------------------------------------------------------------------------------------------------ Unholy Eye
	do
		local model, acc = setup("Unholy Eye", "Noli", "Noli's watching eye: a slit-pupilled violet iris held in a clawed ring of obsidian shards, shadow tendrils curling from its rim. It floats over the shoulder and turns to stare.", "Back")
		local torso = F.anchor(acc, "Torso")
		local s = 0.82
		local center = F.L("Torso", CF(1.65, 1.85, 0.95) * CFrame.Angles(0, rad(25), 0))
		local float = F.hub(acc, "Float", center)
		F.joint(torso, float, center, "Float", { RotAmp = V3(4, 0, 5), RotSpeed = 0.9, PosAmp = V3(0.03, 0.14, 0.04), PosSpeed = 1.3 })
		-- Blender front (-Y) -> Roblox +Z: turn so the eye looks backwards by default (it is a back cosmetic)
		local item = center
		local ring = piece(acc, "eye_EyeRing", item, s, "Ring")
		F.joint(float, ring, center, "RingSpin", { RotAmp = V3(0, 0, 14), RotSpeed = 0.35 })
		local ten = piece(acc, "eye_Tendrils", item, s, "Tendrils")
		F.joint(float, ten, center, "TendrilSway", { RotAmp = V3(5, 5, 9), RotSpeed = 1.3, Phase = 1.2 })
		local look = F.hub(acc, "EyeHub", center)
		F.joint(float, look, center, "Look", { Mode = "Look" })
		local eye = piece(acc, "eye_Eye", item, s, "Eye") F.weld(look, eye)
		F.light(eye, rgb(160, 60, 255), 6, 0.9)
		F.emitter(eye, { name = "Wisps", texture = "rbxasset://textures/particles/smoke_main.dds", color = ColorSequence.new(rgb(70, 20, 120), rgb(10, 0, 20)),
			size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.25), NumberSequenceKeypoint.new(1, 0.7) }), transp = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.75), NumberSequenceKeypoint.new(1, 1) }),
			life = NumberRange.new(1.2, 2), rate = 3, speed = NumberRange.new(0.1, 0.25), rotSpeed = NumberRange.new(-40, 40), accel = V3(0, 0.2, 0), light = 0.3 })
		out[#out + 1] = model
	end

	------------------------------------------------------------------------------------------------ Damned Tail
	do
		local model, acc = setup("Damned Tail", "Guest 666", "Guest 666's demonic tail: dark crimson hide under overlapping blackened plates and side spines, ending in a barbed obsidian spade.", "Back")
		local torso = F.anchor(acc, "Torso")
		local N = 9
		local SEGROT = CFrame.fromMatrix(Vector3.zero, V3(0, 1, 0), V3(0, 0, -1))
		local base = F.L("Torso", CF(0, -0.78, 0.48))
		local root = F.hub(acc, "Root", base) F.weld(torso, root)
		local prev, pos, last = root, base.Position, nil
		for i = 1, N do
			local t = (i - 1) / (N - 1)
			local theta = rad(128 - 90 * t)
			local yaw = rad(10 * math.sin(t * 3))
			local k = 1.25 - 0.62 * t                      -- thickness falloff
			local len = 0.5 * k * 0.92
			local jointCF = CF(pos) * CFrame.Angles(0, yaw, 0) * CFrame.Angles(theta, 0, 0)
			local hub = F.hub(acc, "Seg" .. i, jointCF)
			F.joint(prev, hub, jointCF, "Tail" .. i, { Mode = "Tail", RotAmp = V3(3.6 + 0.6 * i, 8.6 + 1.6 * i, 2), RotSpeed = 1.9, Phase = -0.5 * i, MoveBoost = 1.9 })
			-- the Blender segment runs along +X with its plates on +Z(up) -> Roblox +X, plates +Y; aim X up the joint
			local seg = LIB.tail_TailSeg:Clone()
			seg.Name = "Hide"
			seg.Size = seg:GetAttribute("S") * k
			seg.CFrame = jointCF * CF(0, len / 2, 0) * SEGROT
			seg.Anchored, seg.CanCollide, seg.CanQuery, seg.CanTouch, seg.Massless = true, false, false, false, true
			seg.Parent = acc
			F.weld(hub, seg)
			prev = hub
			pos = (jointCF * CF(0, len, 0)).Position
			last = { hub = hub, cf = jointCF * CF(0, len, 0), k = k }
		end
		local tip = LIB.tail_TailTip:Clone()
		tip.Name = "Tip"
		tip.Size = tip:GetAttribute("S") * 1.05
		tip.CFrame = last.cf * CF(0, 0.33, 0) * SEGROT
		tip.Anchored, tip.CanCollide, tip.CanQuery, tip.CanTouch, tip.Massless = true, false, false, false, true
		tip.Parent = acc
		F.weld(last.hub, tip)
		F.light(tip, rgb(255, 40, 30), 4, 0.7)
		sparks(tip, rgb(255, 60, 40), 3)
		out[#out + 1] = model
	end

	------------------------------------------------------------------------------------------------ Final Catch
	do
		local model, acc = setup("Final Catch", "ITrapped", "ITrapped's rusted bear trap chained to the back: a riveted cross base, leaf springs, a trigger pan and two toothed jaws that twitch and now and then snap shut.", "Back")
		local torso = F.anchor(acc, "Torso")
		local s = 1.05
		-- standing up against the back: Blender top (+Z) -> Roblox +Y; rotate so the jaws face away from the body
		local item = F.L("Torso", CF(0, 0.05, 0.53)) * CFrame.Angles(rad(90), 0, 0)
		local hub = F.hub(acc, "Hang", item)
		F.joint(torso, hub, F.L("Torso", CF(0, 1, 0.6)), "Hang", { RotAmp = V3(3, 0, 4), RotSpeed = 1.2, MoveBoost = 2 })
		local base = piece(acc, "trap_TrapBase", item, s, "Base") F.weld(hub, base)
		local chain = piece(acc, "trap_Chain", item, s, "Chain") F.weld(hub, chain)
		local hinge = item * CF(0, 0.09 * s, 0)
		for k = 0, 1 do
			local jhub = F.hub(acc, "JawHinge" .. k, hinge)
			-- jaw rests at 48 deg open; the snap closes it toward upright
			F.joint(hub, jhub, hinge, "Jaw" .. k, { Mode = "Jaw", Side = (k == 0) and 1 or -1, JawAmp = 38 })
			local j = piece(acc, "trap_Jaw", item, s, "Jaw" .. k)
			if k == 1 then j.CFrame = hinge * CFrame.Angles(0, math.pi, 0) * hinge:ToObjectSpace(j.CFrame) end
			F.weld(jhub, j)
		end
		out[#out + 1] = model
	end

	------------------------------------------------------------------------------------------------ Predator's Claws
	do
		local model, acc = setup("Predator's Claws", "The Rake", "The Rake's claws: long jointed fingers of grimy bone ending in black hooked talons, swollen knuckles and tendons, bound at the wrist in filthy, bloodied bandages.", "Front")
		local s = 1.0
		for _, side in ipairs({ { "Right Arm", "R" }, { "Left Arm", "L" } }) do
			local limb, k = side[1], side[2]
			local arm = F.anchor(acc, limb)
			-- Blender arm: hand end at z=0, arm up to z=2, centred on x=0 (R) / x=-1.6 (L); Roblox arm centre is 1 stud above its bottom
			local ox = (k == "L") and -1.6 or 0
			local item = F.L(limb, CF(0, -1, 0) * CFrame.Angles(0, math.pi, 0) * CF(-ox * s, 0, 0))
			local hand = piece(acc, "claws_ClawHand" .. k, item, s, "Claw" .. k)
			local wrist = item * CF(0, 0.05, 0)
			local hh = F.hub(acc, "Flex" .. k, wrist)
			F.joint(arm, hh, wrist, "Flex" .. k, { RotAmp = V3(5, 0, 2), RotSpeed = 1.4, Phase = (k == "L") and 1.5 or 0, MoveBoost = 1.6 })
			F.weld(hh, hand)
			local band = piece(acc, "claws_Bandage" .. k, item, s, "Bandage" .. k) F.weld(arm, band)
		end
		out[#out + 1] = model
	end

	------------------------------------------------------------------------------------------------ Butcher's Trophy
	do
		local model, acc = setup("Butcher's Trophy", "Jane Doe", "Jane Doe's chipped, blood-stained bearded axe slung across the back: a polished but notched edge, a dark haft bound in filthy bandages and a torn rag knotted under the head.", "Back")
		local torso = F.anchor(acc, "Torso")
		local s = 0.82
		local item = F.L("Torso", CF(-0.45, -1.45, 0.62) * CFrame.Angles(0, math.pi, 0) * CFrame.Angles(0, 0, rad(-32)))
		local hub = F.hub(acc, "Sway", item)
		F.joint(torso, hub, item * CF(0, 1.6, 0), "Sway", { RotAmp = V3(1.2, 0, 1.5), RotSpeed = 1.2 })
		local axe = piece(acc, "axe_Axe", item, s, "Axe") F.weld(hub, axe)
		local knot = item * CF(0.07 * s, 2.4 * s, 0)
		local rh = F.hub(acc, "RagHub", knot)
		F.joint(hub, rh, knot, "Rag", { RotAmp = V3(12, 8, 10), RotSpeed = 2.4, MoveBoost = 2.5 })
		local rag = piece(acc, "axe_Rag", item, s, "Rag") F.weld(rh, rag)
		out[#out + 1] = model
	end

	------------------------------------------------------------------------------------------------ Hacker's Arsenal
	do
		local model, acc = setup("Hacker's Arsenal", "C00lkid", "C00lkid's twin black-steel daggers crossed on the back in a leather harness: serrated spines, burning red edges and grips etched with corrupted code, glitch cubes buzzing round the pommels.", "Back")
		local torso = F.anchor(acc, "Torso")
		local s = 1.0
		-- harness: Blender plane XZ (front -Y at y=0.6) -> Roblox: plate faces +Z (outwards from the back)
		local hitem = F.L("Torso", CF(0, 0, 0.02)) * CFrame.Angles(0, math.pi, 0)
		local harness = piece(acc, "daggers_Harness", hitem, s * 0.86, "Harness") F.weld(torso, harness)
		for k = 0, 1 do
			local sgn = k == 0 and 1 or -1
			local d = LIB.daggers_Dagger:Clone()
			d.Name = "Dagger" .. k
			d.Size = d:GetAttribute("S") * s
			local cf = F.L("Torso", CF(0, 0.15, 0.68)) * CFrame.Angles(0, 0, sgn * rad(38)) * CFrame.Angles(0, (k == 0) and 0 or math.pi, 0) * CF(0, 0.15, 0)
			d.CFrame = cf
			d.Anchored, d.CanCollide, d.CanQuery, d.CanTouch, d.Massless = true, false, false, false, true
			d.Parent = acc
			F.joint(torso, d, cf * CF(0, -0.6, 0), "Rattle" .. k, { RotAmp = V3(1.5, 0, 1.5), RotSpeed = 1.3, Phase = k * 1.7, MoveBoost = 2 })
			F.light(d, rgb(255, 30, 20), 3, 0.5)
		end
		out[#out + 1] = model
	end

	------------------------------------------------------------------------------------------------ Administrator's Toolkit
	do
		local model, acc = setup("Administrator's Toolkit", "Builderman", "Builderman's battered red steel toolbox strapped to the back: chipped paint, dented ribs and corner guards, the lid bouncing on its hinge over a wrench, screwdriver, claw hammer and tape measure, sparks spitting from inside.", "Back")
		local torso = F.anchor(acc, "Torso")
		local s = 1.05
		-- the box sits on the lower back, its long side across the back; its back (+Y in Blender, strap side) against the body
		local item = F.L("Torso", CF(0, -0.95, 0.88))
		local hub = F.hub(acc, "Bob", item)
		F.joint(torso, hub, item, "Bob", { PosAmp = V3(0, 0.03, 0), PosSpeed = 2.2, RotAmp = V3(1.5, 0, 1.5), RotSpeed = 1.6, MoveBoost = 2 })
		local box = piece(acc, "toolbox_Box", item, s, "Box") F.weld(hub, box)
		local straps = piece(acc, "toolbox_Straps", item, s, "Straps") F.weld(hub, straps)
		local tools = piece(acc, "toolbox_Tools", item, s, "Tools")
		F.joint(hub, tools, tools.CFrame, "Rattle", { RotAmp = V3(2, 2, 2), RotSpeed = 3.5, MoveBoost = 3 })
		local hinge = item * CF(0, 0.55 * s, -0.31 * s)
		local lh = F.hub(acc, "LidHinge", hinge)
		F.joint(hub, lh, hinge, "Lid", { RotAmp = V3(8, 0, 0), RotSpeed = 2.6, MoveBoost = 2.5 })
		local lid = piece(acc, "toolbox_Lid", item, s, "Lid") F.weld(lh, lid)
		local spark = F.part(acc, { name = "Sparks", size = V3(0.8, 0.1, 0.4), cf = item * CF(0, 0.6 * s, 0), transp = 1, shadow = false }) F.weld(hub, spark)
		F.emitter(spark, { name = "Sparks", texture = "rbxasset://textures/particles/sparkles_main.dds", color = ColorSequence.new(rgb(255, 210, 90)),
			size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.07), NumberSequenceKeypoint.new(1, 0) }), transp = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(1, 1) }),
			life = NumberRange.new(0.25, 0.5), rate = 5, speed = NumberRange.new(2, 4), spread = Vector2.new(35, 35), light = 1, accel = V3(0, -8, 0) })
		out[#out + 1] = model
	end

	return out
end
