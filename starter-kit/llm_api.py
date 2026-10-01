#!/usr/bin/env python3
"""llm_api.py — the one place CLARK talks to an OpenAI-compatible model API.

Part of CLARK (claude-language-assessment-research-kit). Standard library only — no installs.

Imported by the two audit scripts (`review_audit.py`, `manuscript_audit.py`) so that the
request shape, the response parsing and the error messages cannot drift apart between them.
Nothing here writes a file or makes a decision: it builds a request, reads a reply, and
raises a legible error.

Two wire formats, chosen by the `api:` key in the conventions' `## Audit` block:

  chat       POST {base-url}/chat/completions   — the long-standing format every
             OpenAI-compatible provider speaks. **The default**; absent key means `chat`.
  responses  POST {base-url}/responses          — OpenAI's newer format. Opt in per project.

Why opt-in rather than a swap. OpenAI recommends Responses for new projects but keeps Chat
Completions supported, so there is no deadline. More to the point, `base-url` may be any
OpenAI-compatible endpoint, and providers differ underneath an identical-looking surface:
DeepSeek, for instance, does serve `/responses`, but its own documentation says unsupported
parameters "are silently ignored and do not cause errors", and it accepts only a subset of
the reasoning-effort values. A silent behaviour change is worse than a loud failure, so the
format is always a recorded, deliberate choice — and the report stamps which one ran.

Verified against OpenAI's documentation on 2026-10-01 (the docs now live under
developers.openai.com; platform.openai.com/docs/* redirects there).

Self-test:  python3 llm_api.py --selftest     (parses saved fixtures; makes no network call)
"""
import json
import sys
import urllib.error
import urllib.request

APIS = ("chat", "responses")

# Effort values OpenAI documents for reasoning models. "Not all reasoning models support
# every value" — and other providers support fewer still, so this list only warns; the
# provider is the authority and rejects what it does not accept.
KNOWN_EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh", "max")


class LLMError(Exception):
    """A call that did not yield usable text. `retryable` distinguishes a blip from a config fault."""

    def __init__(self, message, retryable=False):
        super().__init__(message)
        self.retryable = retryable


# ---------- request ----------

