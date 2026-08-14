# Voices

Monarch Video narrates with the local Kokoro-82M neural model (via `hyperframes tts`).
No API key, no network TTS vendor. First run downloads ~27 MB of model data.

## Named profiles

Set the storyboard `"voice"` field to one of these, or pass any raw Kokoro voice id.

| Profile | Kokoro voice | Best for |
|---|---|---|
| `warm` *(default)* | `af_heart` | customer-facing, prospect videos, LinkedIn |
| `pro` | `af_nova` | product explainers — neutral, crisp |
| `bright` | `af_sky` | social, event promos — upbeat |
| `direct` | `am_michael` | executive comms, brand overviews (male) |
| `narrator` | `am_adam` | thought leadership, spotlights (male) |
| `uk-f` / `uk-m` | `bf_emma` / `bm_george` | UK audiences |

## Raw Kokoro ids

Any other `voice` value is passed straight through, e.g. `"voice": "af_bella"`.
Run `hyperframes tts --list` to see every voice the installed model supports
(typically `af_heart`, `af_nova`, `af_sky`, `am_adam`, `am_michael`, `bf_emma`,
`bf_isabella`, `bm_george`, plus several more languages).

## Speed

`voiceover.py` accepts `--speed` (default 1.0). Lower than 1.0 is slower and calmer;
higher is faster. Speed is a narration-level knob — it re-times scenes to whatever
the synthesized clip actually measures.

## Where the model runs

`hyperframes tts` shells out to a local Python that imports `kokoro_onnx`. On macOS
with externally-managed Python, install into a dedicated venv and point the build at it:

```bash
uv venv ~/.venvs/kokoro --python 3.11
uv pip install --python ~/.venvs/kokoro/bin/python kokoro-onnx soundfile
export HYPERFRAMES_PYTHON="$HOME/.venvs/kokoro/bin/python"
```

On a plain sandbox, `pip install kokoro-onnx soundfile` (add `--break-system-packages`
where required) is enough.
