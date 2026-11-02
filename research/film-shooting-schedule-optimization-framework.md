# Computational Film Production Scheduling: Mathematical Formulations, Regulatory Frameworks, and Algorithmic Solvers via Google OR-Tools, msgspec, and uv

Film and high-end video production scheduling is among the most computationally demanding combinatorial optimization problems encountered in industrial operations research1. Generating an executable shooting schedule—traditionally compiled as a physical or digital stripboard—requires balancing millions of dollars in capital expenditure, non-negotiable guild labor mandates, biological human thresholds, spatial logistics, physical asset readiness, calendar phenomena, and creative continuity1. The problem scales non-linearly from nimble commercial and short-form shoots spanning two to three production days to cross-boarded multi-part franchise tentpoles spanning hundreds of production days across international jurisdictions3.
In mathematical scheduling literature, the general film scheduling problem synthesizes the Talent Scheduling Problem, the Resource-Constrained Project Scheduling Problem with Time Windows (RCPSP-TW), and the Traveling Salesperson Problem with Sequence-Dependent Setup Times (TSP-SDST)1. A single operational miscalculation, such as triggering an unnecessary contractual talent hold day, violating union turnaround rules by fifteen minutes, overlooking a practical location's municipal operating window, or exhausting available breakaway props on a high-risk stunt scene, can compound across an entire call sheet, resulting in severe financial penalties, labor audits, or catastrophic completion bond default4.

## 1. Multi-Tier Production Stakeholder Ecosystem

A shooting schedule represents an operational compromise negotiated among stakeholders whose structural incentives directly conflict3. Developing an algorithmic optimization architecture requires translating these human, operational, artistic, and legal agendas into explicit hard constraints or parameterized objective functions8.

| Stakeholder                                       | Primary Objectives                                                           | Primary Constraints Imposed                                                      | Optimization Tension Points                                                                                                                |
| :------------------------------------------------ | :--------------------------------------------------------------------------- | :------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| **1st Assistant Director (1st AD)**               | Operational safety, crew rhythm, schedule feasibility, full scene coverage3. | Daily work caps, turnaround minimums, company move limits, lighting setups3.     | Prefers clustering scenes by lighting and camera angles; conflicts directly with talent availability windows and municipal curfews3.       |
| **Unit Production Manager (UPM) / Line Producer** | Budget integrity, variance control, vendor contractual compliance6.          | Overtime caps, travel/per diem thresholds, meal penalties, fringe labor rates6.  | Minimizes paid talent hold days and crew overtime; conflicts with the director's desire for chronological or emotional sequence padding10. |
| **Director & Cinematographer (DoP)**              | Narrative coherence, dramatic momentum, lighting aesthetics3.                | Golden hour alignments, dramatic progression, actor emotional pacing3.           | Prefers shooting in chronological order to support performance arcs; conflicts with cross-boarding efficiency across script parts5.        |
| **Art Director & Prop Master**                    | Craft execution, physical set readiness, set continuity4.                    | Construction lead times, set dressing intervals, hero prop duplicate counts4.    | Requires physical possession of locations days prior to filming for pre-dressing; conflicts with compressed soundstage leases6.            |
| **Costume Designer & Wardrobe Master**            | Costume distress integrity, character visual continuity4.                    | Unidirectional distress progression, multi-stage duplicate fabrication limits4.  | Enforces strict forward-only shooting orders for distressed garments unless costly duplicates are funded4.                                 |
| **Key Department Heads (SFX, Stunts, HMU)**       | On-set physical safety, specialized equipment deployment4.                   | Rigging and curing windows, prosthetic application times, stunt reset buffers4.  | High setup and turnaround times demand pre-lighting and rigging blocks, reducing active camera rolling time9.                              |
| **Cast & Talent Agents**                          | Remuneration, personal fatigue mitigation, external career availability1.    | Stop dates, blackout windows, 10-day Drop-and-Pickup rules, travel turnaround10. | "Pay-or-Play" contracts demand strict start and completion dates regardless of internal production delays1.                                |
| **Location Manager**                              | Site access, neighborhood relations, municipal compliance6.                  | Permitted operating hours, noise curfews, structural restoration requirements6.  | Practical commercial sites (banks, active schools) restrict access to specific days of the week6.                                          |
| **Completion Guarantor (Bond Company)**           | Mitigation of financial abandonment or delivery failure11.                   | Mandatory cover sets, contingency buffers, locked delivery milestones3.          | Enforces conservative daily page counts, restricting aggressive compression models that lack contingency buffers3.                         |

The 1st AD acts as the operational orchestrator of the physical set, structuring daily stripboards to ensure crew efficiency without exceeding physiological endurance limits3. In parallel, the Line Producer and UPM evaluate the schedule through financial liability, monitoring contractual exposure such as forced calls, meal penalties, and paid talent idle days6. Department heads for art, wardrobe, props, and special effects manage their own internal preparation pipelines, requiring physical access to sets and actors long before the camera rolls4. Overseeing the entire financing structure, the Completion Guarantor imposes institutional risk thresholds, demanding validated "cover sets" for exterior scenes and refusing to insure schedules that leave zero margin for weather interruptions or principal cast illness3.

## 2. Comprehensive Taxonomy of Production Constraints

Production scheduling constraints fall into six primary categories: regulatory and biological labor boundaries; physical breakdown elements and asset logistics; spatial, environmental, and operational parameters; contractual frameworks and hold structures; calendar, meteorological, and astrological dependencies; and granular scene-level configuration requirements1.

### Regulatory and Biological Labor Boundaries

Screen industry operations are governed by detailed collective bargaining agreements21. In the United States and international union shoots, contracts from SAG-AFTRA and IATSE dictate operational limits22. In the Indian production landscape, including Bollywood and regional film sectors, regulations set by the Federation of Western India Cine Employees (FWICE) and artist bodies such as the Cine & TV Artistes' Association (CINTAA) govern shift durations and turnaround standards6.

#### Turnaround Rules

Turnaround defines the mandatory rest period between consecutive work shifts:

- **Daily Turnaround:** SAG-AFTRA Codified Basic Agreements mandate a minimum 12-hour continuous rest period from camera wrap to the call time on the following day for performers at studio zones, expanding to 14 or 36 hours for distant locations requiring travel12. IATSE contracts similarly enforce 10- to 12-hour rest windows for technical crew. Encroaching upon these rest windows incurs "forced call" penalties, billed at punitive hourly rates per crew member12.
- **Weekly Rest Periods:** Standard agreements require 54 to 56 consecutive hours of rest following a five-day work week, or 36 continuous hours following a six-day work week3. Infringing upon weekly rest triggers double-time or golden-time penalty rates across the technical crew.
- **FWICE Regulations:** Across Indian production hubs, standard technical shifts are capped at 12 continuous hours, inclusive of designated meal breaks6. Shift overruns require formal advance notification, supplementary hourly payments, and mandatory 10- to 12-hour turnaround periods before the subsequent technical call6.

#### Meal Intervals and Penalties

Both union and non-union productions enforce regular nutrition schedules to prevent physical exhaustion on set. A compliant meal break must occur no later than six hours after the general crew call, and the subsequent meal must occur within six hours of the conclusion of the first14. Failing to call a meal within these intervals triggers progressive meal penalties assessed across every eligible technician and performer on set for each half-hour fraction until work ceases15.

#### Child Labor Regulations

The employment of child actors introduces non-negotiable boundaries on set hours, camera performance time, and compulsory education21. Violations carry civil penalties and can result in the immediate revocation of filming permits or union certification21.

| Legal Jurisdiction / Union Framework | Performer Age Group    | Maximum Set Time  | Maximum Camera / Work Time                  | Mandatory Educational Time      | Mandatory Curfew Windows                               |
| :----------------------------------- | :--------------------- | :---------------- | :------------------------------------------ | :------------------------------ | :----------------------------------------------------- |
| California DLSE / SAG-AFTRA          | Infants under 6 months | 2 hours per day   | 20 minutes total                            | None                            | 9:30 AM to 11:30 AM or 2:30 PM to 4:30 PM              |
| California DLSE / SAG-AFTRA          | 2 to 5 years           | 3 hours per day   | 3 hours total                               | None                            | 5:00 AM to 10:00 PM                                    |
| California DLSE / SAG-AFTRA          | 6 to 8 years           | 8 hours per day   | 4 hours (School day) / 6 hours (Non-school) | 3 hours (School days)           | 5:00 AM to 10:00 PM (12:30 AM on non-school nights)    |
| California DLSE / SAG-AFTRA          | 9 to 15 years          | 9 hours per day   | 5 hours (School day) / 7 hours (Non-school) | 3 hours (School days)           | 5:00 AM to 10:00 PM (12:30 AM on non-school nights)    |
| California DLSE / SAG-AFTRA          | 16 to 17 years         | 10 hours per day  | 6 hours (School day) / 8 hours (Non-school) | 3 hours (School days)           | 5:00 AM to 10:00 PM (12:30 AM on non-school nights)    |
| United Kingdom (The Children Act)    | 5 to 8 years           | 8 hours per day   | 3 hours total                               | Flexible via licensed tutor log | 7:00 AM to 7:00 PM                                     |
| United Kingdom (The Children Act)    | 9 to 16 years          | 9.5 hours per day | 5 hours total                               | Flexible via licensed tutor log | 7:00 AM to 7:00 PM (Extended to 10:00 PM with notice)  |
| India (NCPCR / Child Labour Act)     | Minors under 18 years  | 5 hours per day   | 3 hours continuous maximum                  | Formal schooling protected      | 7:00 PM to 8:00 AM prohibited; max 27 consecutive days |

### Granular Scene Configuration Attributes and Execution Constraints

Every scene possesses a distinct combination of atmospheric, technical, and calendar preconditions that dictate whether it can execute on a given production day3:

- **Weather Dependency Matrix:** Scenes are classified by strict meteorological compatibility:
  - _Rain Mandatory:_ Sequences that require natural atmospheric precipitation (e.g., an authentic outdoor storm sequence where practical rain machines cannot cover broad vistas). These scenes must be scheduled on days flagged with rain, or placed on conditional call.
  - _Rain Forbidden:_ Exterior scenes requiring sunlight, complex exterior electrical rigs, or sensitive camera optics that cannot operate under precipitation3.
  - _Overcast Only:_ High-contrast dialogue scenes where harsh direct solar shadows break lighting continuity across consecutive takes.
  - _Wet-Down Required:_ Sequences requiring asphalt or ground wet-downs prior to rolling camera, adding 45 to 60 minutes of physical site preparation before photography begins.
- **Lighting and Solar Constraints:** Scenes tied to specific natural lighting states:
  - _Magic Hour / Golden Hour:_ Scenes with a strict operational execution window of 40 to 60 minutes immediately following sunrise or preceding sunset. Multiple golden hour scenes cannot be scheduled on the same day unless split across dawn and dusk.
  - _Day-for-Night vs. True Exterior Night:_ True exterior night scenes (blue strips) demand full night conditions, triggering municipal curfews and late call times3.