def build_body(api, model, system, user, effort=None, temperature=None, max_output_tokens=None):
    """The request body for either format.

    `effort` and `temperature` are mutually exclusive: when an effort is set the sampling
    parameters are omitted, which is what OpenAI's own guidance asks for ("When reasoning
    effort is not `none`, remove `temperature`, `top_p`, and `top_logprobs`"). Temperature is
    sent ONLY when the project pinned one — never as a silent default.
    """
    if api not in APIS:
        raise LLMError(f"unknown api {api!r}: expected one of {' | '.join(APIS)}", retryable=False)
    if max_output_tokens is not None and max_output_tokens <= 0:
        raise LLMError(f"max-output-tokens must be a positive whole number, not {max_output_tokens}")
    if api == "chat":
        body = {"model": model,
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": user}]}
        if effort:
            body["reasoning_effort"] = effort
        elif temperature is not None:
            body["temperature"] = temperature
        if max_output_tokens:
            body["max_completion_tokens"] = max_output_tokens
        return body
    # responses: instructions = the system prompt, input = the user message, both top level.
    # store=False always — "Responses are stored by default … set `store: false`" — and these
    # payloads carry unpublished manuscripts and private review matrices.
    body = {"model": model, "instructions": system, "input": user, "store": False}
    if effort:
        body["reasoning"] = {"effort": effort}        # nested here; `reasoning_effort` is the chat spelling
    elif temperature is not None:
        body["temperature"] = temperature
    if max_output_tokens:
        body["max_output_tokens"] = max_output_tokens
    return body


def endpoint(base_url, api):
    return base_url.rstrip("/") + ("/responses" if api == "responses" else "/chat/completions")


# ---------- response ----------

def _usage(usage, in_key, out_key, details_key):
    usage = usage or {}
    detail = usage.get(details_key) or {}
    return (usage.get(in_key) or 0, usage.get(out_key) or 0, detail.get("reasoning_tokens") or 0)


def parse_reply(api, data):
    """(text, input_tokens, output_tokens, reasoning_tokens) — or LLMError explaining why not."""
    if api not in APIS:
        raise LLMError(f"unknown api {api!r}: expected one of {' | '.join(APIS)}")
    if api == "chat":
        choices = data.get("choices") or []
        if not choices:
            raise LLMError("the provider returned a reply with no answer in it. If this repeats, check that "
                           "the model name in your conventions is one this provider serves.")
        msg = choices[0].get("message") or {}
        if msg.get("refusal"):
            raise LLMError(f"the model refused: {str(msg['refusal'])[:200]}")
        if choices[0].get("finish_reason") == "length":
            raise LLMError(
                "the reply was cut off at the token limit. Treat it as a failed call, not a short answer: "
                "what came back is incomplete, and you were billed for it. Raise `max-output-tokens` in the "
                "conventions (or remove it for the model's own maximum) and run it again.")
        text = msg.get("content")
        if not text:
            raise LLMError(f"the model returned an empty reply "
                           f"(the provider's stated reason: {choices[0].get('finish_reason', 'none given')})")
        return (text, *_usage(data.get("usage"), "prompt_tokens", "completion_tokens",
                              "completion_tokens_details"))

    # --- responses ---
    # A failed generation arrives as HTTP 200 with an error object in the body.
    err = data.get("error")
    if err and not isinstance(err, dict):      # some gateways return {"error": "<string>"} or a list
        err = {"message": str(err)}
    if err:
        raise LLMError(f"the provider reported a failed response: {err.get('code', '?')} — "
                       f"{str(err.get('message', ''))[:200]}",
                       retryable=str(err.get("code", "")) in ("server_error", "rate_limit_exceeded"))
    status = data.get("status")
    if status == "incomplete":
        reason = (data.get("incomplete_details") or {}).get("reason") or "unstated"
        raise LLMError(
            f"the response was truncated before it finished (reason: {reason}). Treat it as a failed "
            "call, not a short answer: output may be empty while input and reasoning tokens were still "
            "billed. Raise `max-output-tokens`, or lower the effort, and run it again.")
    if status in ("queued", "in_progress"):
        raise LLMError(f"the provider accepted the request but has not finished it (status: {status}). "
                       f"This script waits for a complete answer rather than polling; try again.",
                       retryable=True)
    if status not in ("completed", None):
        raise LLMError(f"the provider reported the request as '{status}' without saying why. Nothing usable "
                       f"came back; try again, and if it persists check your account status with the provider.")

    # Walk output[] by type. Never index output[0]: "the length and order of items in the
    # output array is dependent on the model's response", and reasoning items may precede
    # the message — or be absent entirely.
    texts, refusals = [], []
    for item in data.get("output") or []:
        if item.get("type") != "message":
            continue                                   # reasoning items and tool calls are not the answer
        for part in item.get("content") or []:
            kind = part.get("type")
            if kind == "output_text":
                texts.append(part.get("text") or "")
            elif kind == "refusal":
                refusals.append(part.get("refusal") or part.get("text") or "(no reason given)")
    if refusals and not any(t.strip() for t in texts):
        raise LLMError(f"the model refused: {str(refusals[0])[:200]}")
    if not any(t.strip() for t in texts):
        raise LLMError("the model spent its turn thinking and produced no answer text. Raise the output "
                       "limit, or lower the reasoning effort, and run it again.")
    return ("".join(texts), *_usage(data.get("usage"), "input_tokens", "output_tokens",
                                    "output_tokens_details"))


def describe_http_error(e):
    """Turn an HTTPError into something a user can act on — naming the offending field when the body does."""
    try:
        payload = json.loads(e.read().decode())
        err = payload.get("error") or payload
        if not isinstance(err, dict):          # {"error": "Authentication Fails"} is a common shape
            err = {"message": str(err)}
    except Exception:
        return LLMError(f"HTTP {e.code} from the provider (no readable error body)",
                        retryable=e.code in (429, 500, 502, 503, 504))
    bits = [str(err.get("message") or "the provider gave no explanation")[:300]]
    if err.get("param"):
        bits.append(f"offending parameter: `{err['param']}`")
    if err.get("code"):
        bits.append(f"code: {err['code']}")
    return LLMError(f"HTTP {e.code} — " + " · ".join(b for b in bits if b),
                    retryable=e.code in (429, 500, 502, 503, 504))


# ---------- the call ----------

def call(base_url, key, api, model, system, user,
         effort=None, temperature=None, max_output_tokens=None, timeout=180):
    body = build_body(api, model, system, user, effort, temperature, max_output_tokens)
    req = urllib.request.Request(
        endpoint(base_url, api),
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:                 # HTTPError is a URLError subclass: catch it first
        raise describe_http_error(e) from e
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise LLMError(f"could not reach {base_url} — check the address, your connection, and any proxy "
                       f"or VPN. ({e})", retryable=True) from e
    except json.JSONDecodeError as e:
        raise LLMError(f"the provider replied with something that is not JSON — this usually means the "
                       f"base-url points at a web page rather than an API endpoint. ({e})",
                       retryable=True) from e
    except Exception as e:
        # urlopen only wraps failures up to the point it returns; a connection dropped or a chunk
        # mangled *while reading* the body arrives as anything at all. One row must never end a census.
        raise LLMError(f"the reply could not be read to the end ({type(e).__name__}: {e})",
                       retryable=True) from e
    return parse_reply(api, data)


def stamp(api, effort=None, temperature=None, cli_override=False):
    """The one-line provenance string both reports print: which format, which sampling control."""
    if effort:
        sampling = f"effort {effort}" + (" (CLI override)" if cli_override else "")
    elif temperature is not None:
        sampling = f"temperature {temperature}"
    else:
        sampling = "provider defaults"
    return f"api {api}" + (" (storage opt-out sent)" if api == "responses" else "") + f" · {sampling}"


# ---------- self-test (no network) ----------

FIXTURES = {
    # --- responses: the happy paths ---
    "responses · reasoning item then message": ("responses", {
        "id": "resp_1", "object": "response", "status": "completed", "model": "gpt-5.5",
        "output": [
            {"id": "rs_1", "type": "reasoning", "content": [], "summary": []},
            {"id": "msg_1", "type": "message", "status": "completed", "role": "assistant",
             "content": [{"type": "output_text", "annotations": [], "text": '{"verdict":"agree"}'}]},
        ],
        "usage": {"input_tokens": 75, "input_tokens_details": {"cached_tokens": 0},
                  "output_tokens": 1186, "output_tokens_details": {"reasoning_tokens": 1024},
                  "total_tokens": 1261},
    }, {"text": '{"verdict":"agree"}', "in": 75, "out": 1186, "reasoning": 1024}),

    "responses · message only (no reasoning item)": ("responses", {
        "status": "completed",
        "output": [{"type": "message", "role": "assistant",
                    "content": [{"type": "output_text", "text": "OK"}]}],
        "usage": {"input_tokens": 13, "output_tokens": 4},
    }, {"text": "OK", "in": 13, "out": 4, "reasoning": 0}),

    "responses · two message items are joined in order": ("responses", {
        "status": "completed",
        "output": [{"type": "message", "content": [{"type": "output_text", "text": "part one "}]},
                   {"type": "message", "content": [{"type": "output_text", "text": "part two"}]}],
    }, {"text": "part one part two", "in": 0, "out": 0, "reasoning": 0}),

    "responses · usage is null → counts default to 0": ("responses", {
        "status": "completed", "usage": None,
        "output": [{"type": "message", "content": [{"type": "output_text", "text": "x"}]}],
    }, {"text": "x", "in": 0, "out": 0, "reasoning": 0}),

    # --- responses: every way it can fail ---
    "responses · truncated → must fail": ("responses", {
        "status": "incomplete", "incomplete_details": {"reason": "max_output_tokens"},
        "output": [{"type": "reasoning", "content": [], "summary": []}],
        "usage": {"input_tokens": 900, "output_tokens": 4096,
                  "output_tokens_details": {"reasoning_tokens": 4096}},
    }, {"error": "truncated"}),

    "responses · incomplete with no reason → must still fail": ("responses", {
        "status": "incomplete", "incomplete_details": {}, "output": [],
    }, {"error": "unstated"}),

    "responses · incomplete with no details object at all": ("responses", {
        "status": "incomplete", "output": [],
    }, {"error": "unstated"}),

    "responses · content_filter is a truncation reason too": ("responses", {
        "status": "incomplete", "incomplete_details": {"reason": "content_filter"}, "output": [],
    }, {"error": "content_filter"}),

    "responses · in-body error on a 200 → must fail": ("responses", {
        "status": "failed", "error": {"code": "server_error", "message": "upstream hiccup"},
    }, {"error": "failed response"}),

    "responses · error as a bare string → must fail, not crash": ("responses", {
        "status": "failed", "error": "Authentication Fails",
    }, {"error": "Authentication Fails"}),

    "responses · failed with no error object": ("responses", {
        "status": "failed", "output": [],
    }, {"error": "without saying why"}),

    "responses · still queued → retryable failure": ("responses", {
        "status": "queued",
    }, {"error": "has not finished"}),

    "responses · refusal → must fail, not return empty": ("responses", {
        "status": "completed",
        "output": [{"type": "message", "role": "assistant",
                    "content": [{"type": "refusal", "refusal": "I can't help with that."}]}],
    }, {"error": "refused"}),

    "responses · output absent entirely": ("responses", {"status": "completed"}, {"error": "no answer text"}),

    "responses · output present but empty": ("responses", {"status": "completed", "output": []},
                                             {"error": "no answer text"}),

    "responses · message item with an empty content list": ("responses", {
        "status": "completed", "output": [{"type": "message", "content": []}],
    }, {"error": "no answer text"}),

    "responses · only a reasoning item, no message": ("responses", {
        "status": "completed",
        "output": [{"type": "reasoning", "content": [{"type": "reasoning_text", "text": "thinking"}]}],
    }, {"error": "no answer text"}),

    # --- chat ---
    "chat · normal": ("chat", {
        "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": "{\"ok\":1}"}}],
        "usage": {"prompt_tokens": 50, "completion_tokens": 7},
    }, {"text": '{"ok":1}', "in": 50, "out": 7, "reasoning": 0}),

    "chat · reasoning tokens are read from completion_tokens_details": ("chat", {
        "choices": [{"finish_reason": "stop", "message": {"content": "ok"}}],
        "usage": {"prompt_tokens": 9, "completion_tokens": 300,
                  "completion_tokens_details": {"reasoning_tokens": 256}},
    }, {"text": "ok", "in": 9, "out": 300, "reasoning": 256}),

    "chat · usage absent → counts default to 0": ("chat", {
        "choices": [{"message": {"content": "hi"}}],
    }, {"text": "hi", "in": 0, "out": 0, "reasoning": 0}),

    "chat · cut off at the limit → must fail, not return a fragment": ("chat", {
        "choices": [{"finish_reason": "length", "message": {"content": '{"part'}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 99},
    }, {"error": "cut off"}),

    "chat · empty content with a normal finish → must fail": ("chat", {
        "choices": [{"finish_reason": "stop", "message": {"content": ""}}],
    }, {"error": "empty reply"}),

    "chat · refusal → must fail": ("chat", {
        "choices": [{"message": {"refusal": "I can't help with that."}}],
    }, {"error": "refused"}),

    "chat · no choices at all": ("chat", {"usage": {}}, {"error": "no answer in it"}),
}

