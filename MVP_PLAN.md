# BSP AI — MVP Plan for Mechanical Engineering at Bicocca

## Product concept

Help students in the Mechanical Engineering degree at the University of Milano-Bicocca explore careers that fit their goals, and help the university identify where teaching could respond to changing employer needs.

An AI agent works with HR departments to analyze job-market evidence and provide reviewed insights to Bicocca administration and faculty. Students may also use those insights to explore optional course pathways.

AI supports evidence analysis, reporting, and draft creation. HR validates job-market interpretations; faculty and university governance retain authority over courses, teaching materials, and curriculum decisions.

## Recommended MVP

Pilot with **Bicocca's Mechanical Engineering degree**, participating HR partners, and relevant university career-service staff. Use a recent, curated sample of Mechanical Engineering job postings, the approved course catalog and teaching materials, and available career-service information.

The AI agent's main output is a concise, evidence-backed report for university administration: which skills and subject areas employers request, where current courses address them, and where there may be gaps. The pilot also tests whether a student-facing career and course exploration flow is useful.

The primary pilot success measure is a **scenario simulation of possible improvement in relevant university/business-school ranking indicators** if identified teaching and employer-engagement opportunities were acted on. This is a modeled potential impact, not a claim that the pilot caused an actual ranking increase.

## Users and workflows

### Student

1. Complete a short, non-clinical interest and goals questionnaire. Ask about desired work, interests, and topic preferences; avoid presenting it as a psychological diagnosis or fixed personality label.
2. Review suggested careers, skills, courses, and learning pathways.
3. See why each option was suggested, what evidence supports it, and where the recommendation is uncertain.
4. Adjust preferences, compare alternatives, or ignore recommendations. No pathway is mandatory.

### HR / labor-market analyst

1. Import an HR-authorized CSV export or other approved data file; the pilot does not scrape job-board pages.
2. Review normalized posting records, correct invalid rows, and inspect possible duplicates.
3. Confirm extracted skills and topics, merge synonyms, and flag irrelevant or ambiguous postings.
4. Review aggregated demand by skill/topic, role, source, and posting date.
5. Work with the AI agent to prepare a reviewed report for administration and faculty.

### AI agent and university administration

1. The agent analyzes authorized job-market data and the approved course catalog/materials, preserving source and date references.
2. HR reviews the analysis and corrects unsupported or misleading interpretations.
3. The agent prepares an administration-facing report on market demand, course coverage, possible opportunities, and uncertainties.
4. Administration reviews a ranking-impact scenario simulation and decides whether to commission further analysis or action.

### Faculty

1. Review the demand summary alongside existing course learning outcomes and materials.
2. See possible gaps and relevant courses or topics, with links back to the evidence.
3. Ask AI to draft a lesson outline, exercise, or reading-list suggestion using approved source materials.
4. Edit and approve any change before students see it.

## MVP features

- Student goals and interests questionnaire, with editable answers.
- Explainable course and career recommendations based on a faculty-reviewed mapping of skills to courses.
- Job-market inputs led by LinkedIn, supplemented by Indeed and Bicocca's Career Service; support authorized CSV exports, row validation, duplicate detection, and HR review. Do not scrape job-board pages.
- Aggregated, date-stamped labor-market demand dashboard.
- Course-to-skill mapping and gap review for faculty.
- AI-agent-generated, HR-reviewed administration reports with evidence links and uncertainty notes.
- A transparent ranking-indicator scenario simulator comparing a documented baseline with hypothetical interventions and estimated outcomes.
- AI-assisted drafts grounded in approved course materials and reviewed labor-market findings.
- Faculty approval workflow and basic version history for published material changes.
- Clear notices that recommendations are exploratory, not guarantees of employment or required study plans.

## Out of scope for the first pilot

- Automated curriculum changes or publishing AI-generated teaching materials without faculty approval.
- High-stakes student ranking, admissions, grading, or employment selection.
- Personality diagnosis, emotion inference, or opaque aptitude scoring.
- Broad claims about the whole labor market based on a small or unrepresentative sample.
- Unauthorized scraping or use of LinkedIn, Indeed, or career-service data outside applicable access terms.
- Direct job-board crawling, credential-based collection, or automated collection that has not been explicitly approved by the source and the University.
- Treating a simulated ranking change as a predicted or guaranteed actual ranking outcome.
- Full learning-management-system integration or support for every degree program.
- Training a bespoke model on identifiable student data.

## Data and decision rules

