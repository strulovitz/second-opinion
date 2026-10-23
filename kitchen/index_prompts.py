"""BIBLE 3.7 reader prompts. All term interpretation is by the free reader."""

PARSE = """You parse one page of a medical textbook's back-of-book INDEX into
JSON. Output ONLY JSON. Schema:
{"entries":[{"headword":"<main term exactly as printed, including inverted
comma form>","display":"<same term in natural word order; if not inverted,
same as headword>","see":"<target of See X, else null>","pages":["<every
page reference of the headword itself>"],"subentries":[{"text":"<sub-entry
words>","pages":["..."]}]}]}
A MAIN entry starts at the left margin and usually begins with a capital
letter. SUB-entries are indented or begin with a lowercase word or 'in',
'with', 'for', 'and', 'of', 'due to'. Keep page references exactly as printed
(1234, 1234-1236, 1234t, 1234f, e12). Do not invent entries, words or refs.
If the page begins in the middle of a main entry, output that first partial
entry with headword CONTINUED. 'See also' is not a See alias: leave see null.
Do not put subentry page refs in the main entry's own pages list.
Prose, contents, glossaries, references and chapter outlines are not a
back-of-book index. Return an empty entries list if this is not an index page.
"""

CLASSIFY = """You classify medical index terms into exactly one group. Output
ONLY JSON: {"results":[{"display":"<as given>","group":"<symptoms-and-signs |
diseases-and-conditions | treatments-and-drugs | not-an-entity>",
"confidence":<0.0-1.0>,"reason":"<max 12 words>"}]}
symptoms-and-signs: what a patient feels or notices (pain, nausea, tiredness)
or an examiner observes (rash, fever, murmur). Specific or nonspecific, but
NOT chronic. Includes jaundice, edema, cough, hemoptysis.
diseases-and-conditions: named disease, syndrome, infection named as a
disease, injury, poisoning, deficiency, chronic state (chronic pain,
hypertension, obesity, pregnancy, menopause), or an abnormality defined by
a measurement (hyperkalemia, anemia).
treatments-and-drugs: generic or brand drugs, vaccines, substances given to
treat/prevent, therapeutic/preventive procedures (surgery, dialysis,
transplantation, radiation therapy, physiotherapy), diets/lifestyle
interventions named as treatments.
not-an-entity: people's names; anatomy/physiology (liver, nephron, cardiac
output); organisms as organisms; genes/proteins/receptors; lab methods;
diagnostic tests/imaging as methods; statistics, ethics, history, policy,
economics; abbreviations with no meaning alone.
Tie-breaks in order: (1) symptom vs disease without a clue -> symptom;
(2) drug/poison -> treatment only in pharmacology/therapy context, else
poisoning disease; (3) organism with infection/treatment/diagnosis subentries
-> disease; (4) entity vs not-an-entity without a clue -> choose the entity
group you lean to and confidence below 0.5.
Standing project LAW 7 takes precedence: chronic states, test findings and
measured abnormalities are diseases-and-conditions, not symptoms.
Use only the supplied index words/subentries and district context.
"""

RESOLVE = """You decide whether a medical index term is the SAME entity as
one of the supplied registered candidates or a NEW entity. Same means the
same disease, symptom or treatment under a spelling, word-order, synonym,
eponym or abbreviation variant. Related but distinct concepts are different
(hypertension vs pulmonary hypertension; hepatitis B vs hepatitis C; disease
vs complication). Output ONLY JSON:
{"decision":"SAME"|"NEW","candidate_slug":"<slug if SAME else null>",
"confidence":<0.0-1.0>,"reason":"<max 15 words>"}
Use the supplied term, group, subentries, context districts and candidates.
Never merge different groups. Do not invent a candidate slug.
"""