# (name, body-or-exception, fields that must equal, field names that must be ABSENT)
SHAPES = [
    ("chat · nothing pinned → no sampling field at all",
     build_body("chat", "m", "sys", "usr"), {},
     ("temperature", "reasoning_effort", "reasoning", "store", "instructions", "max_completion_tokens")),
    ("responses · nothing pinned → still opts out of storage",
     build_body("responses", "m", "sys", "usr"), {"store": False, "instructions": "sys", "input": "usr"},
     ("temperature", "reasoning", "reasoning_effort", "messages", "max_output_tokens")),
    ("chat · effort only", build_body("chat", "m", "sys", "usr", effort="low"),
     {"reasoning_effort": "low"}, ("temperature", "reasoning", "instructions", "store")),
    ("chat · temperature only", build_body("chat", "m", "sys", "usr", temperature=0),
     {"temperature": 0}, ("reasoning_effort", "reasoning")),
    ("chat · BOTH pinned → effort wins, temperature dropped",
     build_body("chat", "m", "sys", "usr", effort="low", temperature=0),
     {"reasoning_effort": "low"}, ("temperature",)),
    ("responses · BOTH pinned → effort wins, temperature dropped",
     build_body("responses", "m", "sys", "usr", effort="high", temperature=0),
     {"reasoning": {"effort": "high"}}, ("temperature",)),
    ("responses · effort nests under reasoning",
     build_body("responses", "m", "sys", "usr", effort="high"),
     {"reasoning": {"effort": "high"}, "store": False, "instructions": "sys", "input": "usr"},
     ("temperature", "reasoning_effort", "messages")),
    ("responses · temperature only", build_body("responses", "m", "sys", "usr", temperature=0.2),
     {"temperature": 0.2, "store": False}, ("reasoning", "messages")),
    ("chat · cap uses max_completion_tokens",
     build_body("chat", "m", "sys", "usr", effort="low", max_output_tokens=25000),
     {"max_completion_tokens": 25000}, ("max_tokens", "max_output_tokens")),
    ("responses · cap uses max_output_tokens",
     build_body("responses", "m", "sys", "usr", effort="low", max_output_tokens=25000),
     {"max_output_tokens": 25000}, ("max_tokens", "max_completion_tokens")),
]