| Data | Initial source | MVP handling |
|---|---|---|
| Student goals and interests | Student questionnaire | Collect only what is needed; make answers editable and deletable; do not use for admissions or grading |
| Job skills and topics | Primarily LinkedIn; supplement with Indeed and Bicocca Career Service | Import approved exports; record source/reference/date; remove personal contact details; deduplicate and have HR review extracted skills |
| Courses and learning outcomes | Approved university catalog | Faculty validates skill-to-course mappings |
| Teaching materials | Faculty-approved materials | Limit AI drafting to authorized content; retain source references for review |
| Ranking indicators | Applicable ranking's published methodology and Bicocca-approved baseline data | Validate eligibility, definitions, and data availability before modeling; label assumptions and scenario outputs |

Recommendations should be based on transparent rules and mappings in the pilot. Show evidence, dates, and uncertainty. Treat job-posting frequency as an imperfect signal—not proof that a course guarantees a job or that a skill is valuable in every context.

### Ranking simulation guardrails

- Select the exact ranking and edition with administration before building the model. The Financial Times rankings primarily cover business schools/programs; verify that the chosen ranking actually includes the relevant Bicocca unit or program. Do not apply a business-school formula to Mechanical Engineering if it is ineligible.
- If no directly applicable ranking exists, use a clearly named **ranking-indicator proxy scenario** based on relevant, published criteria (for example, employment outcomes, employer engagement, or graduate career progression), not a fabricated overall rank.
- Show the baseline, assumptions, evidence source, uncertainty range, and hypothetical intervention for every scenario. Distinguish measurable pilot outcomes from long-term modeled effects.
- Do not claim causation or promise an improved ranking. The simulation is a decision-support tool; administration validates any interpretation.

## Suggested technical shape

- **Student experience:** questionnaire, pathway results, and preference controls.
- **Staff workspace:** HR-authorized CSV intake, job-market review, AI-agent reports, demand dashboard, skill/course mapping, ranking scenarios, and faculty draft approval.
- **Backend:** authenticated APIs and a relational store for users/consent, courses, skill mappings, job-posting metadata, scenario assumptions, and recommendation explanations.
- **AI services:** structured skill extraction and retrieval-grounded drafting from approved materials; require human confirmation for extracted skills and faculty approval for teaching outputs.
- **Auditability:** keep source references, timestamps, reviewer decisions, and versions of recommendations and published materials.

Run the application, AI processing, and storage inside **University of Milano-Bicocca data centers**. Do not send university or student data to external AI services unless separately reviewed and explicitly authorized. Apply basic role-based permissions: HR can review job-market inputs; faculty can review course mappings and teaching drafts; administration can view reports and ranking scenarios; technical administrators manage access and the service. Keep student identity separate from questionnaire responses where practical, and log access to sensitive records.

### Current prototype boundary

The student questionnaire is a browser-based prototype. The HR intake opens as a standalone page in Chrome and has a demonstration mode with clearly labeled fictional postings and a rule-based source/skill summary. It also accepts authorized CSV exports, validates the agreed posting fields, flags duplicates, and exports unique normalized records as JSON. The main course page, `course-impact.html`, is a teaching-material studio: teachers first paste or import current syllabus titles, compare the lectures with imported student-interest and HR-market snapshots, review a proposed subject syllabus that retains existing lectures and suggests applied coverage, and select one lecture for an editable teaching preview with outcomes, topics, and an applied activity. Mathematics/math and physics titles receive protected mandatory-foundation status only when they appear in the provided syllabus; absent subjects are not shown or inserted. Protected titles are excluded from market matching and cannot be changed in their generated preview, while signals may inform optional application examples. Frequent HR skills not represented by the syllabus are surfaced as possible additions. Low or absent market matches for other lectures are labeled for faculty review, not as evidence that a lecture should be removed. The prototype uses keyword/concept matching and templates, not a connected AI model or curriculum-quality assessment. The former sections 01-04 are hidden from this teaching-facing page; the student and HR intake pages remain separately accessible for demonstration. Drafts are previewed, saved locally, or exported as JSON. Demo source snapshots are fictional. Adjustments and drafts are browser-local and are not shared with the HR API. This is an original, Bicocca-inspired concept page and is not an official university website or curriculum. The optional self-hostable Python API stores submitted records in SQLite at the server-configured path, with HR-only ingestion and HR/admin read access.

