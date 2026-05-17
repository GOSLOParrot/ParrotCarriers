#!/usr/bin/env python3
"""导入《淑女礼仪与社交指南》(pg35123.txt) → Graphiti noble_etiquette 分区。

Schema 设计
-----------
entity_types (prescribed ontology):
  Role      — 社会角色 (Hostess, Guest, Lady, Gentleman, Servant …)
  Occasion  — 社交场合 (Ball, Dinner, Morning Call, Evening Party …)
  Item      — 礼仪物品 (Card, Gloves, Fan, Bouquet, Dress …)
  Rule      — 行为准则条目 (礼仪规则, 禁忌, 惯例)

edge_type_map + edge_types (prescribed relations):
  (Role, Occasion) → MUST_DO_IN       角色在场合的必要行为
  (Role, Occasion) → MUST_AVOID_IN    角色在场合的禁忌行为
  (Role, Rule)     → FOLLOWS          角色遵守某行为准则
  (Rule, Item)     → REQUIRES         行为准则需要某物品
  (Role, Role)     → INTERACTS_WITH   角色间的社交关系
  (Action, Item)   → REQUIRES         某动作需要某物品（Rule 的子集）
  (Occasion, Item) → APPROPRIATE_FOR  某物品在某场合适用

Saga
----
所有章节串入同一 Saga "ladies_book_of_etiquette"，
保留 CHAPTER I → CHAPTER XXVI 的顺序 (NEXT_EPISODE 边)。

用法
----
  # 试运行（只显示分块，不调用 Graphiti）
  python src/scripts/import_ladies_etiquette_book_to_graphiti.py --dry-run

  # 导入前 3 章
  python src/scripts/import_ladies_etiquette_book_to_graphiti.py --apply --chapters 1 2 3

  # 全量导入
  python src/scripts/import_ladies_etiquette_book_to_graphiti.py --apply

  # 导入单章并打印提取到的节点/边
  python src/scripts/import_ladies_etiquette_book_to_graphiti.py --apply --chapters 5 --verbose

  # 可选：额外为每章生成中英双语词汇对照 episode
  python src/scripts/import_ladies_etiquette_book_to_graphiti.py --apply --with-glossary

环境变量
--------
与 graphiti_client 一致：
  GOOGLE_API_KEY       (嵌入仍用 Gemini)
  DEEPSEEK_API_KEY     + GRAPHITI_LLM_PROVIDER=deepseek  (推荐，抽取质量好)
  FALKORDB_HOST / FALKORDB_PORT / FALKORDB_DATABASE
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("import_ladies_etiquette")

# ─── 文本路径 ────────────────────────────────────────────────────────────────
BOOK_PATH = REPO_ROOT / "Noble Etiquette" / "pg35123.txt"
BOOK_PUBDATE = datetime(1860, 1, 1, tzinfo=timezone.utc)
PARTITION = "noble_etiquette"
SAGA_NAME = "ladies_book_of_etiquette"

# 章节大标题前缀（正文里真实存在的格式）
# 正确覆盖减法形式：XIV (14)、XIX (19)、XXIV (24)
CHAPTER_REGEX = re.compile(
    r"^CHAPTER\s+(X{0,2}(?:IX|IV|V?I{0,3}))\.$",
    re.MULTILINE,
)

# 超长章节（Chapter XXI ACCOMPLISHMENTS ~1567 行）拆子块的上限
MAX_EPISODE_CHARS = 8_000

# ─── Prescribed Ontology ─────────────────────────────────────────────────────
from pydantic import BaseModel, Field  # noqa: E402
from graphiti_core.nodes import EpisodeType  # noqa: E402


# ─── DeepSeek json_schema 兼容补丁 ────────────────────────────────────────────
# graphiti_core OpenAIGenericClient 在有 response_model 时发送 json_schema 格式，
# DeepSeek 目前不支持 json_schema，只支持 json_object。
# 此子类在脚本内覆盖该行为，不改 graphiti_core 源码。
class _DeepSeekCompatibleClient:
    """Lazy-initialized patch; call _make_deepseek_client(cfg) to get the real instance."""
    pass


def _make_deepseek_llm_client(cfg: Any) -> Any:
    """Return an OpenAIGenericClient subclass that downgrades json_schema → json_object."""
    import json as _json
    import typing as _typing
    from graphiti_core.llm_client.config import DEFAULT_MAX_TOKENS, LLMConfig, ModelSize
    from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
    from graphiti_core.prompts.models import Message
    from pydantic import BaseModel as _BM

    class _DSClient(OpenAIGenericClient):
        async def _generate_response(
            self,
            messages: list[Message],
            response_model: type[_BM] | None = None,
            max_tokens: int = DEFAULT_MAX_TOKENS,
            model_size: ModelSize = ModelSize.medium,
        ) -> dict[str, _typing.Any]:
            from openai.types.chat import ChatCompletionMessageParam
            import openai as _openai

            openai_messages: list[ChatCompletionMessageParam] = []
            for m in messages:
                m.content = self._clean_input(m.content)
                if m.role == "user":
                    openai_messages.append({"role": "user", "content": m.content})
                elif m.role == "system":
                    openai_messages.append({"role": "system", "content": m.content})

            # DeepSeek 只支持 json_object，不支持 json_schema
            response_format: dict[str, _typing.Any] = {"type": "json_object"}

            try:
                resp = await self.client.chat.completions.create(
                    model=self.model,
                    messages=openai_messages,
                    temperature=self.temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                )
                raw = resp.choices[0].message.content or ""
                result = _json.loads(raw)

                # Normalize field names: DeepSeek often drops the "extracted_" prefix
                # (returns {"entities": ...} instead of {"extracted_entities": ...}).
                # Try to remap using the response_model's expected field names.
                if response_model is not None:
                    try:
                        response_model(**result)
                    except Exception:
                        remapped: dict[str, _typing.Any] = {}
                        for field in response_model.model_fields:
                            if field in result:
                                remapped[field] = result[field]
                            elif field.startswith("extracted_"):
                                # e.g. "extracted_entities" → look for "entities"
                                short = field[len("extracted_"):]
                                if short in result:
                                    remapped[field] = result[short]
                            else:
                                # e.g. "nodes" → look for "extracted_nodes"
                                prefixed = f"extracted_{field}"
                                if prefixed in result:
                                    remapped[field] = result[prefixed]
                        if remapped:
                            result = {**result, **remapped}

                return result
            except _openai.RateLimitError as e:
                from graphiti_core.llm_client.errors import RateLimitError
                raise RateLimitError from e
            except Exception:
                raise

    llm_config = LLMConfig(
        api_key=cfg.graphiti_llm.deepseek_api_key,
        model=cfg.graphiti_llm.deepseek_model,
        small_model=cfg.graphiti_llm.deepseek_small_model,
        base_url=cfg.graphiti_llm.deepseek_base_url.rstrip("/"),
    )
    return _DSClient(config=llm_config)


class Role(BaseModel):
    """A social role or type of person mentioned in Victorian etiquette (e.g. Hostess, Guest, Lady)."""
    description: str = Field(description="Brief description of this role's social standing")
    zh_formal: str = Field(default="", description="正式书面中文名称，例如：女主人、女宾、绅士")
    zh_colloquial: str = Field(default="", description="日常口语化中文称呼，例如：主人娘、来宾、先生")
    zh_vivid: str = Field(default="", description="生动/文学化中文表达，贴近古典小说或大小姐文风，例如：当家女主、座上嘉宾、翩翩公子")
    zh_explanation: str = Field(default="", description="一句中文解释该角色在19世纪维多利亚/美国上流社交语境中的含义")


class Occasion(BaseModel):
    """A social occasion or setting where etiquette rules apply (e.g. Ball, Dinner Party, Morning Call)."""
    formality_level: str = Field(description="Formality level: formal / semi-formal / informal")
    zh_formal: str = Field(default="", description="正式书面中文名称，例如：舞会、晚宴、晨间拜访")
    zh_colloquial: str = Field(default="", description="日常口语化中文名称，例如：晚会、饭局、串门")
    zh_vivid: str = Field(default="", description="生动/文学化中文表达，例如：华灯之夜、盛宴雅集、登门寒暄")
    zh_explanation: str = Field(default="", description="一句中文说明该场合的正式程度和礼仪背景")


class Item(BaseModel):
    """A physical item relevant to etiquette conduct (e.g. Gloves, Calling Card, Fan, Bouquet)."""
    category: str = Field(description="Category: clothing / accessory / stationery / food / other")
    zh_formal: str = Field(default="", description="正式书面中文名称，例如：拜访名片、礼用手套、折扇、花束")
    zh_colloquial: str = Field(default="", description="日常口语化中文名称，例如：名片、手套、扇子")
    zh_vivid: str = Field(default="", description="生动/文学化中文表达，例如：玲珑名帖、丝质纤手、团扇香风")
    zh_explanation: str = Field(default="", description="一句中文说明该物品在维多利亚礼仪中的用途与礼仪含义")


class Rule(BaseModel):
    """A specific etiquette rule, obligation, or prohibition extracted from the text."""
    rule_type: str = Field(description="Type: obligation / prohibition / recommendation / custom")
    applies_to_occasion: str = Field(
        default="",
        description="The occasion this rule specifically applies to, if mentioned",
    )
    zh_formal: str = Field(default="", description="该礼仪准则的正式书面表述，例如：须即时回复邀请函")
    zh_colloquial: str = Field(default="", description="口语化中文表达，例如：收到请柬要马上回复")
    zh_explanation: str = Field(default="", description="一句中文解释该规则的社交意义")


ENTITY_TYPES: dict[str, type[BaseModel]] = {
    "Role": Role,
    "Occasion": Occasion,
    "Item": Item,
    "Rule": Rule,
}

# ─── Custom Edge Types ────────────────────────────────────────────────────────

class MustDoIn(BaseModel):
    """A Role is obligated to perform an action in an Occasion."""
    obligation: str = Field(description="The specific action or behavior required")


class MustAvoidIn(BaseModel):
    """A Role must avoid certain behavior in an Occasion."""
    prohibition: str = Field(description="The specific action or behavior that is forbidden")


class Follows(BaseModel):
    """A Role adheres to a Rule."""
    context: str = Field(default="", description="Social context in which the role follows this rule")


class Requires(BaseModel):
    """A Rule or Action requires a specific Item."""
    reason: str = Field(default="", description="Why this item is required")


class InteractsWith(BaseModel):
    """Describes the etiquette-governed social relationship between two Roles."""
    interaction_type: str = Field(description="Type of interaction: introduction / greeting / dance / visit")


class AppropriateFor(BaseModel):
    """An Item is socially appropriate for a specific Occasion."""
    note: str = Field(default="", description="Additional etiquette notes on appropriateness")


EDGE_TYPES: dict[str, type[BaseModel]] = {
    "MUST_DO_IN": MustDoIn,
    "MUST_AVOID_IN": MustAvoidIn,
    "FOLLOWS": Follows,
    "REQUIRES": Requires,
    "INTERACTS_WITH": InteractsWith,
    "APPROPRIATE_FOR": AppropriateFor,
}

# edge_type_map: (source_entity_type, target_entity_type) → [allowed edge type names]
EDGE_TYPE_MAP: dict[tuple[str, str], list[str]] = {
    ("Role", "Occasion"): ["MUST_DO_IN", "MUST_AVOID_IN"],
    ("Role", "Rule"): ["FOLLOWS"],
    ("Role", "Role"): ["INTERACTS_WITH"],
    ("Rule", "Item"): ["REQUIRES"],
    ("Item", "Occasion"): ["APPROPRIATE_FOR"],
    ("Occasion", "Item"): ["APPROPRIATE_FOR"],
    # Fallback to allow generic relations between anything
    ("Entity", "Entity"): ["MUST_DO_IN", "MUST_AVOID_IN", "FOLLOWS", "REQUIRES", "INTERACTS_WITH", "APPROPRIATE_FOR"],
}

# ─── Custom extraction prompt ─────────────────────────────────────────────────
EXTRACTION_INSTRUCTIONS = """
This text is from "The Ladies' Book of Etiquette, and Manual of Politeness" (1860) by Florence Hartley.
Focus on extracting:
1. ROLES: Social roles such as Hostess, Guest, Lady, Gentleman, Chaperon, Servant.
2. OCCASIONS: Social settings such as Ball, Dinner Party, Morning Call, Evening Party, Church, Street.
3. ITEMS: Physical objects relevant to etiquette: Calling Card, Gloves, Fan, Bouquet, Dress, Bouquet.
4. RULES: Specific etiquette obligations ("must", "should", "ought") and prohibitions ("never", "must not", "avoid").

