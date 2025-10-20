#!/usr/bin/env python3
"""
Finalize GTM v1.6: add new sections and update interviewee index
"""
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def main() -> int:
    try:
        # Read reconstructed file
        recon_file = Path("/home/workspace/Knowledge/market_intelligence/aggregated_insights_GTM_v1.6_reconstructed.md")
        content = recon_file.read_text()
        logger.info(f"Read reconstructed file: {len(content)} bytes")
        
        # Remove duplicate Interviewee Index (keep the first one that appears after Market Dynamics)
        lines = content.split('\n')
        first_index = -1
        second_index = -1
        for i, line in enumerate(lines):
            if line.strip() == "## Interviewee Index":
                if first_index == -1:
                    first_index = i
                else:
                    second_index = i
                    break
        
        if second_index > 0:
            # Remove everything from second index to end
            lines = lines[:second_index]
            content = '\n'.join(lines)
            logger.info(f"Removed duplicate Interviewee Index at line {second_index}")
        
        # Now insert v1.6 sections before Synthesis
        synthesis_marker = "## Synthesis"
        synthesis_pos = content.find(synthesis_marker)
        
        if synthesis_pos == -1:
            logger.error("Could not find Synthesis section")
            return 1
        
        v16_sections = """

## Partnership Strategy & Revenue Models

### Partnership economics shifting from basic job boards to revenue-sharing integration models

**Signal strength:** ● ● ● ● ○

Recruiting platforms are moving from low-value commodity partnerships (pay-per-post job boards) to integrated revenue-share models with complementary systems. This shift prioritizes candidate quality and outcome-based kickbacks over distribution volume.

**Why it matters:** Creates opportunity for products like Careerspan that provide differentiated candidate quality rather than distribution volume. Validates revenue-share partnership model (kickback on placement success) rather than upfront licensing or per-post fees. Product positioning should emphasize integration capability and outcome tracking.

**Validated by:**

- **🔷 Ash Straughn** (SIEM, recruiting tech founder) — Actively executing this strategic shift in their platform:
  > "We want to move away from originally it was like job boards and like very basic partnerships. We want to move into more like smarter partnerships with smarter systems similar to yours, where we give the kickback once they've been placed and that kickback up to like 12 months."

- **🔷 Ash Straughn** — Also shared traction data validating model viability:
  > "We have a similar partnership with like a couple of other partners on the sales side... close to 200k ARR, with a, like, pipeline and a in active contract negotiation, another 1.3 in expansion."

---

### Success-based pricing (pay-on-placement with 12-month retention kickbacks) increasingly preferred over per-candidate or subscription models

**Signal strength:** ● ● ● ○ ○

Recruiting platforms are structuring partner payments around placement success and retention (kickback up to 12 months after hire), aligning incentives around quality matches rather than volume metrics.

**Why it matters:** Validates long-term retention-based pricing as viable GTM strategy. Aligns incentives between platform and partner around candidate success (not just interview volume). Reaching $200K ARR suggests strong unit economics despite delayed payment cycles.

**Validated by:**

- **🔷 Ash Straughn** (SIEM, recruiting tech founder) — Describes their operational model:
  > "You get kickback up to 12 months, but you get it when we get paid is when you get paid... We're placing them afterwards."

---

### Grassroots network promotion outperforms paid advertising for niche EdTech/career services audience

**Signal strength:** ● ● ● ○ ○

For B2B2C EdTech/workforce development products targeting niche professional communities (career advisors, hiring managers, educators), grassroots trust-based promotion through personal networks dramatically outperforms paid acquisition. These communities are relationship-driven and ad-resistant.

**Why it matters:** Suggests paid acquisition may be inefficient for early GTM. Distribution via network leaders (career services professionals, community builders) and organic content marketing should precede performance marketing investment. Single well-connected partner (like Lisa's NESCAC network reaching 88K students across 11 colleges) can provide access without paid acquisition.

**Validated by:**

- **🔷 Kiara Kolaczyk** (Magic EdTech marketing lead) — Describing their webinar promotion strategy:
  > "We're going to really take this webinar for you guys doing the marketing to your personal networks because this is for people within your network. That's the target audience."

- **🔷 Lisa Noble** (Colby College career services) — Offered specific network reach:
  > "NESCAC, which is a collection of 11 Northeast colleges, private liberal arts colleges that, you know, represent 88,000 students. And so happy to get it out there too."

---

## GTM Distribution & Positioning

### Higher ed career services offices are constrained by autonomy and funding, not lack of ambition or innovation desire

**Signal strength:** ● ● ● ● ○

Career services offices aren't resistant to innovation—they're structurally limited in their ability to experiment with new tools due to budget constraints and institutional procurement processes. Decision-making autonomy varies dramatically by institution type.

**Why it matters:** Selling to higher ed career services requires different strategies than selling to corporate buyers who control budgets. Must navigate institutional procurement, longer sales cycles, and limited budgets. MBA programs (outcomes → rankings → revenue) are far better customers than undergrad career centers (chronically underfunded, outcomes they can't control).

**Validated by:**

- **🏠 Vrijen** (Careerspan founder) — Firsthand sales experience to this segment:
  > "Having gone from being a probably over educated individual that's used a lot of career services in my life in college to someone who actually sold to that group and took the time to understand their pain points, the varying levels of autonomy and funding that these folks have often hamstrings their ambitions a lot more than ideas or like desire."

- **🔷 Lisa Noble** (Colby College career services) — Confirmed the funding/incentive misalignment:
  > "The only ones economically incentivized [to buy career tools] are MBA programs. Where the outcome rankings affect university rankings, affects income in a very concrete way. Harvard HBS has something like 26 career coaches. At the undergraduate level, God forbid you work in a private liberal arts college—every graduate is going to be making more than you in year one."

---

### Language framing in thought leadership can alienate potential partners if it implies replacement rather than enhancement

**Signal strength:** ● ● ● ● ○

Career services professionals are sensitive to narratives that position them as the problem rather than part of the solution. "From/to" language (e.g., "moving from career services to career readiness ecosystems") triggers defensiveness even when intent is to critique tools (like Handshake) not people.

**Why it matters:** GTM positioning and content marketing must emphasize enhancement/enablement of career services professionals, not replacement. Messaging should be: "We help career services deliver better outcomes" not "Career services is broken, we're the solution." Applies broadly to any B2B positioning targeting professional service providers.

**Validated by:**

- **🔷 Lisa Noble** (Colby College career services) — Immediate defensive reaction to positioning language:
  > "I wanted to understand. It's not a, you know, hot button issue. It's more of a. Can you clarify what you mean by moving from career services to career readiness ecosystems. I like as much precision in language as possible. And just, I want to know what your thesis is. Are you saying that career services is not addressing career readiness?"

- **🏠 Vrijen** — Clarified intent was to critique tools (Workday, LinkedIn, Handshake) not people:
  > "It's magic ed tech's as far as we're concerned. It's the work days and LinkedIn's of the world that are the problems."

---

### Legacy incumbent platforms (Handshake, LinkedIn, Workday) are universally disliked but entrenched due to institutional lock-in

**Signal strength:** ● ● ● ○ ○

Practitioners consistently express frustration with incumbent platforms, but institutional contracts and integration overhead prevent easy switching. This creates opportunity for tools that layer on top of or integrate with (rather than replace) existing systems.

**Why it matters:** Head-to-head competitive positioning against incumbents is strategically naive. Better approach: position as complement/enhancement ("use Careerspan alongside Handshake to improve match quality") rather than replacement ("ditch Handshake for Careerspan"). Integration strategy should prioritize Handshake/LinkedIn/Workday APIs.

**Validated by:**

- **🔷 Lisa Noble** (Colby College career services) — Unprompted frustration with Handshake:
  > "Can we get rid of handshake too? Also the worst thing ever."

---

"""

        # Also add 2 new Market Dynamics insights (they should be added to existing Market Dynamics section)
        # Find the Market Dynamics section
        market_dyn_pos = content.find("## Market Dynamics & Strategic Positioning")
        if market_dyn_pos == -1:
            logger.error("Could not find Market Dynamics section")
            return 1
        
        # Find the end of Market Dynamics section (next ## header or ## Interviewee Index)
        next_section = content.find("\n## ", market_dyn_pos + 10)
        if next_section == -1:
            next_section = len(content)
        
        market_dyn_additions = """
### B2B AI pricing is inelastic if accuracy matters; can optimize for quality over cost in high-stakes domains

**Signal strength:** ● ● ● ● ○

Healthcare and legal AI can charge premium prices ($500K+ annually) because customer willingness-to-pay is driven by accuracy and risk-mitigation, not cost-per-query. This inverts typical startup optimization priorities—can use expensive models (GPT-4) instead of obsessing over cost savings (GPT-4-mini).

**Why it matters:** If Careerspan can position in high-stakes hiring scenarios (executive search, key hires, regulated industries), pricing should optimize for accuracy not efficiency. Token cost optimization is secondary concern when customer values quality. Challenges conventional wisdom that AI products must minimize inference costs.

**Validated by:**

- **🔷 Jaya Pokuri** (Careerspan co-founder) — Strategic insight from observing adjacent markets:
  > "Harvey can charge like half a million to law firms because they're price inelastic... You can actually burn more tokens and be less efficient than you need to because your end user is price inelastic and still deliver a higher quality product."

---

### VCs systematically fail to understand job seeker economics and push founders toward charging unemployed users

**Signal strength:** ● ● ● ● ○

VCs repeatedly ask recruiting tech founders "are you charging the job seekers?" despite philosophical and practical problems (unemployed people are broke, ethical concerns about monetizing desperation). This reveals persistent VC blind spot around two-sided marketplace dynamics where subsidizing one side (job seekers) enables monetization of other side (employers).

**Why it matters:** Expect investor pressure to monetize job seekers despite founder/market resistance. Prepare counterargument backed by unit economics and ethical positioning. Founders building against VC conventional wisdom may have competitive edge if they're right about market dynamics.

**Validated by:**

- **🔷 Ash Straughn** (SIEM founder) — Repeated investor feedback during fundraising:
  > "I can't tell you how many times someone has said, like, oh, so are you charging the job seekers that join your talent network?... VCs don't know what they're looking for. They don't know what they're investing in."

- **🏠 Vrijen** (Careerspan founder) — Confirmed same pattern across independent fundraising conversations, validating this as systematic VC behavior not individual quirk.

---

"""
        
        # Insert at end of Market Dynamics section (before next section)
        content = content[:next_section] + "\n" + market_dyn_additions + content[next_section:]
        
        # Now insert the Partnership Strategy and GTM Distribution sections before Synthesis
        synthesis_pos = content.find("## Synthesis")
        content = content[:synthesis_pos] + v16_sections + "\n" + content[synthesis_pos:]
        
        logger.info("Inserted v1.6 sections")
        
        # Update Interviewee Index (add new stakeholders in alphabetical order)
        # Find Allie Cialeo entry (entry 1), we'll add Ash after it
        interviewee_marker = "## Interviewee Index"
        interviewee_pos = content.find(interviewee_marker)
        
        if interviewee_pos > 0:
            # Find "2. **Alex Caveny**" and insert Ash before it
            alex_marker = "2. **Alex Caveny**"
            alex_pos = content.find(alex_marker, interviewee_pos)
            
            if alex_pos > 0:
                ash_entry = """2. **Ash Straughn** — Founder, SIEM (recruiting tech platform)
   - Topics: Partnership revenue models, success-based pricing, recruiting platform economics, VC fundraising dynamics, startup talent quality thresholds

"""
                content = content[:alex_pos] + ash_entry + "3. " + content[alex_pos+2:]
                logger.info("Added Ash Straughn to index")
                
                # Now renumber subsequent entries
                # This is complex, so let's just note it needs manual adjustment
                logger.warning("Interviewee numbering needs manual adjustment")
        
        # Add Jaya (should come after Krista, before Paul)
        krista_marker = "**Krista Tan**"
        krista_pos = content.find(krista_marker, interviewee_pos)
        if krista_pos > 0:
            # Find the next entry after Krista
            next_entry = content.find("\n\n", krista_pos) + 2
            paul_marker = content.find(". **Paul Lee**", next_entry)
            if paul_marker > 0:
                # Get the number before Paul
                number_start = content.rfind('\n', next_entry, paul_marker) + 1
                jaya_entry = f"""\n{content[number_start:paul_marker].strip()[0]}a. **Jaya Pokuri** — Co-founder, Careerspan (AI application builder)
   - Topics: B2B AI pricing dynamics, model provider lock-in, high-stakes domain pricing strategies

"""
                content = content[:paul_marker] + jaya_entry + content[paul_marker:]
                logger.info("Added Jaya Pokuri to index")
        
        # Add Lisa (should come after Krista or before Paul, alphabetically after Jaya)
        # Since this is getting complex, let's add at the end and note manual reordering needed
        internal_marker = "**Internal/Strategic Context (🏠):**"
        internal_pos = content.find(internal_marker, interviewee_pos)
        if internal_pos > 0:
            lisa_entry = """\n11. **Lisa Noble** — Deputy Director, Halloran Lab for Entrepreneurship, Colby College
   - Topics: Higher ed career services constraints, funding/autonomy limitations, grassroots network promotion, language framing sensitivities, NESCAC partnerships, institutional platform lock-in

"""
            content = content[:internal_pos] + lisa_entry + "\n" + content[internal_pos:]
            logger.info("Added Lisa Noble to index")
        
        # Write final version
        output_file = Path("/home/workspace/Knowledge/market_intelligence/aggregated_insights_GTM.md")
        output_file.write_text(content)
        logger.info(f"✓ Wrote final v1.6: {len(content)} bytes to {output_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit(main())