For local development, generate two different tokens with `python -c "import secrets; print(secrets.token_urlsafe(32))"`, set `BICOCCA_ROLE_TOKENS` to a JSON object containing the `hr` and `admin` tokens, optionally set `BICOCCA_DB_PATH` to the database file path, then run `python server.py`. Open `http://127.0.0.1:8000` and connect from the HR intake page. Keep the server bound to localhost behind a University-managed HTTPS reverse proxy. The prototype token mechanism is not University SSO. Before real HR data is used, University IT must approve the deployment, authentication, source access, schema, retention, backups, and access policies. No AI processing is connected yet.

## Evaluation

Establish a baseline before the pilot, then review results with students, faculty, and HR.

### Primary success measure: ranking-impact scenario

- Administration approves a target ranking or a clearly labeled set of applicable ranking indicators and verifies that the methodology applies to the unit being assessed.
- Produce a reproducible baseline and at least one hypothetical intervention scenario, such as closing a validated skills gap or strengthening employer engagement.
- For each scenario, show estimated indicator changes, evidence, assumptions, uncertainty, and data limitations. If the necessary ranking data or eligibility is unavailable, report that rather than inventing a rank.
- Success means the simulation is complete, traceable, reviewed by administration, and useful for comparing decisions—not that an actual ranking increase has already occurred.

### Student usefulness

- Percentage of students who say recommendations are understandable and relevant.
- Whether students can identify why a course was suggested.
- Student ability to correct preferences and find alternatives.

### Staff usefulness

- Time required to review a job-posting batch and prepare a demand summary.
- Faculty assessment of whether identified gaps are useful and supported by evidence.
- Percentage of AI drafts accepted, edited, or rejected by faculty, with reasons.

### Quality and safeguards

- Accuracy of extracted skills on a human-reviewed sample.
- Coverage and freshness of LinkedIn, Indeed, and Bicocca Career Service data, reported separately by source.
- Recommendation differences across relevant student groups; investigate unexplained disparities.
- Number of unsupported claims or material errors in AI drafts before and after review.
- Confirmation that no unapproved AI-generated material reaches students.
- Confirmation that all data processing and storage stay within university data centers and access follows the agreed permissions.

Set numeric success thresholds with the pilot stakeholders before launch; do not infer success from engagement alone.

## Delivery sequence

1. **Discovery and governance:** confirm the Mechanical Engineering scope, target roles, authorized access to LinkedIn/Indeed/Career Service data, data-center deployment, roles/permissions, consent and retention rules, and ranking-simulation target.
2. **Prepare the evidence:** curate postings and approved course materials; create and faculty-review the initial skill-to-course map; validate ranking eligibility, methodology, and baseline data with administration.
3. **Build the core:** implement the AI-agent workflow, explainable recommendations, source-separated demand view, administration report, and ranking scenario simulator.
4. **Add controlled teaching support:** ground drafts in approved sources, show citations, and require faculty approval before use.
5. **Pilot and evaluate:** review the report and scenario with administration, HR, faculty, and students; document limitations and decide whether to expand.

## Key risks and mitigations

- **Biased or incomplete job data:** document source coverage and dates for LinkedIn, Indeed, and Career Service separately; use multiple sources where permitted and show uncertainty.
- **Recommendations narrowing student choices:** show alternatives, let students change goals, and position suggestions as optional exploration.
- **Overclaiming the value of a skill or course:** distinguish observed posting frequency from causal employment outcomes.
- **Misleading ranking projections:** confirm ranking eligibility and official criteria, expose assumptions and uncertainty, and report a proxy rather than a rank if the degree is not covered.
- **AI-generated inaccuracies:** ground outputs in approved materials, cite sources, and require faculty review.
- **Data access or residency failure:** confirm source permissions and deploy processing/storage in university data centers; enforce role-based access and audit access.
- **Sensitive student profiling:** keep the questionnaire focused on learning and career preferences; minimize collection, restrict access, and define deletion and retention policies before the pilot.
- **Curriculum disruption:** treat AI output as evidence and drafts only; curriculum decisions remain with faculty and university governance.

## Decisions to make before implementation

- Which Mechanical Engineering roles and geographic job markets will be in scope?
- What authorized LinkedIn and Indeed access is available, and what Career Service data can be used?
- Which ranking and edition, if any, applies to the unit; who validates the methodology and baseline?
- Who owns skill validation, course mapping, AI-agent review, and final content approval?
- Which university data centers and deployment environment will host the system?
- What consent, role permissions, retention, and deletion rules apply to student responses and job-market data?