def selftest():
    ok = True
    for name, (api, payload, want) in FIXTURES.items():
        try:
            text, tin, tout, treason = parse_reply(api, payload)
            got_err = None
        except LLMError as e:
            text = tin = tout = treason = None
            got_err = str(e)
        if "error" in want:
            passed = got_err is not None and want["error"].lower() in got_err.lower()
            detail = f"raised: {got_err[:88]}" if got_err else f"NO ERROR — returned {text!r}"
        else:
            passed = (got_err is None and text == want["text"] and tin == want["in"]
                      and tout == want["out"] and treason == want["reasoning"])
            detail = (f"raised: {got_err[:88]}" if got_err
                      else f"text={text!r} usage={tin}/{tout} reasoning={treason}")
        ok = ok and passed
        print(f"[{'PASS' if passed else 'FAIL'}] {name}\n        {detail}")

    for name, body, must, must_not in SHAPES:
        bad = [f"{k}={body.get(k)!r} (wanted {v!r})" for k, v in must.items() if body.get(k) != v]
        bad += [f"{k} should be absent" for k in must_not if k in body]
        ok = ok and not bad
        print(f"[{'PASS' if not bad else 'FAIL'}] shape · {name}" + (f"\n        {bad}" if bad else ""))

    for name, fn in (("unknown api is refused", lambda: build_body("nope", "m", "s", "u")),
                     ("a zero cap is refused", lambda: build_body("chat", "m", "s", "u", max_output_tokens=0)),
                     ("a negative cap is refused", lambda: build_body("chat", "m", "s", "u", max_output_tokens=-5)),
                     ("parse_reply refuses an unknown api", lambda: parse_reply("nope", {}))):
        try:
            fn()
            raised = False
        except LLMError:
            raised = True
        ok = ok and raised
        print(f"[{'PASS' if raised else 'FAIL'}] guard · {name}")

    for api in APIS:
        got = endpoint("https://api.example.com/v1/", api)
        want = "https://api.example.com/v1" + ("/responses" if api == "responses" else "/chat/completions")
        ok = ok and got == want
        print(f"[{'PASS' if got == want else 'FAIL'}] endpoint · {api} → {got}")
    return ok


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    sys.exit(__doc__)
