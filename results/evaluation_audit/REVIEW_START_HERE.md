# Review start sheet — milestone 2 audit

Ten starter items: five from `single_multi_tool_review_sample.csv`, two
from `distractor_top1_review.csv`, three bounded-catalog items (full
catalog below). Fill the matching rows in the CSVs. Full tool
descriptions and parameters are in the CSV files; they are abbreviated
here for readability.

## General rules (from docs/review_workflow.md)

- Judge from the request text and tool documentation only.
- `human_reviewed` = "yes" only after the row is complete. Never fill it
  otherwise. `reviewer_id` = your initials/ID.
- `unclear` is a valid judgment; record why in `reviewer_notes`.
- Calling the same tool twice (e.g. "for Jan 15 and also Feb 20") still
  counts as single-tool; needing two *different* tools is multi-tool.

---

## A. `review/single_multi_tool_review_sample.csv` — five starter rows

Fill `judgment_request_type` (single-tool | multi-tool | unclear),
`judgment_label_relation` (alternatives | jointly_required | mixed |
not_applicable_one_label | unclear), `judgment_labels_complete`
(yes | no | unclear).

### SR011 — `toolret_apibank_apibank_query_0` (apibank, 2 labels)
Query: "Can you tell me about the historical events of April 21st?"
- `toolret_apibank_tool_33` QueryHistoryToday — query historical events
  for a given date.
- `toolret_apibank_tool_53` Calculator — arithmetic on an infix
  expression. (Does this label look wrong? Note it in reviewer_notes
  and judgment_labels_complete.)

### SR036 — `toolret_apigen_apigen_query_669` (apigen, 2 labels)
Query: "Can you fetch the latest manga from genres 'Action' and 'Sci-Fi'
on page 2, and also get 5 jokes from the API?"
- `toolret_apigen_tool_1352` fetch_latest — latest manga by genre/page.
- `toolret_apigen_tool_1353` v1_jokes — fetch a set number of jokes.

### SR044 — `toolret_gorilla-huggingface_gorilla_huggingface_query_230`
(gorilla-hf, 1 label)
Query: "We need to classify the type of an image for an inventory."
- `toolret_gorilla_huggingface_tool_195` facebook/regnet-y-008 — RegNet
  image classification model.

### SR071 — `toolret_metatool_metatool_which_query_111` (metatool, 2 labels)
Query: "Can you assist me in finding remote job options in the field of
graphic design? Additionally, I'd like to stay updated on any news
regarding the latest design tools and software."
- `toolret_metatool_which_tool_37` JobTool — job search.
- `toolret_metatool_which_tool_2` NewsTool — news.

### SR088 — `toolret_toolalpaca_toolalpaca_query_61` (toolalpaca, 1 label)
Query: "I'm working on a science project and I need to know how many
moons Jupiter has. Can you look that up for me?"
- `toolret_toolalpaca_tool_22` result_get — short answer via Wolfram Alpha.

---

## B. `review/distractor_top1_review.csv` — two starter rows

Fill `judgment_distractor_satisfies_request` (yes | no | unclear). The
distractor is NOT in the annotated labels; the question is whether it
would actually satisfy the request.

### DR105 — `toolret_gorilla-huggingface_gorilla_huggingface_query_243` (test)
Query: "Create interesting variations of the given phrase 'How can I
improve my time management skills?'."
- Annotated: `gorilla_huggingface_tool_625` parrot_paraphraser_on_T5.
- Distractor: `toolret_toolACE_tool_10331` "schedule_family_meeting" —
  schedule a family meeting to improve parent-child communication.

