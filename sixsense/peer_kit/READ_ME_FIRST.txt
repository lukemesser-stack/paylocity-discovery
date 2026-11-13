TARGET NOW: YOUR OWN 6SENSE CALL DASHBOARD
Setup takes about 10 minutes. You need: a paid Claude plan (with Claude Code at
claude.ai/code), ZoomInfo and BenefitFlow, and 6sense Hot Accounts alert emails.
The full guide with a tour of the page is Target_Now_Setup_Guide.docx.

WHAT YOU GET
A private web page (your own link) that ranks your accounts by who to call today, with
ZoomInfo intent, news, new leaders and contacts, and BenefitFlow renewal dates, broker,
carrier and buyers. It saves itself, and you can share it view-only with your SDR.
It starts empty. None of the original owner's data is in it.

SETUP
1. Connect ZoomInfo and BenefitFlow in Claude: claude.ai -> Settings -> Connectors.
   Keep their names exactly "ZoomInfo" and "BenefitFlow".

2. Open Claude Code at claude.ai/code and start a new session (no repository needed).

3. Attach Target_Now_Starter.html, paste the prompt below, and approve the publish when
   Claude asks. (Tip: double-click Target_Now_Starter.html to open it in your browser.
   It shows these steps and has a "Copy prompt" button.)

   ---- copy from here ----
   Publish the attached file Target_Now_Starter.html as a new artifact for me, exactly as it is (do not edit, rewrite or redesign it).
   - Title: Target Now
   - Icon: chart
   - Capabilities (pass exactly this):
   {"artifact":{},"downloads":{},"user":{},"sample":{},"mcp":{"servers":[{"server":"ZoomInfo","tools":["search_companies","enrich_company_signals","search_contacts","enrich_companies","lookup"]},{"server":"BenefitFlow","tools":["search_employers","search_contacts","get_contact"]}]}}
   When it is published, give me the link.
   ---- to here ----

4. Open the link Claude gives you. That's your dashboard. Bookmark it.

5. Load your first emails: drag a few 6sense alert emails from Outlook to your desktop
   (they save as .msg files), click "⬆ Import" (top right), drop them in, click "Apply".
   The first time, Claude asks to allow ZoomInfo and BenefitFlow for the page: choose
   Allow. Keep the page open a minute or two while they fill in.

6. Share with your SDR (optional): Share -> anyone with the link, then send the link.
   They can view everything but can't change your data.

DAY TO DAY
- Open the dashboard. The first open each day refreshes ZoomInfo for your hottest
  accounts by itself (free accounts only).
- "⬆ Import" the new 6sense email, plus any ZoomInfo weekly digest or ZoomInfo 🚨 alert
  emails (key contact visits, leadership changes, competitor research). Emails already
  loaded are skipped.
- Work "Call today". Click an account for Call prep: why now, who to call, openers.
- Mark "Worked" after you reach out. Keep logging activity in Salesforce as usual.
- 🎨 Look (top right): light/dark and colour. Saved in each person's own browser.
- Once a week: ⚙ Owner -> 💾 Save JSON backup, and keep the file.

CREDITS
Everything automatic is free. Anything that costs ZoomInfo or BenefitFlow credits
(a company not under management, "Get email / phone") asks for a second click first.
The optional ✨ AI openers button uses your own Claude usage; nothing else uses AI.

IF SOMETHING LOOKS OFF
- ZoomInfo or BenefitFlow buttons greyed out: check both connectors (step 1), with those
  exact names, then reload and choose Allow if asked.
- Claude won't publish: make sure you're in Claude Code (claude.ai/code), not a chat.
  If it says "sample" isn't available on your plan, ask it to publish without "sample"
  (only the ✨ AI openers button stops working).
- "Already loaded" / "Not on the dashboard, skipped": nothing is wrong. See the guide.
- Want the dashboard changed? See "Getting Claude to change or update your dashboard"
  in the guide for the block to paste into Claude Code first.