For relationships, prefer:
- (Role) --[MUST_DO_IN]--> (Occasion): when the text says a lady/hostess/guest MUST or SHOULD do something at an occasion.
- (Role) --[MUST_AVOID_IN]--> (Occasion): when the text says a lady MUST NOT or SHOULD NEVER do something.
- (Rule) --[REQUIRES]--> (Item): when performing an action or following a rule requires a specific item.
- (Role) --[INTERACTS_WITH]--> (Role): when describing how two roles interact (introductions, greetings, etc.).

BILINGUAL ANNOTATION (important): For every extracted entity, fill in ALL three Chinese translation fields:
- zh_formal: Formal written Chinese (正式书面语). Examples: Hostess→女主人, Ball→舞会, Calling Card→拜访名片
- zh_colloquial: Casual everyday Chinese (口语/日常表达). Examples: Hostess→主人娘, Ball→晚会, Calling Card→名片
- zh_vivid: Vivid/literary Chinese that evokes Victorian-era elegance or classical novel style (生动文学化).
  Examples: Hostess→当家女主, Ball→华灯之夜, Calling Card→玲珑名帖, Gloves→丝质纤手
- zh_explanation: One sentence in Chinese explaining this entity in Victorian social context.

Extract ALL explicit and implied etiquette rules. Use 19th-century English social vocabulary faithfully.
""".strip()

# ─── TOC: chapter titles (from Table of Contents, lines 153–268) ──────────────
CHAPTER_TITLES: dict[int, str] = {
    1: "CONVERSATION",
    2: "DRESS",
    3: "TRAVELING",
    4: "HOW TO BEHAVE AT A HOTEL",
    5: "EVENING PARTIES – Etiquette for the Hostess",
    6: "EVENING PARTIES – Etiquette for the Guest",
    7: "VISITING – Etiquette for the Hostess",
    8: "VISITING – Etiquette for the Guest",
    9: "MORNING RECEPTIONS OR CALLS – Etiquette for the Hostess",
    10: "MORNING RECEPTIONS OR CALLS – Etiquette for the Caller",
    11: "DINNER COMPANY – Etiquette for the Hostess",
    12: "DINNER COMPANY – Etiquette for the Guest",
    13: "TABLE ETIQUETTE",
    14: "CONDUCT IN THE STREET",
    15: "LETTER WRITING",
    16: "POLITE DEPORTMENT AND GOOD HABITS",
    17: "CONDUCT IN CHURCH",
    18: "BALL ROOM ETIQUETTE – For the Hostess",
    19: "BALL ROOM ETIQUETTE – For the Guest",
    20: "PLACES OF AMUSEMENT",
    21: "ACCOMPLISHMENTS",
    22: "SERVANTS",
    23: "ON A YOUNG LADY'S CONDUCT WHEN CONTEMPLATING MARRIAGE",
    24: "BRIDAL ETIQUETTE",
    25: "HINTS ON HEALTH",
    26: "MISCELLANEOUS",
}


def _roman_to_int(roman: str) -> int:
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    total, prev = 0, 0
    for ch in reversed(roman.upper()):
        v = vals.get(ch, 0)
        total += v if v >= prev else -v
        prev = v
    return total


def split_chapters(text: str) -> list[dict[str, Any]]:
    """Split full text into chapters based on 'CHAPTER <ROMAN>.' markers.

    The file has a Table of Contents (TOC) before the body. TOC entries are
    bare one-liners with no real content (<200 chars between them), so we
    skip those stubs and keep only the first substantive occurrence per number.
    """
    matches = list(CHAPTER_REGEX.finditer(text))
    seen: dict[int, bool] = {}
    chapters = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        num = _roman_to_int(m.group(1))
        # Skip TOC stub entries (very short: just the chapter label + title line)
        if len(body) < 200:
            continue
        # Keep first substantive occurrence of each chapter number
        if num in seen:
            continue
        seen[num] = True
        title = CHAPTER_TITLES.get(num, f"Chapter {num}")
        chapters.append({"number": num, "title": title, "body": body})
    return sorted(chapters, key=lambda c: c["number"])


def split_into_sub_chunks(text: str, max_chars: int = MAX_EPISODE_CHARS) -> list[str]:
    """Split a long text into paragraphs-aware chunks <= max_chars."""
    if len(text) <= max_chars:
        return [text]
    paragraphs = re.split(r"\n{2,}", text)
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current = (current + "\n\n" + para).lstrip("\n")
        else:
            if current:
                chunks.append(current.strip())
            # If single paragraph is too long, hard-split at sentence boundary
            if len(para) > max_chars:
                sentences = re.split(r"(?<=[.!?])\s+", para)
                buf = ""
                for sent in sentences:
                    if len(buf) + len(sent) + 1 <= max_chars:
                        buf = (buf + " " + sent).lstrip()
                    else:
                        if buf:
                            chunks.append(buf.strip())
                        buf = sent
                if buf:
                    current = buf
                else:
                    current = ""
            else:
                current = para
    if current.strip():
        chunks.append(current.strip())
    return chunks


async def _build_graphiti():
    """Construct a Graphiti instance from ParrotConfig (same pattern as get_graphiti)."""
    import asyncio
    import logging as _logging
    from graphiti_core import Graphiti
    from graphiti_core.driver.falkordb_driver import FalkorDriver
    from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
    from graphiti_core.nodes import EpisodeType  # noqa: F401 — re-exported for callers
    from parrot.shared.config import ParrotConfig
    from parrot.memory.graphiti_client import get_llm_clients

    cfg = ParrotConfig()
    fdb = cfg.falkordb

    driver = FalkorDriver(host=fdb.host, port=fdb.port, database=fdb.database)
    llm_client, cross_encoder, provider = get_llm_clients(cfg)

    # For DeepSeek, replace the LLM client with the json_schema-compatible subclass
    if provider == "deepseek":
        llm_client = _make_deepseek_llm_client(cfg)
        logger.info("Using DeepSeek-compatible LLM client (json_object mode)")
    embedder = GeminiEmbedder(
        config=GeminiEmbedderConfig(
            api_key=cfg.google_api_key,
            embedding_model=cfg.gemini.embedding_model,
        )
    )
    g = Graphiti(
        graph_driver=driver,
        llm_client=llm_client,
        embedder=embedder,
        cross_encoder=cross_encoder,
    )
    # build_indices fires background tasks; suppress noisy "already exists" / connection-reset
    # errors that occur when indices were already created by a prior run.
    _falkor_logger = _logging.getLogger("graphiti_core.driver.falkordb_driver")
    prev_level = _falkor_logger.level
    _falkor_logger.setLevel(_logging.CRITICAL)
    try:
        await g.build_indices_and_constraints()
        await asyncio.sleep(0.5)   # let background index tasks settle before first query
    except Exception:
        pass
    finally:
        _falkor_logger.setLevel(prev_level)
    logger.info("Graphiti ready (provider=%s, FalkorDB %s:%d)", provider, fdb.host, fdb.port)
    return g, cfg


# ─── Bilingual Glossary Generation ───────────────────────────────────────────
_GLOSSARY_SYSTEM = """你是19世纪维多利亚时代礼仪专家，同时精通中英双语翻译与文学表达。
你的任务：从英文礼仪文本的段落中提取核心词汇，为每个词提供三种中文表达维度，
生成可收录进知识图谱的结构化词汇对照表，供中文自然语言检索使用。

