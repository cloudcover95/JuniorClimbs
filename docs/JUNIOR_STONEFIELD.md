# JuniorStoneField

**The product space** inside JuniorClimbs for outdoor boulders *and* indoor gym programs.
POS, coaching, BitNet IoT remain; this is the climbing-knowledge + teaching surface.

## Access covenant (private land)

We do **not** publish private-land boulders, pins, topos, or beta unless the landowner
(or a person with authority to speak for them) has given **word of consent** that the
location may be uploaded and made available to the public.

- Public land / OSMP / USFS / Jeffco Open Space / state park: allowed, still follow posted rules.
- Private land / ranch / inholding: **blocked** until `owner_consent=true` and a named attester.
- Unknown tenure: treated as private until clarified.
- Gym walls: `visibility=gym_internal` by default (camps and classes), not a public crag dump.

Full text: `GET /stonefield/terms`

## Product map

| Name | Role |
|------|------|
| JuniorStoneField | Field / area (outdoor *or* a gym as a field) |
| JuniorBoulderNode | Outdoor boulder **or** indoor wall volume |
| JuniorProblem | Line |
| JuniorTopoMesh | Photo / overlay |
| JuniorRouteSetLedger | Gym set or outdoor FA ledger |
| JuniorAccessPledge | Consent + visibility on every outdoor submit |
| JuniorGymProgram | Season / camp / team / after-school |
| JuniorClassBlock | A class on the calendar |
| JuniorStudyPlan | Curriculum: problems + sets a group studies |
| JuniorBetaBoard / ForumMesh | Discussion |
| JuniorRegionSphere / NavMesh | 360 + offline nav |
| JuniorSourceLedger | Licensed community packs |

## Gym use

A local gym can:
- Present current sets on walls (`/stonefield/routesets?venue=gym`)
- Plan a camp week as a **JuniorGymProgram** with **ClassBlocks**
- Attach indoor problems + outdoor field trips to a **StudyPlan**
- Keep camp material `gym_internal` so it does not leak as a public guidebook

## Endpoints

- `/stonefield/terms`
- `/stonefield/app` — product hub
- `/stonefield/fields|nodes|problems|topos|routesets|board`
- `/stonefield/programs` `/stonefield/classes` `/stonefield/study-plans`
- `/source/*` `/arena` `/nav/*` `/forum/*`