### DR012 — `toolret_apibank_apibank_query_62` (test)
Query: "Can you tell me the definition of the word 'perplexed'?"
- Annotated: `apibank_tool_37` Dictionary — word definitions.
- Distractor: `toolret_toolACE_tool_5141` "norwegianDictionary" — get the
  definition of a word **in Norwegian**. (Tricky: is a Norwegian
  dictionary's definition of "perplexed" satisfactory? Judge honestly.)

---

## C. Bounded-catalog items — three complete catalogs

Read EVERY tool below, then fill the row for the item in
`human_labeling/responses/bounded_round<N>_responses.csv`:
`individually_satisfying_tool_ids` (each sufficient alone; repeated
calls to one tool still count as single-tool), `required_tool_combinations`
(`id1+id2 | id3+id4`, only if no single tool suffices),
`answerability` (answerable | no_suitable_tool |
insufficient_information), `explanation`, `reviewer_id`,
`human_reviewed`. Do not open
`bounded_catalog_review_KEY_do_not_open_before_review.csv` until done.

### BC001 — query:
"I have a long list of URLs from various sources such as news articles,
blog posts, and research papers, covering a wide range of topics. I need
your assistance in generating well-written articles that effectively
summarize the content, key points, and main arguments found within each
of these URLs."

| slot | tool | what it does |
|---|---|---|
| 1 | metatool_which_tool_170 C3_Glide | live aviation data (METARs/TAFs/NOTAMs) |
| 2 | metatool_which_tool_6 CourseTool | learning platform / courses |
| 3 | metatool_which_tool_22 DietTool | calorie counting, diet tracking |
| 4 | metatool_which_tool_0 FinanceTool | financial updates, stocks/crypto |
| 5 | metatool_which_tool_71 mbti | administer MBTI test |
| 6 | metatool_which_tool_83 GifApi | search gifs (Giphy) |
| 7 | metatool_which_tool_40 ResearchHelper | academic papers, mind maps, Q&A |
| 8 | metatool_which_tool_88 aiAgents | multiple-AI productivity |
| 9 | metatool_which_tool_20 VideoSummarizeTool | summarize YouTube videos, Q&A on content |
| 10 | metatool_which_tool_55 search | design courses / mentorship |
| 11 | metatool_which_tool_21 MediaModifyTool | image editing, filters |
| 12 | metatool_which_tool_41 SEOTool | SEO analytics |
| 13 | metatool_which_tool_15 CompanyInfoTool | company info from knowledge graphs |
| 14 | metatool_which_tool_105 Substack_IQ | search/analyze/summarize Substack newsletters |
| 15 | metatool_which_tool_92 Man_of_Many | product/culture news headlines |

### BC010 — query: "Can you help me change my account password?"

| slot | tool | what it does |
|---|---|---|
| 1 | apibank_tool_86 QueryHotelBooking | hotel bookings by user_id |
| 2 | apibank_tool_16 QueryAgenda | user's agenda by token |
| 3 | apibank_tool_26 DeleteBankAccount | delete bank account |
| 4 | apibank_tool_30 QueryTradeDetail | trade details |
| 5 | apibank_tool_17 AssignPriority | assign task priority |
| 6 | apibank_tool_4 ForgotPassword | password reset by username/email |
| 7 | apibank_tool_27 ModifyBankAccount | modify account: password, name, email |
| 8 | apibank_tool_55 QueryHealthData | user health data |
| 9 | apibank_tool_25 OpenBankAccount | open account |
| 10 | apibank_tool_32 QueryBalance | account balance |
| 11 | apibank_tool_28 QueryBankAccount | bank account info |
| 12 | apibank_tool_49 SendMessage | send message w/ attachment |
| 13 | apibank_tool_1 RegisterUser | register user |
| 14 | apibank_tool_94 OnlineCourseSearch | course search |
| 15 | apibank_tool_24 Transfer | money transfer |

### BC020 — query: "We are working on a language learning app for
Chinese. We need to give audio examples for each lesson."

| slot | tool | what it does |
|---|---|---|
| 1 | gorilla_huggingface_tool_291 ddpm-bedroom | image synthesis (diffusion) |
| 2 | gorilla_huggingface_tool_389 german-sentiment-bert | German sentiment |
| 3 | gorilla_huggingface_tool_592 blenderbot-9B | open-domain chatbot |
| 4 | gorilla_huggingface_tool_811 hubert-large-superb-sid | speaker identification |
| 5 | gorilla_huggingface_tool_653 mbart_ruDialogSum | Russian dialog summarization |
| 6 | gorilla_huggingface_tool_852 autotrain-iris-knn | KNN on Iris |
| 7 | gorilla_huggingface_tool_805 hubert-base-superb-er | emotion recognition (speech) |
| 8 | gorilla_huggingface_tool_571 rut5-base-absum | Russian summarization |
| 9 | gorilla_huggingface_tool_572 Randeng-Pegasus-238M-Summary-Chinese | Chinese text summarization |
| 10 | gorilla_huggingface_tool_12 hubert-large-ll60k | speech representation |
| 11 | gorilla_huggingface_tool_597 gpt2 | English text generation |
| 12 | gorilla_huggingface_tool_52 DreamShaper | text-to-image |
| 13 | gorilla_huggingface_tool_15 rubert-base-cased | Russian BERT |
| 14 | gorilla_huggingface_tool_459 BioM-ELECTRA-SQuAD2 | biomedical QA |
| 15 | gorilla_huggingface_tool_862 timeseries-anomaly-detection | anomaly detection |

---

Everything above is a starting subset. Total remaining: 95 rows in sheet
A, 166 rows in sheet B, 37 items in sheet C.