三种翻译维度：
① 正式书面语（学术/文献类）——用于学术语境、字典定义
② 日常口语（现代汉语通俗表达）——符合当代用语习惯
③ 生动文学化（日语轻小说小说/大小姐/异世界和西幻与奇幻文学文笔/中国古典小说与民国风文笔）——有画面感，富有文艺气息"""

_GLOSSARY_USER_TMPL = """请为《淑女礼仪与社交指南》(The Ladies' Book of Etiquette, 1860, Florence Hartley)
第{num}章「{title}」提取三维度中英双语词汇对照表。

章节原文节选（前5000字）：
{body}

---
请严格按以下格式输出（每类别3-10条，若无则省略该类别）：

维多利亚礼仪词汇对照 — 第{num}章：{title}
Victorian Etiquette Three-Register Bilingual Glossary — Chapter {num}: {title}

【社会角色 Social Roles】
英文原词 | ①正式 / ②口语 / ③文学
  →一句中文背景解释（点明19世纪维多利亚/美国上流社会语境）

示例：
Hostess | ①女主人 / ②主人娘 / ③兰堂主母
  →作为聚会举办者，全程负责接待与统筹的女性，是社交圈地位与品味的象征。

【社交场合 Social Occasions】
（同上格式）

示例：
Ball | ①正式舞会 / ②舞会 / ③华灯夜宴
  →维多利亚时代最正式的大型社交聚会，是淑女展示身段、礼仪与社交手腕之地。

【礼仪物品 Etiquette Items】
（同上格式）

【礼仪准则摘要 Key Rules (本章3-8条核心规则)】
英文规则简述（≤12词） | ①正式书面 / ②口语表达 / ③文学化表达
  →中文解释（一句，指出违反此规则的社交后果或意义）

示例：
Reply to invitation promptly | ①须及时回复邀请函 / ②收到请柬要马上回复 / ③鱼雁往来当速答
  →延迟或不回复邀请被视为极度失礼，令女主人无法安排席次，损及双方情谊。

输出要求：
- 三种译法须风格明显区分，不要三个都写成同一文风
- 生动/文学化译法可参考《红楼梦》《三国演义》《民国才女》风格，有画面感
- 礼仪准则须从原文提取真实规则，不要杜撰"""


async def _generate_chapter_glossary_body(
    chapter_num: int,
    chapter_title: str,
    chapter_body: str,
    cfg: Any,
) -> str:
    """Call LLM directly (OpenAI-compatible) to produce a bilingual vocabulary episode body.

    Returns the generated text, or "" if the LLM key is unavailable or generation fails.
    Falls back to Gemini-style prompt if DEEPSEEK_API_KEY is not set but GOOGLE_API_KEY is.
    """
    from openai import AsyncOpenAI

    key = (cfg.graphiti_llm.deepseek_api_key or "").strip()
    if key:
        base = cfg.graphiti_llm.deepseek_base_url.rstrip("/")
        model = cfg.graphiti_llm.deepseek_model
        client = AsyncOpenAI(api_key=key, base_url=base, timeout=120.0)
    elif (cfg.google_api_key or "").strip():
        # Gemini also supports OpenAI-compatible endpoint
        key = cfg.google_api_key.strip()
        base = "https://generativelanguage.googleapis.com/v1beta/openai"
        model = "gemini-2.0-flash"
        client = AsyncOpenAI(api_key=key, base_url=base, timeout=120.0)
    else:
        logger.warning("Ch.%d: no LLM key available, skipping glossary", chapter_num)
        return ""

    user_msg = _GLOSSARY_USER_TMPL.format(
        num=chapter_num,
        title=chapter_title,
        body=chapter_body[:5000],
    )
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _GLOSSARY_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=2048,
            temperature=0.3,
        )
        text = (resp.choices[0].message.content or "").strip()
        logger.info("  ✓ glossary generated for Ch.%d (%d chars)", chapter_num, len(text))
        return text
    except Exception as exc:
        logger.warning("  ✗ glossary LLM call failed for Ch.%d: %s", chapter_num, exc)
        return ""


async def import_book(
    chapters_filter: list[int] | None,
    dry_run: bool,
    verbose: bool,
    with_glossary: bool,
) -> dict[str, Any]:
    if not BOOK_PATH.exists():
        logger.error("Book file not found: %s", BOOK_PATH)
        sys.exit(1)

    text = BOOK_PATH.read_text(encoding="utf-8")
    all_chapters = split_chapters(text)
    logger.info("Parsed %d chapters from %s", len(all_chapters), BOOK_PATH.name)

    if chapters_filter:
        chapters = [c for c in all_chapters if c["number"] in chapters_filter]
        logger.info("Filtered to chapters: %s", chapters_filter)
    else:
        chapters = all_chapters

    total_episodes = sum(len(split_into_sub_chunks(c["body"])) for c in chapters)
    if with_glossary:
        total_episodes += len(chapters)  # one glossary episode per chapter

    summary: dict[str, Any] = {
        "dry_run": dry_run,
        "partition": PARTITION,
        "saga": SAGA_NAME,
        "with_glossary": with_glossary,
        "chapters_selected": [c["number"] for c in chapters],
        "total_sub_episodes": total_episodes,
        "written": 0,
        "chapters": [],
    }

    if dry_run:
        for ch in chapters:
            chunks = split_into_sub_chunks(ch["body"])
            summary["chapters"].append({
                "number": ch["number"],
                "title": ch["title"],
                "chunks": len(chunks),
                "glossary_episode": with_glossary,
                "first_chunk_preview": chunks[0][:200] if chunks else "",
            })
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return summary

    graphiti, cfg = await _build_graphiti()
    prev_episode_uuid: str | None = None
    written = 0

    # Extraction instructions for bilingual glossary episodes (slightly different emphasis)
    glossary_extract_instructions = (
        "这是《淑女礼仪与社交指南》的中英三维度词汇对照表（正式/口语/文学化三种中文译法）。"
        "请同时提取英文术语和其对应的中文术语（如 Hostess 与 女主人/主人娘/兰堂主母）为独立实体节点，"
        "中文术语和英文术语都要作为独立节点被记录，优先使用正式书面译名作为节点 name。"
        "对出现的礼仪准则（标注了①②③三种表达的规则条目），提取为 Rule 节点。"
        "建立 INTERACTS_WITH 或同义关联将中英文同义节点联系起来，"
        "确保后续中文自然语言查询（如：女主人在舞会上该做什么）能命中对应英文节点。"
    )

    try:
        for ch in chapters:
            chunks = split_into_sub_chunks(ch["body"])
            chapter_info: dict[str, Any] = {
                "number": ch["number"],
                "title": ch["title"],
                "chunks": len(chunks),
                "episodes_written": 0,
                "glossary_written": False,
            }

            # ── 正文 episodes ──────────────────────────────────────────────
            for i, chunk in enumerate(chunks):
                ep_name = (
                    f"Ladies Etiquette Ch.{ch['number']}"
                    + (f" part {i+1}/{len(chunks)}" if len(chunks) > 1 else "")
                )
                ep_source = (
                    f"The Ladies' Book of Etiquette (1860), "
                    f"Chapter {ch['number']}: {ch['title']}"
                )
                logger.info("  → episode '%s' (%d chars)", ep_name, len(chunk))
                result = await graphiti.add_episode(
                    name=ep_name,
                    episode_body=chunk,
                    source_description=ep_source,
                    reference_time=BOOK_PUBDATE,
                    source=EpisodeType.text,
                    group_id=PARTITION,
                    entity_types=ENTITY_TYPES,
                    edge_types=EDGE_TYPES,
                    edge_type_map=EDGE_TYPE_MAP,
                    custom_extraction_instructions=EXTRACTION_INSTRUCTIONS,
                    saga=SAGA_NAME,
                    saga_previous_episode_uuid=prev_episode_uuid,
                )
                prev_episode_uuid = result.episode.uuid
                written += 1
                chapter_info["episodes_written"] += 1
                if verbose:
                    logger.info(
                        "    nodes=%d edges=%d",
                        len(result.nodes),
                        len(result.edges),
                    )
                    for node in result.nodes:
                        logger.info("      NODE %s [%s]", node.name, node.labels)
                    for edge in result.edges:
                        logger.info(
                            "      EDGE %s → %s : %s",
                            edge.source_node_uuid[:8],
                            edge.target_node_uuid[:8],
                            edge.name,
                        )

            # ── 词汇对照 episode（每章一条，追加在正文之后）──────────────
            if with_glossary:
                logger.info("  → generating bilingual glossary for Ch.%d …", ch["number"])
                glossary_body = await _generate_chapter_glossary_body(
                    ch["number"], ch["title"], ch["body"], cfg
                )
                if glossary_body:
                    glossary_result = await graphiti.add_episode(
                        name=f"Bilingual Glossary Ch.{ch['number']}: {ch['title']}",
                        episode_body=glossary_body,
                        source_description=(
                            f"中英双语词汇对照 — 第{ch['number']}章：{ch['title']} | "
                            f"The Ladies' Book of Etiquette (1860), Ch.{ch['number']} Glossary"
                        ),
                        reference_time=BOOK_PUBDATE,
                        source=EpisodeType.text,
                        group_id=PARTITION,
                        entity_types=ENTITY_TYPES,
                        edge_types=EDGE_TYPES,
                        edge_type_map=EDGE_TYPE_MAP,
                        custom_extraction_instructions=glossary_extract_instructions,
                        saga=SAGA_NAME,
                        saga_previous_episode_uuid=prev_episode_uuid,
                    )
                    prev_episode_uuid = glossary_result.episode.uuid
                    written += 1
                    chapter_info["glossary_written"] = True
                    if verbose:
                        logger.info(
                            "    glossary nodes=%d edges=%d",
                            len(glossary_result.nodes),
                            len(glossary_result.edges),
                        )

            summary["chapters"].append(chapter_info)

        summary["written"] = written
    finally:
        try:
            await graphiti.close()
        except Exception:
            pass

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="解析分块，不写 Graphiti")
    mode.add_argument("--apply", action="store_true", help="实际写入 Graphiti")
    p.add_argument(
        "--chapters", nargs="+", type=int, metavar="N",
        help="仅导入指定章节编号（阿拉伯数字，如 --chapters 1 2 5）",
    )
    p.add_argument("--verbose", "-v", action="store_true", help="打印每 episode 提取到的节点/边")
    p.add_argument(
        "--with-glossary",
        action="store_true",
        help="额外为每章生成中英双语词汇对照 episode（默认不生成，保持全书 76 个正文 sub-episode）",
    )
    p.add_argument(
        "--no-glossary",
        action="store_true",
        help="兼容旧参数；默认已不生成 glossary episode",
    )
    args = p.parse_args()

    asyncio.run(import_book(
        chapters_filter=args.chapters,
        dry_run=args.dry_run,
        verbose=args.verbose,
        with_glossary=args.with_glossary and not args.no_glossary,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
