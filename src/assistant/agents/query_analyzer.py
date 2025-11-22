import re
from enum import Enum, auto
from typing import Dict, List, Tuple


# ---------- ENUM DEFINITION ----------

class Intent(Enum):
    CREATE_PROPOSAL = auto()
    IMPLEMENT_PROPOSAL = auto()
    ARCHIVE_PROPOSAL = auto()
    NEW_FEATURE = auto()
    MODIFY_EXISTING = auto()
    UNKNOWN = auto()


# ---------- MAIN FUNCTION ----------

def analyze_user_intent(user_text: str, convo_context: str = "") -> Intent:
    """
    Identify the primary intent from the user's query.

    Returns one of:
      - Intent.CREATE_PROPOSAL
      - Intent.IMPLEMENT_PROPOSAL
      - Intent.ARCHIVE_PROPOSAL
      - Intent.NEW_FEATURE
      - Intent.MODIFY_EXISTING
      - Intent.UNKNOWN
    """
    text = _normalize(user_text + " " + (convo_context or ""))
    scores = _score_all(text)
    _semantic_boosts(text, scores)

    # Priority order for tie-breaking (most specific first)
    priority = [
        Intent.MODIFY_EXISTING,
        Intent.NEW_FEATURE,
        Intent.ARCHIVE_PROPOSAL,
        Intent.IMPLEMENT_PROPOSAL,
        Intent.CREATE_PROPOSAL,
    ]

    # Pick the best-scoring intent
    ordered = sorted(scores.items(), key=lambda kv: (kv[1], -priority.index(kv[0])), reverse=True)
    top_intent, top_score = ordered[0]

    # Return UNKNOWN if no strong match
    return top_intent if top_score > 0 else Intent.UNKNOWN


# ---------- LEXICON DEFINITIONS ----------

LEX = {
    Intent.CREATE_PROPOSAL: {
        "verbs": ["create", "draft", "write", "prepare", "put together", "produce", "make", "craft", "develop"],
        "nouns": ["proposal", "plan", "business case", "rfp", "rfi", "sow", "statement of work", "scope", "pitch"],
        "phrases": ["write a proposal", "draft a proposal", "put together a proposal", "prepare a proposal"],
        "neg": ["review the proposal", "implement the proposal", "execute the proposal", "archive the proposal"],
    },
    Intent.IMPLEMENT_PROPOSAL: {
        "verbs": ["implement", "execute", "apply", "roll out", "deploy", "start", "launch"],
        "nouns": ["proposal", "plan"],
        "phrases": ["implement the proposal", "execute the proposal", "put the proposal into action"],
        "neg": ["draft a proposal", "write a proposal", "prepare a proposal", "archive the proposal"],
    },
    Intent.ARCHIVE_PROPOSAL: {
        "verbs": ["archive", "close", "finalize", "retire", "complete", "wrap up", "store", "finish"],
        "nouns": ["proposal", "plan", "project"],
        "phrases": [
            "archive the proposal", "close the proposal", "finalize the proposal",
            "mark the proposal as done", "wrap up the proposal", "store the proposal"
        ],
        "neg": ["draft a proposal", "implement the proposal"],
    },
    Intent.NEW_FEATURE: {
        "verbs": ["add", "support", "build", "introduce", "include", "enable", "provide"],
        "nouns": ["feature", "capability", "integration", "endpoint", "api", "module", "dashboard", "export", "import"],
        "phrases": ["can we have", "i need a feature", "support for", "add support for"],
        "neg": ["rename", "increase limit", "change default", "modify", "update", "fix", "tweak"],
    },
    Intent.MODIFY_EXISTING: {
        "verbs": ["update", "change", "modify", "tweak", "adjust", "refactor", "optimize", "fix", "rename", "deprecate"],
        "nouns": ["function", "method", "endpoint", "query", "workflow", "job", "script", "component", "api"],
        "phrases": ["increase the limit", "change the default", "accept nulls", "make it faster", "handle duplicates"],
        "neg": ["there is no", "doesn't exist yet", "missing feature"],
    },
}


# ---------- HELPERS ----------

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _count_matches(text: str, terms: List[str]) -> int:
    return sum(t in text for t in terms)


def _rule_score(intent: Intent, text: str) -> int:
    cfg = LEX[intent]
    score = 0
    score += 2 * _count_matches(text, cfg["verbs"])
    score += 2 * _count_matches(text, cfg["nouns"])
    score += 3 * _count_matches(text, cfg["phrases"])
    score -= 2 * _count_matches(text, cfg["neg"])
    return score


def _score_all(text: str) -> Dict[Intent, int]:
    return {intent: _rule_score(intent, text) for intent in LEX.keys()}


def _semantic_boosts(text: str, scores: Dict[Intent, int]) -> None:
    """Lightweight semantic boosts for paraphrases."""
    if any(p in text for p in ["put together something formal", "compose a proposal", "business justification"]):
        scores[Intent.CREATE_PROPOSAL] += 3
    if any(p in text for p in ["move forward with the proposal", "proceed with the plan", "roll this out"]):
        scores[Intent.IMPLEMENT_PROPOSAL] += 3
    if any(p in text for p in ["archive this proposal", "close this out", "mark as done", "wrap it up", "finalize proposal"]):
        scores[Intent.ARCHIVE_PROPOSAL] += 3
    if any(p in text for p in ["it would be nice if", "add the ability to", "new capability", "introduce support for", "add new"]):
        scores[Intent.NEW_FEATURE] += 3
    if any(p in text for p in ["adjust the behavior", "change how it works", "rename the method", "increase the threshold"]):
        scores[Intent.MODIFY_EXISTING] += 3


# ---------- DEMO ----------

if __name__ == "__main__":
    examples = [
        "Can you draft a proposal for the Q1 rollout?",
        "Let's implement the proposal we agreed on last week.",
        "Archive the proposal from last quarter.",
        "Add support for SSO with Okta.",
        "Update process_orders to handle duplicates.",
        "Proceed with the plan and roll this out to EMEA first.",
        "Change the default timeout of the /search endpoint to 30s.",
        "Please close the project proposal and mark it as completed.",
    ]

    for ex in examples:
        intent = analyze_user_intent(ex)
        print(f"{ex} → {intent.name}")