- **Acoustic and Sound Recording Regimes:**
  - _Sync Sound:_ High-fidelity on-set dialogue recording requiring full ambient silence. Sync sound scenes cannot run concurrently with noisy stage builds, adjacent construction, or heavy rain on non-soundproofed tin stage roofs6.
  - _MOS (Mit Out Sound / Wild Track):_ Action, visual effects background plates, second-unit inserts, or stunt sequences filmed without sound recording, allowing concurrent work or scheduling in acoustically noisy environments.
- **Calendar, Holiday, and Special Event Intersections:**
  - _Holiday Mandatory:_ Scenes requiring actual public festive backgrounds (e.g., shooting in an authentic Mardi Gras, Christmas parade, or Diwali street celebration).
  - _Holiday Forbidden:_ Scenes involving standard public or municipal property where holiday labor surcharges or public closures make filming illegal or cost-prohibitive25.
  - _Public Operational Windows:_ Commercial venues such as operational bank branches, active subway stations, or university classrooms allow filming exclusively during off-peak windows (e.g., weekends only, Sunday evenings, or statutory bank holidays).

### Physical Breakdown Elements and Asset Logistics

Every scene on a production board requires specific physical and department-level assets identified during the script breakdown phase4:

- **Hero Props vs. Set Dressing:** Props actively handled by performers (e.g., hero weapons, character heirlooms, operational laptops) require dedicated standby supervision and maintenance4. If a scene involves prop destruction (such as smashing a bottle or destroying a vehicle), the art and props department requires duplicate "breakaways"4. The physical quantity of manufactured duplicate assets sets a hard ceiling on allowable takes per shoot day before requiring a reset, drying, or repair buffer4.
- **Costume Distress and Continuity Ladders:** Costumes evolve across narrative timelines4. A hero costume often exists across distinct visual states: Stage 1 (pristine/clean), Stage 2 (road dirt/weathered), Stage 3 (ballistic puncture/combat tear), and Stage 4 (bloodied/charred)4. Unless duplicate hero wardrobe builds exist (frequently cost-prohibitive in independent film), scenes must follow a strict, unidirectional forward progression4.
- **Specialty Equipment Lease Windows:** High-end technical equipment—such as 50-foot Technocranes, Russian Arms, high-speed Phantom cameras, motion control rigs, and underwater camera housings—is rarely rented across an entire multi-month shoot. They are leased in tight, targeted rental windows. Scenes demanding this equipment must be clustered within these explicit calendar intervals.
- **Special Effects (SFX) and Stunt Rigging Windows:** Practical action sequences requiring wire work, air ratchets, pyrotechnics, or squibs demand substantial prep, pre-rigging, and rehearsal intervals4. A high-impact scene scheduled for 8:00 AM on a Tuesday requires the rigging grips and SFX team to have access to the set for 8 to 12 hours on Monday for structural anchoring and safety verification4.

### Spatial, Environmental, and Operational Logistics

The traditional stripboard categorizes screenplay scenes into four primary visual palettes to represent lighting and environmental risk factors3:

| Strip Color Identifier | Setting & Time Designation  | Environmental Risk Level           | Production Setup Overhead                  | Operational Considerations                                                          |
| :--------------------- | :-------------------------- | :--------------------------------- | :----------------------------------------- | :---------------------------------------------------------------------------------- |
| **White Strip**        | Interior Day (INT. DAY)     | Negligible                         | Baseline stage / practical rigging         | Stable lighting conditions; easily scheduled across any shift time3.                |
| **Yellow Strip**       | Exterior Day (EXT. DAY)     | Severe (Rain, cloud, solar shifts) | High (Grip diffusion, negative fill)       | Requires mandatory cover sets; vulnerable to weather delays3.                       |
| **Green Strip**        | Interior Night (INT. NIGHT) | Low                                | Moderate (Tent/blackout requirements)      | Can be shot during day hours using window blackouts to prevent night calls3.        |
| **Blue Strip**         | Exterior Night (EXT. NIGHT) | Moderate to Severe                 | High (Condors, balloon lights, generators) | Strict municipal noise curfews; triggers late-call schedules and turnaround risks3. |

Sequencing across these strip classifications introduces substantial sequence-dependent changeovers3. The most operationally disruptive sequence is the industry-standard "Fraturday" pattern3. If a production schedules an EXT. NIGHT sequence on a Friday evening, filming typically continues until dawn on Saturday3. Under standard 54-hour weekend turnaround mandates, the crew cannot be legally called back to set until Monday afternoon, forcing Monday's call to 1:00 PM or 2:00 PM3. This progressive shift erodes available daylight hours for subsequent Monday scenes and risks pushing the entire following week into late-afternoon and evening shifts3.
Physical filming locations also impose strict lifecycle requirements:

| Location Lifecycle Phase   | Dedicated Department Focus                      | Camera Unit Status                   | Operational Site Constraint                                                   |
| :------------------------- | :---------------------------------------------- | :----------------------------------- | :---------------------------------------------------------------------------- |
| **Pre-Dressing & Rigging** | Art department, construction, rigging electrics | Inactive / Main Unit on separate set | Site secured; dressing and cable distribution access only4.                   |
| **Principal Photography**  | Main camera unit, sound, director, cast         | Active camera rolling                | Full street closures, generator permits, sound containment6.                  |
| **Strike & Restoration**   | Art strike crew, location managers, cleaners    | Inactive / Main Unit wrapped         | Site restoration to original condition; security deposit release inspection6. |

Company moves—relocating all cast, technical crew, and basecamp infrastructure between separate physical locations—consume two to four hours of non-productive transit and setup time6. In congested media hubs such as Mumbai or Los Angeles, municipal traffic patterns dictate that intra-day company moves must occur outside peak congestion windows, or be eliminated entirely by grouping scenes within localized filming zones6.

### Contractual Frameworks and the Day Out of Days Matrix

The primary analytical document derived from the shooting schedule is the Day Out of Days (DOOD) report10. The DOOD tracks the status of every cast member across every calendar day of production using standardized shorthand10. The designation "SW" marks the Start Work day, "W" marks an active Work day on camera, "H" indicates a Hold day where the performer is inactive but compensated at their full contractual daily rate, "WD" and "PU" mark Work Drop and Pick-Up transitions, and "WF" marks Work Finish, concluding contractual obligations10.
Under SAG-AFTRA theatrical agreements, performers are engaged on a consecutive employment basis: once a performer starts work ("SW"), every intervening calendar day must be fully compensated as a work or hold day until their final wrap ("WF")1. The sole legal exception is the 10-Day Drop-and-Pickup (DPU) rule10. A day performer may be temporarily released from production payroll only if the hiatus between their drop and subsequent pickup comprises at least ten continuous calendar days10. Additionally, the production must commit to a firm return date at the moment of release, and this drop provision may be invoked only once per performer across the entire project10. If an operational delay compresses this hiatus to nine days or fewer, the drop is invalidated, and the production becomes retroactively liable for all intervening days as paid holds10.

### Calendar, Meteorological, and Astrological Dependencies

Filming plans intersect directly with external calendar, seasonal, and regional dynamics6:

- **Seasonal Macro-Windows and Monsoons:** Production in tropical or sub-tropical hubs must work around monsoons6. In Mumbai or Southeast Asia, exterior schedules are compressed into dry winter bands (October through March), while the heavy monsoon window (June through September) is restricted strictly to interior soundstages or post-production6. Similarly, alpine shoots depend on snowmelt windows or safe pack-ice conditions.
- **Sun Tracking and Golden Hour Alignment:** Scenes requiring low-angle sun or golden hour lighting have effective daily filming windows of only 45 to 75 minutes, capping daily setup volume15. Schedules must calculate daily solar dawn, sunrise, sunset, and civil dusk.
- **Mandatory Interior Cover Sets:** Completion guarantors generally will not bond a schedule that lacks validated interior cover sets3. If an exterior shoot is hit by unexpected storms, the schedule must pivot to an interior set with minimal notice3.
- **Statutory and Guild Holidays:** Major calendar holidays (e.g., Thanksgiving, Christmas, New Year's Day, Memorial Day under US IATSE/SAG-AFTRA agreements, or Diwali, Eid, and Independence Day under Indian FWICE/CINTAA frameworks) carry severe financial penalties6. Scheduling work on these designated days triggers double-time or triple-time penalty rates across the technical crew25.
- **Shubh Muhurat (Auspicious Starting Moments):** In multiple filmmaking traditions, especially within the Indian film industry (Bollywood, Tollywood, Kollywood), cultural and calendar factors serve as hard scheduling constraints6. The initiation of principal photography—the ceremonial _Muhurat shot_—must occur within a precise astrological window (calculated via the Vedic Panchang based on planetary alignments, nakshatras, and tithis)24. Day 1 of production is frequently fixed to a specific calendar date and time, constraining all downstream schedule blocks.
- **Inauspicious Period Avoidance:** Certain lunar or solar calendar intervals (such as daily _Rahu Kaal_ windows, or extended periods like _Pitru Paksha_) are considered unfavorable by traditional producers and investors for launching new ventures or filming major sequences.

### Daily Call Sheet Mechanics and Character Call Calculations

The call sheet is the operational contract of a shoot day, generated the evening prior once the current day wraps14. It details general crew call, shooting call, advance schedules, safety notes, and precise character arrival times14.
Unlike general crew calls which anchor the entire day, character call times are calculated backward from the exact moment each performer is needed on set for camera blocking12. Calling an actor to set hours before their scene rolls wastes payroll, triggers premature fatigue, and pushes the performer's turnaround window deeper into the following evening, risking a forced call the next day12.
The mathematical backward calculation for actor call times is defined as follows12:
$$\text{Shooting Call} = \text{Anchor Time for First Shot of the Day}$$
$$\text{Performer Set Call}_a = \text{Scheduled Start Time of Scene requiring Actor } a - \text{Blocking/Rehearsal Buffer}$$
$$\text{Performer HMU Call}_a = \text{Performer Set Call}_a - \text{HMU Duration}_a - \text{Wardrobe Fitting Duration}_a$$
$$\text{Performer Pickup Call}_a = \text{Performer HMU Call}_a - \text{Transit Time from Basecamp / Residence}_a$$
$$\text{Meal Break Window} \le \text{General Crew Call} + 6\text{ hours}$$
$$\text{Mandatory Next Day Call Threshold}_a \ge \text{Wrap Time}_a + \text{Turnaround Minimum}_a$$

## 3. Cross-Boarding Logistics in Multi-Part and Episodic Productions

Cross-boarding is the practice of combining the scene requirements of multiple feature scripts (such as Part 1 and Part 2 of a unified film saga) or multiple episodic scripts into a unified production schedule3. Rather than shooting Part 1 sequentially and then entering a second pre-production phase for Part 2, cross-boarding arranges scenes based on physical location, set builds, and cast availability across both scripts simultaneously5.

| Scheduling Mode                     | Script / Location Context | Scene Execution Order                                               | Production Lifecycle Action                                                   |
| :---------------------------------- | :------------------------ | :------------------------------------------------------------------ | :---------------------------------------------------------------------------- |
| **Chronological Script Continuity** | Part 1 Script             | Scene 10 (Palace Hall) -> Scene 45 (Mountain) -> Scene 80 (Dungeon) | Requires storing or striking and rebuilding sets between film installments16. |
| **Chronological Script Continuity** | Part 2 Script             | Scene 12 (Palace Hall) -> Scene 30 (Dungeon) -> Scene 95 (Beach)    | Soundstage holding fees accrue across intervening hiatuses16.                 |
| **Cross-Boarded Production Board**  | Location 1: Palace Hall   | Part 1, Scene 10 -> Part 2, Scene 12                                | Set permanently wrapped and struck; stage cleared immediately16.              |
| **Cross-Boarded Production Board**  | Location 2: Dungeon Set   | Part 1, Scene 80 -> Part 2, Scene 30                                | Set permanently wrapped and struck; stage cleared immediately16.              |
| **Cross-Boarded Production Board**  | Location 3: Mountain Pass | Part 1, Scene 45                                                    | Unit shoots out practical mountain location completely16.                     |
| **Cross-Boarded Production Board**  | Location 4: Beach Landing | Part 2, Scene 95                                                    | Unit shoots out practical coastal location completely16.                      |

### Capital Expenditure and Physical Set Amortization

The primary financial driver of cross-boarding is amortizing physical set construction, soundstage rentals, and geographic relocation overhead16. Large-scale set builds on soundstages follow an inflexible, capital-intensive life cycle:

1. Construction and structural build
2. Scenic painting and set dressing
3. Pre-lighting and rigging
4. Principal photography
5. Strike and stage restoration

If Part 2 contains a five-minute flashback sequence utilizing an ancestral estate prominently featured throughout Part 1, producing the films sequentially creates an expensive logistical trade-off. The production must either pay soundstage holding costs for months while Part 1 wraps and Part 2 completes prep, strike the set and reconstruct it from scratch months later (doubling construction labor and material costs), or cross-board the schedule to shoot the Part 2 flashback during Part 1 principal photography. Cross-boarding allows the set to be permanently struck once all camera coverage across both parts is complete, freeing soundstage space and eliminating duplicate construction expenses.

### Biological Continuity and the Adolescent Maturation Constraint

Cross-boarding can also be dictated by human biology rather than financial optimization alone31. In productions featuring child or adolescent performers across multi-part sagas, physical maturation introduces an irreversible time constraint31.
During the production of the _Avatar_ sequels (_Avatar: The Way of Water_, _Avatar 3_, and _Avatar 4_), director James Cameron addressed what he termed the "Stranger Things effect," wherein child and adolescent actors physically outgrow their roles when production cycles span several calendar years31. For example, cast member Jack Champion was cast at age 12 and was undergoing rapid adolescent growth during photography32. To prevent visual discontinuities between scenes set mere days apart in story continuity, Cameron cross-boarded the productions: all performance-capture and live-action scenes involving the young cast for _Avatar 2_, _Avatar 3_, and the first act of _Avatar 4_ were filmed concurrently across an 18-month production block32. Production on the later acts of _Avatar 4_ was intentionally deferred, aligning real-world actor maturation with a planned narrative time jump32.

### Physical, Grooming, and Transformative Continuity

Cross-boarding complicates cosmetic continuity, including hair, makeup, wardrobe, and physical fitness:

- **Facial and Scalp Hair Growth Sequences:** If a lead character begins Part 1 clean-shaven and appears in Part 2 with a long beard, but the schedule cross-boards scenes across both parts based on set availability, hair growth acts as a strict, unidirectional scheduling barrier. All bearded scenes must be scheduled first, followed by a planned haircut and shave on the stripboard, after which clean-shaven scenes are executed. Reversing this sequence requires realistic facial hair prosthetics, increasing makeup application times from thirty minutes to over three hours per day.
- **Actor Physical Conditioning:** Drastic physical transformations, such as rapid muscle gain or weight cuts, impose hard boundaries across the shooting schedule. Scenes depicting an actor in an emaciated state cannot be alternated with peak-physique scenes on a daily basis; they must be clustered into distinct blocks separated by planned production hiatuses.
- **Costume Distress and Weaponry Continuity:** Hero costumes and practical picture vehicles undergo progressive distressing, bullet damage, and wear across continuous story arcs4. If scenes are cross-boarded non-chronologically, the costume department must build multiple identical copies across distinct wear stages (Stage 1: Pristine, Stage 2: Road Dirt, Stage 3: Combat Torn, Stage 4: Bloodied)4. When asset duplication is limited by budget, scenes must be strictly sequenced from lowest to highest level of physical distress4.

## 4. Comprehensive Data Modeling via msgspec Contracts

To make film production data structures computationally accessible to high-performance solvers, every element must be formalized into typed data contracts38. msgspec delivers C-speed validation and JSON encoding/decoding, enforcing structural integrity across complex relational hierarchies38.
Below is the complete, production-grade taxonomy of `msgspec.Struct` contracts covering every production facet:

```python
from typing import List, Optional, Literal
import msgspec

class Prop(msgspec.Struct, gc=False):
    id: int
    name: str
    category: Literal["HERO", "SET_DRESSING", "BREAKAWAY", "WEAPON", "VEHICLE"]
    total_quantity: int
    is_destructible: bool = False
    requires_armorer: bool = False
    reset_duration_minutes: int = 0

class Costume(msgspec.Struct, gc=False):
    id: int
    character_id: int
    costume_code: str
    distress_stage: int  # 1: Clean, 2: Weathered, 3: Damaged, 4: Destroyed
    available_duplicates: int = 1
    requires_specialist_dresser: bool = False

class SpecialtyEquipment(msgspec.Struct, gc=False):
    id: int
    name: str
    equipment_type: Literal["TECHNOCRANE", "PHANTOM_HIGH_SPEED", "MOTION_CONTROL", "UNDERWATER_HOUSING", "RUSSIAN_ARM", "DRONE"]
    daily_rental_cost: float
    rental_start_day: int
    rental_end_day: int
    requires_certified_technician: bool = True

class StuntSFXPackage(msgspec.Struct, gc=False):
    id: int
    has_wirework: bool = False
    has_pyrotechnics: bool = False
    has_squibs: bool = False
    pre_rigging_hours_required: float = 0.0
    mandatory_medic_count: int = 1

class Talent(msgspec.Struct, gc=False):
    id: int
    name: str
    character_name: str
    daily_rate: float
    is_minor: bool = False
    max_daily_hours: float = 10.0
    hmu_duration_minutes: int = 60
    wardrobe_duration_minutes: int = 30
    travel_duration_minutes: int = 30
    blackout_days: List[int] = []

class Location(msgspec.Struct, gc=False):
    id: int
    name: str
    location_type: Literal["SOUNDSTAGE", "PRACTICAL_INT", "PRACTICAL_EXT"]
    permitted_days: List[int]
    noise_curfew_hour: Optional[int] = None
    allows_sync_sound: bool = True
    daily_rental_cost: float = 0.0
    prep_days_required: int = 0
    strike_days_required: int = 0

class CalendarDay(msgspec.Struct, gc=False):
    day_number: int
    calendar_date: str
    is_statutory_holiday: bool = False
    is_inauspicious: bool = False
    expected_weather: Literal["CLEAR", "OVERCAST", "RAIN", "MONSOON"] = "CLEAR"
    sunrise_time: str = "06:15"
    sunset_time: str = "18:30"
    is_weekend: bool = False

class Scene(msgspec.Struct, gc=False):
    id: int
    scene_number: str
    part: int
    location_id: int
    setting: Literal["INT", "EXT"]
    time_of_day: Literal["DAY", "NIGHT", "MAGIC_HOUR"]
    page_eighths: int
    duration_hours: float
    required_cast: List[int]
    required_prop_ids: List[int] = []
    required_costume_ids: List[int] = []
    required_equipment_ids: List[int] = []
    stunt_sfx_package_id: Optional[int] = None
    weather_requirement: Literal["ANY", "CLEAR_ONLY", "OVERCAST_ONLY", "RAIN_MANDATORY", "NO_RAIN"] = "ANY"
    sound_recording: Literal["SYNC_SOUND", "MOS", "WILD_TRACK"] = "SYNC_SOUND"
    holiday_compatibility: Literal["NORMAL", "HOLIDAY_ONLY", "FORBID_HOLIDAY"] = "NORMAL"
    earliest_allowed_day: Optional[int] = None
    latest_allowed_day: Optional[int] = None
    is_cover_set: bool = False
    cover_for_scene_id: Optional[int] = None
    requires_precedence_over: Optional[int] = None

class ProductionDataset(msgspec.Struct, gc=False):
    project_title: str
    talents: List[Talent]
    locations: List[Location]
    props: List[Prop]
    costumes: List[Costume]
    equipment: List[SpecialtyEquipment]
    stunts: List[StuntSFXPackage]
    calendar: List[CalendarDay]
    scenes: List[Scene]
    max_shooting_days: int
    max_hours_per_day: float
```

## 5. Mathematical Formulation of the Extended Film Scheduling Problem

The film scheduling problem can be formulated as a discrete combinatorial optimization model that synthesizes the Talent Scheduling Problem with sequence-dependent resource allocation, calendar availability masks, and multi-part precedence constraints1.

### Indices, Sets, and Parameters

- $s, j \in S = \{1, \dots, N\}$: Set of all scenes to be scheduled across all parts or episodes1.
- $d, k \in D = \{1, \dots, K\}$: Set of available production calendar days1.
- $a \in A = \{1, \dots, M\}$: Set of all performers and key talent1.
- $l \in L = \{1, \dots, \Lambda\}$: Set of available physical locations and soundstages8.
- $e \in \mathcal{E}$: Set of specialized leased equipment items.
- $T_{as} \in \{0, 1\}$: Binary parameter equal to 1 if actor $a$ is required in scene $s$, and 0 otherwise1.
- $L_{sl} \in \{0, 1\}$: Binary parameter equal to 1 if scene $s$ takes place at location $l$, and 0 otherwise8.
- $E_{se} \in \{0, 1\}$: Binary parameter equal to 1 if scene $s$ requires specialized equipment $e$, and 0 otherwise.
- $\Omega_{sd} \in \{0, 1\}$: Comprehensive scene configuration compatibility mask; equal to 1 if scene $s$ satisfies all weather, holiday, location permit, and acoustic constraints on day $d$, and 0 otherwise:
  $$\Omega_{sd} = \text{WeatherMatch}(s, d) \land \text{PermitMatch}(s, d) \land \text{HolidayMatch}(s, d) \land \text{AcousticMatch}(s, d)$$
- $\mathcal{D}_s = \{d \in D \mid \Omega_{sd} = 1\}$: Dynamically pruned feasible domain of days for scene $s$.
- $C_a$: Daily financial compensation rate for actor $a$1.
- $w_s$: Duration or weight of scene $s$, quantified in fractional production hours or script page eighths4.
- $W_d^{\max}$: Maximum allowable working hours on day $d$ before triggering illegal overtime or union violations6.
- $C_{ll'}^{\text{move}}$: Cost and setup time penalty incurred when transitioning between location $l$ and location $l'$7.
- $P_{ss'}$: Minimum precedence lag required between scene $s$ and scene $s'$ (e.g., set redressing, physical transformation, or narrative order)8.

### Decision Variables

- $x_{sd} \in \{0, 1\}$: Sparse binary decision variable; defined strictly for $(s, d)$ pairs where $d \in \mathcal{D}_s$, indicating whether scene $s$ is assigned to day $d$1.
- $u_{ad} \in \{0, 1\}$: Binary variable; 1 if actor $a$ is actively working on camera on day $d$, and 0 otherwise1.
- $e_a \in D$: Integer variable representing the earliest shoot day for actor $a$ (Start Work)1.
- $l_a \in D$: Integer variable representing the latest shoot day for actor $a$ (Work Finish)1.
- $y_{ld} \in \{0, 1\}$: Binary variable; 1 if location $l$ is active on day $d$, and 0 otherwise8.
- $z_{ll'd} \in \{0, 1\}$: Binary variable; 1 if an intra-day company move occurs between location $l$ and $l'$ on day $d$8.

### Formal Optimization Model

The objective function minimizes total talent holding expenditures, location relocation penalties, and workload variance across the schedule1:
$$\min Z = \sum_{a \in A} C_a (l_a - e_a + 1) + \sum_{d \in D} \sum_{l \in L} \sum_{l' \in L} C_{ll'}^{\text{move}} z_{ll'd} + \lambda_{\text{var}} \left[ \max_{d \in D} \sum_{s \in S : d \in \mathcal{D}_s} w_s x_{sd} - \min_{d \in D} \sum_{s \in S : d \in \mathcal{D}_s} w_s x_{sd} \right]$$
[cite: 1, 8]
Subject to the following operational constraints:

1. **Scene Assignment Uniqueness (Sparse Domain):** Every non-cover scene $s \in S_{\text{primary}}$ must be scheduled exactly once across its feasible domain $\mathcal{D}_s$1:
   $$\sum_{d \in \mathcal{D}_s} x_{sd} = 1 \quad \forall s \in S_{\text{primary}}$$
2. **Specialized Equipment Rental Window Adherence:**
   $$\mathcal{D}_s \subseteq [D_{e,\text{start}}, D_{e,\text{end}}] \quad \forall e \in \mathcal{E}, \forall s \in S \text{ such that } E_{se} = 1$$
3. **Daily Workload Capacity Caps:** Total scene duration allocated to day $d$ cannot exceed maximum allowable hours6:
   $$\sum_{s \in S : d \in \mathcal{D}_s} w_s x_{sd} \le W_d^{\max} \quad \forall d \in D$$
4. **Talent Daily Work Tracking:** An actor is marked active on day $d$ if any scene containing that actor is scheduled on that day1:
   $$u_{ad} \ge T_{as} x_{sd} \quad \forall a \in A, \forall s \in S : d \in \mathcal{D}_s, \forall d \in D$$
5. **Earliest and Latest Call Day Bounding:** Determining the Start Work ($e_a$) and Work Finish ($l_a$) parameters to calculate compensated spans1:
   $$e_a \le d \cdot u_{ad} + M(1 - u_{ad}) \quad \forall a \in A, \forall d \in D$$
   $$l_a \ge d \cdot u_{ad} \quad \forall a \in A, \forall d \in D$$
6. **Location Utilization Tracking:**
   $$y_{ld} \ge L_{sl} x_{sd} \quad \forall s \in S : d \in \mathcal{D}_s, \forall l \in L, \forall d \in D$$
7. **Daily Company Move Limits:** To prevent crew exhaustion, the count of distinct locations accessed on a single day is capped:
   $$\sum_{l \in L} y_{ld} \le M_{\text{move}} \quad \forall d \in D$$
8. **Linear-Time Precedence Constraints:** For any precedence pair $(s, s')$ requiring $s$ before $s'$:
   $$\sum_{d \in \mathcal{D}_{s'}} d \cdot x_{s'd} - \sum_{d \in \mathcal{D}_s} d \cdot x_{sd} \ge P_{ss'}$$
9. **Linear-Time Costume Distress Ladders:** For character $a$ across ordered distress stages $k \in \{1, \dots, K - 1\}$, let $S_{ak}$ be the set of scenes requiring stage $k$. Using auxiliary stage-boundary integer variables $\eta_{ak}^{\max}$ and $\eta_{a,k+1}^{\min}$, distress progression is enforced strictly in linear complexity:
   $$\eta_{ak}^{\max} \le \eta_{a,k+1}^{\min} \quad \forall k \in \{1, \dots, K - 1\}$$
10. **SAG-AFTRA 10-Day Drop-and-Pickup Formulation:** Consecutive employment can be partitioned into two distinct working intervals $[e_{a,1}, l_{a,1}]$ and $[e_{a,2}, l_{a,2}]$ using an indicator variable $\delta_a \in \{0, 1\}$10:
   $$e_{a,2} - l_{a,1} \ge 11 \cdot \delta_a$$
   $$\text{Compensated Days}_a = (l_{a,1} - e_{a,1} + 1) + (l_{a,2} - e_{a,2} + 1)$$
   If the drop provision is triggered ($\delta_a = 1$), the hiatus must span at least ten calendar days, eliminating paid hold costs over that interval10.

## 6. Algorithmic and Computational Performance Optimizations

To execute film production models with hundreds of scenes and tens of thousands of potential combinations in seconds, computational bottlenecks must be systematically identified and resolved41:

- **Upfront Domain Pruning (Sparse Variable Generation):** Rather than generating a complete Cartesian product of boolean variables across all scenes and days and then pinning infeasible variables to 0, candidate days are filtered before calling the solver42. If an exterior scene cannot legally shoot on day $d$ due to rain or practical location closure, that variable is never instantiated. This eliminates between 40% and 70% of potential decision variables from the solver's presolve stage42.
- **Inverted Indexing for Fast Relation Lookups:** The pre-solver avoids nested linear list scans inside tight loops by pre-indexing relationships using hash tables (`defaultdict(list)`). Inverted indices for talent, locations, props, and costumes build constraints in linear time.
- **Linear Stage-Chaining vs. Quadratic Pairwise Loops:** Naive implementations of costume distress ladders and precedence rules evaluate all scene pairs, creating a quadratic constraint explosion43. By sorting scenes into distinct distress stage buckets and chaining consecutive stage bounds, constraint count collapses from quadratic to strictly linear.
- **CP-SAT Solver Parameter Tuning:**
  - _Multi-threading (`num_search_workers`):_ Configured to match available physical CPU cores (typically 8 to 16 threads), allowing CP-SAT to execute distinct search heuristics (LNS, core-guided SAT, LP relaxation, random walk) in parallel41.
  - _Linearization Level (`linearization_level = 2`):_ Forces strong continuous linear programming cuts on all integer and boolean constraints, accelerating dual-bound convergence42.
  - _Symmetry Breaking (`symmetry_level = 2`):_ Detects identical scenes and interchangeable production days, pruning redundant permutations from the search tree13.
- **High-Throughput Serialization via msgspec:** Setting `gc=False` on `msgspec.Struct` definitions disables per-instance garbage collection overhead, accelerating data ingestion and validation for large breakdown sheet datasets38.

| Optimization Technique     | Naive Implementation                     | Optimized Strategy                            | Computational Impact                                       |
| :------------------------- | :--------------------------------------- | :-------------------------------------------- | :--------------------------------------------------------- |
| **Variable Instantiation** | Dense matrix of Booleans                 | Sparse allocation for valid days only         | 40% to 70% reduction in solver variable count42            |
| **Relational Lookups**     | Linear scans per entity query            | Hash indexing via defaultdict                 | Model build time reduced from quadratic to linear          |
| **Costume Ladders**        | Pairwise all-pairs quadratic constraints | Consecutive stage-chaining bounds             | Prevents constraint bloating in CP-SAT presolve42          |
| **Search Architecture**    | Single-threaded default CP search        | Multi-threaded portfolio workers with LP cuts | Order-of-magnitude reduction in solve time to optimality41 |

### Environment Setup with uv

The environment is configured using uv to establish an isolated, reproducible Python environment46:

```bash
# Initialize a new project directory
uv init film-production-scheduler
cd film-production-scheduler

# Add runtime dependencies
uv add ortools msgspec

# Execute the scheduling optimizer
uv run python schedule_optimizer.py
```

### Complete Optimized CP-SAT Production Solver Implementation

The Python script below incorporates all performance optimizations, sparse variable generation, inverted hash tables, linear stage chaining, and CP-SAT parameter tuning1.

```python
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Set, Tuple, Literal
import msgspec
from ortools.sat.python import cp_model

# ==============================================================================
# 1. HIGH-PERFORMANCE MSGSPEC DATA SCHEMAS
# ==============================================================================

class Prop(msgspec.Struct, gc=False):
    id: int
    name: str
    category: Literal["HERO", "SET_DRESSING", "BREAKAWAY", "WEAPON", "VEHICLE"]
    total_quantity: int
    is_destructible: bool = False
    requires_armorer: bool = False
    reset_duration_minutes: int = 0

class Costume(msgspec.Struct, gc=False):
    id: int
    character_id: int
    costume_code: str
    distress_stage: int  # 1: Clean, 2: Weathered, 3: Damaged, 4: Destroyed
    available_duplicates: int = 1
    requires_specialist_dresser: bool = False

class SpecialtyEquipment(msgspec.Struct, gc=False):
    id: int
    name: str
    equipment_type: Literal["TECHNOCRANE", "PHANTOM_HIGH_SPEED", "MOTION_CONTROL", "UNDERWATER_HOUSING", "RUSSIAN_ARM", "DRONE"]
    daily_rental_cost: float
    rental_start_day: int
    rental_end_day: int
    requires_certified_technician: bool = True

class StuntSFXPackage(msgspec.Struct, gc=False):
    id: int
    has_wirework: bool = False
    has_pyrotechnics: bool = False
    has_squibs: bool = False
    pre_rigging_hours_required: float = 0.0
    mandatory_medic_count: int = 1

class Talent(msgspec.Struct, gc=False):
    id: int
    name: str
    character_name: str
    daily_rate: float
    is_minor: bool = False
    max_daily_hours: float = 10.0
    hmu_duration_minutes: int = 60
    wardrobe_duration_minutes: int = 30
    travel_duration_minutes: int = 30
    blackout_days: List[int] = []

class Location(msgspec.Struct, gc=False):
    id: int
    name: str
    location_type: Literal["SOUNDSTAGE", "PRACTICAL_INT", "PRACTICAL_EXT"]
    permitted_days: List[int]
    noise_curfew_hour: Optional[int] = None
    allows_sync_sound: bool = True
    daily_rental_cost: float = 0.0
    prep_days_required: int = 0
    strike_days_required: int = 0

class CalendarDay(msgspec.Struct, gc=False):
    day_number: int
    calendar_date: str
    is_statutory_holiday: bool = False
    is_inauspicious: bool = False
    expected_weather: Literal["CLEAR", "OVERCAST", "RAIN", "MONSOON"] = "CLEAR"
    sunrise_time: str = "06:15"
    sunset_time: str = "18:30"
    is_weekend: bool = False

class Scene(msgspec.Struct, gc=False):
    id: int
    scene_number: str
    part: int
    location_id: int
    setting: Literal["INT", "EXT"]
    time_of_day: Literal["DAY", "NIGHT", "MAGIC_HOUR"]
    page_eighths: int
    duration_hours: float
    required_cast: List[int]
    required_prop_ids: List[int] = []
    required_costume_ids: List[int] = []
    required_equipment_ids: List[int] = []
    stunt_sfx_package_id: Optional[int] = None
    weather_requirement: Literal["ANY", "CLEAR_ONLY", "OVERCAST_ONLY", "RAIN_MANDATORY", "NO_RAIN"] = "ANY"
    sound_recording: Literal["SYNC_SOUND", "MOS", "WILD_TRACK"] = "SYNC_SOUND"
    holiday_compatibility: Literal["NORMAL", "HOLIDAY_ONLY", "FORBID_HOLIDAY"] = "NORMAL"
    earliest_allowed_day: Optional[int] = None
    latest_allowed_day: Optional[int] = None
    is_cover_set: bool = False
    cover_for_scene_id: Optional[int] = None
    requires_precedence_over: Optional[int] = None

class ProductionDataset(msgspec.Struct, gc=False):
    project_title: str
    talents: List[Talent]
    locations: List[Location]
    props: List[Prop]
    costumes: List[Costume]
    equipment: List[SpecialtyEquipment]
    stunts: List[StuntSFXPackage]
    calendar: List[CalendarDay]
    scenes: List[Scene]
    max_shooting_days: int
    max_hours_per_day: float

# ==============================================================================
# 2. OPTIMIZED SOLVER ENGINE
# ==============================================================================

def build_and_solve_schedule(data: ProductionDataset):
    t_start = datetime.now()
    model = cp_model.CpModel()
    num_days = data.max_shooting_days

    # Pre-build lookup dictionaries (O(1) access)
    scene_dict: Dict[int, Scene] = {s.id: s for s in data.scenes}
    talent_dict: Dict[int, Talent] = {t.id: t for t in data.talents}
    location_dict: Dict[int, Location] = {l.id: l for l in data.locations}
    calendar_dict: Dict[int, CalendarDay] = {c.day_number: c for c in data.calendar}
    prop_dict: Dict[int, Prop] = {p.id: p for p in data.props}
    costume_dict: Dict[int, Costume] = {c.id: c for c in data.costumes}
    equipment_dict: Dict[int, SpecialtyEquipment] = {e.id: e for e in data.equipment}

    # Inverted Indexing for Fast Relational Constraint Assembly
    scenes_by_talent: Dict[int, List[Scene]] = defaultdict(list)
    scenes_by_location: Dict[int, List[Scene]] = defaultdict(list)
    scenes_by_prop: Dict[int, List[Scene]] = defaultdict(list)
    scenes_by_costume: Dict[int, List[Scene]] = defaultdict(list)

    for s in data.scenes:
        for cid in s.required_cast:
            scenes_by_talent[cid].append(s)
        scenes_by_location[s.location_id].append(s)
        for pid in s.required_prop_ids:
            scenes_by_prop[pid].append(s)
        for c_id in s.required_costume_ids:
            scenes_by_costume[c_id].append(s)

    # --------------------------------------------------------------------------
    # OPTIMIZATION 1: Upfront Domain Pruning (Sparse Variable Instantiation)
    # --------------------------------------------------------------------------
    feasible_days_by_scene: Dict[int, List[int]] = {}
    x: Dict[Tuple[int, int], cp_model.IntVar] = {}
    day_scene_vars: Dict[int, List[cp_model.IntVar]] = defaultdict(list)
    day_scene_coeffs: Dict[int, List[int]] = defaultdict(list)
    scene_vars_by_day: Dict[int, Dict[int, cp_model.IntVar]] = defaultdict(dict)

    scale = 10
    max_daily_units = int(data.max_hours_per_day * scale)

    for s in data.scenes:
        valid_days: List[int] = []
        loc = location_dict[s.location_id]

        for d in range(1, num_days + 1):
            cal = calendar_dict[d]
            is_valid = True

            # Calendar Window Bounds
            if s.earliest_allowed_day is not None and d < s.earliest_allowed_day:
                is_valid = False
            elif s.latest_allowed_day is not None and d > s.latest_allowed_day:
                is_valid = False
            # Location Permits
            elif d not in loc.permitted_days:
                is_valid = False
            # Astrological / Inauspicious Days
            elif cal.is_inauspicious:
                is_valid = False
            # Holiday Filtering
            elif s.holiday_compatibility == "FORBID_HOLIDAY" and cal.is_statutory_holiday:
                is_valid = False
            elif s.holiday_compatibility == "HOLIDAY_ONLY" and not cal.is_statutory_holiday:
                is_valid = False
            # Weather Compatibility
            elif s.weather_requirement == "RAIN_MANDATORY" and cal.expected_weather not in ("RAIN", "MONSOON"):
                is_valid = False
            elif s.weather_requirement in ("NO_RAIN", "CLEAR_ONLY") and cal.expected_weather in ("RAIN", "MONSOON"):
                is_valid = False
            elif s.weather_requirement == "OVERCAST_ONLY" and cal.expected_weather != "OVERCAST":
                is_valid = False
            # Acoustic Noise vs Rain
            elif s.sound_recording == "SYNC_SOUND" and not loc.allows_sync_sound and cal.expected_weather in ("RAIN", "MONSOON"):
                is_valid = False
            else:
                # Equipment Leases
                for eq_id in s.required_equipment_ids:
                    eq = equipment_dict[eq_id]
                    if d < eq.rental_start_day or d > eq.rental_end_day:
                        is_valid = False
                        break
                # Cast Blackouts
                if is_valid:
                    for cid in s.required_cast:
                        if d in talent_dict[cid].blackout_days:
                            is_valid = False
                            break

            if is_valid:
                valid_days.append(d)

        feasible_days_by_scene[s.id] = valid_days

        # Instantiate sparse decision variables only for valid days
        for d in valid_days:
            var = model.NewBoolVar(f"x_s{s.id}_d{d}")
            x[s.id, d] = var
            day_scene_vars[d].append(var)
            day_scene_coeffs[d].append(int(s.duration_hours * scale))
            scene_vars_by_day[d][s.id] = var

    # Constraint 1: Scene Assignment Uniqueness
    for s in data.scenes:
        if not s.is_cover_set:
            candidate_vars = [x[s.id, d] for d in feasible_days_by_scene[s.id]]
            if not candidate_vars:
                print(f"Error: Scene {s.scene_number} has an empty feasible day set. Infeasible instance.")
                return
            model.AddExactlyOne(candidate_vars)

    # Constraint 2: Daily Workload & Child Labor Limits
    for d in range(1, num_days + 1):
        if day_scene_vars[d]:
            daily_expr = cp_model.LinearExpr.WeightedSum(day_scene_vars[d], day_scene_coeffs[d])
            model.Add(daily_expr <= max_daily_units)

            # Child Labor Caps
            for t in data.talents:
                if t.is_minor:
                    minor_max = int(t.max_daily_hours * scale)
                    minor_scenes_on_day = [
                        scene_vars_by_day[d][s.id]
                        for s in scenes_by_talent[t.id]
                        if s.id in scene_vars_by_day[d]
                    ]
                    if minor_scenes_on_day:
                        is_minor_working = model.NewBoolVar(f"minor_{t.id}_active_d{d}")
                        model.AddMaxEquality(is_minor_working, minor_scenes_on_day)
                        model.Add(daily_expr <= minor_max).OnlyEnforceIf(is_minor_working)

    # Constraint 3: Explicit Precedence Constraints
    for s in data.scenes:
        if s.requires_precedence_over is not None:
            target_id = s.requires_precedence_over
            if target_id in scene_dict:
                s1_day = cp_model.LinearExpr.WeightedSum(
                    [x[s.id, d] for d in feasible_days_by_scene[s.id]],
                    feasible_days_by_scene[s.id]
                )
                s2_day = cp_model.LinearExpr.WeightedSum(
                    [x[target_id, d] for d in feasible_days_by_scene[target_id]],
                    feasible_days_by_scene[target_id]
                )
                model.Add(s1_day < s2_day)

    # --------------------------------------------------------------------------
    # OPTIMIZATION 2: Linear Stage-Chaining for Costume Distress Ladders
    # --------------------------------------------------------------------------
    character_costumes: Dict[int, List[Costume]] = defaultdict(list)
    for c in data.costumes:
        character_costumes[c.character_id].append(c)

    for char_id, c_list in character_costumes.items():
        if len(c_list) > 1:
            sorted_costumes = sorted(c_list, key=lambda c: c.distress_stage)
            for idx in range(len(sorted_costumes) - 1):
                c_early = sorted_costumes[idx]
                c_late = sorted_costumes[idx + 1]
                if c_early.distress_stage < c_late.distress_stage:
                    scenes_early = scenes_by_costume[c_early.id]
                    scenes_late = scenes_by_costume[c_late.id]
                    if scenes_early and scenes_late:
                        max_early_day = model.NewIntVar(1, num_days, f"max_day_c{c_early.id}")
                        early_day_exprs = [
                            cp_model.LinearExpr.WeightedSum(
                                [x[s.id, d] for d in feasible_days_by_scene[s.id]],
                                feasible_days_by_scene[s.id]
                            )
                            for s in scenes_early
                        ]
                        model.AddMaxEquality(max_early_day, early_day_exprs)

                        for s_late in scenes_late:
                            late_day_expr = cp_model.LinearExpr.WeightedSum(
                                [x[s_late.id, d] for d in feasible_days_by_scene[s_late.id]],
                                feasible_days_by_scene[s_late.id]
                            )
                            model.Add(max_early_day <= late_day_expr)

    # Constraint 4: Breakaway Prop Daily Exhaustion Limits
    for p in data.props:
        if p.category == "BREAKAWAY" and p.is_destructible:
            scenes_with_prop = scenes_by_prop[p.id]
            for d in range(1, num_days + 1):
                p_vars = [scene_vars_by_day[d][s.id] for s in scenes_with_prop if s.id in scene_vars_by_day[d]]
                if p_vars:
                    model.Add(sum(p_vars) <= p.total_quantity)

    # Constraint 5: Location Tracking & Move Limits
    loc_active: Dict[Tuple[int, int], cp_model.IntVar] = {}
    for l in data.locations:
        scenes_at_loc = scenes_by_location[l.id]
        if not scenes_at_loc:
            continue
        for d in range(1, num_days + 1):
            active_scenes = [scene_vars_by_day[d][s.id] for s in scenes_at_loc if s.id in scene_vars_by_day[d]]
            if active_scenes:
                loc_var = model.NewBoolVar(f"loc_{l.id}_d{d}")
                loc_active[l.id, d] = loc_var
                model.AddMaxEquality(loc_var, active_scenes)

    for d in range(1, num_days + 1):
        day_locs = [loc_active[l.id, d] for l in data.locations if (l.id, d) in loc_active]
        if day_locs:
            model.Add(sum(day_locs) <= 2)

    # Constraint 6: Day Out of Days (DOOD) Talent Hold Bounds
    hold_cost_terms = []
    talent_work: Dict[Tuple[int, int], cp_model.IntVar] = {}
    earliest: Dict[int, cp_model.IntVar] = {}
    latest: Dict[int, cp_model.IntVar] = {}

    for t in data.talents:
        scenes_with_t = scenes_by_talent[t.id]
        if not scenes_with_t:
            continue

        all_t_days = {d for s in scenes_with_t for d in feasible_days_by_scene[s.id]}
        if not all_t_days:
            print(f"Error: Cast {t.name} has no feasible work days.")
            return

        t_min_day, t_max_day = min(all_t_days), max(all_t_days)
        earliest[t.id] = model.NewIntVar(t_min_day, t_max_day, f"earliest_t{t.id}")
        latest[t.id] = model.NewIntVar(t_min_day, t_max_day, f"latest_t{t.id}")

        for d in range(1, num_days + 1):
            active_cast_scenes = [scene_vars_by_day[d][s.id] for s in scenes_with_t if s.id in scene_vars_by_day[d]]
            if active_cast_scenes:
                w_var = model.NewBoolVar(f"twork_t{t.id}_d{d}")
                talent_work[t.id, d] = w_var
                model.AddMaxEquality(w_var, active_cast_scenes)
                model.Add(earliest[t.id] <= d).OnlyEnforceIf(w_var)
                model.Add(latest[t.id] >= d).OnlyEnforceIf(w_var)

        span_var = model.NewIntVar(0, num_days, f"span_t{t.id}")
        model.Add(span_var == latest[t.id] - earliest[t.id] + 1)
        hold_cost_terms.append(span_var * int(t.daily_rate))

    # Move Penalties
    move_cost_terms = [var * 500 for var in loc_active.values()]

    # Objective Function
    model.Minimize(cp_model.LinearExpr.Sum(hold_cost_terms + move_cost_terms))

    # --------------------------------------------------------------------------
    # OPTIMIZATION 3: CP-SAT Multithreading & Solver Tuning Parameters
    # --------------------------------------------------------------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    solver.parameters.num_search_workers = os.cpu_count() or 8
    solver.parameters.linearization_level = 2
    solver.parameters.cp_model_presolve = True
    solver.parameters.symmetry_level = 2

    status = solver.Solve(model)
    solve_duration = (datetime.now() - t_start).total_seconds()

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("================================================================================")
        print(f"OPTIMIZATION RESULT: {solver.StatusName(status)} | SOLVE TIME: {solve_duration:.3f}s")
        print(f"PROJECT: {data.project_title.upper()} | TOTAL OBJECTIVE COST: ${solver.ObjectiveValue():,.2f}")
        print("================================================================================\n")

        # Stripboard Output
        print("--- MASTER STRIPBOARD SCHEDULE ---")
        scheduled_day_scenes: Dict[int, List[Scene]] = defaultdict(list)
        for s in data.scenes:
            for d in feasible_days_by_scene[s.id]:
                if (s.id, d) in x and solver.Value(x[s.id, d]) == 1:
                    scheduled_day_scenes[d].append(s)

        for d in range(1, num_days + 1):
            day_scenes = scheduled_day_scenes.get(d, [])
            cal = calendar_dict[d]
            if not day_scenes:
                print(f"DAY {d:02d} | {cal.calendar_date} | IDLE / REST DAY (Weather: {cal.expected_weather})")
                continue

            loc_names = {location_dict[s.location_id].name for s in day_scenes}
            total_hours = sum(s.duration_hours for s in day_scenes)
            total_eighths = sum(s.page_eighths for s in day_scenes)

            print(f"DAY {d:02d} | {cal.calendar_date} | {total_hours:.1f} Hrs | {total_eighths}/8 Pgs | Weather: {cal.expected_weather} | Loc: {', '.join(loc_names)}")
            for s in day_scenes:
                cast_names = [talent_dict[cid].name for cid in s.required_cast]
                props = [prop_dict[pid].name for pid in s.required_prop_ids]
                print(f"  Strip {s.scene_number:<4} | Part {s.part} | {s.setting} {s.time_of_day:<5} | "
                      f"Dur: {s.duration_hours}h | Sound: {s.sound_recording:<10} | Props: {', '.join(props) if props else 'None'} | Cast: {', '.join(cast_names)}")
            print("")

        # DOOD Report
        print("--- DAY OUT OF DAYS (DOOD) REPORT ---")
        header = f"{'Talent Name':<20}" + "".join([f"D{d:<3}" for d in range(1, num_days + 1)]) + " Total Paid"
        print(header)
        print("-" * len(header))

        for t in data.talents:
            row_str = f"{t.name:<20}"
            scenes_with_t = scenes_by_talent[t.id]
            if not scenes_with_t or t.id not in earliest:
                print(f"{row_str}{' .  ' * num_days} 0 days")
                continue

            e_val = solver.Value(earliest[t.id])
            l_val = solver.Value(latest[t.id])
            paid_count = 0

            for d in range(1, num_days + 1):
                is_working = (t.id, d) in talent_work and solver.Value(talent_work[t.id, d]) == 1
                if d < e_val or d > l_val:
                    row_str += " .  "
                elif d == e_val and d == l_val:
                    row_str += "SWF "
                    paid_count += 1
                elif d == e_val:
                    row_str += "SW  "
                    paid_count += 1
                elif d == l_val:
                    row_str += "WF  "
                    paid_count += 1
                elif is_working:
                    row_str += "W   "
                    paid_count += 1
                else:
                    row_str += "H   "
                    paid_count += 1
            print(f"{row_str} {paid_count} days")
        print("")

        # Algorithmic Call Sheet for Day 1
        target_day = 1
        if scheduled_day_scenes.get(target_day):
            generate_daily_call_sheet(
                data, target_day, scheduled_day_scenes[target_day],
                calendar_dict[target_day], location_dict, talent_dict
            )
    else:
        print("No feasible shooting schedule found within the specified constraint envelope.")

# ==============================================================================
# 3. ALGORITHMIC CALL SHEET GENERATOR
# ==============================================================================

def generate_daily_call_sheet(data: ProductionDataset, day_num: int, scenes: List[Scene],
                              cal: CalendarDay, locations: Dict[int, Location], talents: Dict[int, Talent]):
    print("================================================================================")
    print(f"OFFICIAL DAILY CALL SHEET: DAY {day_num} OF {data.max_shooting_days}")
    print(f"PRODUCTION: {data.project_title.upper()} | DATE: {cal.calendar_date}")
    print(f"SUNRISE: {cal.sunrise_time} | SUNSET: {cal.sunset_time} | WEATHER: {cal.expected_weather}")
    print("NEAREST EMERGENCY HOSPITAL: St. Jude Medical Center, 24/7 Trauma Wing (Tel: 555-0199)")
    print("================================================================================")

    general_crew_call = datetime.strptime("07:00", "%H:%M")
    shooting_call = datetime.strptime("08:00", "%H:%M")

    print(f"GENERAL CREW CALL: {general_crew_call.strftime('%I:%M %p')}")
    print(f"SHOOTING CALL:     {shooting_call.strftime('%I:%M %p')}")
    print(f"FIRST MEAL DUE:    {(general_crew_call + timedelta(hours=6)).strftime('%I:%M %p')}")
    print("--------------------------------------------------------------------------------")

    current_time = shooting_call
    scene_schedule = []
    cast_first_seen: Dict[int, datetime] = {}

    for s in scenes:
        start_t = current_time
        end_t = start_t + timedelta(hours=s.duration_hours)
        scene_schedule.append((s, start_t, end_t))
        for cid in s.required_cast:
            if cid not in cast_first_seen:
                cast_first_seen[cid] = start_t
        current_time = end_t

    print("SHOOTING SCHEDULE:")
    print(f"{'Time':<18} | {'Scn':<5} | {'Setting':<10} | {'Description / Location':<30} | {'Pages'}")
    print("-" * 80)
    for s, st, et in scene_schedule:
        cast_ids = ", ".join(f"[{cid}]" for cid in s.required_cast)
        loc_str = locations[s.location_id].name
        time_block = f"{st.strftime('%I:%M %p')} - {et.strftime('%I:%M %p')}"
        print(f"{time_block:<18} | {s.scene_number:<5} | {s.setting} {s.time_of_day:<6} | {loc_str[:18]} Cast: {cast_ids:<6} | {s.page_eighths}/8")
    print("--------------------------------------------------------------------------------")

    print("CHARACTER & TALENT CALL MATRIX:")
    print(f"{'ID':<4} | {'Character':<15} | {'Actor':<18} | {'Pickup':<8} | {'HMU':<8} | {'Wardrobe':<8} | {'On Set'}")
    print("-" * 80)

    for cid, first_scene_time in cast_first_seen.items():
        t = talents[cid]
        set_call = first_scene_time - timedelta(minutes=15)
        wardrobe_call = set_call - timedelta(minutes=t.wardrobe_duration_minutes)
        hmu_call = wardrobe_call - timedelta(minutes=t.hmu_duration_minutes)
        pickup_call = hmu_call - timedelta(minutes=t.travel_duration_minutes)

        print(f"[{t.id:<2}] | {t.character_name:<15} | {t.name:<18} | "
              f"{pickup_call.strftime('%I:%M %p')} | {hmu_call.strftime('%I:%M %p')} | "
              f"{wardrobe_call.strftime('%I:%M %p')} | {set_call.strftime('%I:%M %p')}")
    print("================================================================================\n")

if __name__ == "__main__":
    sample_dataset_json = """
    {
        "project_title": "The Chronicles of Eternity (Parts 1 & 2)",
        "talents": [
            {"id": 1, "name": "Marcus Vance", "character_name": "Commander Reyes", "daily_rate": 8000.0, "is_minor": false, "max_daily_hours": 12.0, "hmu_duration_minutes": 60, "wardrobe_duration_minutes": 30, "travel_duration_minutes": 45, "blackout_days": []},
            {"id": 2, "name": "Elena Rostova", "character_name": "Dr. Aris", "daily_rate": 5500.0, "is_minor": false, "max_daily_hours": 12.0, "hmu_duration_minutes": 45, "wardrobe_duration_minutes": 20, "travel_duration_minutes": 30, "blackout_days": []},
            {"id": 3, "name": "Leo Sterling", "character_name": "Young Toby", "daily_rate": 2000.0, "is_minor": true, "max_daily_hours": 5.0, "hmu_duration_minutes": 30, "wardrobe_duration_minutes": 15, "travel_duration_minutes": 30, "blackout_days": []}
        ],
        "locations": [
            {"id": 1, "name": "Soundstage 4 (Palace)", "location_type": "SOUNDSTAGE", "permitted_days": [1, 2, 3, 4, 5], "noise_curfew_hour": null, "allows_sync_sound": true, "daily_rental_cost": 2500.0, "prep_days_required": 1, "strike_days_required": 1},
            {"id": 2, "name": "Dune Practical Ridge", "location_type": "PRACTICAL_EXT", "permitted_days": [1, 2, 5], "noise_curfew_hour": 22, "allows_sync_sound": false, "daily_rental_cost": 1200.0, "prep_days_required": 0, "strike_days_required": 0},
            {"id": 3, "name": "Municipal Bank Vault", "location_type": "PRACTICAL_INT", "permitted_days": [5], "noise_curfew_hour": 20, "allows_sync_sound": true, "daily_rental_cost": 3000.0, "prep_days_required": 1, "strike_days_required": 1}
        ],
        "props": [
            {"id": 1, "name": "Laser Map", "category": "HERO", "total_quantity": 2, "is_destructible": false, "requires_armorer": false, "reset_duration_minutes": 0},
            {"id": 2, "name": "Stunt Glass Bottle", "category": "BREAKAWAY", "total_quantity": 4, "is_destructible": true, "requires_armorer": false, "reset_duration_minutes": 15},
            {"id": 3, "name": "Plasma Blaster", "category": "WEAPON", "total_quantity": 3, "is_destructible": false, "requires_armorer": true, "reset_duration_minutes": 0}
        ],
        "costumes": [
            {"id": 1, "character_id": 1, "costume_code": "REYES_PRISTINE", "distress_stage": 1, "available_duplicates": 2, "requires_specialist_dresser": false},
            {"id": 2, "character_id": 1, "costume_code": "REYES_DAMAGED",  "distress_stage": 3, "available_duplicates": 1, "requires_specialist_dresser": true}
        ],
        "equipment": [
            {"id": 1, "name": "50ft Technocrane", "equipment_type": "TECHNOCRANE", "daily_rental_cost": 3500.0, "rental_start_day": 1, "rental_end_day": 3, "requires_certified_technician": true}
        ],
        "stunts": [
            {"id": 1, "has_wirework": true, "has_pyrotechnics": false, "has_squibs": true, "pre_rigging_hours_required": 4.0, "mandatory_medic_count": 1}
        ],
        "calendar": [
            {"day_number": 1, "calendar_date": "2026-11-03", "is_statutory_holiday": false, "is_inauspicious": false, "expected_weather": "CLEAR", "sunrise_time": "06:12", "sunset_time": "18:22", "is_weekend": false},
            {"day_number": 2, "calendar_date": "2026-11-04", "is_statutory_holiday": false, "is_inauspicious": false, "expected_weather": "CLEAR", "sunrise_time": "06:13", "sunset_time": "18:21", "is_weekend": false},
            {"day_number": 3, "calendar_date": "2026-11-05", "is_statutory_holiday": false, "is_inauspicious": true,  "expected_weather": "CLEAR", "sunrise_time": "06:14", "sunset_time": "18:20", "is_weekend": false},
            {"day_number": 4, "calendar_date": "2026-11-06", "is_statutory_holiday": false, "is_inauspicious": false, "expected_weather": "RAIN",  "sunrise_time": "06:15", "sunset_time": "18:19", "is_weekend": false},
            {"day_number": 5, "calendar_date": "2026-11-07", "is_statutory_holiday": false, "is_inauspicious": false, "expected_weather": "CLEAR", "sunrise_time": "06:16", "sunset_time": "18:18", "is_weekend": true}
        ],
        "scenes": [
            {"id": 1, "scene_number": "10A", "part": 1, "location_id": 1, "setting": "INT", "time_of_day": "DAY", "page_eighths": 14, "duration_hours": 3.5, "required_cast": [1, 3], "required_prop_ids": [1], "required_costume_ids": [1], "required_equipment_ids": [1], "stunt_sfx_package_id": null, "weather_requirement": "ANY", "sound_recording": "SYNC_SOUND", "holiday_compatibility": "NORMAL", "earliest_allowed_day": 1, "latest_allowed_day": 5, "is_cover_set": false, "cover_for_scene_id": null, "requires_precedence_over": null},
            {"id": 2, "scene_number": "10B", "part": 2, "location_id": 1, "setting": "INT", "time_of_day": "DAY", "page_eighths": 10, "duration_hours": 2.5, "required_cast": [1], "required_prop_ids": [1], "required_costume_ids": [1], "required_equipment_ids": [1], "stunt_sfx_package_id": null, "weather_requirement": "ANY", "sound_recording": "SYNC_SOUND", "holiday_compatibility": "NORMAL", "earliest_allowed_day": 1, "latest_allowed_day": 5, "is_cover_set": false, "cover_for_scene_id": null, "requires_precedence_over": null},
            {"id": 3, "scene_number": "22",  "part": 1, "location_id": 2, "setting": "EXT", "time_of_day": "DAY", "page_eighths": 22, "duration_hours": 4.0, "required_cast": [1, 2], "required_prop_ids": [3], "required_costume_ids": [1], "required_equipment_ids": [], "stunt_sfx_package_id": null, "weather_requirement": "NO_RAIN", "sound_recording": "MOS", "holiday_compatibility": "NORMAL", "earliest_allowed_day": 1, "latest_allowed_day": 5, "is_cover_set": false, "cover_for_scene_id": null, "requires_precedence_over": null},
            {"id": 4, "scene_number": "45",  "part": 2, "location_id": 1, "setting": "INT", "time_of_day": "NIGHT", "page_eighths": 18, "duration_hours": 4.5, "required_cast": [1, 2], "required_prop_ids": [2], "required_costume_ids": [2], "required_equipment_ids": [], "stunt_sfx_package_id": 1, "weather_requirement": "ANY", "sound_recording": "SYNC_SOUND", "holiday_compatibility": "NORMAL", "earliest_allowed_day": 1, "latest_allowed_day": 5, "is_cover_set": false, "cover_for_scene_id": null, "requires_precedence_over": null},
            {"id": 5, "scene_number": "80",  "part": 1, "location_id": 3, "setting": "INT", "time_of_day": "DAY", "page_eighths": 16, "duration_hours": 3.5, "required_cast": [2], "required_prop_ids": [], "required_costume_ids": [], "required_equipment_ids": [], "stunt_sfx_package_id": null, "weather_requirement": "ANY", "sound_recording": "SYNC_SOUND", "holiday_compatibility": "NORMAL", "earliest_allowed_day": 5, "latest_allowed_day": 5, "is_cover_set": false, "cover_for_scene_id": null, "requires_precedence_over": null}
        ],
        "max_shooting_days": 5,
        "max_hours_per_day": 10.0
    }
    """
    dataset = msgspec.json.decode(sample_dataset_json.encode("utf-8"), type=ProductionDataset)
    build_and_solve_schedule(dataset)
```

## 7. Operational Risk Mitigation and Rescheduling Dynamics

A mathematically optimal schedule remains theoretical until deployed on a live production set11. Real-world filming introduces constant volatility, requiring automated fallback plans built directly into the operational model3.
When unpredictable weather threatens an exterior shoot, the production shifts to a pre-planned cover set3. The Unit Production Manager and 1st Assistant Director activate a pre-lit interior soundstage or controlled practical location in the same geographical zone, minimizing lost time3.
This shift triggers a rolling-horizon re-optimization in the CP-SAT engine. The solver locks in past and completed shooting days as fixed constants, while unfilmed scenes are released back into the scheduling pool. The system then re-evaluates the schedule against constraints like child performer daily work limits and the SAG-AFTRA ten-day Drop-and-Pickup rule, generating updated call sheets and stripboards without violating union contracts10.

### Cover Sets and Meteorological Contingencies

To satisfy completion bond requirements on exterior-heavy productions, schedules must include interior cover sets3. A cover set is an interior scene—typically on a permanent soundstage or controlled practical interior—that can be activated when weather disrupts an exterior shoot3.
In CP-SAT, cover sets are modeled as optional interval variables that share cast and crew requirements with scheduled exterior scenes47. When a weather alert is logged, the solver deactivates the exterior interval variable and activates the corresponding cover set variable, updating subsequent daily calls while keeping talent hold days within legal limits10.

### Dynamic Rescheduling Under Operational Set Disruptions

Principal photography often faces unexpected disruptions, such as cast illness, transit delays, damaged equipment, or sudden location permit issues16. Rather than manually rebuilding the schedule from scratch, the CP-SAT solver operates in a rolling-horizon or warm-restart mode:

1. **State Preservation:** All elapsed production days $1, \dots, d - 1$ are marked immutable, fixing their historical scene assignments and costs.
2. **Dynamic Unassignment:** Uncompleted scenes from day $d$ are returned to the unassigned pool.
3. **Constraint Injection:** New operational restrictions—such as a performer being unavailable for 48 hours—are added as temporary hard bounds.
4. **Targeted Re-Optimization:** The solver runs with a restricted time window (e.g., 5 to 10 seconds), finding an optimal solution that minimizes disruptions to the existing stripboard order, protecting downstream equipment rentals, soundstage bookings, and travel arrangements6.

## 8. Conclusions and Operational Synthesis

Film production scheduling is an intricate logistical challenge that benefits significantly from mathematical optimization1. By formalizing physical scene requirements alongside guild rules, child labor laws, and cross-boarding dependencies, production teams can systematically reduce financial waste and protect cast and crew well-being1.
Incorporating complex labor rules—such as the SAG-AFTRA 10-day Drop-and-Pickup threshold and IATSE forced-call penalties—directly into the objective function prevents unintended talent hold costs, saving productions significant capital10. In multi-part franchises, cross-boarding by location optimizes soundstage rentals and practical set lifecycles5. When working with young performers, cross-boarding across sequels avoids visible aging discontinuities that could otherwise undermine narrative consistency31.
Modern software tools make this computational approach practical on set. Combining uv for environment management, msgspec for fast schema decoding, and Google OR-Tools CP-SAT for constraint satisfaction delivers a high-performance optimization pipeline38. The CP-SAT solver efficiently manages discrete interval variables, daily work capacities, and location changeovers, generating balanced production stripboards, accurate Day Out of Days reports, and precise daily call sheets in seconds3. Adopting these operational research techniques enables studios, line producers, and independent filmmakers to protect their creative vision while maintaining strict control over schedule and budget constraints3.

### Works Cited

1. Talent scheduling - Wikipedia, [https://en.wikipedia.org/wiki/Talent_scheduling](https://en.wikipedia.org/wiki/Talent_scheduling)
2. Domain-Independent Dynamic Programming by Ryo Kuroiwa, [https://tidel.mie.utoronto.ca/pubs/Theses/Kuroiwa_Ryo_20249_PhD_thesis.pdf](https://tidel.mie.utoronto.ca/pubs/Theses/Kuroiwa_Ryo_20249_PhD_thesis.pdf)
3. Production Board for Film: Build Your Stripboard and Shooting, [https://www.drawstory.ai/blog/film-production-board](https://www.drawstory.ai/blog/film-production-board)
4. Free Script Breakdown Sheet Template - ScenePaper, [https://scenepaper.com/templates/script-breakdown-sheet](https://scenepaper.com/templates/script-breakdown-sheet)
5. In film production scheduling, what are shooting blocks? - Reddit, [https://www.reddit.com/r/Filmmakers/comments/149jnbh/in_film_production_scheduling_what_are_shooting/](https://www.reddit.com/r/Filmmakers/comments/149jnbh/in_film_production_scheduling_what_are_shooting/)
6. Line Producer in Mumbai | Budget, Crew & Studios - Celluloid Pact, [https://celluloidpact.com/film-fixers-line-producer-in-mumbai/](https://celluloidpact.com/film-fixers-line-producer-in-mumbai/)
7. Dynamic job-shop scheduling with sequence-dependent setup times, [https://www.researchgate.net/publication/226219690_Dynamic_job-shop_scheduling_with_sequence-dependent_setup_times_Simulation_modeling_and_analysis](https://www.researchgate.net/publication/226219690_Dynamic_job-shop_scheduling_with_sequence-dependent_setup_times_Simulation_modeling_and_analysis)
8. Research on the Scheduling Problem of Movie Scenes, [https://www.researchgate.net/publication/330853083_Research_on_the_Scheduling_Problem_of_Movie_Scenes](https://www.researchgate.net/publication/330853083_Research_on_the_Scheduling_Problem_of_Movie_Scenes)
9. Talent scheduling with daily working capacity and scene, [https://ideas.repec.org/a/eee/jomega/v138y2026ics0305048325001653.html](https://ideas.repec.org/a/eee/jomega/v138y2026ics0305048325001653.html)
10. Drop and pickup: Meaning in Film Production | Storiara, [https://storiara.com/glossary/drop-pickup](https://storiara.com/glossary/drop-pickup)
11. Completion Bonds - Film Finances Scandinavia, [https://www.filmfinances.se/completion-bonds](https://www.filmfinances.se/completion-bonds)
12. Call time: Meaning in Film Production | Storiara, [https://storiara.com/glossary/call-time](https://storiara.com/glossary/call-time)
13. Exploiting Functional Constraints in Automatic Dominance Breaking, [https://www.jair.org/index.php/jair/article/download/14714/26965/35881](https://www.jair.org/index.php/jair/article/download/14714/26965/35881)
14. Call Sheet Guide: Everything Filmmakers Need to Know, [https://filmmakergenius.com/blog/call-sheet-guide-everything-filmmakers-need-to-know](https://filmmakergenius.com/blog/call-sheet-guide-everything-filmmakers-need-to-know)
15. What is a Call Sheet — Everything You Need to Know - StudioBinder, [https://www.studiobinder.com/blog/what-is-a-call-sheet/](https://www.studiobinder.com/blog/what-is-a-call-sheet/)
16. Steven Soderbergh Film School: Filmmaking Techniques Behind, [https://blog.studiovity.com/steven-soderbergh-film-school/](https://blog.studiovity.com/steven-soderbergh-film-school/)
17. Script Breakdown Elements — The Complete Guide - StudioBinder, [https://www.studiobinder.com/blog/the-complete-guide-to-mastering-script-breakdown-elements/](https://www.studiobinder.com/blog/the-complete-guide-to-mastering-script-breakdown-elements/)
18. Acting Glossary - Talent Consult LA, [https://talentconsultla.com/acting-glossary](https://talentconsultla.com/acting-glossary)
19. Film Production Completion Bond - Allen Financial Insurance Group, [https://www.eqgroup.com/completion_bond/](https://www.eqgroup.com/completion_bond/)
20. How To Bond a Film: A Definitive Guide to Completion Bonds, [https://www.mediaservices.com/blog/how-to-bond-a-film-a-definitive-guide-to-completion-bonds/](https://www.mediaservices.com/blog/how-to-bond-a-film-a-definitive-guide-to-completion-bonds/)
21. Labor Law Archives – Southern California Law Review, [https://southerncalifornialawreview.com/tag/labor-law/](https://southerncalifornialawreview.com/tag/labor-law/)
22. SAMPLE Version 3 2023 Interim Agreement - TV/Theatrical - sag-aftra, [https://www.sagaftra.org/sites/default/files/sa_documents/SAMPLE%20Interim%20Agreement%20-%20TV_Theatrical.pdf](https://www.sagaftra.org/sites/default/files/sa_documents/SAMPLE%20Interim%20Agreement%20-%20TV_Theatrical.pdf)
23. Set Safety Handbook | Towson University, [https://www.towson.edu/cofac/departments/film-audio-media/resources/documents/set-safety-handbook.pdf](https://www.towson.edu/cofac/departments/film-audio-media/resources/documents/set-safety-handbook.pdf)
24. Rakhi Sawant Backs Ranveer Singh, Challenges FWICE Over Non, [https://www.bumppy.com/news/they-are-jealous-of-him-rakhi-sawant-backs-ranveer-singh-challenges-fwice-over-non-cooperation-ban](https://www.bumppy.com/news/they-are-jealous-of-him-rakhi-sawant-backs-ranveer-singh-challenges-fwice-over-non-cooperation-ban)
25. What Is a Day Out of Days (DOOD) Report? | Lowerated, [https://www.lowerated.com/post/day-out-of-days-report](https://www.lowerated.com/post/day-out-of-days-report)
26. Online School for Actors and Performers: State Rules, [https://foresttrailacademy.com/online-school-actors-performers/](https://foresttrailacademy.com/online-school-actors-performers/)
27. why isn't children acting considered child labour? - Reddit, [https://www.reddit.com/r/NoStupidQuestions/comments/wpvegr/why_isnt_children_acting_considered_child_labour/](https://www.reddit.com/r/NoStupidQuestions/comments/wpvegr/why_isnt_children_acting_considered_child_labour/)
28. Reading a day out of days without guessing - TillyBoard, [https://www.tillyboard.com/glossary/day-out-of-days](https://www.tillyboard.com/glossary/day-out-of-days)
29. How to Make a Call Sheet (With a Template) | Lowerated, [https://www.lowerated.com/post/how-to-make-a-call-sheet](https://www.lowerated.com/post/how-to-make-a-call-sheet)
30. What is a Call Sheet? (Free Guide & Template), [https://www.prodigium-pictures.com/blog/call-sheet](https://www.prodigium-pictures.com/blog/call-sheet)
31. James Cameron on Avatar sequels & child actor growth spurts - SYFY, [https://www.syfy.com/syfy-wire/james-cameron-avatar-sequels-account-for-child-actor-growth-spurts](https://www.syfy.com/syfy-wire/james-cameron-avatar-sequels-account-for-child-actor-growth-spurts)
32. James Cameron says Stranger Things issue prompted Avatar, [https://www.independent.co.uk/arts-entertainment/films/news/james-cameron-avatar-films-stranger-things-b2251074.html](https://www.independent.co.uk/arts-entertainment/films/news/james-cameron-avatar-films-stranger-things-b2251074.html)
33. James Cameron shot 'Avatar' sequels back-to-back, didn't want child, [https://malaysia.news.yahoo.com/james-cameron-shot-avatar-sequels-044919117.html](https://malaysia.news.yahoo.com/james-cameron-shot-avatar-sequels-044919117.html)
34. 'Avatar 3' And 'Avatar 4' Scenes Already Shot To Avoid 'Stranger, [https://www.reddit.com/r/entertainment/comments/zsccqz/avatar_3_and_avatar_4_scenes_already_shot_to/](https://www.reddit.com/r/entertainment/comments/zsccqz/avatar_3_and_avatar_4_scenes_already_shot_to/)
35. 'Avatar 3' And 'Avatar 4' Scenes Already Shot To Avoid 'Stranger, [https://www.reddit.com/r/boxoffice/comments/zsjcx7/avatar_3_and_avatar_4_scenes_already_shot_to/](https://www.reddit.com/r/boxoffice/comments/zsjcx7/avatar_3_and_avatar_4_scenes_already_shot_to/)
36. Latest Avatar 4 News And Rumors - Giant Freakin Robot, [https://www.giantfreakinrobot.com/topic/avatar-4](https://www.giantfreakinrobot.com/topic/avatar-4)
37. Avatar 2: James Cameron explains avoiding “Stranger Things effect, [https://www.dexerto.com/tv-movies/avatar-2-james-cameron-explains-avoiding-stranger-things-effect-with-sequels-2016245/](https://www.dexerto.com/tv-movies/avatar-2-james-cameron-explains-avoiding-stranger-things-effect-with-sequels-2016245/)
38. GitHub - msgspec/msgspec: A fast serialization and validation library, [https://github.com/msgspec/msgspec](https://github.com/msgspec/msgspec)
39. msgspec - PyPI, [https://pypi.org/project/msgspec/0.6.0/](https://pypi.org/project/msgspec/0.6.0/)
40. Fast JSON Validation with msgspec in Python | 2026 - YouTube, [https://www.youtube.com/watch?v=eHtkUvZGxBs](https://www.youtube.com/watch?v=eHtkUvZGxBs)
41. Well, that escalated quickly: OR-Tools - Solver Max, [https://www.solvermax.com/blog/well-that-escalated-quickly-or-tools](https://www.solvermax.com/blog/well-that-escalated-quickly-or-tools)
42. OR-Tools, [https://egon.cheme.cmu.edu/ewo/docs/CP-SAT%20and%20OR-Tools.pdf](https://egon.cheme.cmu.edu/ewo/docs/CP-SAT%20and%20OR-Tools.pdf)
43. Optimizing ortools cp-sat for best speed - Stack Overflow, [https://stackoverflow.com/questions/76170228/optimizing-ortools-cp-sat-for-best-speed](https://stackoverflow.com/questions/76170228/optimizing-ortools-cp-sat-for-best-speed)
44. CP-SAT Solver | OR-Tools - Google for Developers, [https://developers.google.com/optimization/cp/cp_solver](https://developers.google.com/optimization/cp/cp_solver)
45. (PDF) Towards Modern and Modular SAT for LCG - ResearchGate, [https://www.researchgate.net/publication/392722924_Towards_Modern_and_Modular_SAT_for_LCG](https://www.researchgate.net/publication/392722924_Towards_Modern_and_Modular_SAT_for_LCG)
46. uv: A Complete Guide to Python's Fastest Package Manager, [https://pydevtools.com/handbook/explanation/uv-complete-guide/](https://pydevtools.com/handbook/explanation/uv-complete-guide/)
47. or-tools/ortools/sat/docs/scheduling.md at stable - GitHub, [https://github.com/google/or-tools/blob/stable/ortools/sat/docs/scheduling.md](https://github.com/google/or-tools/blob/stable/ortools/sat/docs/scheduling.md)
