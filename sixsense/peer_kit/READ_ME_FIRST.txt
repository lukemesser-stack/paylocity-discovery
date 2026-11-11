TARGET NOW: YOUR OWN 6SENSE CALL DASHBOARD
Setup takes about 5 minutes. You need: a paid Claude plan, ZoomInfo, and BenefitFlow.

WHAT YOU GET
A private web page (your own link) that ranks your 6sense hot accounts by who to call
today, with ZoomInfo intent, triggers, who to call, and BenefitFlow renewal dates,
broker and contacts. It saves itself, and you can share it view-only with your SDR.
It starts empty. None of the original owner's data is in it.

SETUP
1. Connect ZoomInfo and BenefitFlow in Claude:
   claude.ai -> Settings -> Connectors. Keep their names as "ZoomInfo" and "BenefitFlow".

2. Open Claude Code at claude.ai/code and start a new session (no repository needed).
   Attach Target_Now_Starter.html and paste the prompt below. Approve the publish when
   Claude asks. (Tip: double-click Target_Now_Starter.html to open it in your browser.
   It shows these same steps and has a "Copy prompt" button.)

   ---- copy from here ----
   Publish the attached file Target_Now_Starter.html as a new artifact for me, exactly as it is (do not edit, rewrite or redesign it).
   - Title: Target Now
   - Icon: chart
   - Capabilities (pass exactly this):
   {"artifact":{},"downloads":{},"user":{},"mcp":{"servers":[{"server":"ZoomInfo","tools":["search_companies","enrich_company_signals","search_contacts","enrich_companies"]},{"server":"BenefitFlow","tools":["search_employers","search_contacts","get_contact"]}]}}
   When it is published, give me the link.
   ---- to here ----

3. Open the link Claude gives you. That's your dashboard. Bookmark it.

4. Add your 6sense alert emails: drag them from Outlook to your desktop (they save as
   .msg files), click "Add emails" on the dashboard, drop them in, then click "Apply".
   The first time, Claude asks you to allow ZoomInfo and BenefitFlow for the page.
   Choose Allow.

5. Share with your SDR: on the dashboard page, Share -> anyone with the link
   (view only). Send them the link.

DAY TO DAY
- Each morning: add the new 6sense email and click Apply. ZoomInfo and BenefitFlow fill
  in by themselves for Call today, This week and Heating up accounts.
- Click a card (Call today, Heating up, Renewing soon...) to show just those accounts.
- Mark "Worked" after you reach out. The account steps aside for 7 days unless
  6sense shows new activity. Keep activity tracking in Salesforce as usual.
- "Get email + phone" on a contact: the first click is a free price check; the second
  click spends 1 BenefitFlow credit. Nothing that costs credits happens without that
  second click.
- The page's own buttons use no AI. Only ask Claude in chat when you want the
  dashboard itself changed.

IF SOMETHING LOOKS OFF
- No ZoomInfo or BenefitFlow buttons: check both are connected (step 1), with those
  exact names, then reload the page.
- An email says "already loaded": every account in it already has that day's activity.
- Claude says it can't publish with those capabilities: make sure you're in Claude Code
  (claude.ai/code), not a regular chat.
